"""One isolated-local regression for concurrent deletion identity reuse."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import subprocess
import time
from uuid import uuid4
from save_provider_acceptance import sql,DOCKER,DB_CONTAINER,assert_local_stack
from save_sql_concurrency_acceptance import literal


def run():
    assert_local_stack()
    owner,operation,first,second=[str(uuid4()) for _ in range(4)]
    gate,key=uuid4().hex,'delete-identity-'+uuid4().hex
    names=['delete-identity-'+uuid4().hex for _ in range(2)]
    holder=None
    def authenticated(document):
        payload=json.dumps({'schemaVersion':'1.0','documentId':document,'operationId':operation})
        return ("begin; set local role authenticated; set local statement_timeout='25s'; "
            'set local request.jwt.claim.sub='+literal(owner)+'; set local request.jwt.claims='+
            literal(json.dumps({'sub':owner,'role':'authenticated'}))+'; set local request.headers='+
            literal(json.dumps({'x-studybuddy-backend':gate}))+'; select public.sb_save_delete_v1('+literal(payload)+'::jsonb); commit;')
    try:
        sql('insert into auth.users(id,email) values('+literal(owner)+','+literal(key+'@example.invalid')+'); '+
            'insert into studybuddy.backend_verifiers values('+literal(key)+','+literal(hashlib.sha256(gate.encode()).hexdigest())+',true); '+
            'insert into studybuddy.documents(owner_id,document_id,generation_id,title,lifecycle) values '+
            ','.join('('+','.join(map(literal,(owner,d,str(uuid4()),'Synthetic identity race','ready')))+')' for d in (first,second))+';')
        holder=subprocess.Popen(DOCKER+['exec','-i',DB_CONTAINER,'psql','-U','postgres','-d','postgres','-qAt','-v','ON_ERROR_STOP=1'],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        holder.stdin.write('begin; select 1 from studybuddy.documents where document_id='+literal(first)+" for update; select 'LOCK_HELD';\n")
        holder.stdin.flush()
        def marker():
            while True:
                line=holder.stdout.readline()
                if not line:raise AssertionError('identity race lock fixture ended')
                if line.strip()=='LOCK_HELD':return
        with ThreadPoolExecutor(1) as pool:pool.submit(marker).result(timeout=10)
        def waiting(selected):
            return int(sql('select count(*) from pg_stat_activity where application_name in ('+
                ','.join(map(literal,selected))+") and wait_event_type='Lock';"))
        with ThreadPoolExecutor(2) as pool:
            one=pool.submit(sql,'set application_name='+literal(names[0])+'; '+authenticated(first))
            try:
                until=time.monotonic()+10
                while time.monotonic()<until and waiting(names[:1])!=1:time.sleep(.05)
                assert waiting(names[:1])==1,'first deletion must reach held document row'
                two=pool.submit(sql,'set application_name='+literal(names[1])+'; '+authenticated(second))
                until=time.monotonic()+10
                while time.monotonic()<until and not two.done() and waiting(names)!=2:time.sleep(.05)
                both_waiting=waiting(names)==2
            finally:
                holder.stdin.write('rollback;\n');holder.stdin.flush();holder.stdin.close();holder.wait(timeout=10)
            results=[json.loads(next(line for line in task.result(timeout=15).splitlines() if line.startswith('{'))) for task in (one,two)]
        assert both_waiting,'second document deletion must wait for the shared operation identity'
        assert results[0]['status']=='deleting' and results[1]=={'error':'delete_mismatch'}
        assert sql('select lifecycle from studybuddy.documents where document_id='+literal(second)+';')=='ready'
        assert sql('select document_id from studybuddy.deletions where owner_id='+literal(owner)+' and operation_id='+literal(operation)+';')==first
        print('PASS concurrent identity reuse fences only its bound document; unrelated document stays ready',flush=True)
    finally:
        if holder and holder.poll() is None:
            try:holder.stdin.write('rollback;\n');holder.stdin.flush();holder.stdin.close();holder.wait(timeout=10)
            except Exception:holder.terminate()
        sql('delete from studybuddy.deletions where owner_id='+literal(owner)+'; delete from studybuddy.documents where owner_id='+
            literal(owner)+'; delete from auth.users where id='+literal(owner)+'; delete from studybuddy.backend_verifiers where key_id='+literal(key)+';')


if __name__=='__main__':run()
