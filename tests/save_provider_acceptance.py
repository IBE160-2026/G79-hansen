"""Explicit isolated-provider acceptance; never uses .env or a hosted target.

Run with uv run python tests/save_provider_acceptance.py. Requires the named
local WSL stack. Local admin credentials only create/remove synthetic fixtures;
all business operations use owner JWTs and the backend-origin capability.
Prints fixed test labels only, never credentials or provider response bodies.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import json
import os
from ipaddress import ip_address
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
from threading import Event
import time
from types import SimpleNamespace
from uuid import uuid4
from urllib.parse import urlsplit

import httpx
from botocore.auth import S3SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
from app.adapters.documents import SupabaseDocuments, DocumentFailure
from app.adapters.storage import SupabaseStorage
from app.contracts.documents import SaveRequest, snapshot, snapshot_digest
from test_documents import setup, draft

PROJECT = 'studybuddy-save-local'
DB_CONTAINER = 'supabase_db_' + PROJECT
WINDOWS = os.name == 'nt'
WSL = ['wsl'] + (['-d', os.environ['SAVE_TEST_WSL_DISTRO']] if os.environ.get('SAVE_TEST_WSL_DISTRO') else [])
# Only local sockets are accepted. These settings choose local tools, never a
# project ref, URL, credentials or remote Docker daemon.
DOCKER_SOCKET = os.environ.get('SAVE_TEST_DOCKER_SOCKET', 'unix:///var/run/docker.sock')
if not DOCKER_SOCKET.startswith('unix:///'):
    raise ValueError('Save acceptance requires a local Unix Docker socket.')
DOCKER = (WSL + ['-e'] if WINDOWS else []) + ['docker', '--host', DOCKER_SOCKET]


def cli_command():
    binary = os.environ.get('SAVE_TEST_CLI_PATH', './test-results/supabase-cli-3.1.0/supabase-arm64')
    if WINDOWS:
        checkout = subprocess.check_output(WSL + ['-e', 'wslpath', '-a', str(ROOT)], text=True).strip()
        return WSL + ['--cd', checkout, '-e', 'env', 'DOCKER_HOST=' + DOCKER_SOCKET, binary]
    return ['env', 'DOCKER_HOST=' + DOCKER_SOCKET, binary]


def assert_local_stack():
    names = subprocess.check_output(DOCKER + ['ps', '--format', '{{.Names}}'], text=True).splitlines()
    assert DB_CONTAINER in names, 'isolated local Save database required'


def local_api_url(config):
    advertised = urlsplit(config['API_URL'])
    assert advertised.scheme == 'http' and advertised.hostname in ('127.0.0.1', 'localhost', '::1')
    assert not advertised.username and not advertised.password and not advertised.query and not advertised.fragment
    assert advertised.port == 54421 and advertised.path in ('', '/'), 'isolated local Save API required'
    if WINDOWS:
        addresses = subprocess.check_output(WSL + ['-e', 'hostname', '-I'], text=True).split()
        address = ip_address(addresses[0])
        assert address.is_private and not address.is_unspecified and address.version == 4
        return 'http://' + str(address) + ':54421'
    return 'http://127.0.0.1:54421'


def sql(query):
    result = subprocess.run(DOCKER + ['exec', '-i', DB_CONTAINER,
        'psql', '-U', 'postgres', '-d', 'postgres', '-v', 'ON_ERROR_STOP=1', '-At'],
        input=query.encode(), capture_output=True, timeout=40)
    if result.returncode:
        # Fixed categories aid local diagnosis without exposing SQL, fixture
        # payloads, connection strings or capability values in stderr.
        detail=result.stderr.decode(errors='replace').lower()
        category=next((name for name in ('deadlock detected','lock timeout','statement timeout',
            'permission denied','syntax error','violates check constraint','violates foreign key constraint')
            if name in detail),'unclassified')
        raise AssertionError('local SQL failed: '+category)
    return result.stdout.decode().strip()


def run():
    assert_local_stack()
    status = subprocess.run(cli_command() + ['status', '-o', 'json'], cwd=ROOT, capture_output=True, timeout=30)
    assert status.returncode == 0, 'local CLI status failed'
    config = json.loads(status.stdout)
    url = local_api_url(config)
    key, key_id = secrets.token_hex(32), 'fixture-' + uuid4().hex
    verifier = hashlib.sha256(key.encode()).hexdigest()
    sql("insert into studybuddy.backend_verifiers(key_id,verifier) values ('" + key_id + "','" + verifier + "'); notify pgrst,'reload schema';")
    admin = {'apikey': config['ANON_KEY'], 'Authorization': 'Bearer ' + config['SERVICE_ROLE_KEY']}
    settings = SimpleNamespace(supabase_url=url, supabase_key=config['ANON_KEY'], save_backend_key=lambda: key,
        supabase_s3_region='local', supabase_s3_key_id='stub', supabase_s3_anon_key=config['ANON_KEY'])
    repository, storage = SupabaseDocuments(settings), SupabaseStorage(settings)
    owners, passed = [], []
    label = 'setup'

    def check(name, condition):
        nonlocal label
        label = name
        assert condition, name
        passed.append(name)
        print('PASS ' + name, flush=True)

    with httpx.Client(timeout=15, trust_env=False) as client:
        def request(identity, method, path, *, gate=True, extra=None, **kwargs):
            headers = {'apikey': config['ANON_KEY'], 'Authorization': 'Bearer ' + identity.access_token}
            if gate:
                headers['x-studybuddy-backend'] = key
            headers.update(extra or {})
            return client.request(method, url + path, headers=headers, **kwargs)

        def call(identity, action, payload):
            return repository.call(identity, action, payload, time.monotonic() + 20)

        def s3_read(identity, object_key, *, gate=True, verification=False):
            headers = {'x-studybuddy-backend': key} if gate else {}
            if verification: headers['x-studybuddy-operation'] = 'verify'
            signed = AWSRequest(method='GET', url=url+'/storage/v1/s3/studybuddy-sources/'+object_key, headers=headers)
            S3SigV4Auth(Credentials('stub',config['ANON_KEY'],identity.access_token),'s3','local').add_auth(signed)
            return client.get(signed.url,headers=dict(signed.headers))

        def operation(identity, *, file=None, target=None, revision=None):
            with tempfile.TemporaryDirectory(prefix='save-provider-fixture-') as directory:
                browser, headers, model, _, _ = setup(Path(directory))
                submitted = draft(browser, headers, **({'file': file} if file else {}))
                browser.close()
                assert len(model.calls) == 1  # injected, never a provider/model API
            if target:
                submitted.update(documentId=target, expectedRevision=revision)
            frozen = snapshot(SaveRequest.model_validate(submitted), identity.owner_id,
                hashlib.sha256(file).hexdigest() if file is not None else None,
                len(file) if file is not None else None)
            payload = {'operationId': submitted['operationId'], 'digest': snapshot_digest(frozen), 'snapshot': frozen}
            return payload, call(identity, 'admit', payload)['operation']

        try:
            for _ in range(2):
                password = secrets.token_urlsafe(32)
                email = 'save-local-' + uuid4().hex + '@example.invalid'
                created = client.post(url + '/auth/v1/admin/users', headers=admin,
                    json={'email': email, 'password': password, 'email_confirm': True})
                assert created.status_code == 200
                owner = created.json()['id']
                owners.append(owner)
                login = client.post(url + '/auth/v1/token?grant_type=password', headers={'apikey': config['ANON_KEY']},
                    json={'email': email, 'password': password})
                assert login.status_code == 200
                owners[-1] = SimpleNamespace(owner_id=owner, access_token=login.json()['access_token'])
            one, two = owners
            for value in (None, 'incorrect'):
                denied = request(one, 'POST', '/rest/v1/rpc/sb_save_pending_v1', gate=False,
                    extra={'x-studybuddy-backend': value} if value else {}, json={'payload': {}})
                check('RPC denies ' + ('wrong' if value else 'missing') + ' gate', denied.status_code in (401, 403))
            check('anonymous RPC denied', client.post(url + '/rest/v1/rpc/sb_save_pending_v1',
                headers={'apikey': config['ANON_KEY']}, json={'payload': {}}).status_code in (401, 403))
            check('application tables unexposed', request(one, 'GET', '/rest/v1/save_operations').status_code == 404)
            p, op = operation(one)
            check('durable admission', op['status'] == 'pending' and op['snapshot'] == p['snapshot'])
            pending_row=next(item for item in call(one,'pending',{})['operations'] if item['operationId']==p['operationId'])
            check('pending recovery identifies private title and lifetime without content',
                pending_row['title']==p['snapshot']['title'] and bool(pending_row['admittedAt']) and bool(pending_row['expiresAt'])
                and 'snapshot' not in pending_row and 'bundle' not in pending_row)
            check('foreign owner cannot recover', call(two, 'get', {'operationId': p['operationId']})['operation'] is None)
            check('pending target unreadable', request(one, 'POST', '/rest/v1/rpc/sb_save_reload_v1',
                json={'payload': {'documentId': op['documentId']}}).json().get('error') == 'save_unknown')
            ready = call(one, 'commit', p)
            check('atomic ready', ready['status'] == 'ready' and ready['revision'] == 1)
            check('idempotent completed replay', call(one, 'commit', p) == ready)
            ready_row=next(item for item in call(one,'pending',{})['operations'] if item['operationId']==p['operationId'])
            check('lost ready response remains discoverable across restart',ready_row['status']=='ready' and
                ready_row['outcome']==ready and not ready_row['cleanupOnly'])
            changed = request(one, 'POST', '/rest/v1/rpc/sb_save_get_v1',
                json={'payload': {'operationId': p['operationId'], 'digest': '0' * 64}})
            check('changed digest rejected', changed.json().get('error') == 'save_mismatch')
            loaded = call(one, 'reload', {'documentId': op['documentId']})
            check('consistent source bundle progress', loaded['acceptance'] == p['snapshot']['acceptance'] and
                loaded['bundle'] == p['snapshot']['bundle'] and loaded['positions'] == p['snapshot']['positions'])
            replacements = [operation(one, target=op['documentId'], revision=1) for _ in range(2)]
            a, b = replacements[0][0], replacements[1][0]
            check('replacement advances once', call(one, 'commit', a)['revision'] == 2)
            stale = request(one, 'POST', '/rest/v1/rpc/sb_save_commit_v1', json={'payload': b})
            check('stale replacement conflicts', stale.json().get('error') == 'save_conflict')
            check('conflict erases staged private content', call(one,'get',b)['operation']['snapshot'] is None)
            content = b'Isolated synthetic source with enough material for the fixture.'
            p, op = operation(one, file=content)
            path = '/storage/v1/object/studybuddy-sources/' + op['objectKey']
            authpath = '/storage/v1/object/authenticated/studybuddy-sources/' + op['objectKey']
            check('storage missing gate denied', request(one, 'POST', path, gate=False,
                content=content, extra={'Content-Type':'text/plain'}).status_code not in (200, 201))
            check('foreign gated upload denied', request(two, 'POST', path, content=content,
                extra={'Content-Type':'text/plain'}).status_code not in (200, 201))
            call(one, 'attempt', p)
            storage.upload(one, op, content, time.monotonic() + 20)
            check('pending download denied', request(one, 'GET', authpath).status_code != 200)
            check('pending signed URL denied', request(one, 'POST', '/storage/v1/object/sign/studybuddy-sources/' + op['objectKey'],
                json={'expiresIn':60}).status_code != 200)
            storage.verify(one, op, time.monotonic() + 20)
            check('internal byte verification succeeds', True)
            check('pending S3 read without internal marker denied after verification',s3_read(one,op['objectKey']).status_code!=200)
            check('pending S3 read without backend gate denied after verification',s3_read(one,op['objectKey'],gate=False,verification=True).status_code!=200)
            check('foreign internal verification denied', request(two, 'GET', authpath,
                extra={'x-studybuddy-operation':'verify'}).status_code != 200)
            call(one, 'verified', p)
            check('file commit ready with truthful cleanup', call(one, 'commit', p)['cleanupStatus'] == 'pending')
            internal=call(one,'get',p)['operation']
            check('completed file retains internal exact-byte identity',internal['snapshot'] is None and
                  internal['fileHash']==hashlib.sha256(content).hexdigest() and internal['fileSize']==len(content))
            unrelated,_=operation(one)
            check('unrelated file uncertainty cannot taint object-free Save',call(one,'commit',unrelated)['cleanupStatus']=='complete')
            check('ready exact object readable', s3_read(one,op['objectKey']).content == content)
            check('ready requires backend gate after successful read', s3_read(one,op['objectKey'],gate=False).status_code != 200)
            check('ready foreign object denied', s3_read(two,op['objectKey']).status_code != 200)
            check('REST ready read denied even with gate and verify marker',request(one,'GET',authpath,extra={'x-studybuddy-operation':'verify'}).status_code!=200)
            check('ready signed URL denied', request(one, 'POST', '/storage/v1/object/sign/studybuddy-sources/' + op['objectKey'],
                json={'expiresIn':60}).status_code != 200)
            check('immutable object overwrite denied', request(one, 'PUT', path, content=b'changed',
                extra={'Content-Type':'text/plain'}).status_code not in (200, 201))
            replacement, _ = operation(one, target=op['documentId'], revision=1)
            call(one, 'commit', replacement)
            check('superseded object denied after successful ready read', s3_read(one,op['objectKey']).status_code != 200)
            check('superseded cleanup remains discoverable after ready replacement', any(
                item['operationId'] == p['operationId'] for item in call(one, 'pending', {})['operations']))
            cleanup = call(one, 'cancel', p)
            check('registered superseded cleanup exposed', op['objectKey'] in cleanup['cleanupKeys'])
            storage.delete(one, op['objectKey'], time.monotonic() + 20)
            check('registered cleanup endpoint succeeds', True)
            # A cancelled admission can never finalize a subsequent upload.
            p, op = operation(one, file=content)
            call(one, 'attempt', p)
            call(one, 'cancel', p)
            blocked = request(one, 'POST', '/storage/v1/object/studybuddy-sources/' + op['objectKey'],
                content=content, extra={'Content-Type':'text/plain'})
            check('cancel fence denies upload finalization', blocked.status_code not in (200, 201))
            check('cancel erases staging', call(one, 'get', p)['operation']['snapshot'] is None)
            p, op = operation(one, file=content)
            call(one, 'attempt', p)
            started, release = Event(), Event()
            def delayed_body():
                yield content[:8]
                started.set()
                assert release.wait(10)
                yield content[8:]
            def delayed_upload():
                with httpx.Client(timeout=15, trust_env=False) as delayed:
                    return delayed.post(url + '/storage/v1/object/studybuddy-sources/' + op['objectKey'],
                        headers={'apikey':config['ANON_KEY'], 'Authorization':'Bearer '+one.access_token,
                                 'x-studybuddy-backend':key, 'Content-Type':'text/plain'}, content=delayed_body()).status_code
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(delayed_upload)
                assert started.wait(5)
                try:
                    call(one, 'cancel', p)
                finally:
                    release.set()
                check('in-flight late upload cannot finalize after cancel', future.result(timeout=20) not in (200,201))
            check('late upload leaves no published object metadata', sql("select count(*) from storage.objects where bucket_id='studybuddy-sources' and name='" + op['objectKey'] + "';") == '0')
            check('unknown late write remains registered for cleanup', sql("select cleanup_needed and write_unknown and not upload_enabled from studybuddy.save_objects where owner_id='"+one.owner_id+"' and operation_id='"+p['operationId']+"';") == 't')
            p, op = operation(one)
            # Move an isolated no-file fixture into the past without weakening the
            # immutable UPDATE trigger used by ordinary requests.
            sql("with x as (delete from studybuddy.save_operations where owner_id='" + one.owner_id + "' and operation_id='" + p['operationId'] + "' returning *) "
                "insert into studybuddy.save_operations(owner_id,operation_id,document_id,generation_id,digest,snapshot,expected_revision,status,admitted_at,expires_at,outcome) "
                "select owner_id,operation_id,document_id,generation_id,digest,snapshot,expected_revision,status,admitted_at-interval '8 days',expires_at-interval '8 days',outcome from x;")
            expired = call(one, 'get', p)['operation']
            check('seven-day expiry erases private staging', expired['status']=='expired' and expired['snapshot'] is None)
            check('expired admission cannot commit', request(one,'POST','/rest/v1/rpc/sb_save_commit_v1',json={'payload':p}).json().get('error')=='save_expired')
            p, op = operation(one)
            cancelled=call(one,'cancel',p)
            check('object-free cancellation completes without false file uncertainty',cancelled['cleanupStatus']=='cleanup_complete')
            check('object-free cleanup disappears while immutable tombstone survives',not any(
                item['operationId']==p['operationId'] for item in call(one,'pending',{})['operations']) and
                call(one,'get',p)['operation']['snapshot'] is None)
            check('cancel scrubs private initial title',sql("select title is distinct from '"+
                p['snapshot']['title'].replace("'","''")+"' from studybuddy.documents where owner_id='"+
                one.owner_id+"' and document_id='"+p['snapshot']['documentId']+"';")=='t')
            # Bulk fixture setup is administrative; the actual paginated read is
            # exercised through ordinary owner JWT/gate HTTP requests.
            paging_ids=[]
            commands=['begin;']
            for _ in range(55):
                frozen=deepcopy(p['snapshot'])
                frozen['documentId']=str(uuid4())
                oid=str(uuid4());paging_ids.append(oid)
                def quoted(value): return "'"+str(value).replace("'","''")+"'"
                commands.append('insert into studybuddy.documents(owner_id,document_id,generation_id,title,lifecycle) values ('+
                    ','.join(quoted(value) for value in (one.owner_id,frozen['documentId'],frozen['generationId'],frozen['title'],'pending'))+');')
                commands.append('insert into studybuddy.save_operations(owner_id,operation_id,document_id,generation_id,digest,snapshot) values ('+
                    ','.join(quoted(value) for value in (one.owner_id,oid,frozen['documentId'],frozen['generationId'],
                        snapshot_digest(frozen),json.dumps(frozen)))+'::jsonb);')
            sql(''.join(commands)+'commit;')
            seen=[];cursor=None;pages=0
            while True:
                page=call(one,'pending',{'cursor':cursor})
                seen.extend(item['operationId'] for item in page['operations'])
                pages+=1;cursor=page.get('nextCursor')
                if not cursor: break
                assert pages<5
            check('UUID pagination finds every pending operation without duplicate rows',
                pages>=2 and set(paging_ids).issubset(seen) and len(seen)==len(set(seen)))
            check('foreign owner sees no paginated operation metadata',not call(two,'pending',{})['operations'])
            sql("update studybuddy.backend_verifiers set active=false where key_id='" + key_id + "';")
            check('retired gate denied', request(one, 'POST', '/rest/v1/rpc/sb_save_pending_v1',
                json={'payload': {}}).status_code in (401,403))
            print('Provider acceptance:', len(passed), 'checks passed; no hosted/model calls.', flush=True)
            return passed
        except Exception as exc:
            print('FAIL after ' + label + ': ' + type(exc).__name__, flush=True)
            raise SystemExit(1) from None
        finally:
            # Cleanup only fixture owners created in this invocation, local admin.
            for identity in owners:
                own = identity.owner_id if hasattr(identity, 'owner_id') else identity
                assert str(uuid4().__class__(own)) == own
                objects = sql("select object_key from studybuddy.save_objects where owner_id='" + own + "';").splitlines()
                if objects:
                    client.request('DELETE', url + '/storage/v1/object/studybuddy-sources', headers=admin, json={'prefixes': objects})
                sql('begin;' + ''.join("delete from studybuddy." + table + " where owner_id='" + own + "';"
                    for table in ('save_objects','save_operations','progress','bundles','contents','documents')) + 'commit;')
                client.delete(url + '/auth/v1/admin/users/' + own, headers=admin)
            sql("delete from studybuddy.backend_verifiers where key_id='" + key_id + "';")


if __name__ == '__main__':
    run()
