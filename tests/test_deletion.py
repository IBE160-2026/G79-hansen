"""Synthetic deletion orchestration; provider/SQL evidence is separate."""
from concurrent.futures import ThreadPoolExecutor
import asyncio
from copy import deepcopy
import base64
from threading import Event
from uuid import uuid4
import time
from types import SimpleNamespace
import httpx
import pytest
from app.adapters.auth import Identity
from app.adapters.documents import DocumentFailure
from app.adapters.storage import SupabaseStorage
from test_documents import setup, draft, post
from test_generation import extract, generate, WORKSPACE
from test_sources import login
from fastapi.testclient import TestClient
from test_auth import ORIGIN


def saved(tmp_path, file=None):
    client,headers,model,repository,storage=setup(tmp_path)
    body=draft(client,headers,**({'file':file} if file else {}))
    assert post(client,headers,body).status_code==200
    request={'schemaVersion':'1.0','documentId':body['documentId'],'operationId':str(uuid4())}
    return client,headers,model,repository,storage,body,request


def test_cancel_has_no_mutation_then_complete_removes_content_progress_and_payloads(tmp_path):
    client,headers,model,repository,storage,body,request=saved(tmp_path,b'Synthetic source')
    before=deepcopy(repository.documents)
    assert post(client,headers,{'schemaVersion':'1.0'},'library').json()['items']
    assert repository.documents==before and not storage.deletes  # Cancel sends nothing.
    calls=len(model.calls)
    result=post(client,headers,request,'delete')
    assert result.status_code==200 and result.json()['status']=='deleted'
    assert result.headers['cache-control']=='no-store'
    assert not repository.documents and not repository.operations and not storage.objects
    assert not repository.progress_mutations and len(model.calls)==calls
    assert not {'objects','objectKey','title','bundle','ownerId'} & result.json().keys()
    assert post(client,headers,body).status_code==409
    assert post(client,headers,request,'delete').json()==result.json()


@pytest.mark.parametrize('action',['delete','deletions'])
def test_delete_requires_current_auth_csrf_and_session_view(tmp_path,action):
    client,headers,_,repository,_,_,request=saved(tmp_path)
    payload=request if action=='delete' else {'schemaVersion':'1.0'}
    for altered in ({},headers|{'X-Session-View':'old'},headers|{'X-CSRF-Token':'bad'}):
        assert post(client,altered,payload,action).status_code in (401,403)
    assert not repository.deletions


@pytest.mark.parametrize('change',[{'ownerId':'foreign'},{'operationId':'bad'},{'documentId':'bad'},{'schemaVersion':'2.0'},{'title':'injected'}])
def test_delete_contract_is_strict(tmp_path,change):
    client,headers,_,repository,_,_,request=saved(tmp_path)
    assert post(client,headers,request|change,'delete').status_code==422
    assert not repository.deletions


@pytest.mark.parametrize('state',['foreign','unknown'])
def test_foreign_or_unknown_delete_discloses_no_authority(tmp_path,state):
    client,headers,_,repository,storage,body,request=saved(tmp_path,b'Synthetic source')
    key=next(iter(repository.documents))
    if state=='foreign':repository.documents['another-owner',key[1]]=repository.documents.pop(key)
    else:request['documentId']=str(uuid4())
    result=post(client,headers,request,'delete')
    assert result.status_code==404 and not storage.deletes
    assert not repository.deletions
    assert post(client,headers,{'schemaVersion':'1.0'},'deletions').json()['deletions']==[]


def test_failed_cleanup_persists_fence_and_discovery_across_restart(tmp_path):
    client,headers,_,repository,storage,body,request=saved(tmp_path,b'Synthetic source')
    original=storage.delete
    storage.delete=lambda *args: (_ for _ in ()).throw(DocumentFailure())
    assert post(client,headers,request,'delete').status_code==503
    for action in ('file','reload'):
        assert post(client,headers,{'schemaVersion':'1.0','documentId':body['documentId']},action).status_code==404
    assert post(client,headers,{'schemaVersion':'1.0'},'library').json()['items']==[]
    assert post(client,headers,body).status_code==409
    second,fresh,_,_,_=setup(tmp_path,repository,storage)
    discovered=post(second,fresh,{'schemaVersion':'1.0'},'deletions').json()['deletions']
    assert discovered[0]['operationId']==request['operationId']
    storage.delete=original
    assert post(second,fresh,request,'delete').json()['status']=='deleted'


def test_lost_completed_response_replays_after_fresh_login(tmp_path):
    client,headers,_,repository,storage,body,request=saved(tmp_path)
    original=repository.call
    def lost(identity,action,payload,deadline):
        result=original(identity,action,payload,deadline)
        if action=='delete_complete':raise DocumentFailure('delete_pending')
        return result
    repository.call=lost
    assert post(client,headers,request,'delete').status_code==503
    assert not repository.documents
    repository.call=original
    second,fresh,_,_,_=setup(tmp_path,repository,storage)
    assert post(second,fresh,request,'delete').json()['status']=='deleted'
    assert post(second,fresh,request|{'documentId':str(uuid4())},'delete').status_code==409


def test_unknown_attempt_survives_delete_metadata_absence_retry_and_restart(tmp_path):
    client,headers,_,repository,storage,body,request=saved(tmp_path,b'Synthetic source')
    operation=next(iter(repository.operations.values()));operation['writeUnknown']=True
    assert post(client,headers,request,'delete').json()['status']=='deleting'
    assert not storage.objects and repository.operations and repository.documents
    # Simulate a provider write finishing AFTER the first successful DELETE.
    storage.objects[operation['objectKey']]=b'Synthetic source'
    second,fresh,_,_,_=setup(tmp_path,repository,storage)
    assert post(second,fresh,request,'delete').json()['status']=='deleting'
    assert repository.operations and not storage.objects
    assert post(second,fresh,{'schemaVersion':'1.0'},'pending').json()['operations']==[]


def test_all_superseded_and_current_objects_are_removed(tmp_path):
    client,headers,_,repository,storage,body,request=saved(tmp_path,b'First synthetic')
    client.post('/api/v1/workspaces/invalidate',headers=headers,json={'schemaVersion':'1.0','workspaceId':WORKSPACE,'clientRevision':1,'commandSequence':3})
    content=base64.b64encode(b'Second synthetic').decode()
    accepted=extract(client,headers,sequence=4,revision=1,kind='text-file',contentBase64=content)
    generated=generate(client,headers,accepted,sequence=5).json()
    replacement=deepcopy(body)|{'operationId':str(uuid4()),'expectedRevision':1,'acceptance':accepted,
        'bundle':generated['bundle'],'receipt':generated['receipt'],'contentBase64':content}
    assert post(client,headers,replacement).status_code==200
    assert len(storage.objects)==2
    assert post(client,headers,request,'delete').json()['status']=='deleted'
    assert len(storage.deletes)==2 and not storage.objects and not repository.operations


def test_inflight_file_is_fenced_before_delete_waits_for_file_lock(tmp_path):
    client,headers,_,repository,storage,body,request=saved(tmp_path,b'Synthetic source')
    other=TestClient(client.app,base_url=ORIGIN);fresh=login(other)
    entered,release=Event(),Event();original=storage.download
    def blocked(*args):
        entered.set();assert release.wait(5);return original(*args)
    storage.download=blocked
    with ThreadPoolExecutor(2) as pool:
        download=pool.submit(post,client,headers,{'schemaVersion':'1.0','documentId':body['documentId']},'file')
        assert entered.wait(5)
        deletion=pool.submit(post,other,fresh,request,'delete')
        until=time.monotonic()+5
        while not repository.deletions and time.monotonic()<until:time.sleep(.01)
        assert repository.deletions;release.set()
        assert download.result().status_code==404
        assert deletion.result().json()['status']=='deleted'


@pytest.mark.parametrize('status',[200,404,403,500])
def test_s3_absence_is_fresh_internal_evidence_not_a_removal_receipt(status):
    observed=[]
    def provider(request):observed.append(request);return httpx.Response(status,content=b'')
    settings=SimpleNamespace(supabase_url='https://synthetic.test',supabase_key='anon',supabase_s3_region='local',
        supabase_s3_key_id='stub',supabase_s3_anon_key='anon',save_backend_key=lambda:'gate')
    adapter=SupabaseStorage(settings,transport=httpx.MockTransport(provider))
    identity=Identity('owner','synthetic@example.test','owner-token','',time.time()+100)
    if status in (200,404): assert adapter.absent(identity,'owner/document/object',time.monotonic()+5) is (status==404)
    else:
        with pytest.raises(DocumentFailure):adapter.absent(identity,'owner/document/object',time.monotonic()+5)
    assert observed[0].headers['x-amz-security-token']=='owner-token'
    assert observed[0].headers['x-studybuddy-operation']=='cleanup'


@pytest.mark.parametrize('receipt,expected',[([],False),([{'name':'other','bucket_id':'studybuddy-sources'}],False),
    ([{'name':'owner/document/object','bucket_id':'other'}],False),
    ([{'name':'owner/document/object','bucket_id':'studybuddy-sources'}],True)])
def test_remove_requires_exact_positive_named_bucket_receipt(receipt,expected):
    settings=SimpleNamespace(supabase_url='https://synthetic.test',supabase_key='anon',save_backend_key=lambda:'gate')
    adapter=SupabaseStorage(settings,transport=httpx.MockTransport(lambda request:httpx.Response(200,json=receipt)))
    identity=Identity('owner','synthetic@example.test','owner-token','',time.time()+100)
    assert adapter.delete(identity,'owner/document/object',time.monotonic()+5) is expected


def test_empty_200_delete_and_missing_metadata_do_not_complete(tmp_path):
    client,headers,_,repository,storage,body,request=saved(tmp_path,b'Synthetic source')
    storage.delete=lambda *args:False
    storage.absent=lambda *args:True
    assert post(client,headers,request,'delete').json()['status']=='deleting'
    assert repository.documents and repository.operations


@pytest.mark.parametrize('complete',[False,True])
def test_captured_ready_replay_rechecks_deletion_after_waiting_for_file_io(tmp_path,complete):
    client,headers,_,repository,_,body,request=saved(tmp_path)
    service=client.app.state.documents
    session=next(iter(client.app.state.auth_registry.sessions.values()))
    identity=session.identity
    captured=deepcopy(next(iter(repository.operations.values())))
    replay_started,release_replay=Event(),Event()
    async def replay():
        async with service.file_io(identity,body['documentId'],time.monotonic()+10):
            task=asyncio.create_task(service.finish(identity,captured,None,time.monotonic()+10))
            await asyncio.sleep(0)
            replay_started.set()
            await asyncio.to_thread(release_replay.wait,5)
        return await task
    with ThreadPoolExecutor(1) as pool:
        pending=pool.submit(asyncio.run,replay())
        assert replay_started.wait(5)
        repository.call(identity,'delete',request,time.monotonic()+5)
        if complete:repository.call(identity,'delete_complete',request|{'removedKeys':[]},time.monotonic()+5)
        release_replay.set()
        with pytest.raises(DocumentFailure,match='save_conflict'):
            pending.result(timeout=5)
