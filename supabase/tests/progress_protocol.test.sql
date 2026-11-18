-- Synthetic fixtures, transaction rollback. Isolated local database only.
begin;
create extension if not exists pgtap with schema extensions;
select no_plan();
insert into auth.users(id,email) values
 ('12000000-0000-4000-8000-000000000001','progress-one@example.test'),
 ('12000000-0000-4000-8000-000000000002','progress-two@example.test');
insert into studybuddy.backend_verifiers values('progress-local',encode(extensions.digest('progress-synthetic-gate','sha256'),'hex'),true);
insert into studybuddy.documents(owner_id,document_id,generation_id,title,lifecycle,revision) values
 ('12000000-0000-4000-8000-000000000001','22000000-0000-4000-8000-000000000001','32000000-0000-4000-8000-000000000001','Synthetic progress','ready',1);
insert into studybuddy.contents select owner_id,document_id,generation_id,'{}' from studybuddy.documents where document_id='22000000-0000-4000-8000-000000000001';
insert into studybuddy.bundles select owner_id,document_id,generation_id,
 jsonb_build_object('generationId',generation_id,'flashcards','[{"id":"f1"},{"id":"f2"}]'::jsonb,'quiz','[{"id":"q1"},{"id":"q2"}]'::jsonb)
 from studybuddy.documents where document_id='22000000-0000-4000-8000-000000000001';
insert into studybuddy.progress select owner_id,document_id,generation_id,'f1','q1',1 from studybuddy.documents where document_id='22000000-0000-4000-8000-000000000001';
select is(has_function_privilege('anon','public.sb_save_progress_write_v1(jsonb)','execute'),false,'anonymous mutation execution revoked');
select is(has_function_privilege('anon','public.sb_save_progress_read_v1(jsonb)','execute'),false,'anonymous read execution revoked');
select is((select prosecdef from pg_proc where oid='public.sb_save_progress_write_v1(jsonb)'::regprocedure),false,'write is security invoker');
select is((select prosecdef from pg_proc where oid='public.sb_save_progress_read_v1(jsonb)'::regprocedure),false,'read is security invoker');
select is(has_table_privilege('authenticated','studybuddy.progress_mutations','update'),false,'replay records cannot be updated');
select is(has_table_privilege('authenticated','studybuddy.progress_mutations','delete'),true,'owner plus backend gate permits deletion cleanup of replay payloads');
set local role authenticated;
select set_config('request.jwt.claim.sub','12000000-0000-4000-8000-000000000001',true);
select set_config('request.jwt.claims','{"sub":"12000000-0000-4000-8000-000000000001","role":"authenticated"}',true);
select set_config('request.headers','{}',true);
select throws_ok($$select public.sb_save_progress_write_v1('{}')$$,'42501',null,'write requires backend gate');
select throws_ok($$select public.sb_save_progress_read_v1('{}')$$,'42501',null,'read requires backend gate');
select set_config('request.headers','{"x-studybuddy-backend":"progress-synthetic-gate"}',true);
create temp table requests as select
 '{"schemaVersion":"1.0","documentId":"22000000-0000-4000-8000-000000000001","generationId":"32000000-0000-4000-8000-000000000001"}'::jsonb as read,
 '{"schemaVersion":"1.0","documentId":"22000000-0000-4000-8000-000000000001","generationId":"32000000-0000-4000-8000-000000000001","mutationId":"42000000-0000-4000-8000-000000000001","expectedProgressRevision":1,"positions":{"flashcardId":"f2","quizId":"q1"}}'::jsonb as write;
select is(public.sb_save_progress_read_v1((select read from requests))->>'progressRevision','1','fresh read returns initial revision');
select is(public.sb_save_progress_write_v1((select write from requests)||'{"ownerId":"foreign"}')->>'error','progress_mismatch','direct RPC rejects owner injection');
select is(public.sb_save_progress_write_v1((select write from requests)||'{"positions":{"flashcardId":null,"quizId":"q1"}}')->>'error','progress_mismatch','nonempty section requires real item');
select is(public.sb_save_progress_write_v1((select write from requests)||'{"positions":{"flashcardId":"f1","quizId":"unknown"}}')->>'error','progress_mismatch','both section memberships checked');
create temp table acknowledged as select public.sb_save_progress_write_v1((select write from requests)) as value;
select is((select value->>'progressRevision' from acknowledged),'2','mutation advances progress revision once');
select is((select value->'positions' from acknowledged),'{"flashcardId":"f2","quizId":"q1"}'::jsonb,'independent positions saved');
select is(public.sb_save_progress_write_v1((select write from requests)),(select value from acknowledged),'identical retry replays before old expected revision');
select is((select revision::integer from studybuddy.progress),2,'retry leaves revision unchanged');
select is(public.sb_save_progress_write_v1((select write from requests)||'{"expectedProgressRevision":2}')->>'error','progress_mismatch','mutation identity binds expected revision');
select is(public.sb_save_progress_write_v1((select write from requests)||'{"positions":{"flashcardId":"f1","quizId":"q1"}}')->>'error','progress_mismatch','mutation identity binds both IDs');
select is(public.sb_save_progress_write_v1((select write from requests)||'{"mutationId":"42000000-0000-4000-8000-000000000002"}')->>'error','progress_conflict','stale distinct mutation conflicts');
select is(public.sb_save_reload_v1((select read from requests))->>'progressRevision','2','reload atomically includes progress revision');
select is(public.sb_save_reload_v1((select read from requests))->'positions',(select value->'positions' from acknowledged),'reload returns acknowledged positions');
select is(public.sb_save_progress_write_v1((select write from requests)||'{"mutationId":"42000000-0000-4000-8000-000000000003","expectedProgressRevision":2,"positions":{"flashcardId":"f1","quizId":"q2"}}')->>'progressRevision','3','fresh revision permits backward flashcard navigation');
select is(public.sb_save_progress_write_v1((select write from requests)||'{"mutationId":"42000000-0000-4000-8000-000000000002"}')->>'error','progress_conflict','conflicting outcome is durable');
select is((select count(*)::integer from studybuddy.progress_mutations),3,'one durable record per admitted outcome');
select set_config('request.jwt.claim.sub','12000000-0000-4000-8000-000000000002',true);
select set_config('request.jwt.claims','{"sub":"12000000-0000-4000-8000-000000000002","role":"authenticated"}',true);
select is(public.sb_save_progress_read_v1((select read from requests))->>'error','document_unknown','foreign read has no metadata');
select is(public.sb_save_progress_write_v1((select write from requests))->>'error','document_unknown','foreign write has no metadata');
select is((select count(*)::integer from studybuddy.progress_mutations),0,'owner RLS hides replay metadata');
select set_config('request.jwt.claim.sub','12000000-0000-4000-8000-000000000001',true);
select set_config('request.jwt.claims','{"sub":"12000000-0000-4000-8000-000000000001","role":"authenticated"}',true);
update studybuddy.documents set lifecycle='deleting' where document_id='22000000-0000-4000-8000-000000000001';
select is(public.sb_save_progress_write_v1((select write from requests))->>'error','document_unknown','deleting target cannot replay');
select is(public.sb_save_progress_read_v1((select read from requests))->>'error','document_unknown','deleting target cannot read');
update studybuddy.documents set lifecycle='ready' where document_id='22000000-0000-4000-8000-000000000001';
update studybuddy.bundles set bundle=bundle||'{"quiz":[]}' where document_id='22000000-0000-4000-8000-000000000001';
select is(public.sb_save_progress_write_v1((select write from requests))->>'error','progress_mismatch','current membership is checked before historical replay');
select is(public.sb_save_progress_write_v1((select write from requests)||'{"mutationId":"42000000-0000-4000-8000-000000000004","expectedProgressRevision":3,"positions":{"flashcardId":"f2","quizId":null}}')->>'progressRevision','4','empty section accepts only null position');
select is(public.sb_save_progress_write_v1((select write from requests)||'{"mutationId":"42000000-0000-4000-8000-000000000005","expectedProgressRevision":4}')->>'error','progress_mismatch','empty section rejects invented item');
-- Replace generation like Save: erase children, keep durable request records.
delete from studybuddy.progress where document_id='22000000-0000-4000-8000-000000000001';
delete from studybuddy.bundles where document_id='22000000-0000-4000-8000-000000000001';
delete from studybuddy.contents where document_id='22000000-0000-4000-8000-000000000001';
update studybuddy.documents set generation_id='32000000-0000-4000-8000-000000000002' where document_id='22000000-0000-4000-8000-000000000001';
select is(public.sb_save_progress_write_v1((select write from requests))->>'error','progress_generation','current generation is checked before replay');
select is((select count(*)::integer from studybuddy.progress),0,'old generation never recreates progress');
select is((select count(*)::integer from studybuddy.progress_mutations),4,'replacement preserves old generation replay identity');
select is((select generation_id::text from studybuddy.progress_mutations limit 1),'32000000-0000-4000-8000-000000000001','generation identities are not cascaded');
select * from finish();
rollback;
