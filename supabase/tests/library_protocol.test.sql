-- Synthetic local fixtures; always rolled back. Never target a hosted database.
begin;
create extension if not exists pgtap with schema extensions;
select plan(23);
insert into auth.users(id,email) values
 ('11000000-0000-4000-8000-000000000001','library-one@example.test'),
 ('11000000-0000-4000-8000-000000000002','library-two@example.test');
insert into studybuddy.backend_verifiers values('library-local',encode(extensions.digest('library-synthetic-gate','sha256'),'hex'),true);
insert into studybuddy.documents(owner_id,document_id,generation_id,title,lifecycle,revision)
 select '11000000-0000-4000-8000-000000000001',('21000000-0000-4000-8000-'||lpad(i::text,12,'0'))::uuid,
 '31000000-0000-4000-8000-000000000001','Synthetic '||i,
 case when i=54 then 'pending' when i=55 then 'deleting' else 'ready' end,1 from generate_series(1,55) i;
insert into studybuddy.contents select owner_id,document_id,generation_id,'{"source":{"title":"Private source"}}' from studybuddy.documents where owner_id='11000000-0000-4000-8000-000000000001';
insert into studybuddy.bundles select owner_id,document_id,generation_id,
 jsonb_build_object('generationId',generation_id,'flashcards','[{"id":"f1"},{"id":"f2"}]'::jsonb,'quiz','[]'::jsonb)
 from studybuddy.documents where owner_id='11000000-0000-4000-8000-000000000001';
insert into studybuddy.progress select owner_id,document_id,generation_id,'f2',null,1 from studybuddy.documents where owner_id='11000000-0000-4000-8000-000000000001';
insert into studybuddy.save_operations(owner_id,operation_id,document_id,generation_id,digest,status,outcome,completed_at)
 values('11000000-0000-4000-8000-000000000001','41000000-0000-4000-8000-000000000001',
 '21000000-0000-4000-8000-000000000001','31000000-0000-4000-8000-000000000001',repeat('a',64),'ready','{}',now());
insert into studybuddy.save_objects(owner_id,operation_id,object_key,file_hash,file_size,media_type)
 values('11000000-0000-4000-8000-000000000001','41000000-0000-4000-8000-000000000001','synthetic/library/object',repeat('b',64),12,'text/plain');
update studybuddy.documents set object_key='synthetic/library/object' where document_id='21000000-0000-4000-8000-000000000001';

select is(has_function_privilege('anon','public.sb_save_library_v1(jsonb)','execute'),false,'anonymous library execution revoked');
select is(has_function_privilege('anon','public.sb_save_file_v1(jsonb)','execute'),false,'anonymous descriptor execution revoked');
select is((select prosecdef from pg_proc where oid='public.sb_save_library_v1(jsonb)'::regprocedure),false,'library is security invoker');
select is((select prosecdef from pg_proc where oid='public.sb_save_file_v1(jsonb)'::regprocedure),false,'descriptor is security invoker');
set local role authenticated;
select set_config('request.jwt.claim.sub','11000000-0000-4000-8000-000000000001',true);
select set_config('request.jwt.claims','{"sub":"11000000-0000-4000-8000-000000000001","role":"authenticated"}',true);
select set_config('request.headers','{}',true);
select throws_ok($$select public.sb_save_library_v1('{}')$$,'42501',null,'library requires backend gate');
select throws_ok($$select public.sb_save_file_v1('{"documentId":"21000000-0000-4000-8000-000000000001"}')$$,'42501',null,'descriptor requires backend gate');
select set_config('request.headers','{"x-studybuddy-backend":"library-synthetic-gate"}',true);
create temp table library_first as select public.sb_save_library_v1('{}') as value;
select is(jsonb_array_length((select value->'items' from library_first)),50,'first page bounded to fifty');
select is((select value->>'nextCursor' from library_first),'21000000-0000-4000-8000-000000000050','cursor is last visible UUID');
select is((select value->'items'->0->'positions'->'flashcard' from library_first),'{"ordinal":2,"total":2}'::jsonb,'stored independent ordinal and total');
select is((select value->'items'->0->'positions'->'quiz' from library_first),'null'::jsonb,'absent exercises have null position');
select is((select value->'items'->0->>'hasOriginalFile' from library_first),'true','original file metadata flag');
select is((select count(*)::integer from jsonb_object_keys((select value->'items'->0 from library_first))),6,'metadata excludes source bundle keys and hashes');
create temp table library_second as select public.sb_save_library_v1(jsonb_build_object('cursor',(select value->>'nextCursor' from library_first))) as value;
select is(jsonb_array_length((select value->'items' from library_second)),3,'remaining ready entries only');
select is((select value->'nextCursor' from library_second),'null'::jsonb,'last page has no cursor');
select is(public.sb_save_reload_v1('{"documentId":"21000000-0000-4000-8000-000000000054"}')->>'error','save_unknown','pending cannot reload');
select is(public.sb_save_reload_v1('{"documentId":"21000000-0000-4000-8000-000000000055"}')->>'error','save_unknown','deleting cannot reload');
select is(public.sb_save_file_v1('{"documentId":"21000000-0000-4000-8000-000000000001"}')->>'fileHash',repeat('b',64),'internal descriptor has exact current integrity identity');
select is(public.sb_save_file_v1('{"documentId":"21000000-0000-4000-8000-000000000002"}')->>'error','document_unknown','paste has no original descriptor');
select is(public.sb_save_file_v1('{"documentId":"21000000-0000-4000-8000-000000000054"}')->>'error','document_unknown','pending has no descriptor');
select set_config('request.jwt.claim.sub','11000000-0000-4000-8000-000000000002',true);
select set_config('request.jwt.claims','{"sub":"11000000-0000-4000-8000-000000000002","role":"authenticated"}',true);
select is(jsonb_array_length(public.sb_save_library_v1('{}')->'items'),0,'foreign owner receives no metadata');
select is(public.sb_save_reload_v1('{"documentId":"21000000-0000-4000-8000-000000000001"}')->>'error','save_unknown','foreign owner receives no content');
select is(public.sb_save_file_v1('{"documentId":"21000000-0000-4000-8000-000000000001"}')->>'error','document_unknown','foreign owner receives no descriptor');
select is((select count(*)::integer from studybuddy.documents),0,'actual owner RLS denies foreign rows');
select * from finish();
rollback;
