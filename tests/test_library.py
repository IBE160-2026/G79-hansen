"""Library projection, exact reopen, fresh attachment and read fencing evidence."""
from copy import deepcopy
import hashlib
import time
from types import SimpleNamespace
from uuid import uuid4
import httpx
import pytest
from app.adapters.auth import Identity
from app.adapters.documents import DocumentFailure
from app.adapters.storage import SupabaseStorage
from test_documents import setup, draft, post


def saved(client, headers, **changes):
    body = draft(client, headers, **changes)
    assert post(client, headers, body).status_code == 200
    return body


def test_empty_library_excludes_pending_and_returns_no_content(tmp_path):
    client, headers, _, repository, _ = setup(tmp_path)
    assert post(client, headers, {'schemaVersion':'1.0'}, 'library').json()['items'] == []
    body = draft(client, headers)
    repository.fail_action = 'commit'
    post(client, headers, body)
    result = post(client, headers, {'schemaVersion':'1.0'}, 'library')
    assert result.headers['cache-control'] == 'no-store' and result.json()['items'] == []


def test_library_metadata_bounded_keyset_and_absent_sections(tmp_path):
    client, headers, _, repository, _ = setup(tmp_path)
    body = saved(client, headers, title='<img src=x> Private')
    owner = next(iter(repository.documents))[0]
    original = next(iter(repository.documents.values()))
    repository.documents.clear()
    for i in range(53):
        document_id = f'20000000-0000-4000-8000-{i:012d}'
        value = deepcopy(original) | {'documentId':document_id}
        repository.documents[owner, document_id] = value
    first = post(client, headers, {'schemaVersion':'1.0'}, 'library').json()
    assert len(first['items']) == 50 and first['nextCursor'] == first['items'][-1]['documentId']
    assert set(first['items'][0]) == {'documentId','title','revision','updatedAt','positions','hasOriginalFile'}
    assert first['items'][0]['positions']['flashcard'] == {'ordinal':1,'total':1}
    second = post(client, headers, {'schemaVersion':'1.0','cursor':first['nextCursor']}, 'library').json()
    assert len(second['items']) == 3 and second['nextCursor'] is None
    assert not set(x['documentId'] for x in first['items']) & set(x['documentId'] for x in second['items'])
    value = repository.documents[owner, first['items'][0]['documentId']]
    value['bundle']['quiz'] = []; value['positions']['quizId'] = None
    assert post(client, headers, {'schemaVersion':'1.0'}, 'library').json()['items'][0]['positions']['quiz'] is None


def test_reopen_same_owner_after_restart_exact_snapshot_and_no_receipt_or_inference(tmp_path):
    client, headers, _, repository, storage = setup(tmp_path)
    body = saved(client, headers, file=b'Synthetic original source.', title='Private')
    second, fresh, model, _, _ = setup(tmp_path, repository, storage)
    metadata = post(second, fresh, {'schemaVersion':'1.0'}, 'library').json()['items'][0]
    assert metadata['hasOriginalFile'] is True
    opened = post(second, fresh, {'schemaVersion':'1.0','documentId':body['documentId']}, 'reload').json()
    assert opened['bundle'] == body['bundle'] and opened['positions'] == body['positions']
    assert opened['acceptance']['source'] == body['acceptance']['source']
    assert not model.calls and 'receipt' not in opened
    assert not {'ownerId','objectKey','fileHash','fileSize'} & opened.keys()


@pytest.mark.parametrize('action', ['library','reload','file'])
def test_library_reads_require_auth_csrf_and_current_session_view(tmp_path, action):
    client, headers, _, repository, storage = setup(tmp_path)
    body = saved(client, headers, file=b'Synthetic file')
    request = {'schemaVersion':'1.0'} | ({} if action=='library' else {'documentId':body['documentId']})
    for altered in ({}, headers | {'X-Session-View':'old-view'}, headers | {'X-CSRF-Token':'wrong'}):
        assert post(client, altered, request, action).status_code in (401,403)


@pytest.mark.parametrize('state', ['pending','deleting','foreign','unknown'])
def test_nonready_foreign_and_unknown_have_no_metadata_content_or_bytes(tmp_path, state):
    client, headers, _, repository, _ = setup(tmp_path)
    body = saved(client, headers, file=b'Synthetic original')
    key = next(iter(repository.documents))
    if state == 'foreign': repository.documents['another-owner',key[1]] = repository.documents.pop(key)
    elif state == 'unknown': repository.documents.clear()
    else: repository.documents[key]['status'] = state
    assert post(client, headers, {'schemaVersion':'1.0'}, 'library').json()['items'] == []
    for action in ('reload','file'):
        response = post(client, headers, {'schemaVersion':'1.0','documentId':body['documentId']}, action)
        assert response.status_code == 404 and 'Synthetic original' not in response.text


def test_original_file_attachment_is_exact_no_keys_or_urls_and_no_model_call(tmp_path):
    client, headers, model, _, _ = setup(tmp_path)
    original = b'Synthetic original \xe2\x98\x83\n'
    body = saved(client, headers, file=original, title='Private <title>')
    calls = len(model.calls)
    result = post(client, headers, {'schemaVersion':'1.0','documentId':body['documentId']}, 'file')
    assert result.status_code == 200 and result.content == original
    assert result.headers['content-disposition'].startswith('attachment;')
    assert "filename*=UTF-8''Private%20%3Ctitle%3E.txt" in result.headers['content-disposition']
    assert result.headers['cache-control'] == 'no-store' and result.headers['x-content-type-options'] == 'nosniff'
    assert len(model.calls) == calls and 'objectKey' not in str(result.headers)


@pytest.mark.parametrize('failure', ['missing','corrupt','superseded','deleting','logout'])
def test_file_failures_and_authority_changes_never_return_bytes(tmp_path, failure):
    client, headers, _, repository, storage = setup(tmp_path)
    body = saved(client, headers, file=b'Synthetic original')
    document = next(iter(repository.documents.values()))
    original = storage.download
    def download(*args):
        if failure == 'missing': storage.objects.clear()
        if failure == 'corrupt': storage.objects[document['objectKey']] = b'wrong'
        result = original(*args)
        if failure == 'superseded': document['revision'] += 1
        if failure == 'deleting': document['status'] = 'deleting'
        if failure == 'logout':
            registry = client.app.state.auth_registry
            for session in tuple(registry.sessions.values()): registry.terminate(session.browser_id)
        return result
    storage.download = download
    result = post(client, headers, {'schemaVersion':'1.0','documentId':body['documentId']}, 'file')
    assert result.status_code in (401,404,503) and result.content != b'Synthetic original'


@pytest.mark.parametrize('payload', [{'schemaVersion':'1.0','cursor':'bad'}, {'schemaVersion':'1.0','limit':500}, {'schemaVersion':'1.0','ownerId':'foreign'}])
def test_library_contract_rejects_unbounded_or_owner_payload(tmp_path, payload):
    client, headers, _, _, _ = setup(tmp_path)
    assert post(client, headers, payload, 'library').status_code == 422


@pytest.mark.parametrize('content,size,hash_ok', [(b'exact',5,True),(b'extra',4,True),(b'short',6,True),(b'wrong',5,False)])
def test_s3_download_is_fresh_user_scoped_and_integrity_checked(content,size,hash_ok):
    observed = []
    def provider(request):
        observed.append(request)
        return httpx.Response(200,content=content)
    settings = SimpleNamespace(supabase_url='https://synthetic.test',supabase_key='public',
        supabase_s3_region='local',supabase_s3_key_id='stub',supabase_s3_anon_key='anon',save_backend_key=lambda:'gate')
    adapter = SupabaseStorage(settings,transport=httpx.MockTransport(provider))
    identity = Identity('owner','synthetic@example.test','user-token','',time.time()+100)
    descriptor = {'objectKey':'owner/document/object','fileHash':hashlib.sha256(content if hash_ok else b'other').hexdigest(),'fileSize':size}
    if size == len(content) and hash_ok:
        assert adapter.download(identity,descriptor,time.monotonic()+5) == content
    else:
        with pytest.raises(DocumentFailure): adapter.download(identity,descriptor,time.monotonic()+5)
    assert '/storage/v1/s3/' in str(observed[0].url)
    assert observed[0].headers['x-amz-security-token'] == 'user-token'
    assert 'x-studybuddy-operation' not in observed[0].headers
