-- Synthetic fixtures only; rollback leaves the isolated local DB unchanged.
begin;
create extension if not exists pgtap with schema extensions;
select no_plan();
insert into auth.users(id,email) values
 ('13000000-0000-4000-8000-000000000001','delete-one@example.test'),
 ('13000000-0000-4000-8000-000000000002','delete-two@example.test');
insert into studybuddy.backend_verifiers values('delete-local',encode(extensions.digest('deletion-synthetic-gate','sha256'),'hex'),true);
insert into studybuddy.documents(owner_id,document_id,generation_id,title,lifecycle,revision) values
 ('13000000-0000-4000-8000-000000000001','23000000-0000-4000-8000-000000000001','33000000-0000-4000-8000-000000000001','Synthetic delete','ready',1),
 ('13000000-0000-4000-8000-000000000001','23000000-0000-4000-8000-000000000002','33000000-0000-4000-8000-000000000002','Synthetic uncertain','ready',1);
insert into studybuddy.contents select owner_id,document_id,generation_id,'{"private":"source"}' from studybuddy.documents where owner_id='13000000-0000-4000-8000-000000000001';
insert into studybuddy.bundles select owner_id,document_id,generation_id,jsonb_build_object('generationId',generation_id,'flashcards','[]'::jsonb,'quiz','[]'::jsonb)
 from studybuddy.documents where owner_id='13000000-0000-4000-8000-000000000001';
insert into studybuddy.progress select owner_id,document_id,generation_id,null,null,1 from studybuddy.documents where owner_id='13000000-0000-4000-8000-000000000001';
insert into studybuddy.save_operations(owner_id,operation_id,document_id,generation_id,digest,status,outcome,completed_at) values
 ('13000000-0000-4000-8000-000000000001','43000000-0000-4000-8000-000000000001','23000000-0000-4000-8000-000000000001','33000000-0000-4000-8000-000000000001',repeat('a',64),'ready','{"status":"ready"}',clock_timestamp()),
 ('13000000-0000-4000-8000-000000000001','43000000-0000-4000-8000-000000000002','23000000-0000-4000-8000-000000000002','33000000-0000-4000-8000-000000000002',repeat('b',64),'pending',null,null);
insert into studybuddy.save_objects(owner_id,operation_id,object_key,file_hash,file_size,media_type,write_unknown) values
 ('13000000-0000-4000-8000-000000000001','43000000-0000-4000-8000-000000000001','synthetic/current',repeat('c',64),1,'text/plain',false),
 ('13000000-0000-4000-8000-000000000001','43000000-0000-4000-8000-000000000002','synthetic/uncertain',repeat('d',64),1,'text/plain',true);
insert into studybuddy.progress_mutations(owner_id,mutation_id,document_id,generation_id,request,outcome) values
 ('13000000-0000-4000-8000-000000000001','63000000-0000-4000-8000-000000000001','23000000-0000-4000-8000-000000000001','33000000-0000-4000-8000-000000000001','{"private":"payload"}','{}');
select is(has_function_privilege('anon','public.sb_save_delete_v1(jsonb)','execute'),false,'anonymous deletion revoked');
select is((select prosecdef from pg_proc where oid='public.sb_save_delete_v1(jsonb)'::regprocedure),false,'deletion is invoker');
select is((select prosecdef from pg_proc where oid='public.sb_save_delete_complete_v1(jsonb)'::regprocedure),false,'completion is invoker');
set local role authenticated;
select set_config('request.jwt.claim.sub','13000000-0000-4000-8000-000000000002',true);
select set_config('request.jwt.claims','{"sub":"13000000-0000-4000-8000-000000000002","role":"authenticated"}',true);
select set_config('request.headers','{"x-studybuddy-backend":"deletion-synthetic-gate"}',true);
create temp table requests as select
 '{"schemaVersion":"1.0","documentId":"23000000-0000-4000-8000-000000000001","operationId":"53000000-0000-4000-8000-000000000001"}'::jsonb as one,
 '{"schemaVersion":"1.0","documentId":"23000000-0000-4000-8000-000000000002","operationId":"53000000-0000-4000-8000-000000000002"}'::jsonb as two;
select is(public.sb_save_delete_v1((select one from requests))->>'error','document_unknown','foreign delete has no authority');
select is(public.sb_save_deletions_v1('{}')->'deletions','[]'::jsonb,'foreign discovery leaks nothing');
select is((select count(*)::integer from studybuddy.save_objects),0,'RLS hides object keys');
select set_config('request.jwt.claim.sub','13000000-0000-4000-8000-000000000001',true);
select set_config('request.jwt.claims','{"sub":"13000000-0000-4000-8000-000000000001","role":"authenticated"}',true);
select set_config('request.headers','{}',true);
select throws_ok($$select public.sb_save_delete_v1((select one from requests))$$,'42501',null,'delete requires backend gate');
select set_config('request.headers','{"x-studybuddy-backend":"deletion-synthetic-gate"}',true);
select is(public.sb_save_delete_v1((select one from requests))->>'status','deleting','confirmation persists lifecycle');
select is((select lifecycle from studybuddy.documents where document_id='23000000-0000-4000-8000-000000000001'),'deleting','fence is durable');
select is(public.sb_save_reload_v1((select one from requests))->>'error','save_unknown','deleting content cannot reopen');
select is(public.sb_save_file_v1((select one from requests))->>'error','document_unknown','deleting file cannot read');
select is(public.sb_save_get_v1('{"operationId":"43000000-0000-4000-8000-000000000001"}')->>'error','save_conflict','ready Save replay fenced');
select is(public.sb_save_commit_v1('{"operationId":"43000000-0000-4000-8000-000000000001","digest":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}')->>'error','save_conflict','stale commit fenced');
select is((select jsonb_array_length(public.sb_save_deletions_v1('{}')->'deletions')),1,'recovery discoverable');
select is(public.sb_save_delete_complete_v1((select one from requests)||'{"removedKeys":[]}')->>'status','deleting','no physical proof cannot complete');
select is(public.sb_save_delete_complete_v1((select one from requests)||'{"removedKeys":["foreign/key"]}')->>'status','deleting','foreign cleanup keys grant no authority');
select is(public.sb_save_delete_complete_v1((select one from requests)||'{"removedKeys":["synthetic/current"]}')->>'status','deleted','verified object removal permits completion');
select is((select count(*)::integer from studybuddy.documents where document_id='23000000-0000-4000-8000-000000000001'),0,'document removed');
select is((select count(*)::integer from studybuddy.contents where document_id='23000000-0000-4000-8000-000000000001'),0,'source removed');
select is((select count(*)::integer from studybuddy.bundles where document_id='23000000-0000-4000-8000-000000000001'),0,'bundle removed');
select is((select count(*)::integer from studybuddy.progress where document_id='23000000-0000-4000-8000-000000000001'),0,'progress removed');
select is((select count(*)::integer from studybuddy.progress_mutations),0,'old progress request payload erased');
select is((select count(*)::integer from studybuddy.save_operations where document_id='23000000-0000-4000-8000-000000000001'),0,'immutable ready operation deleted in FK order');
select is((select count(*)::integer from studybuddy.deleted_operations),1,'content-free operation tombstone retained');
select is(public.sb_save_delete_v1((select one from requests))->>'status','deleted','exact lost-reply retry replays');
select is(public.sb_save_delete_v1((select one from requests)||'{"documentId":"23000000-0000-4000-8000-000000000002"}')->>'error','delete_mismatch','retry identity binds document');
select is(public.sb_save_admit_v1('{"operationId":"43000000-0000-4000-8000-000000000001","snapshot":{}}')->>'error','save_conflict','deleted operation cannot be readmitted');
select is(public.sb_save_admit_v1('{"operationId":"43000000-0000-4000-8000-000000000003","snapshot":{"documentId":"23000000-0000-4000-8000-000000000001"}}')->>'error','save_conflict','deleted document ID cannot be recreated');
select is(public.sb_save_progress_write_v1('{"schemaVersion":"1.0","documentId":"23000000-0000-4000-8000-000000000001","generationId":"33000000-0000-4000-8000-000000000001","mutationId":"63000000-0000-4000-8000-000000000001","expectedProgressRevision":1,"positions":{"flashcardId":null,"quizId":null}}')->>'error','document_unknown','deleted progress mutation cannot recreate state');
select is(public.sb_save_delete_v1((select two from requests))->>'status','deleting','uncertain object fenced');
select is((select status from studybuddy.save_operations where operation_id='43000000-0000-4000-8000-000000000002'),'cancelled','pending Save cancelled');
select is(public.sb_save_delete_complete_v1((select two from requests)||'{"removedKeys":["synthetic/uncertain"]}')->>'status','deleting','uncertain writes cannot be certified by delete acknowledgement');
select is((select count(*)::integer from studybuddy.save_objects where object_key='synthetic/uncertain'),1,'uncertain object durable record retained');
select is((select upload_enabled from studybuddy.save_objects where object_key='synthetic/uncertain'),false,'new uploads disabled');
select is(has_function_privilege('authenticated','studybuddy.purge_deletion_tombstones_admin()','execute'),false,'ordinary user cannot purge retry tombstones');
reset role;
update studybuddy.deleted_operations set completed_at=clock_timestamp()-interval '8 days' where owner_id='13000000-0000-4000-8000-000000000001';
update studybuddy.deleted_progress set completed_at=clock_timestamp()-interval '8 days' where owner_id='13000000-0000-4000-8000-000000000001';
update studybuddy.deletions set completed_at=clock_timestamp()-interval '8 days' where owner_id='13000000-0000-4000-8000-000000000001' and status='deleted';
select studybuddy.purge_deletion_tombstones_admin();
select is((select count(*)::integer from studybuddy.deleted_operations where owner_id='13000000-0000-4000-8000-000000000001'),0,'seven-day outcomes are purged');
select is((select count(*)::integer from studybuddy.deleted_progress where owner_id='13000000-0000-4000-8000-000000000001'),0,'seven-day progress tombstones are purged');
select is((select count(*)::integer from studybuddy.deletions where owner_id='13000000-0000-4000-8000-000000000001' and status='deleted'),0,'completed deletion tombstone purged after seven days');
select is((select count(*)::integer from studybuddy.save_objects where object_key='synthetic/uncertain'),1,'uncertain object survives retry tombstone maintenance');
select is((select count(*)::integer from studybuddy.deletions where owner_id='13000000-0000-4000-8000-000000000001' and status='deleting'),1,'pending deletion has no automatic expiry');
select * from finish();
rollback;
