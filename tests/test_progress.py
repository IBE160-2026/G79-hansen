"""Progress wire/auth/lifecycle tests. Actual SQL races are checked separately."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4
import pytest
from test_documents import setup, draft, post


def fixture(tmp_path):
    client, headers, model, repository, storage = setup(tmp_path)
    model.result['flashcards'] *= 2; model.result['quiz'] *= 2
    body = draft(client, headers)
    assert post(client, headers, body).json()['progressRevision'] == 1
    read = {'schemaVersion':'1.0','documentId':body['documentId'],'generationId':body['bundle']['generationId']}
    write = read | {'mutationId':str(uuid4()),'expectedProgressRevision':1,'positions':{
        'flashcardId':body['bundle']['flashcards'][1]['id'],'quizId':body['bundle']['quiz'][0]['id']}}
    return client,headers,model,repository,storage,body,read,write


def progress(client,headers,payload,action='write'):
    return client.post('/api/v1/progress/'+action,headers=headers,json=payload)


def test_independent_positions_revision_replay_restart_and_no_inference(tmp_path):
    client,headers,model,repository,storage,body,read,write = fixture(tmp_path)
    before = len(model.calls)
    saved = progress(client,headers,write)
    assert saved.status_code == 200 and saved.json()['progressRevision'] == 2
    assert saved.headers['cache-control'] == 'no-store'
    assert progress(client,headers,write).json() == saved.json()
    assert len(repository.progress_mutations) == 1
    fresh,new_headers,new_model,_,_ = setup(tmp_path,repository,storage)
    reopened = post(fresh,new_headers,{'schemaVersion':'1.0','documentId':body['documentId']},'reload').json()
    assert reopened['positions'] == write['positions'] and reopened['progressRevision'] == 2
    assert progress(fresh,new_headers,read,'read').json() == saved.json()
    assert len(model.calls) == before and not new_model.calls
    # Save replay retains its original initial revision instead of adopting 2.
    assert post(client,headers,body).json()['progressRevision'] == 1


def test_lost_success_replays_once_without_second_revision(tmp_path):
    client,headers,_,repository,_,_,_,write = fixture(tmp_path)
    repository.lose_progress_reply = True
    assert progress(client,headers,write).json()['code'] == 'progress_pending'
    assert progress(client,headers,write).json()['progressRevision'] == 2
    assert next(iter(repository.documents.values()))['progressRevision'] == 2
    assert len(repository.progress_mutations) == 1


def test_conflict_durable_until_explicit_read_then_backward_navigation(tmp_path):
    client,headers,_,_,_,body,read,write = fixture(tmp_path)
    assert progress(client,headers,write).status_code == 200
    stale = write | {'mutationId':str(uuid4()),'positions':body['positions']}
    assert progress(client,headers,stale).json()['code'] == 'progress_conflict'
    latest = progress(client,headers,read,'read').json()
    backwards = stale | {'mutationId':str(uuid4()),'expectedProgressRevision':latest['progressRevision']}
    assert progress(client,headers,backwards).json()['progressRevision'] == 3
    assert progress(client,headers,stale).json()['code'] == 'progress_conflict'


@pytest.mark.parametrize('change',['positions','expectedProgressRevision','documentId'])
def test_mutation_id_reuse_is_bound_to_entire_request(tmp_path,change):
    client,headers,_,repository,_,body,_,write = fixture(tmp_path)
    assert progress(client,headers,write).status_code == 200
    changed = deepcopy(write)
    if change == 'positions': changed['positions'] = body['positions']
    if change == 'expectedProgressRevision': changed[change] = 2
    if change == 'documentId':
        key = next(iter(repository.documents)); new_id = str(uuid4())
        repository.documents[key[0],new_id] = deepcopy(repository.documents[key]) | {'documentId':new_id}
        changed[change] = new_id
    assert progress(client,headers,changed).json()['code'] == 'progress_mismatch'


@pytest.mark.parametrize('state',['unknown','foreign','deleting','pending','generation','item','null'])
def test_lifecycle_membership_and_owner_cannot_create_progress(tmp_path,state):
    client,headers,_,repository,_,_,read,write = fixture(tmp_path)
    key = next(iter(repository.documents)); document = repository.documents[key]
    if state == 'unknown': repository.documents.clear()
    if state == 'foreign': repository.documents['foreign',key[1]] = repository.documents.pop(key)
    if state in {'deleting','pending'}: document['status'] = state
    if state == 'generation': document['generationId'] = str(uuid4())
    if state == 'item': write['positions']['quizId'] = 'not-a-current-item'
    if state == 'null': write['positions']['quizId'] = None
    assert progress(client,headers,write).status_code in (404,409)
    assert not repository.progress_mutations
    if state not in {'item','null'}: assert progress(client,headers,read,'read').status_code in (404,409)


def test_current_generation_checked_before_completed_replay(tmp_path):
    client,headers,_,repository,_,_,_,write = fixture(tmp_path)
    assert progress(client,headers,write).status_code == 200
    next(iter(repository.documents.values()))['generationId'] = str(uuid4())
    assert progress(client,headers,write).json()['code'] == 'progress_generation'


def test_empty_sections_require_null_positions(tmp_path):
    client,headers,_,repository,_,_,_,write = fixture(tmp_path)
    saved = next(iter(repository.documents.values()))
    saved['bundle']['quiz'] = []; saved['positions']['quizId'] = None
    assert progress(client,headers,write).json()['code'] == 'progress_mismatch'
    write['positions']['quizId'] = None
    assert progress(client,headers,write).json()['positions']['quizId'] is None


@pytest.mark.parametrize('action',['write','read'])
def test_auth_csrf_view_backend_and_bounds_before_provider(tmp_path,action):
    client,headers,_,repository,_,_,read,write = fixture(tmp_path)
    payload = write if action == 'write' else read
    before = len(repository.calls)
    for bad in ({},headers|{'X-CSRF-Token':'wrong'},headers|{'X-Session-View':'old'}):
        assert progress(client,bad,payload,action).status_code in (401,403)
    assert client.post('/api/v1/progress/'+action,headers=headers|{'Content-Type':'application/json','Content-Length':'4097'},content=b'{}').status_code == 413
    assert len(repository.calls) == before
    client.app.state.documents_injected = False
    assert progress(client,headers,payload,action).json()['code'] == 'save_unavailable'


@pytest.mark.parametrize('change',['owner','rpc','revisionType','missingId','tooLongId','extraPosition'])
def test_strict_owner_free_dto(tmp_path,change):
    client,headers,_,repository,_,_,_,write = fixture(tmp_path)
    if change == 'owner': write['ownerId'] = 'foreign'
    if change == 'rpc': write['action'] = 'commit'
    if change == 'revisionType': write['expectedProgressRevision'] = True
    if change == 'missingId': del write['positions']['quizId']
    if change == 'tooLongId': write['positions']['quizId'] = 'x'*101
    if change == 'extraPosition': write['positions']['index'] = 2
    before = len(repository.calls)
    assert progress(client,headers,write).status_code == 422
    assert len(repository.calls) == before
