"""Actual local expiry fairness/replay checks; no hosted or model calls."""
import hashlib
import json
import subprocess
import time
from uuid import uuid4
from save_provider_acceptance import sql, DOCKER, assert_local_stack


def quoted(value):
    return "'"+str(value).replace("'","''")+"'"


def run():
    assert_local_stack()
    owner, busy, free, ready = [str(uuid4()) for _ in range(4)]
    generation, ready_op = str(uuid4()), str(uuid4())
    key, key_id = uuid4().hex+uuid4().hex, 'batch-fixture-'+uuid4().hex
    passed, lock = [], None
    def check(name, condition):
        assert condition,name
        passed.append(name)
        print('PASS '+name,flush=True)
    try:
        commands=['begin; insert into auth.users(id,email) values ('+quoted(owner)+",'batch-local@example.invalid');",
            'insert into studybuddy.backend_verifiers values ('+quoted(key_id)+','+
            quoted(hashlib.sha256(key.encode()).hexdigest())+',true);']
        for did in (busy,free,ready):
            commands.append('insert into studybuddy.documents(owner_id,document_id,generation_id,title,lifecycle,revision) values ('+
                ','.join(map(quoted,(owner,did,generation,'Synthetic batch staging', 'ready' if did==ready else 'pending')))+
                (',1);' if did==ready else ',0);'))
        for did, count, hours in ((busy,101,2),(free,1,1)):
            for _ in range(count):
                oid=str(uuid4())
                snapshot={'ownerId':owner,'documentId':did,'generationId':generation,'source':'synthetic staging'}
                commands.append('insert into studybuddy.save_operations(owner_id,operation_id,document_id,generation_id,digest,snapshot,admitted_at,expires_at) select '+
                    ','.join(map(quoted,(owner,oid,did,generation,'a'*64,json.dumps(snapshot))))+
                    "::jsonb, cutoff-interval '7 days',cutoff from (select clock_timestamp()-interval '"+str(hours)+" hours' cutoff) q;")
        outcome={'status':'ready','operationId':ready_op,'documentId':ready,'generationId':generation,'revision':1,'digest':'b'*64}
        commands.append('insert into studybuddy.save_operations(owner_id,operation_id,document_id,generation_id,digest,status,outcome,completed_at) values ('+
            ','.join(map(quoted,(owner,ready_op,ready,generation,'b'*64,'ready',json.dumps(outcome))))+'::jsonb,clock_timestamp()); commit;')
        sql(''.join(commands))
        lock=subprocess.Popen(DOCKER+['exec','-i','supabase_db_studybuddy-save-local','psql','-U','postgres','-d','postgres','-qAt','-v','ON_ERROR_STOP=1'],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        lock.stdin.write("begin; set local statement_timeout='20s'; select 1 from studybuddy.documents where document_id="+quoted(busy)+" for update; select 'LOCK_HELD';\n")
        lock.stdin.flush()
        while True:
            line=lock.stdout.readline()
            if not line: raise AssertionError('fixture lock process ended')
            if line.strip()=='LOCK_HELD':break
        sql("set statement_timeout='4s'; select studybuddy.expire_staging_admin(100);")
        check('busy first batch cannot starve later unlocked staging',sql("select status='expired' and snapshot is null from studybuddy.save_operations where document_id="+quoted(free)+';')=='t')
        claims=json.dumps({'sub':owner,'role':'authenticated'})
        headers=json.dumps({'x-studybuddy-backend':key})
        payload=json.dumps({'operationId':ready_op,'digest':'b'*64})
        result=sql("set statement_timeout='3s'; begin; set local role authenticated; set local request.jwt.claims="+quoted(claims)+
            '; set local request.jwt.claim.sub='+quoted(owner)+'; set local request.headers='+quoted(headers)+
            '; select public.sb_save_get_v1('+quoted(payload)+'::jsonb); commit;')
        replay=json.loads(next(line for line in result.splitlines() if line.startswith('{')))
        check('completed owner replay skips unrelated locked expiry targets',replay['operation']['status']=='ready')
        check('locked staging is retained for later maintenance',sql("select count(*) from studybuddy.save_operations where document_id="+quoted(busy)+" and status='pending' and snapshot is not null;")=='101')
        lock.stdin.write('rollback;\n');lock.stdin.flush();lock.stdin.close();lock.wait(timeout=10)
        # A concurrently scheduled batch may temporarily own rows skipped by
        # this manual batch. Use fresh bounded transactions until both settle.
        until=time.monotonic()+15
        remaining='101'
        while remaining!='0' and time.monotonic()<until:
            sql('select studybuddy.expire_staging_admin(100);')
            remaining=sql("select count(*) from studybuddy.save_operations where document_id="+quoted(busy)+" and (status<>'expired' or snapshot is not null);")
            if remaining!='0':time.sleep(.2)
        if remaining!='0':print('Remaining synthetic expiry rows: '+remaining,flush=True)
        check('released staging expires in subsequent bounded batches',remaining=='0')
        print('Local expiry fairness acceptance:',len(passed),'checks passed.',flush=True)
    except Exception as exc:
        print('FAIL local expiry fairness: '+type(exc).__name__,flush=True)
        if str(exc).startswith('local SQL failed: '):print(str(exc),flush=True)
        raise SystemExit(1) from None
    finally:
        if lock is not None and lock.poll() is None:
            try:
                lock.stdin.write('rollback;\n');lock.stdin.flush();lock.stdin.close();lock.wait(timeout=10)
            except Exception:
                lock.terminate()
        sql('begin; '+''.join('delete from studybuddy.'+table+' where owner_id='+quoted(owner)+';'
            for table in ('save_objects','save_operations','progress','bundles','contents','documents'))+
            'delete from auth.users where id='+quoted(owner)+'; delete from studybuddy.backend_verifiers where key_id='+quoted(key_id)+'; commit;')


if __name__=='__main__':
    run()
