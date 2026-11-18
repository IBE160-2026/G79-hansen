"""Guarded isolated-local progress RPC race and lost-successful-reply evidence.

Uses only temporary local synthetic accounts; never reads .env or hosted config.
Production deadlines remain unchanged. Imported local harness gives tests timeout
headroom and checks the named isolated stack and loopback-advertised endpoint.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import tempfile
from threading import Barrier
import time
from types import SimpleNamespace
from uuid import uuid4
import httpx
from save_provider_acceptance import assert_local_stack, cli_command, local_api_url, sql, ROOT
from library_provider_acceptance import LocalDocuments
from app.adapters.documents import DocumentFailure
from app.contracts.documents import SaveRequest, snapshot, snapshot_digest
from test_documents import setup, draft


class DropSuccessfulReply(httpx.BaseTransport):
    """Perform the real RPC, consume committed success, then lose its reply."""
    def __init__(self):
        self.transport = httpx.HTTPTransport(retries=0,trust_env=False)
        self.committed = None

    def handle_request(self,request):
        response = self.transport.handle_request(request)
        response.read()
        if response.status_code == 200 and request.url.path.endswith('/sb_save_progress_write_v1'):
            value = response.json()
            if 'error' not in value:
                self.committed = value
                response.close()
                raise httpx.ReadError('synthetic lost committed reply')
        return response

    def close(self):
        self.transport.close()


def run():
    assert_local_stack()
    status = subprocess.run(cli_command()+['status','-o','json'],cwd=ROOT,capture_output=True,timeout=45)
    assert status.returncode == 0, 'local CLI unavailable'
    config = json.loads(status.stdout); url = local_api_url(config)
    gate,key_id = secrets.token_hex(32),'progress-fixture-'+uuid4().hex
    sql("insert into studybuddy.backend_verifiers values ('"+key_id+"','"+hashlib.sha256(gate.encode()).hexdigest()+"',true); notify pgrst,'reload schema';")
    settings = SimpleNamespace(supabase_url=url,supabase_key=config['ANON_KEY'],save_backend_key=lambda:gate)
    repository = LocalDocuments(settings)
    admin = {'apikey':config['ANON_KEY'],'Authorization':'Bearer '+config['SERVICE_ROLE_KEY']}
    owners=[]; passed=[]; stage='setup'
    def check(label,condition):
        assert condition,label
        passed.append(label); print('PASS '+label,flush=True)
    def call(identity,action,payload,repo=repository):
        nonlocal stage
        stage=action
        return repo.call(identity,action,payload,time.monotonic()+45)
    def failure(identity,action,payload,expected):
        try: call(identity,action,payload)
        except DocumentFailure as error: return error.code==expected
        return False
    with httpx.Client(timeout=30,trust_env=False) as client:
        try:
            for _ in range(2):
                password=secrets.token_urlsafe(32);email='progress-local-'+uuid4().hex+'@example.invalid'
                response=client.post(url+'/auth/v1/admin/users',headers=admin,json={'email':email,'password':password,'email_confirm':True})
                assert response.status_code==200
                owners.append(SimpleNamespace(owner_id=response.json()['id'],access_token=''))
                response=client.post(url+'/auth/v1/token?grant_type=password',headers={'apikey':config['ANON_KEY']},json={'email':email,'password':password})
                assert response.status_code==200;owners[-1].access_token=response.json()['access_token']
            one,two=owners
            with tempfile.TemporaryDirectory(prefix='progress-provider-') as directory:
                browser,headers,model,_,_=setup(Path(directory))
                model.result['flashcards']*=2;model.result['quiz']*=2
                submitted=draft(browser,headers,title='Synthetic progress');browser.close()
            frozen=snapshot(SaveRequest.model_validate(submitted),one.owner_id,None,None)
            save={'operationId':submitted['operationId'],'digest':snapshot_digest(frozen),'snapshot':frozen}
            call(one,'admit',save);ready=call(one,'commit',save)
            check('Save records initial progress revision1',ready['progressRevision']==1)
            read={'schemaVersion':'1.0','documentId':submitted['documentId'],'generationId':frozen['generationId']}
            initial=call(one,'progress_read',read)
            check('fresh progress read matches Save',initial['progressRevision']==1 and initial['positions']==frozen['positions'])
            cards=frozen['bundle']['flashcards'];quiz=frozen['bundle']['quiz']
            writes=[read|{'mutationId':str(uuid4()),'expectedProgressRevision':1,'positions':{
                'flashcardId':cards[index]['id'],'quizId':quiz[1-index]['id']}} for index in range(2)]
            barrier=Barrier(2)
            def race(payload):
                barrier.wait(timeout=10)
                started=time.monotonic()
                try: result=call(one,'progress_write',payload)
                except DocumentFailure as error: result={'error':error.code}
                return started,time.monotonic(),result,payload
            with ThreadPoolExecutor(max_workers=2) as pool:
                results=list(pool.map(race,writes))
            check('actual same-revision RPC requests overlap',max(item[0] for item in results)<min(item[1] for item in results))
            winners=[item for item in results if 'error' not in item[2]]
            losers=[item for item in results if item[2].get('error')=='progress_conflict']
            check('one concurrent CAS wins and one conflicts',len(winners)==len(losers)==1)
            winner=winners[0];latest=call(one,'progress_read',read)
            check('race advanced exactly one independent revision',latest['progressRevision']==2 and latest['positions']==winner[3]['positions'])
            check('identical winning retry replays old expected revision',call(one,'progress_write',winner[3])==winner[2])
            check('same mutation changed request rejected',failure(one,'progress_write',winner[3]|{'expectedProgressRevision':2},'progress_mismatch'))
            # Simulate an actual successful network reply lost after DB commit.
            lost=read|{'mutationId':str(uuid4()),'expectedProgressRevision':2,'positions':frozen['positions']}
            drop=DropSuccessfulReply();dropping=LocalDocuments(settings,transport=drop)
            check('successful real RPC reply is lost',failure_with_drop(one,lost,dropping))
            check('lost reply exact retry returns committed outcome',drop.committed is not None and call(one,'progress_write',lost)==drop.committed)
            check('lost reply advances once',call(one,'progress_read',read)['progressRevision']==3)
            check('stale losing request remains conflict',failure(one,'progress_write',losers[0][3],'progress_conflict'))
            check('Save replay never adopts newer progress revision',call(one,'commit',save)['progressRevision']==1)
            check('fresh adapter restores durable acknowledged positions',call(one,'progress_read',read,LocalDocuments(settings))==drop.committed)
            check('foreign read and write reveal no metadata',failure(two,'progress_read',read,'document_unknown') and failure(two,'progress_write',lost,'document_unknown'))
            bad=lost|{'mutationId':str(uuid4()),'expectedProgressRevision':3,'positions':{'flashcardId':cards[0]['id'],'quizId':'unknown'}}
            check('both current item memberships checked',failure(one,'progress_write',bad,'progress_mismatch'))
            unknown=read|{'documentId':str(uuid4())}
            check('unknown progress target never recreated',failure(one,'progress_write',lost|unknown,'document_unknown'))
            # Replacement Save uses the same document lock and retains history.
            replacement=deepcopy(frozen);replacement['generationId']=str(uuid4());replacement['bundle']['generationId']=replacement['generationId'];replacement['expectedRevision']=1
            next_save={'operationId':str(uuid4()),'digest':snapshot_digest(replacement),'snapshot':replacement}
            count_before=sql("select count(*) from studybuddy.progress_mutations where owner_id='"+one.owner_id+"';")
            call(one,'admit',next_save);call(one,'commit',next_save)
            check('replacement rejects old committed replay',failure(one,'progress_write',lost,'progress_generation'))
            check('replacement preserves exact old generation identities',sql("select count(*) from studybuddy.progress_mutations where owner_id='"+one.owner_id+"' and generation_id='"+frozen['generationId']+"';")==count_before)
            changed_read=read|{'generationId':replacement['generationId']}
            check('replacement progress starts at1',call(one,'progress_read',changed_read)['progressRevision']==1)
            sql("update studybuddy.documents set lifecycle='deleting' where owner_id='"+one.owner_id+"';")
            check('deleting blocks read and write without resurrection',failure(one,'progress_read',changed_read,'document_unknown') and failure(one,'progress_write',lost|changed_read,'document_unknown'))
            print('Progress provider acceptance: '+str(len(passed))+' checks passed; isolated local only, zero real inference.',flush=True)
        except Exception as error:
            print('FAIL stage='+stage+' class='+type(error).__name__,flush=True)
            raise SystemExit(1) from None
        finally:
            for identity in owners:
                owner=identity.owner_id
                sql('begin;'+''.join("delete from studybuddy."+table+" where owner_id='"+owner+"';" for table in
                    ('progress_mutations','save_objects','save_operations','progress','bundles','contents','documents'))+'commit;')
                client.delete(url+'/auth/v1/admin/users/'+owner,headers=admin)
            sql("delete from studybuddy.backend_verifiers where key_id='"+key_id+"';")


def failure_with_drop(identity,payload,repository):
    try: repository.call(identity,'progress_write',payload,time.monotonic()+45)
    except DocumentFailure: return True
    return False


if __name__=='__main__':run()
