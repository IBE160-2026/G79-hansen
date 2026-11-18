"""Focused, guarded LOCAL deletion protocol/Storage race acceptance.

Creates only temporary synthetic accounts in studybuddy-save-local. No .env,
hosted targets, real model calls or global reset. Never prints credentials.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import tempfile
from threading import Event
import time
from types import SimpleNamespace
from uuid import uuid4
import httpx
from save_provider_acceptance import assert_local_stack,cli_command,local_api_url,sql,ROOT
from library_provider_acceptance import LocalDocuments,LocalStorage
from app.adapters.documents import DocumentFailure
from app.contracts.documents import SaveRequest,DeleteRequest,snapshot,snapshot_digest
from app.services.documents import Documents,SaveAdmission
from test_documents import setup,draft


def run():
    assert_local_stack()
    status=subprocess.run(cli_command()+['status','-o','json'],cwd=ROOT,capture_output=True,timeout=45)
    assert status.returncode==0,'isolated local CLI required'
    config=json.loads(status.stdout);url=local_api_url(config)
    gate,key_id=secrets.token_hex(32),'deletion-fixture-'+uuid4().hex
    sql("insert into studybuddy.backend_verifiers values ('"+key_id+"','"+hashlib.sha256(gate.encode()).hexdigest()+"',true); notify pgrst,'reload schema';")
    settings=SimpleNamespace(supabase_url=url,supabase_key=config['ANON_KEY'],save_backend_key=lambda:gate,
        supabase_s3_region='local',supabase_s3_key_id='stub',supabase_s3_anon_key=config['ANON_KEY'])
    repository,storage=LocalDocuments(settings),LocalStorage(settings)
    admin={'apikey':config['ANON_KEY'],'Authorization':'Bearer '+config['SERVICE_ROLE_KEY']}
    owners=[];passed=[];stage='setup'
    def check(label,condition):
        assert condition,label
        passed.append(label);print('PASS '+label,flush=True)
    def call(owner,action,payload):
        nonlocal stage
        stage=action;return repository.call(owner,action,payload,time.monotonic()+45)
    def failure(owner,action,payload,code):
        try:call(owner,action,payload)
        except DocumentFailure as result:return result.code==code
        return False
    with httpx.Client(timeout=30,trust_env=False) as client:
        try:
            for _ in range(2):
                password=secrets.token_urlsafe(32);email='deletion-local-'+uuid4().hex+'@example.invalid'
                response=client.post(url+'/auth/v1/admin/users',headers=admin,json={'email':email,'password':password,'email_confirm':True})
                assert response.status_code==200;owners.append(SimpleNamespace(owner_id=response.json()['id'],access_token=''))
                response=client.post(url+'/auth/v1/token?grant_type=password',headers={'apikey':config['ANON_KEY']},json={'email':email,'password':password})
                assert response.status_code==200;owners[-1].access_token=response.json()['access_token']
            one,two=owners;content=b'Isolated synthetic deletion original.'
            with tempfile.TemporaryDirectory(prefix='deletion-provider-') as directory:
                browser,headers,_,_,_=setup(Path(directory));submitted=draft(browser,headers,file=content);browser.close()
            frozen=snapshot(SaveRequest.model_validate(submitted),one.owner_id,hashlib.sha256(content).hexdigest(),len(content))
            def admission(target=None,revision=None):
                value=deepcopy(frozen);value['documentId']=target or str(uuid4());value['expectedRevision']=revision
                value['generationId']=str(uuid4());value['bundle']['generationId']=value['generationId']
                payload={'operationId':str(uuid4()),'digest':snapshot_digest(value),'snapshot':value}
                return payload,call(one,'admit',payload)['operation']
            def ready(payload,operation):
                attempt=call(one,'attempt',payload)
                storage.upload(one,operation,content,time.monotonic()+45)
                call(one,'upload_settled',payload|{'uploadId':attempt['uploadId']})
                storage.verify(one,operation,time.monotonic()+45);call(one,'verified',payload)
                return call(one,'commit',payload)
            first,old=admission();ready(first,old)
            change,current=admission(old['documentId'],1);ready(change,current)
            deletion={'schemaVersion':'1.0','documentId':old['documentId'],'operationId':str(uuid4())}
            check('foreign RPC cannot delete owned document',failure(two,'delete',deletion,'document_unknown'))
            check('foreign discovery reveals no deletion',call(two,'deletions',{})['deletions']==[])
            raw={'apikey':config['ANON_KEY'],'Authorization':'Bearer '+two.access_token,'x-studybuddy-backend':gate}
            response=client.request('DELETE',url+'/storage/v1/object/studybuddy-sources',headers=raw,json={'prefixes':[current['objectKey']]})
            check('foreign Storage DELETE has no named removal receipt',response.status_code!=200 or response.json()==[])
            service=Documents(repository,storage,None,SaveAdmission())
            deleted=asyncio.run(service.delete(one,DeleteRequest.model_validate(deletion),time.monotonic()+90))
            check('current and superseded files complete after exact provider acknowledgements',deleted['status']=='deleted')
            check('completed deletion erases document and source bundle progress',sql("select count(*) from studybuddy.documents where owner_id='"+one.owner_id+"';")=='0')
            check('completed deletion erases obsolete Save payload rows',sql("select count(*) from studybuddy.save_operations where owner_id='"+one.owner_id+"';")=='0')
            check('fresh service exact retry replays lost successful reply',asyncio.run(Documents(repository,storage,None,SaveAdmission()).delete(one,DeleteRequest.model_validate(deletion),time.monotonic()+45))==deleted)
            check('stale Save cannot resurrect document',failure(one,'admit',first,'save_conflict'))
            # Actual HTTP upload paused after the first chunk. Delete fences
            # metadata finalization, but the durable uncertain intent remains.
            base,baseop=admission();ready(base,baseop)
            late,lateop=admission(baseop['documentId'],1)
            attempt=call(one,'attempt',late);entered,release=Event(),Event()
            def chunks():
                yield content[:1];entered.set();assert release.wait(20);yield content[1:]
            def upload():
                with httpx.Client(timeout=30,trust_env=False) as delayed:
                    return delayed.post(url+'/storage/v1/object/studybuddy-sources/'+lateop['objectKey'],headers={
                        'apikey':config['ANON_KEY'],'Authorization':'Bearer '+one.access_token,
                        'x-studybuddy-backend':gate,'Content-Type':'text/plain'},content=chunks()).status_code
            retry={'schemaVersion':'1.0','documentId':baseop['documentId'],'operationId':str(uuid4())}
            with ThreadPoolExecutor(1) as pool:
                future=pool.submit(upload)
                assert entered.wait(10)
                pending=asyncio.run(service.delete(one,DeleteRequest.model_validate(retry),time.monotonic()+60))
                check('delayed actual upload keeps deletion pending',pending['status']=='deleting')
                release.set();status=future.result(timeout=35)
                check('deleting fences late provider upload finalization',status not in (200,201))
            check('uncertain attempt is not settled by a timer or missing metadata',sql("select count(*) from studybuddy.upload_attempts where owner_id='"+one.owner_id+"' and not settled;")=='1')
            check('fresh process discovery retains retry identity',call(one,'deletions',{})['deletions'][0]['operationId']==retry['operationId'])
            check('restart retry cannot falsely complete unknown object',asyncio.run(Documents(repository,storage,None,SaveAdmission()).delete(one,DeleteRequest.model_validate(retry),time.monotonic()+60))['status']=='deleting')
            check('late Save commit cannot publish',failure(one,'commit',late,'save_conflict'))
            check('late progress cannot recreate state',failure(one,'progress_write',{'schemaVersion':'1.0','documentId':baseop['documentId'],
                'generationId':base['snapshot']['generationId'],'mutationId':str(uuid4()),'expectedProgressRevision':1,
                'positions':base['snapshot']['positions']},'document_unknown'))
            print('Deletion provider acceptance: '+str(len(passed))+' checks passed; local synthetic data only.',flush=True)
        except Exception as failure_result:
            print('FAIL stage='+stage+' class='+type(failure_result).__name__,flush=True)
            raise SystemExit(1) from None
        finally:
            for owner in owners:
                oid=owner.owner_id
                objects=sql("select object_key from studybuddy.save_objects where owner_id='"+oid+"';").splitlines()
                if objects:client.request('DELETE',url+'/storage/v1/object/studybuddy-sources',headers=admin,json={'prefixes':objects})
                sql('begin;'+''.join("delete from studybuddy."+table+" where owner_id='"+oid+"';" for table in
                    ('upload_attempts','save_objects','progress_mutations','save_operations','progress','bundles','contents','documents','deleted_operations','deleted_progress','deletions'))+'commit;')
                client.delete(url+'/auth/v1/admin/users/'+oid,headers=admin)
            sql("delete from studybuddy.backend_verifiers where key_id='"+key_id+"';")


if __name__=='__main__':run()
