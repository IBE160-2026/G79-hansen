-- Isolated local fixture owners only. Never run against the hosted project.
begin;
create extension if not exists pgtap with schema extensions;
select plan(23);
insert into auth.users(id,email) values
 ('10000000-0000-4000-8000-000000000001','save-owner-one@example.test'),
 ('10000000-0000-4000-8000-000000000002','save-owner-two@example.test');
insert into studybuddy.backend_verifiers values('local-synthetic',encode(extensions.digest('synthetic-local-capability','sha256'),'hex'),true);
set local role authenticated;
select set_config('request.jwt.claim.sub','10000000-0000-4000-8000-000000000001',true);
select set_config('request.jwt.claims','{"sub":"10000000-0000-4000-8000-000000000001","role":"authenticated"}',true);
select set_config('request.headers','{}',true);
select is(studybuddy.backend_gate(),false,'owner JWT without backend gate is denied');
select throws_ok($$select public.sb_save_pending_v1('{}')$$,'42501',null,'direct RPC without gate denied');
select throws_ok($$insert into studybuddy.documents values('10000000-0000-4000-8000-000000000001','20000000-0000-4000-8000-000000000001','30000000-0000-4000-8000-000000000001','bad','pending',0,null,now())$$,'42501',null,'direct table write without gate denied');
select set_config('request.headers','{"x-studybuddy-backend":"wrong"}',true);
select is(studybuddy.backend_gate(),false,'wrong gate denied');
select set_config('request.headers','{"x-studybuddy-backend":"synthetic-local-capability"}',true);
select is(studybuddy.backend_gate(),true,'configured synthetic gate accepted');
select throws_ok($$insert into studybuddy.documents values('10000000-0000-4000-8000-000000000002','20000000-0000-4000-8000-000000000002','30000000-0000-4000-8000-000000000002','bad','pending',0,null,now())$$,'42501',null,'correct gate does not bypass owner');

-- Empty sections have null practice positions. Bundle/source use schema-valid synthetic material.
select is(public.sb_save_admit_v1(jsonb_build_object('operationId','40000000-0000-4000-8000-000000000001','digest',repeat('a',64),'snapshot',jsonb_build_object(
 'schemaVersion','1.0','ownerId','10000000-0000-4000-8000-000000000001','documentId','20000000-0000-4000-8000-000000000001',
 'generationId','30000000-0000-4000-8000-000000000001','expectedRevision',null,'title','Synthetic local Save',
 'acceptance',jsonb_build_object('source','{"id":"source","schemaVersion":"1.0","title":"Synthetic","units":[{"id":"p1","kind":"paragraph","location":1,"text":"Synthetic source."}]}'::jsonb,'settings','{"language":"nb","detail":"short","subject":""}'::jsonb),
 'bundle',jsonb_build_object('schemaVersion','1.0','generationId','30000000-0000-4000-8000-000000000001',
 'source','{"id":"source","schemaVersion":"1.0","title":"Synthetic","units":[{"id":"p1","kind":"paragraph","location":1,"text":"Synthetic source."}]}'::jsonb,
 'settings','{"language":"nb","detail":"short","subject":""}'::jsonb,'summary','[]'::jsonb,'concepts','[]'::jsonb,'flashcards','[]'::jsonb,'quiz','[]'::jsonb),
 'positions','{"flashcardId":null,"quizId":null}'::jsonb,'fileHash',null,'fileSize',null)))->'operation'->>'status','pending','admission persists private pending snapshot');
select is((select count(*)::integer from studybuddy.contents),0,'admission does not publish content');
create temp table synthetic_snapshot as select snapshot from studybuddy.save_operations where operation_id='40000000-0000-4000-8000-000000000001';
select is(public.sb_save_commit_v1(jsonb_build_object('operationId','40000000-0000-4000-8000-000000000001','digest',repeat('a',64)))->>'status','ready','transaction commits ready');
select is((select count(*)::integer from studybuddy.contents),1,'committed content exists');
select is((select count(*)::integer from studybuddy.bundles),1,'committed bundle exists');
select is((select count(*)::integer from studybuddy.progress),1,'committed independent progress exists');
select is(public.sb_save_commit_v1(jsonb_build_object('operationId','40000000-0000-4000-8000-000000000001','digest',repeat('a',64)))->>'revision','1','identical completed replay does not advance revision');
select is(public.sb_save_commit_v1(jsonb_build_object('operationId','40000000-0000-4000-8000-000000000001','digest',repeat('b',64)))->>'error','save_mismatch','changed replay fails');
select is(public.sb_save_pending_v1('{}')->'operations'->0->>'recoveryState','ready','lost ready reply discoverable as confirmed outcome');
select is(has_function_privilege('authenticated','studybuddy.expire_staging_admin(integer)','execute'),false,'ordinary role cannot run all-owner maintenance');
select public.sb_save_admit_v1(jsonb_build_object('operationId','40000000-0000-4000-8000-000000000003','digest',repeat('c',64),
  'snapshot',(select jsonb_set(snapshot,'{documentId}','"20000000-0000-4000-8000-000000000003"') from synthetic_snapshot)));
select is(public.sb_save_cancel_v1('{"operationId":"40000000-0000-4000-8000-000000000003"}')->>'cleanupStatus','cleanup_complete','object-free cancellation completes cleanup');
select is((select title from studybuddy.documents where document_id='20000000-0000-4000-8000-000000000003'),'Avsluttet lagring','cancellation scrubs pending title');
select is((select snapshot from studybuddy.save_operations where operation_id='40000000-0000-4000-8000-000000000003'),null::jsonb,'terminal staging erased');
select is((select digest from studybuddy.save_operations where operation_id='40000000-0000-4000-8000-000000000003'),repeat('c',64),'content-free operation identity retained');
select is(jsonb_array_length(public.sb_save_pending_v1('{}')->'operations'),1,'completed object-free cleanup hidden while ready outcome retained');
select set_config('request.jwt.claim.sub','10000000-0000-4000-8000-000000000002',true);
select set_config('request.jwt.claims','{"sub":"10000000-0000-4000-8000-000000000002","role":"authenticated"}',true);
select is((select count(*)::integer from studybuddy.contents),0,'second owner cannot select first owner content with valid gate');
select is(public.sb_save_get_v1('{"operationId":"40000000-0000-4000-8000-000000000001"}')->'operation','null'::jsonb,'second owner cannot recover first operation');
select * from finish();
rollback;
