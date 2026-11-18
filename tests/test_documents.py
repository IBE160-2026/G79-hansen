"""Injected-port lifecycle evidence. These tests do not establish SQL/Storage isolation."""
import asyncio
import base64
from datetime import datetime, timezone
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from threading import Event, RLock
import time
from uuid import uuid4
import httpx
import pytest
from fastapi.testclient import TestClient
from app.adapters.documents import DocumentFailure, SupabaseDocuments
from app.adapters.storage import SupabaseStorage
from app.contracts.documents import SaveRequest, snapshot, snapshot_digest
from app.main import create_app
from app.services.documents import Documents, SaveAdmission
from app.services.model_budget import ModelBudget
from test_auth import FakeAuth, SETTINGS, ORIGIN, session_cookie
from test_sources import login
from test_generation import Model, extract, generate, WORKSPACE


class MemoryRepository:
    """Durable-in-fixture state survives app reconstruction; all content is synthetic."""
    def __init__(self):
        self.operations, self.documents, self.objects = {}, {}, {}
        self.calls, self.hook, self.fail_action = [], None, None
        self.lose_ready_reply = False
        self.progress_mutations = {}
        self.lose_progress_reply = False
        self.clock = time.time
        self.lock = RLock()

    def call(self, identity, action, payload, deadline):
        if self.hook:
            self.hook(action)
        if action == self.fail_action:
            self.fail_action = None
            raise DocumentFailure()
        with self.lock:
            self.calls.append(action)
            owner = identity.owner_id
            if action in {'progress_read', 'progress_write'}:
                saved = self.documents.get((owner, payload['documentId']))
                if not saved or saved.get('status') != 'ready': raise DocumentFailure('document_unknown')
                if saved['generationId'] != payload['generationId']: raise DocumentFailure('progress_generation')
                def result():
                    return deepcopy({key:saved[key] for key in ('schemaVersion','documentId','generationId','progressRevision','positions')})
                if action == 'progress_read': return result()
                mutation_key = owner,payload['mutationId']
                for section,key in (('flashcards','flashcardId'),('quiz','quizId')):
                    if payload['positions'][key] not in ({item['id'] for item in saved['bundle'][section]} or {None}):
                        raise DocumentFailure('progress_mismatch')
                previous = self.progress_mutations.get(mutation_key)
                if previous:
                    if previous['request'] != payload: raise DocumentFailure('progress_mismatch')
                    if 'error' in previous['outcome']: raise DocumentFailure(previous['outcome']['error'])
                    return deepcopy(previous['outcome'])
                if saved['progressRevision'] != payload['expectedProgressRevision']:
                    self.progress_mutations[mutation_key] = {'request':deepcopy(payload),'outcome':{'error':'progress_conflict'}}
                    raise DocumentFailure('progress_conflict')
                saved['positions'] = deepcopy(payload['positions']); saved['progressRevision'] += 1
                outcome = result()
                self.progress_mutations[mutation_key] = {'request':deepcopy(payload),'outcome':deepcopy(outcome)}
                if self.lose_progress_reply:
                    self.lose_progress_reply = False
                    raise DocumentFailure('progress_pending')
                return outcome
            key = owner, payload.get('operationId')
            operation = self.operations.get(key)
            for (own, _), value in self.operations.items():
                if own == owner and value['status'] in ('pending','conflict','cancelled') and value['expires'] <= self.clock():
                    value['status'], value['snapshot'] = 'expired', None
                    value['cleanupNeeded'] = bool(value.get('objectKey'))
            if operation and 'digest' in payload and payload['digest'] != operation['digest']:
                raise DocumentFailure('save_mismatch')
            if action == 'get':
                return {'operation': deepcopy(operation)}
            if action == 'pending':
                return {'schemaVersion': '1.0', 'operations': [{k: v for k, v in value.items() if k in
                    ('operationId', 'documentId', 'digest', 'status')} | {'requiresFile': value['status']=='pending' and bool(value.get('objectKey')),
                    'cleanupOnly':bool(value.get('cleanupNeeded')),
                    'recoveryState':'cleanup_only' if value.get('cleanupNeeded') else value['status'],
                    'title':value['snapshot']['title'] if value['status']=='pending' else None,
                    'admittedAt':datetime.fromtimestamp(value['expires']-604800,timezone.utc).isoformat(),
                    'expiresAt':datetime.fromtimestamp(value['expires'],timezone.utc).isoformat(),
                    'outcome':value.get('outcome') if value['status']=='ready' else None}
                    for (own, _), value in self.operations.items() if own == owner and
                    (value['status']=='pending' or (value['status']=='ready' and value['completed']+604800>self.clock()) or value.get('cleanupNeeded'))]}
            if action == 'library':
                rows = sorted((value for (own, document_id), value in self.documents.items() if own == owner and
                    value.get('status') == 'ready' and (not payload.get('cursor') or document_id > payload['cursor'])), key=lambda value: value['documentId'])[:51]
                def position(value, section, key):
                    items = value['bundle'][section]
                    return {'ordinal':next((i+1 for i,item in enumerate(items) if item['id']==value['positions'][key]),None),'total':len(items)} if items else None
                return {'schemaVersion':'1.0','items':[{'documentId':value['documentId'],'title':value['title'],
                    'revision':value['revision'],'updatedAt':value['updatedAt'],'hasOriginalFile':bool(value.get('objectKey')),
                    'positions':{'flashcard':position(value,'flashcards','flashcardId'),'quiz':position(value,'quiz','quizId')}} for value in rows[:50]],
                    'nextCursor':rows[49]['documentId'] if len(rows)>50 else None}
            if action in {'reload', 'file'}:
                saved = self.documents.get((owner, payload['documentId']))
                if not saved or saved.get('status') != 'ready': raise DocumentFailure('document_unknown')
                if action == 'file':
                    if not saved.get('objectKey'): raise DocumentFailure('document_unknown')
                    return {key:saved[key] for key in ('documentId','generationId','revision','title','objectKey','fileHash','fileSize')} | {
                        'mediaType':'application/pdf' if saved['acceptance']['kind']=='pdf' else 'text/plain'}
                return deepcopy({key:saved[key] for key in ('schemaVersion','status','documentId','generationId','revision','progressRevision','title','acceptance','bundle','positions')})
            if action == 'admit':
                if operation:
                    return {'operation': deepcopy(operation)}
                frozen = deepcopy(payload['snapshot'])
                document = self.documents.get((owner, frozen['documentId']))
                if (document and frozen['expectedRevision'] is None) or (frozen['expectedRevision'] is not None and
                    (not document or document['revision'] != frozen['expectedRevision'])):
                    raise DocumentFailure('save_conflict')
                operation = {'operationId': payload['operationId'], 'documentId': frozen['documentId'], 'digest': payload['digest'],
                    'status': 'pending', 'snapshot': frozen, 'expires': self.clock()+604800, 'verified': False, 'cleanupNeeded':False,
                    'fileHash':frozen['fileHash'],'fileSize':frozen['fileSize'],
                    'objectKey': '/'.join((owner, frozen['documentId'], frozen['generationId'], payload['operationId'])) if frozen['fileHash'] else None,
                    'mediaType': 'application/pdf' if frozen['acceptance']['kind'] == 'pdf' else 'text/plain'}
                self.operations[key] = operation
                return {'operation': deepcopy(operation)}
            if not operation: raise DocumentFailure('save_unknown')
            if action == 'cancel':
                if operation['status'] == 'ready':
                    current = self.documents[(owner,operation['documentId'])].get('objectKey')
                    return {'cleanupKeys':[value['objectKey'] for (own,_),value in self.operations.items() if own==owner
                        and value['documentId']==operation['documentId'] and value.get('cleanupNeeded') and value.get('objectKey') != current]}
                if operation['status'] != 'ready':
                    operation['status'], operation['snapshot'] = 'cancelled', None
                    operation['cleanupNeeded'] = bool(operation.get('objectKey'))
                return {'cleanupKeys': [operation['objectKey']] if operation.get('objectKey') else [],
                        'cleanupStatus':'cleanup_pending' if operation.get('objectKey') else 'cleanup_complete'}
            if operation['status'] == 'expired': raise DocumentFailure('save_expired')
            if action == 'attempt': return {'status': 'pending'}
            if action == 'verified':
                operation['verified'] = True
                return {'status': 'pending'}
            if action == 'commit':
                if operation['status'] == 'ready': return deepcopy(operation['outcome'])
                frozen = operation['snapshot']
                document_key = owner, frozen['documentId']
                previous = self.documents.get(document_key)
                if previous and previous['revision'] != frozen['expectedRevision']:
                    operation['status'],operation['snapshot'] = 'conflict',None
                    raise DocumentFailure('save_conflict')
                if operation['objectKey'] and not operation['verified']: raise DocumentFailure('file_required')
                revision = previous['revision']+1 if previous else 1
                for (own,_),value in self.operations.items():
                    if own==owner and value['documentId']==frozen['documentId'] and value['status']=='ready' and value.get('objectKey'):
                        value['cleanupNeeded']=True
                self.documents[document_key] = {**deepcopy(frozen), 'status': 'ready', 'revision': revision,'progressRevision':1,'objectKey':operation['objectKey'],
                    'updatedAt':datetime.fromtimestamp(self.clock(),timezone.utc).isoformat()}
                outcome = {'schemaVersion': '1.0', 'status': 'ready', 'operationId': payload['operationId'],
                    'documentId': frozen['documentId'], 'generationId': frozen['generationId'], 'digest': operation['digest'],
                    'revision': revision, 'progressRevision':1, 'cleanupStatus': 'pending' if operation['objectKey'] else 'complete'}
                operation.update(status='ready', outcome=outcome, snapshot=None, completed=self.clock())
                if self.lose_ready_reply:
                    self.lose_ready_reply = False
                    raise DocumentFailure()
                return deepcopy(outcome)
            raise AssertionError(action)


class MemoryStorage:
    def __init__(self):
        self.objects, self.uploads, self.deletes = {}, [], []
        self.lose_reply = False
        self.fail_before_upload = False

    def upload(self, identity, operation, content, deadline):
        if self.fail_before_upload:
            self.fail_before_upload = False
            raise DocumentFailure()
        self.uploads.append(operation['objectKey'])
        self.objects.setdefault(operation['objectKey'], content)
        if self.lose_reply:
            self.lose_reply = False
            raise DocumentFailure()

    def verify(self, identity, operation, deadline):
        import hashlib
        content = self.objects.get(operation['objectKey'])
        if content is None: raise DocumentFailure('file_required')
        if len(content) != operation['snapshot']['fileSize'] or hashlib.sha256(content).hexdigest() != operation['snapshot']['fileHash']:
            raise DocumentFailure('save_mismatch')

    def download(self, identity, descriptor, deadline):
        self.verify(identity, {'objectKey':descriptor['objectKey'],'snapshot':descriptor}, deadline)
        return self.objects[descriptor['objectKey']]

    def delete(self, identity, key, deadline):
        self.deletes.append(key)
        self.objects.pop(key, None)


def setup(tmp_path, repository=None, storage=None):
    repository, storage = repository or MemoryRepository(), storage or MemoryStorage()
    path = tmp_path / (str(uuid4())+'.json')
    ModelBudget.initialize(path)
    model = Model()
    app = create_app(SETTINGS, auth_adapter=FakeAuth(), model_adapter=model, model_budget=ModelBudget(path),
                     documents_repository=repository, storage_adapter=storage)
    client = TestClient(app, base_url=ORIGIN)
    return client, login(client), model, repository, storage


def draft(client, headers, **changes):
    content = changes.pop('file', None)
    acceptance = extract(client, headers, **({'kind': 'text-file', 'contentBase64': base64.b64encode(content).decode()} if content else {}))
    generated = generate(client, headers, acceptance).json()
    bundle = generated['bundle']
    result = {'schemaVersion': '1.0', 'operationId': str(uuid4()), 'documentId': str(uuid4()), 'expectedRevision': None,
        'acceptance': acceptance, 'bundle': bundle, 'receipt': generated['receipt'],
        'positions': {'flashcardId': bundle['flashcards'][0]['id'], 'quizId': bundle['quiz'][0]['id']}, **changes}
    if content: result['contentBase64'] = base64.b64encode(content).decode()
    return result


def post(client, headers, body, action='save'):
    return client.post('/api/v1/documents/'+action, headers=headers, json=body)


def test_explicit_save_atomic_snapshot_replay_and_no_new_model_call(tmp_path):
    client, headers, model, repository, _ = setup(tmp_path)
    model.result['flashcards'] *= 3
    model.result['quiz'] *= 3
    body = draft(client, headers, title='Privat 😀')
    body['positions'] = {'flashcardId':body['bundle']['flashcards'][1]['id'],
                         'quizId':body['bundle']['quiz'][2]['id']}
    assert not repository.operations
    response = post(client, headers, body)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result['status'] == 'ready' and result['revision'] == 1
    assert response.headers['cache-control'] == 'no-store'
    assert post(client, headers, body).json() == result
    assert len(repository.documents) == 1 and len(model.calls) == 1
    saved = next(iter(repository.documents.values()))
    assert saved['title'] == 'Privat 😀' and saved['positions'] == body['positions']
    assert saved['acceptance']['source'] == body['acceptance']['source']
    assert 'receipt' not in saved and 'sourceProof' not in saved['acceptance']


@pytest.mark.parametrize('change', ['receipt','source','bundle','position','file','title','extra'])
def test_invalid_authority_never_admitted(tmp_path, change):
    client, headers, _, repository, _ = setup(tmp_path)
    body = draft(client, headers)
    if change == 'receipt': body['receipt'] = 'bad'
    if change == 'source': body['acceptance']['source']['units'][0]['text'] = 'changed'
    if change == 'bundle': body['bundle']['summary'][0]['text'] = 'changed'
    if change == 'position': body['positions']['quizId'] = 'unknown'
    if change == 'file': body['contentBase64'] = 'YQ=='
    if change == 'title': body['title'] = '😀'*161
    if change == 'extra': body['ownerId'] = 'foreign'
    assert post(client, headers, body).status_code in (409,422)
    assert not repository.operations


def test_digest_captures_title_and_independent_positions(tmp_path):
    client, headers, _, _, _ = setup(tmp_path)
    body = draft(client, headers)
    value = snapshot(SaveRequest.model_validate(body), 'owner', None, None)
    base = snapshot_digest(value)
    assert snapshot_digest(value | {'title': 'Other'}) != base
    assert snapshot_digest(value | {'positions': {'flashcardId': None, 'quizId': None}}) != base
    assert snapshot_digest(dict(reversed(list(value.items())))) == base


def test_completed_replay_precedes_revoked_receipt_and_revision(tmp_path):
    client, headers, _, _, _ = setup(tmp_path)
    body = draft(client, headers)
    ready = post(client, headers, body).json()
    client.post('/api/v1/workspaces/invalidate', headers=headers, json={'schemaVersion':'1.0', 'workspaceId': WORKSPACE,
        'clientRevision': 1, 'commandSequence': 3})
    body['receipt'] = 'expired old proof'
    assert post(client, headers, body).json() == ready
    body['title'] = 'changed'
    assert post(client, headers, body).json()['code'] == 'save_mismatch'


def test_admitted_restart_recovery_with_fresh_login_without_receipt(tmp_path):
    client, headers, _, repository, storage = setup(tmp_path)
    body = draft(client, headers)
    repository.fail_action = 'commit'
    assert post(client, headers, body).json()['code'] == 'save_pending'
    operation = next(iter(repository.operations.values()))
    second, fresh, model, _, _ = setup(tmp_path, repository, storage)
    listing = post(second, fresh, {'schemaVersion':'1.0'}, 'pending').json()['operations']
    assert listing[0]['operationId'] == body['operationId'] and 'snapshot' not in listing[0]
    result = post(second, fresh, {'schemaVersion':'1.0', 'operationId':body['operationId'], 'digest':operation['digest']}, 'retry')
    assert result.json()['status'] == 'ready' and not model.calls
    assert len(repository.documents) == 1


@pytest.mark.parametrize('unknown', [True,False])
def test_unknown_and_foreign_recovery_do_not_admit(tmp_path, unknown):
    client, headers, _, repository, _ = setup(tmp_path)
    body = draft(client, headers)
    repository.fail_action = 'commit'
    post(client, headers, body)
    operation = next(iter(repository.operations.values()))
    if not unknown:
        key = next(iter(repository.operations)); repository.operations[('foreign',key[1])] = repository.operations.pop(key)
    response = post(client, headers, {'schemaVersion':'1.0', 'operationId':str(uuid4()) if unknown else body['operationId'],
                                     'digest':operation['digest']}, 'retry')
    assert response.json()['code'] == 'save_unknown' and not repository.documents


def test_expiry_erases_staging_and_cleanup_never_claims_physical_completion(tmp_path):
    client, headers, _, repository, storage = setup(tmp_path)
    body = draft(client, headers, file=b'Synthetic original source.')
    repository.fail_action = 'commit'
    post(client, headers, body)
    operation = next(iter(repository.operations.values()))
    repository.clock = lambda: time.time()+604801
    response = post(client, headers, {'schemaVersion':'1.0','operationId':body['operationId'],'digest':operation['digest']}, 'retry')
    assert response.json()['code'] == 'save_expired'
    assert operation['snapshot'] is None and not repository.documents
    cleanup = post(client, headers, {'schemaVersion':'1.0','operationId':body['operationId']},'cleanup').json()
    assert cleanup['status'] == 'cleanup_pending' and storage.deletes and repository.operations


def test_lost_upload_reply_reconciles_exact_bytes_and_no_second_upload(tmp_path):
    client, headers, model, repository, storage = setup(tmp_path)
    body = draft(client, headers, file=b'Synthetic original source.')
    storage.lose_reply = True
    assert post(client, headers, body).json()['code'] == 'save_pending'
    operation = next(iter(repository.operations.values()))
    retry = {'schemaVersion':'1.0','operationId':body['operationId'],'digest':operation['digest']}
    assert post(client, headers, retry | {'contentBase64':'d3Jvbmc='}, 'retry').json()['code'] == 'save_mismatch'
    assert post(client, headers, retry, 'retry').json()['status'] == 'ready'
    assert len(storage.uploads) == 1 and len(model.calls) == 1


def test_file_resupply_after_upload_failure_and_missing_readback(tmp_path):
    client, headers, _, repository, storage = setup(tmp_path)
    body = draft(client, headers, file=b'Synthetic original source.')
    original = storage.upload
    storage.upload = lambda *args: (_ for _ in ()).throw(DocumentFailure())
    assert post(client, headers, body).json()['code'] == 'save_pending'
    operation = next(iter(repository.operations.values()))
    retry = {'schemaVersion':'1.0','operationId':body['operationId'],'digest':operation['digest']}
    assert post(client, headers, retry, 'retry').json()['code'] == 'file_required'
    storage.upload = original
    assert post(client, headers, retry | {'contentBase64':body['contentBase64']}, 'retry').json()['status'] == 'ready'


def test_invalidation_wins_before_admission(tmp_path):
    client, headers, _, repository, _ = setup(tmp_path)
    body = draft(client, headers)
    client.post('/api/v1/workspaces/invalidate', headers=headers, json={'schemaVersion':'1.0','workspaceId':WORKSPACE,'clientRevision':1,'commandSequence':3})
    assert post(client, headers, body).json()['code'] == 'stale_workspace'
    assert not repository.operations


def test_admission_io_does_not_hold_auth_lock_and_logout_wins_display(tmp_path):
    client, headers, _, repository, _ = setup(tmp_path)
    body = draft(client, headers)
    entered, release = Event(), Event()
    def hook(action):
        if action == 'admit': entered.set(); assert release.wait(5)
    repository.hook = hook
    with ThreadPoolExecutor() as pool:
        future = pool.submit(post, client, headers, body)
        assert entered.wait(3)
        started = time.monotonic()
        response = client.post('/api/v1/auth/logout', headers=headers, json={})
        assert response.status_code == 200 and time.monotonic()-started < 1
        release.set()
        assert future.result().json()['code'] == 'session_ended'
    assert len(repository.documents) == 1  # The explicit already-dispatched action survives.


def test_logout_before_admission_dispatch_prevents_new_operation(tmp_path):
    client, headers, _, repository, _ = setup(tmp_path)
    body = draft(client, headers)
    registry = client.app.state.auth_registry
    def hook(action):
        if action == 'get':
            session = registry.live_session(session_cookie(client)); registry.terminate(session.browser_id)
    repository.hook = hook
    assert post(client, headers, body).json()['code'] == 'session_ended'
    assert not repository.operations


def test_owned_workspace_gate_orders_admission_before_invalidation(tmp_path):
    client, headers, _, repository, _ = setup(tmp_path)
    body = draft(client, headers)
    entered, release = Event(), Event()
    def hook(action):
        if action == 'admit': entered.set(); assert release.wait(5)
    repository.hook = hook
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=client.app),base_url=ORIGIN,cookies=client.cookies) as http:
            saving = asyncio.create_task(http.post('/api/v1/documents/save',headers=headers,json=body))
            while not entered.is_set(): await asyncio.sleep(.001)
            invalidating = asyncio.create_task(http.post('/api/v1/workspaces/invalidate',headers=headers,json={
                'schemaVersion':'1.0','workspaceId':WORKSPACE,'clientRevision':1,'commandSequence':3}))
            await asyncio.sleep(.03)
            assert not invalidating.done()
            # Auth lock is free while the workspace gate waits on remote IO.
            assert client.app.state.auth_registry.lock.acquire(blocking=False)
            client.app.state.auth_registry.lock.release()
            release.set()
            assert (await saving).json()['status'] == 'ready'
            assert (await invalidating).status_code == 200
    asyncio.run(run())


def test_http_timeout_retains_worker_permit_and_lost_reply_replays(tmp_path, monkeypatch):
    from app.api import documents as api
    monkeypatch.setattr(api, 'SAVE_SECONDS', .03)
    client, headers, _, repository, _ = setup(tmp_path)
    body = draft(client, headers)
    entered, release = Event(), Event()
    def hook(action):
        if action == 'commit': entered.set(); assert release.wait(5)
    repository.hook = hook
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=client.app),base_url=ORIGIN,cookies=client.cookies) as http:
            response = await http.post('/api/v1/documents/save',headers=headers,json=body)
            assert entered.is_set() and response.json()['code'] == 'save_pending'
            # No queued or duplicate work is admitted while the owned worker runs.
            assert (await http.post('/api/v1/documents/save',headers=headers,json=body)).json()['code'] == 'save_capacity'
            assert client.app.state.save_admission.tasks
            release.set()
            while client.app.state.save_admission.tasks: await asyncio.sleep(.001)
            assert (await http.post('/api/v1/documents/save',headers=headers,json=body)).json()['status'] == 'ready'
    asyncio.run(run())
    assert len(repository.documents)==1


def test_replacement_resets_positions_and_stale_target_keeps_draft(tmp_path):
    client, headers, model, repository, _ = setup(tmp_path)
    model.result['flashcards'] *= 3
    model.result['quiz'] *= 3
    first = draft(client, headers)
    ready = post(client, headers, first).json()
    # Generate a fresh revision through the real authority path.
    client.post('/api/v1/workspaces/invalidate', headers=headers,json={'schemaVersion':'1.0','workspaceId':WORKSPACE,'clientRevision':1,'commandSequence':3})
    accepted = extract(client, headers, sequence=4, revision=1)
    result = generate(client, headers, accepted, sequence=5).json()
    replacement = deepcopy(first) | {'operationId':str(uuid4()),'expectedRevision':1,'acceptance':accepted,
        'bundle':result['bundle'],'receipt':result['receipt'],
        'positions':{'flashcardId':result['bundle']['flashcards'][1]['id'],'quizId':result['bundle']['quiz'][2]['id']}}
    response = post(client, headers,replacement)
    assert response.status_code == 200 and response.json()['revision'] == 2
    saved = next(iter(repository.documents.values()))
    assert saved['positions'] == {'flashcardId':result['bundle']['flashcards'][0]['id'],
                                  'quizId':result['bundle']['quiz'][0]['id']}
    replacement['operationId'] = str(uuid4())
    assert post(client, headers,replacement).json()['code'] == 'save_conflict'
    reload = post(client, headers,{'schemaVersion':'1.0','documentId':first['documentId']},'reload').json()
    assert reload['revision'] == 2 and reload['bundle'] == result['bundle']


def test_superseded_ready_file_discovered_after_restart_and_cli_only_deletes_old_key(tmp_path,monkeypatch):
    from scripts import save_cleanup
    client, headers, _, repository, storage = setup(tmp_path)
    first=draft(client,headers,file=b'Synthetic first original.')
    assert post(client,headers,first).json()['status']=='ready'
    old_key=next(iter(repository.operations.values()))['objectKey']
    client.post('/api/v1/workspaces/invalidate',headers=headers,json={
        'schemaVersion':'1.0','workspaceId':WORKSPACE,'clientRevision':1,'commandSequence':3})
    original=base64.b64encode(b'Synthetic replacement original.').decode()
    accepted=extract(client,headers,sequence=4,revision=1,kind='text-file',contentBase64=original)
    result=generate(client,headers,accepted,sequence=5).json()
    replacement=deepcopy(first)|{'operationId':str(uuid4()),'expectedRevision':1,'acceptance':accepted,
        'bundle':result['bundle'],'receipt':result['receipt'],'contentBase64':original}
    assert post(client,headers,replacement).json()['status']=='ready'
    new_key=repository.operations[next(key for key in repository.operations if key[1]==replacement['operationId'])]['objectKey']
    fresh, fresh_headers, _, _, _=setup(tmp_path,repository,storage)
    listing=post(fresh,fresh_headers,{'schemaVersion':'1.0'},'pending').json()['operations']
    assert len(listing)==2
    old = next(value for value in listing if value['operationId']==first['operationId'])
    assert old['status']=='ready' and old['cleanupOnly'] and not old['requiresFile']
    monkeypatch.setattr(save_cleanup,'SupabaseDocuments',lambda _:repository)
    monkeypatch.setattr(save_cleanup,'SupabaseStorage',lambda _:storage)
    identity=fresh.app.state.auth_registry.live_session(session_cookie(fresh)).identity
    assert asyncio.run(save_cleanup.cleanup(None,identity))==(0,1)
    assert storage.deletes==[old_key] and new_key in storage.objects and old_key not in storage.objects
    assert len(repository.operations)==2  # Uncertain records remain durable.
    post(fresh,fresh_headers,{'schemaVersion':'1.0','operationId':replacement['operationId']},'cleanup')
    assert storage.deletes==[old_key,old_key] and new_key in storage.objects


def test_commit_conflict_erases_staging_but_keeps_digest_and_recovery_metadata(tmp_path):
    client,headers,_,repository,_=setup(tmp_path)
    first=draft(client,headers)
    post(client,headers,first)
    client.post('/api/v1/workspaces/invalidate',headers=headers,json={
        'schemaVersion':'1.0','workspaceId':WORKSPACE,'clientRevision':1,'commandSequence':3})
    accepted=extract(client,headers,sequence=4,revision=1)
    result=generate(client,headers,accepted,sequence=5).json()
    a=deepcopy(first)|{'operationId':str(uuid4()),'expectedRevision':1,'acceptance':accepted,
        'bundle':result['bundle'],'receipt':result['receipt']}
    b=a|{'operationId':str(uuid4())}
    for body in (a,b):
        repository.fail_action='commit'
        assert post(client,headers,body).json()['code']=='save_pending'
    def retry(body):
        operation=next(value for value in repository.operations.values() if value['operationId']==body['operationId'])
        return post(client,headers,{'schemaVersion':'1.0','operationId':body['operationId'],'digest':operation['digest']},'retry')
    assert retry(a).json()['status']=='ready'
    assert retry(b).json()['code']=='save_conflict'
    failed=next(value for value in repository.operations.values() if value['operationId']==b['operationId'])
    assert failed['snapshot'] is None and failed['status']=='conflict' and failed['digest']


def test_auth_origin_csrf_and_bounded_intake_before_repository(tmp_path):
    client, headers, _, repository, _ = setup(tmp_path)
    assert client.post('/api/v1/documents/save',json={}).status_code == 403
    assert client.post('/api/v1/documents/save',headers=headers|{'content-type':'application/json','content-length':str(16*1024*1024+1)},content=b'{}').status_code == 413
    assert not repository.calls


def test_disabled_save_does_not_read_key_or_admit(tmp_path):
    client, headers, _, _, _ = setup(tmp_path)
    client.app.state.documents_injected = False
    result = post(client,headers,{}).json()
    assert result['code'] == 'save_unavailable' and result['saveDisabled'] is True


def test_enabled_save_configuration_failure_does_not_masquerade_as_disabled(tmp_path):
    from dataclasses import replace
    client, headers, _, _, _ = setup(tmp_path)
    client.app.state.documents_injected = False
    client.app.state.settings = replace(SETTINGS, save_enabled=True)
    result = post(client,headers,{}).json()
    assert result['code']=='save_unavailable' and 'saveDisabled' not in result


def test_storage_readback_bounded_hash_and_server_only_headers():
    from dataclasses import replace
    from app.adapters.auth import Identity
    import hashlib
    content=b'original'
    class Config:
        supabase_url='https://synthetic.test'; supabase_key='publishable'
        supabase_s3_region='local'; supabase_s3_key_id='stub'; supabase_s3_anon_key='synthetic-anon'
        def save_backend_key(self): return 'server-owned-test-gate'
    identity=Identity('owner','synthetic@example.test','user-token','',time.time()+100)
    observed=[]
    def transport(request):
        observed.append(request)
        return httpx.Response(200,content=content)
    storage=SupabaseStorage(Config(),transport=httpx.MockTransport(transport))
    operation={'objectKey':'owner/document/generation/operation','snapshot':{'fileSize':len(content),'fileHash':hashlib.sha256(content).hexdigest()}}
    storage.verify(identity,operation,time.monotonic()+5)
    assert observed[0].url.path.startswith('/storage/v1/s3/')
    assert observed[0].headers['authorization'].startswith('AWS4-HMAC-SHA256 ')
    assert observed[0].headers['x-amz-security-token']=='user-token'
    assert observed[0].headers['x-studybuddy-backend']=='server-owned-test-gate'
    assert observed[0].headers['x-studybuddy-operation']=='verify'
    operation['snapshot']['fileSize']=1
    with pytest.raises(DocumentFailure): storage.verify(identity,operation,time.monotonic()+5)


@pytest.mark.parametrize('missing', ['supabase_s3_region','supabase_s3_key_id','supabase_s3_anon_key'])
def test_storage_s3_missing_configuration_never_dispatches(missing):
    from types import SimpleNamespace
    config=SimpleNamespace(supabase_url='https://synthetic.test',supabase_s3_region='local',
        supabase_s3_key_id='stub',supabase_s3_anon_key='synthetic-anon')
    setattr(config,missing,'')
    observed=[]
    storage=SupabaseStorage(config,transport=httpx.MockTransport(lambda request:observed.append(request)))
    with pytest.raises(DocumentFailure) as failure:
        storage.verify(None,{'objectKey':'synthetic'},time.monotonic()+5)
    assert failure.value.code=='save_unavailable' and not observed


@pytest.mark.parametrize('action,status', [('upload',200),('upload',409),('upload',500),('delete',200),('delete',500)])
def test_storage_unused_oversized_response_is_not_consumed_and_is_closed(action,status):
    from app.adapters.auth import Identity
    class Config:
        supabase_url='https://synthetic.test'; supabase_key='publishable'
        def save_backend_key(self): return 'server-owned-test-gate'
    class OversizedStream(httpx.SyncByteStream):
        closed=False
        def __iter__(self):
            raise AssertionError('unused unbounded body must not be consumed')
            yield b'x' * (32 * 1024 * 1024)
        def close(self): self.closed=True
    stream=OversizedStream()
    storage=SupabaseStorage(Config(),transport=httpx.MockTransport(lambda request:httpx.Response(status,stream=stream)))
    identity=Identity('owner','synthetic@example.test','user-token','',time.time()+100)
    operation={'objectKey':'owner/document/generation/operation','mediaType':'text/plain'}
    def invoke():
        if action=='upload': storage.upload(identity,operation,b'original',time.monotonic()+5)
        else: storage.delete(identity,operation['objectKey'],time.monotonic()+5)
    if status==500:
        with pytest.raises(DocumentFailure): invoke()
    else: invoke()
    assert stream.closed


def test_ready_file_retry_validates_supplied_bytes_without_old_receipt(tmp_path):
    client, headers, model, repository, storage = setup(tmp_path)
    body=draft(client,headers,file=b'Synthetic original source.')
    ready=post(client,headers,body).json()
    operation=next(iter(repository.operations.values()))
    request={'schemaVersion':'1.0','operationId':body['operationId'],'digest':operation['digest']}
    second,fresh,model,_,_=setup(tmp_path,repository,storage)
    assert post(second,fresh,request|{'contentBase64':base64.b64encode(b'Wrong original source.').decode()},'retry').json()['code']=='save_mismatch'
    assert post(second,fresh,request|{'contentBase64':body['contentBase64']},'retry').json()==ready
    assert post(second,fresh,request,'retry').json()==ready
    assert not model.calls and len(storage.uploads)==1


def test_ready_paste_retry_rejects_unexpected_bytes(tmp_path):
    client, headers, _, repository, _=setup(tmp_path)
    body=draft(client,headers)
    ready=post(client,headers,body).json()
    operation=next(iter(repository.operations.values()))
    request={'schemaVersion':'1.0','operationId':body['operationId'],'digest':operation['digest']}
    assert post(client,headers,request|{'contentBase64':'YQ=='},'retry').json()['code']=='save_mismatch'
    assert post(client,headers,request,'retry').json()==ready


def test_lost_ready_reply_is_discoverable_after_restart_without_private_content(tmp_path):
    client, headers, _, repository, storage = setup(tmp_path)
    body = draft(client, headers)
    original = repository.call
    def lose(identity, action, payload, deadline):
        result = original(identity, action, payload, deadline)
        if action == 'commit': raise DocumentFailure()
        return result
    repository.call = lose
    assert post(client, headers, body).json()['code'] == 'save_pending'
    repository.call = original
    second, fresh, model, _, _ = setup(tmp_path, repository, storage)
    listing = post(second, fresh, {'schemaVersion':'1.0'}, 'pending').json()['operations']
    assert len(listing)==1 and listing[0]['operationId']==body['operationId']
    assert listing[0]['recoveryState']=='ready' and listing[0]['outcome']['status']=='ready'
    assert not any(key in listing[0] for key in ('snapshot','bundle','acceptance'))
    assert not model.calls


def test_ready_discovery_keeps_seven_days_from_completion_after_late_recovery(tmp_path):
    client, headers, _, repository, _ = setup(tmp_path)
    body = draft(client, headers)
    repository.fail_action = 'commit'
    post(client, headers, body)
    operation = next(iter(repository.operations.values()))
    now = operation['expires']-10
    repository.clock = lambda: now
    request = {'schemaVersion':'1.0','operationId':body['operationId'],'digest':operation['digest']}
    assert post(client, headers, request, 'retry').json()['status']=='ready'
    now += 20
    assert post(client, headers, {'schemaVersion':'1.0'}, 'pending').json()['operations'][0]['status']=='ready'
    now += 604800
    assert post(client, headers, {'schemaVersion':'1.0'}, 'pending').json()['operations']==[]
    assert post(client, headers, request, 'retry').json()['status']=='ready'


@pytest.mark.parametrize('expire', [False, True])
def test_object_free_terminal_cleanup_completes_and_disappears_with_tombstone(tmp_path, expire):
    client, headers, _, repository, storage = setup(tmp_path)
    body = draft(client, headers, title='Recognizable pending synthetic title')
    repository.fail_action = 'commit'
    post(client, headers, body)
    listing = post(client, headers, {'schemaVersion':'1.0'}, 'pending').json()['operations']
    assert listing[0]['title']==body['title'] and listing[0]['admittedAt'] and listing[0]['expiresAt']
    if expire: repository.clock = lambda: time.time()+604801
    result = post(client, headers, {'schemaVersion':'1.0','operationId':body['operationId']}, 'cleanup').json()
    assert result['status']=='cleanup_complete' and not storage.deletes
    assert post(client, headers, {'schemaVersion':'1.0'}, 'pending').json()['operations']==[]
    tombstone = next(iter(repository.operations.values()))
    assert tombstone['snapshot'] is None and tombstone['digest']


def test_many_short_paragraphs_pass_source_generation_and_save_bounded_intake(tmp_path):
    client, headers, model, repository, _ = setup(tmp_path)
    acceptance = extract(client, headers, text='\n\n'.join(['a']*6000))
    assert len(acceptance['source']['units'])==6000
    generated = generate(client, headers, acceptance)
    assert generated.status_code==200, generated.text
    value = generated.json()
    body = {'schemaVersion':'1.0','operationId':str(uuid4()),'documentId':str(uuid4()),
            'acceptance':acceptance,'bundle':value['bundle'],'receipt':value['receipt'],
            'positions':{'flashcardId':value['bundle']['flashcards'][0]['id'],'quizId':value['bundle']['quiz'][0]['id']}}
    result = post(client, headers, body)
    assert result.status_code==200, result.text
    assert len(next(iter(repository.documents.values()))['acceptance']['source']['units'])==6000
    assert len(model.calls)==1
