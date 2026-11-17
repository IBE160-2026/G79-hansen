-- Policy decisions only; synthetic rows roll back. No hosted accounts are created.
begin;
select plan(15);
insert into auth.users(id,email) values
 ('10000000-0000-4000-8000-000000000011','storage-info-one@example.invalid'),
 ('10000000-0000-4000-8000-000000000012','storage-info-two@example.invalid');
insert into studybuddy.backend_verifiers values('storage-info-fixture',encode(extensions.digest('storage-info-fixture-capability','sha256'),'hex'),true);
set local role authenticated;
set local request.jwt.claims='{"sub":"10000000-0000-4000-8000-000000000011","role":"authenticated"}';
set local request.jwt.claim.sub='10000000-0000-4000-8000-000000000011';
set local request.headers='{"x-studybuddy-backend":"storage-info-fixture-capability"}';
insert into studybuddy.documents(owner_id,document_id,generation_id,title,lifecycle) values
 ('10000000-0000-4000-8000-000000000011','20000000-0000-4000-8000-000000000011','30000000-0000-4000-8000-000000000011','Synthetic policy fixture','pending');
insert into studybuddy.save_operations(owner_id,operation_id,document_id,generation_id,digest,snapshot) values
 ('10000000-0000-4000-8000-000000000011','40000000-0000-4000-8000-000000000011','20000000-0000-4000-8000-000000000011','30000000-0000-4000-8000-000000000011',repeat('a',64),
 '{"ownerId":"10000000-0000-4000-8000-000000000011","documentId":"20000000-0000-4000-8000-000000000011","generationId":"30000000-0000-4000-8000-000000000011"}');
insert into studybuddy.save_objects(owner_id,operation_id,object_key,file_hash,file_size,media_type) values
 ('10000000-0000-4000-8000-000000000011','40000000-0000-4000-8000-000000000011','synthetic-info-key',repeat('a',64),1,'text/plain');
set local storage.operation='storage.s3.object.get';
select is(studybuddy.storage_read_allowed('synthetic-info-key'),false,'pending info requires internal marker');
set local request.headers='{"x-studybuddy-backend":"storage-info-fixture-capability","x-studybuddy-operation":"verify"}';
select is(studybuddy.storage_read_allowed('synthetic-info-key'),true,'registered pending info allowed for internal verification');
set local storage.operation='storage.s3.object.get';
select is(studybuddy.storage_read_allowed('synthetic-info-key'),true,'registered pending S3 byte read allowed for verification');
set local storage.operation='object.get_authenticated';
select is(studybuddy.storage_read_allowed('synthetic-info-key'),false,'cached REST bytes denied even with internal marker');
set local storage.operation='object.get_authenticated_info';
select is(studybuddy.storage_read_allowed('synthetic-info-key'),false,'cached REST metadata denied even with internal marker');
set local storage.operation='object.sign';
select is(studybuddy.storage_read_allowed('synthetic-info-key'),false,'verification marker never enables signing');
set local storage.operation='object.list';
select is(studybuddy.storage_read_allowed('synthetic-info-key'),false,'verification marker never enables listing');
set local storage.operation='storage.s3.object.get';
set local request.jwt.claims='{"sub":"10000000-0000-4000-8000-000000000012","role":"authenticated"}';
set local request.jwt.claim.sub='10000000-0000-4000-8000-000000000012';
select is(studybuddy.storage_read_allowed('synthetic-info-key'),false,'foreign owner info denied with valid gate and marker');
set local request.jwt.claims='{"sub":"10000000-0000-4000-8000-000000000011","role":"authenticated"}';
set local request.jwt.claim.sub='10000000-0000-4000-8000-000000000011';
set local request.headers='{"x-studybuddy-operation":"verify"}';
select is(studybuddy.storage_read_allowed('synthetic-info-key'),false,'missing gate still denies pending info');
set local request.headers='{"x-studybuddy-backend":"storage-info-fixture-capability"}';
update studybuddy.documents set lifecycle='ready',revision=1,object_key='synthetic-info-key';
update studybuddy.save_operations set status='ready',snapshot=null,outcome='{"status":"ready"}',completed_at=clock_timestamp();
select is(studybuddy.storage_read_allowed('synthetic-info-key'),true,'exact current ready info allowed to backend owner');
set local storage.operation='storage.s3.object.get';
select is(studybuddy.storage_read_allowed('synthetic-info-key'),true,'exact current ready byte read allowed');
set local storage.operation='object.get_authenticated';
select is(studybuddy.storage_read_allowed('synthetic-info-key'),false,'ready REST bytes cannot warm CDN cache');
set local storage.operation='storage.s3.object.info';
select is(studybuddy.storage_read_allowed('synthetic-info-key'),false,'unneeded S3 HEAD remains denied');
set local storage.operation='storage.s3.object.get';
select is(studybuddy.storage_read_allowed('another-key'),false,'unknown ready key denied');
set local request.jwt.claims='{"sub":"10000000-0000-4000-8000-000000000012","role":"authenticated"}';
set local request.jwt.claim.sub='10000000-0000-4000-8000-000000000012';
set local storage.operation='storage.s3.object.get';
select is(studybuddy.storage_read_allowed('synthetic-info-key'),false,'foreign ready info denied');
select * from finish();
rollback;
