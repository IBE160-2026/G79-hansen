"""Focused isolated-local library/RLS/S3 acceptance; no hosted or model calls.

Reuses the Save runner's guarded local stack helpers. Only the harness uses
15-second read timeout headroom; production per-phase and elapsed budgets stay
unchanged. Failures print fixed stage/status/timing categories, never payloads.
"""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import tempfile
import time
from types import SimpleNamespace
from uuid import uuid4
import httpx
from save_provider_acceptance import assert_local_stack, cli_command, local_api_url, sql, ROOT
from app.adapters.documents import SupabaseDocuments, DocumentFailure
from app.adapters.storage import SupabaseStorage
from app.contracts.documents import SaveRequest, ReloadRequest, snapshot, snapshot_digest
from app.services.documents import Documents, SaveAdmission
from test_documents import setup, draft
import asyncio


class LocalHeadroom:
    @contextmanager
    def client(self, *args, **kwargs):
        with super().client(*args, **kwargs) as client:
            client.timeout = httpx.Timeout(15, connect=5)
            started = time.monotonic()
            client.event_hooks['response'] = [lambda response: print(
                'LOCAL HTTP failure status=' + str(response.status_code) if response.status_code >= 500 else '', flush=True)
                if response.status_code >= 500 else None]
            try:
                yield client
            except DocumentFailure:
                raise
            except Exception as failure:
                print('LOCAL client class=' + type(failure).__name__ + ' seconds=' + str(round(time.monotonic()-started,1)),flush=True)
                raise


class LocalDocuments(LocalHeadroom, SupabaseDocuments):
    pass


class LocalStorage(LocalHeadroom, SupabaseStorage):
    pass


def run():
    assert_local_stack()
    status = subprocess.run(cli_command()+['status','-o','json'],cwd=ROOT,capture_output=True,timeout=45)
    assert status.returncode == 0
    config=json.loads(status.stdout);url=local_api_url(config)
    gate,key_id=secrets.token_hex(32),'library-fixture-'+uuid4().hex
    sql("insert into studybuddy.backend_verifiers values ('"+key_id+"','"+hashlib.sha256(gate.encode()).hexdigest()+"',true); notify pgrst,'reload schema';")
    settings=SimpleNamespace(supabase_url=url,supabase_key=config['ANON_KEY'],save_backend_key=lambda:gate,
        supabase_s3_region='local',supabase_s3_key_id='stub',supabase_s3_anon_key=config['ANON_KEY'])
    repository,storage=LocalDocuments(settings),LocalStorage(settings)
    admin={'apikey':config['ANON_KEY'],'Authorization':'Bearer '+config['SERVICE_ROLE_KEY']}
    owners=[];passed=[];stage='setup'
    def check(label,condition):
        assert condition,label
        passed.append(label);print('PASS '+label,flush=True)
    def call(identity,action,payload):
        nonlocal stage
        stage=action;started=time.monotonic()
        try: return repository.call(identity,action,payload,time.monotonic()+45)
        except DocumentFailure as failure:
            print('LOCAL RPC stage='+action+' code='+failure.code+' seconds='+str(round(time.monotonic()-started,1)),flush=True)
            raise
    with httpx.Client(timeout=30,trust_env=False) as client:
        try:
            for _ in range(2):
                password=secrets.token_urlsafe(32);email='library-local-'+uuid4().hex+'@example.invalid'
                result=client.post(url+'/auth/v1/admin/users',headers=admin,json={'email':email,'password':password,'email_confirm':True})
                assert result.status_code==200;owner=result.json()['id'];owners.append(SimpleNamespace(owner_id=owner,access_token=''))
                result=client.post(url+'/auth/v1/token?grant_type=password',headers={'apikey':config['ANON_KEY']},json={'email':email,'password':password})
                assert result.status_code==200;owners[-1].access_token=result.json()['access_token']
            one,two=owners;content=b'Isolated exact library original source.'
            with tempfile.TemporaryDirectory(prefix='library-provider-') as directory:
                browser,headers,_,_,_=setup(Path(directory));submitted=draft(browser,headers,file=content,title='Synthetic library')
                browser.close()
            frozen=snapshot(SaveRequest.model_validate(submitted),one.owner_id,hashlib.sha256(content).hexdigest(),len(content))
            payload={'operationId':submitted['operationId'],'digest':snapshot_digest(frozen),'snapshot':frozen}
            operation=call(one,'admit',payload)['operation']
            document={'schemaVersion':'1.0','documentId':submitted['documentId']}
            check('pending library is empty',call(one,'library',{})['items']==[])
            try: call(one,'file',document)
            except DocumentFailure as failure: check('pending file descriptor denied',failure.code=='document_unknown')
            else: raise AssertionError('pending descriptor')
            call(one,'attempt',payload);storage.upload(one,operation,content,time.monotonic()+45)
            storage.verify(one,operation,time.monotonic()+45);call(one,'verified',payload);call(one,'commit',payload)
            listed=call(one,'library',{})['items'][0]
            check('ready metadata only',set(listed)=={'documentId','title','updatedAt','revision','positions','hasOriginalFile'})
            check('title date original flag',listed['title']=='Synthetic library' and bool(listed['updatedAt']) and listed['hasOriginalFile'])
            check('independent ordinals and totals',listed['positions']=={'flashcard':{'ordinal':1,'total':1},'quiz':{'ordinal':1,'total':1}})
            check('foreign library empty',call(two,'library',{})['items']==[])
            loaded=SupabaseDocuments(settings).call(one,'reload',document,time.monotonic()+45)
            check('fresh repository restores exact bundle source positions',loaded['bundle']==frozen['bundle'] and loaded['acceptance']==frozen['acceptance'] and loaded['positions']==frozen['positions'])
            descriptor=call(one,'file',document)
            check('S3 exact integrity verified original',storage.download(one,descriptor,time.monotonic()+45)==content)
            service=Documents(repository,storage,None,SaveAdmission())
            downloaded,returned=asyncio.run(service.download(one,ReloadRequest.model_validate(document),time.monotonic()+45))
            check('service rechecks ready descriptor after S3 bytes',downloaded==content and returned==descriptor)
            for action in ('reload','file'):
                try: call(two,action,document)
                except DocumentFailure as failure: check('foreign '+action+' denied',failure.code in {'save_unknown','document_unknown'})
                else: raise AssertionError('foreign access')
            raw={'apikey':config['ANON_KEY'],'Authorization':'Bearer '+one.access_token,'x-studybuddy-backend':gate}
            rest=url+'/storage/v1/object/authenticated/studybuddy-sources/'+descriptor['objectKey']
            check('REST download denied after successful S3 read',client.get(rest,headers=raw).status_code!=200)
            sql("update studybuddy.documents set lifecycle='deleting' where document_id='"+submitted['documentId']+"';")
            check('deleting library empty',call(one,'library',{})['items']==[])
            try: storage.download(one,descriptor,time.monotonic()+45)
            except DocumentFailure: check('deleting blocks formerly readable S3 bytes',True)
            else: raise AssertionError('deleting bytes')
            sql("update studybuddy.documents set lifecycle='ready' where document_id='"+submitted['documentId']+"';")
            sql("update studybuddy.backend_verifiers set active=false where key_id='"+key_id+"';")
            try: storage.download(one,descriptor,time.monotonic()+45)
            except DocumentFailure: check('revoked backend gate blocks formerly readable S3 bytes',True)
            else: raise AssertionError('revoked bytes')
            sql("update studybuddy.backend_verifiers set active=true where key_id='"+key_id+"';")
            # A new ready generation supersedes the old key without a new model call.
            replacement=frozen | {'generationId':str(uuid4()),'expectedRevision':1,'fileHash':None,'fileSize':None}
            replacement['bundle']=frozen['bundle'] | {'generationId':replacement['generationId']}
            replacement['acceptance']=frozen['acceptance'] | {'kind':'paste'}
            change={'operationId':str(uuid4()),'digest':snapshot_digest(replacement),'snapshot':replacement}
            call(one,'admit',change);call(one,'commit',change)
            try: storage.download(one,descriptor,time.monotonic()+45)
            except DocumentFailure: check('superseded object denied after earlier S3 read',True)
            else: raise AssertionError('superseded bytes')
            check('replacement reports no original file',not call(one,'library',{})['items'][0]['hasOriginalFile'])
            print('Library provider acceptance: '+str(len(passed))+' checks passed; local only, zero model calls.',flush=True)
        except Exception as failure:
            print('FAIL stage='+stage+' class='+type(failure).__name__,flush=True)
            raise SystemExit(1) from None
        finally:
            for identity in owners:
                owner=identity.owner_id
                objects=sql("select object_key from studybuddy.save_objects where owner_id='"+owner+"';").splitlines()
                if objects: client.request('DELETE',url+'/storage/v1/object/studybuddy-sources',headers=admin,json={'prefixes':objects})
                sql('begin;'+''.join("delete from studybuddy."+table+" where owner_id='"+owner+"';" for table in ('save_objects','save_operations','progress','bundles','contents','documents'))+'commit;')
                client.delete(url+'/auth/v1/admin/users/'+owner,headers=admin)
            sql("delete from studybuddy.backend_verifiers where key_id='"+key_id+"';")


if __name__=='__main__': run()
