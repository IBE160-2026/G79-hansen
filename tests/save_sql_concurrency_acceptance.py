"""Explicit local-only lock/expiry/cron acceptance; no hosted or model calls.

Uses the same fixed, isolated WSL stack as save_provider_acceptance.py. Database
administration creates/removes synthetic rows; business commits run with the
authenticated role plus fixture owner claims/backend gate. No credentials print.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import subprocess
import time
from uuid import uuid4

from save_provider_acceptance import sql, DOCKER, DB_CONTAINER, assert_local_stack


def literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def run():
    owner, other = str(uuid4()), str(uuid4())
    key, key_id = uuid4().hex + uuid4().hex, 'expiry-fixture-' + uuid4().hex
    verifier = hashlib.sha256(key.encode()).hexdigest()
    passed, label = [], 'setup'

    def check(name, condition):
        nonlocal label
        label = name
        assert condition, name
        passed.append(name)
        print('PASS ' + name, flush=True)

    def authenticated(query, own=owner):
        claims = json.dumps({'sub':own,'role':'authenticated'})
        headers = json.dumps({'x-studybuddy-backend':key})
        return ('begin; set local role authenticated; set local request.jwt.claims=' + literal(claims) +
            '; set local request.jwt.claim.sub=' + literal(own) + '; set local request.headers=' + literal(headers) +
            '; ' + query + '; commit;')

    def fixture(*, seconds=8, own=owner, file=False, target=None, revision=None):
        oid, did, gid = str(uuid4()), target or str(uuid4()), str(uuid4())
        source={'schemaVersion':'1.0','id':'fixture','title':'Synthetic private staging title',
                'units':[{'id':'u1','kind':'paragraph','location':1,'text':'Synthetic source '+gid}]}
        settings={'language':'nb','detail':'short','subject':''}
        bundle={'schemaVersion':'1.0','generationId':gid,'source':source,'settings':settings,
                'summary':[],'concepts':[],
                'flashcards':[{'id':'flash-'+gid,'question':'Synthetic question','answer':'Synthetic answer','references':[]}],
                'quiz':[{'id':'quiz-'+gid,'question':'Synthetic question','answer':'Synthetic answer','references':[]}],
                'insufficiency':dict.fromkeys(
                    ('summary','concepts','flashcards','quiz'),'Synthetic insufficient section'),'warnings':[]}
        snapshot={'schemaVersion':'1.0','ownerId':own,'documentId':did,'generationId':gid,
                  'expectedRevision':revision,'title':'Synthetic private staging title',
                  'acceptance':{'source':source,'settings':settings,'kind':'text-file' if file else 'paste'},
                  'bundle':bundle,'positions':{'flashcardId':'flash-'+gid,'quizId':'quiz-'+gid},
                  'fileHash':'a'*64 if file else None,'fileSize':1 if file else None}
        digest=hashlib.sha256(json.dumps(snapshot,sort_keys=True).encode()).hexdigest()
        sql('begin; '+('insert into studybuddy.documents(owner_id,document_id,generation_id,title,lifecycle) values ('+
            ','.join(map(literal,(own,did,gid,snapshot['title'],'pending')))+'); ' if target is None else '')+
            'insert into studybuddy.save_operations(owner_id,operation_id,document_id,generation_id,digest,snapshot,expected_revision,admitted_at,expires_at) '+
            'select '+','.join(map(literal,(own,oid,did,gid,digest,json.dumps(snapshot))))+'::jsonb,'+
            (str(revision) if revision is not None else 'null')+", cutoff-interval '7 days',cutoff "+
            'from (select clock_timestamp()+('+str(seconds)+"*interval '1 second') cutoff) q; "+
            ("insert into studybuddy.save_objects(owner_id,operation_id,object_key,file_hash,file_size,media_type,attempts,write_unknown) values ("+
             ','.join(map(literal,(own,oid,own+'/'+did+'/'+gid+'/'+oid,'a'*64)))+",1,'text/plain',1,true); " if file else '')+'commit;')
        return {'operationId':oid,'documentId':did,'digest':digest,'ownerId':own,'snapshot':snapshot,
                'objectKey':own+'/'+did+'/'+gid+'/'+oid if file else None}

    def operation_payload(operation):
        return literal(json.dumps({key:operation[key] for key in ('operationId','digest')}))+'::jsonb'

    def result_json(result):
        return json.loads(next(line for line in result.splitlines() if line.startswith('{')))

    def race(operation, actions, lock_table, lock_column, identifier):
        """Separate psql connections genuinely wait at one held row, then race."""
        lock=subprocess.Popen(DOCKER+['exec','-i',DB_CONTAINER,'psql','-U','postgres','-d','postgres','-qAt',
            '-v','ON_ERROR_STOP=1'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        names=['save-race-'+uuid4().hex for _ in actions]
        try:
            lock.stdin.write("begin; set local statement_timeout='35s'; select 1 from studybuddy."+lock_table+
                ' where '+lock_column+'='+literal(identifier)+" for update; select 'LOCK_HELD';\n")
            lock.stdin.flush()
            def marker():
                while True:
                    line=lock.stdout.readline()
                    if not line: raise AssertionError('race lock fixture ended')
                    if line.strip()=='LOCK_HELD': return
            with ThreadPoolExecutor(max_workers=1) as pool: pool.submit(marker).result(timeout=10)
            with ThreadPoolExecutor(max_workers=2) as pool:
                pending=[pool.submit(sql,'set application_name='+literal(name)+"; set statement_timeout='30s'; "+
                    authenticated('select public.sb_save_'+action+'_v1('+operation_payload(op)+')'))
                    for name,(action,op) in zip(names,actions)]
                until=time.monotonic()+10
                waiting='0'
                while time.monotonic()<until:
                    waiting=sql('select count(*) from pg_stat_activity where application_name in ('+
                        ','.join(map(literal,names))+") and wait_event_type='Lock';")
                    if waiting==str(len(actions)): break
                    time.sleep(.1)
                check('concurrent '+operation+' connections both reach lock barrier',waiting==str(len(actions)) and
                    not any(task.done() for task in pending))
                lock.stdin.write('rollback;\n');lock.stdin.flush();lock.stdin.close();lock.wait(timeout=10)
                return [result_json(task.result(timeout=15)) for task in pending]
        finally:
            if lock.poll() is None:
                try:
                    lock.stdin.write('rollback;\n');lock.stdin.flush();lock.stdin.close();lock.wait(timeout=10)
                except Exception: lock.terminate()

    def coherent(operation):
        saved=result_json(sql(authenticated('select public.sb_save_reload_v1('+literal(json.dumps(
            {'documentId':operation['documentId']}))+'::jsonb)')))
        return (saved['bundle']==operation['snapshot']['bundle'] and
                saved['acceptance']==operation['snapshot']['acceptance'] and
                saved['positions']==operation['snapshot']['positions'] and
                sql('select d.generation_id=c.generation_id and d.generation_id=b.generation_id and '+
                    'd.generation_id=p.generation_id and d.object_key is not distinct from '+literal(operation['objectKey'])+
                    ' and exists(select 1 from studybuddy.save_objects f where f.operation_id='+literal(operation['operationId'])+
                    ' and f.object_key=d.object_key) from studybuddy.documents d join studybuddy.contents c using(owner_id,document_id) '+
                    'join studybuddy.bundles b using(owner_id,document_id) join studybuddy.progress p using(owner_id,document_id) '+
                    'where d.document_id='+literal(operation['documentId'])+';')=='t')

    def state(operation):
        return json.loads(sql("select jsonb_build_object('status',o.status,'erased',o.snapshot is null,"+
            "'title',d.title,'lifecycle',d.lifecycle,'revision',d.revision) from studybuddy.save_operations o "+
            'join studybuddy.documents d using(owner_id,document_id) where o.operation_id='+literal(operation['operationId'])+';'))

    try:
        assert_local_stack()
        sql('insert into auth.users(id,email) values ('+literal(owner)+",'expiry-local-one@example.invalid'),("+
            literal(other)+",'expiry-local-two@example.invalid'); insert into studybuddy.backend_verifiers values ("+
            ','.join(map(literal,(key_id,verifier)))+',true);')
        for kind in ('operation','document'):
            operation=fixture(seconds=8)
            table, column = ('save_operations','operation_id') if kind=='operation' else ('documents','document_id')
            identifier=operation['operationId'] if kind=='operation' else operation['documentId']
            lock=subprocess.Popen(DOCKER+['exec','-i',DB_CONTAINER,'psql','-U','postgres','-d','postgres','-qAt',
                '-v','ON_ERROR_STOP=1'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                lock.stdin.write("begin; set local statement_timeout='35s'; select 1 from studybuddy."+table+
                    ' where '+column+'='+literal(identifier)+" for update; select 'LOCK_HELD';\n")
                lock.stdin.flush()
                with ThreadPoolExecutor(max_workers=1) as pool:
                    def wait_marker():
                        while True:
                            line=lock.stdout.readline()
                            if not line: raise AssertionError('lock fixture ended')
                            if line.strip()=='LOCK_HELD': return
                    pool.submit(wait_marker).result(timeout=10)
                app_name='save-expiry-'+uuid4().hex
                payload={k:operation[k] for k in ('operationId','digest')}
                # The synthetic admission expires after eight seconds. Give
                # fixture transport/process scheduling separate headroom; its
                # timeout must not compete with the expiry behavior under test.
                query="set application_name="+literal(app_name)+"; set statement_timeout='30s'; "+authenticated(
                    'select public.sb_save_commit_v1('+literal(json.dumps(payload))+'::jsonb)')
                with ThreadPoolExecutor(max_workers=1) as pool:
                    pending=pool.submit(sql,query)
                    waited=False
                    for _ in range(8):
                        if sql('select count(*) from pg_stat_activity where application_name='+literal(app_name)+
                               " and wait_event_type='Lock';")=='1':
                            waited=True
                            break
                        time.sleep(.1)
                    check(kind+' commit actually waits on row lock',waited and not pending.done())
                    sql('select pg_sleep(greatest(0,extract(epoch from (expires_at-clock_timestamp())))+0.3) '+
                        'from studybuddy.save_operations where operation_id='+literal(operation['operationId'])+';')
                    lock.stdin.write('rollback;\n');lock.stdin.flush();lock.stdin.close();lock.wait(timeout=10)
                    result=pending.result(timeout=15)
                    check(kind+' wait cannot cross expiry into publication','save_expired' in result)
                value=state(operation)
                check(kind+' expired staging erased with target unpublished',value['erased'] and
                    value['status']=='expired' and value['lifecycle']=='pending' and value['revision']==0 and
                    value['title']!='Synthetic private staging title')
            finally:
                if lock.poll() is None:
                    try:
                        lock.stdin.write('rollback;\n');lock.stdin.flush();lock.stdin.close();lock.wait(timeout=10)
                    except Exception:
                        lock.terminate()
        # Two independently admitted replacements contend for the same revision.
        initial=fixture(seconds=3600)
        sql(authenticated('select public.sb_save_commit_v1('+operation_payload(initial)+')'))
        replacements=[fixture(seconds=3600,file=True,target=initial['documentId'],revision=1) for _ in range(2)]
        sql('update studybuddy.save_objects set verified=true,upload_enabled=false where operation_id in ('+
            ','.join(literal(op['operationId']) for op in replacements)+');')
        outcomes=race('replacement CAS',[('commit',op) for op in replacements],
                      'documents','document_id',initial['documentId'])
        winners=[index for index,outcome in enumerate(outcomes) if outcome.get('status')=='ready']
        check('concurrent replacement CAS has exactly one revision winner',len(winners)==1 and
              outcomes[1-winners[0]].get('error')=='save_conflict' and outcomes[winners[0]]['revision']==2)
        check('CAS winner installs coherent content bundle progress and object references',coherent(replacements[winners[0]]))
        loser=replacements[1-winners[0]]
        check('CAS loser staging erased and upload fenced',state(loser)['status']=='conflict' and state(loser)['erased'] and
              sql('select cleanup_needed and not upload_enabled from studybuddy.save_objects where operation_id='+
                  literal(loser['operationId'])+';')=='t')

        # Commit and cancellation contend for the same immutable operation.
        contested=fixture(seconds=3600,file=True)
        sql('update studybuddy.save_objects set verified=true,upload_enabled=false where operation_id='+
            literal(contested['operationId'])+';')
        committed,cancelled=race('commit cancellation',[('commit',contested),('cancel',contested)],
            'save_operations','operation_id',contested['operationId'])
        final=state(contested)
        if final['status']=='ready':
            consistent=(committed.get('status')=='ready' and final['revision']==1 and coherent(contested) and
                        contested['objectKey'] not in cancelled.get('cleanupKeys',[]))
        else:
            consistent=(final['status']=='cancelled' and committed.get('error')=='save_conflict' and final['erased'] and
                        final['revision']==0 and final['lifecycle']=='pending' and
                        contested['objectKey'] in cancelled.get('cleanupKeys',[]) and
                        sql('select cleanup_needed and not upload_enabled from studybuddy.save_objects where operation_id='+
                            literal(contested['operationId'])+';')=='t' and
                        sql('select count(*) from studybuddy.contents where document_id='+literal(contested['documentId'])+';')=='0')
        check('concurrent commit cancellation yields coherent ready or cancelled state',consistent)

        # No owner RPC touches this expired operation; only the scheduled admin
        # maintenance job may erase it while the owners are absent.
        overdue=fixture(seconds=-1,file=True)
        fresh=fixture(seconds=3600,own=other)
        jobs=sql("select count(*) from cron.job where active and command like '%studybuddy.expire_staging_admin%';")
        check('automatic staging expiry job is active',jobs=='1')
        until=time.monotonic()+85
        while state(overdue)['status']=='pending' and time.monotonic()<until:
            time.sleep(2)
        value=state(overdue)
        check('absent owner staging erased by scheduled job',value['status']=='expired' and value['erased'] and
            value['title']!='Synthetic private staging title')
        check('other unexpired owner staging preserved',state(fresh)['status']=='pending' and not state(fresh)['erased'])
        check('uncertain expired file remains fenced and registered',sql('select cleanup_needed and write_unknown and not upload_enabled '+
            'from studybuddy.save_objects where operation_id='+literal(overdue['operationId'])+';')=='t')
        check('maintenance health records execution',sql('select count(*) from studybuddy.expiry_maintenance_health '+
            "where last_completed_at>clock_timestamp()-interval '2 minutes';")=='1')
        denied=False
        try:
            sql(authenticated('select studybuddy.expire_staging_admin(100)'))
        except AssertionError:
            denied=True
        check('ordinary authenticated role cannot invoke admin expiry',denied)
        print('Local SQL/cron acceptance:',len(passed),'checks passed; no hosted/model calls.',flush=True)
    except Exception as exc:
        print('FAIL after '+label+': '+type(exc).__name__,flush=True)
        if str(exc).startswith('local SQL failed: '):
            print(str(exc),flush=True)
        raise SystemExit(1) from None
    finally:
        for own in (owner,other):
            sql('begin; '+''.join('delete from studybuddy.'+table+' where owner_id='+literal(own)+';'
                for table in ('save_objects','save_operations','progress','bundles','contents','documents'))+
                'delete from auth.users where id='+literal(own)+'; commit;')
        sql('delete from studybuddy.backend_verifiers where key_id='+literal(key_id)+';')


if __name__=='__main__':
    run()
