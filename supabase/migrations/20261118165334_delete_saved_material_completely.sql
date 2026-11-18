-- Story 3.4. LOCAL ONLY; hosted application requires separate approval.
begin;
create table studybuddy.deletions (
 owner_id uuid not null references auth.users(id), operation_id uuid not null,
 document_id uuid not null, status text not null check(status in ('deleting','deleted')),
 admitted_at timestamptz not null default clock_timestamp(), completed_at timestamptz,
 primary key(owner_id,operation_id), unique(owner_id,document_id)
 -- Deliberately no document FK: this content-free retry identity outlives it.
);
create table studybuddy.deleted_operations (
 owner_id uuid not null references auth.users(id), operation_id uuid not null,
 document_id uuid not null, completed_at timestamptz not null default clock_timestamp(),
 primary key(owner_id,operation_id)
);
create table studybuddy.deleted_progress (
 owner_id uuid not null references auth.users(id), mutation_id uuid not null,
 document_id uuid not null, completed_at timestamptz not null default clock_timestamp(),
 primary key(owner_id,mutation_id)
);
alter table studybuddy.save_objects add column legacy_unknown boolean not null default false;
update studybuddy.save_objects set legacy_unknown=write_unknown;
alter table studybuddy.save_objects add column removal_verified boolean not null default false;
create table studybuddy.upload_attempts (
 owner_id uuid not null, operation_id uuid not null, upload_id uuid not null,
 settled boolean not null default false,
 primary key(owner_id,operation_id,upload_id),
 foreign key(owner_id,operation_id) references studybuddy.save_objects(owner_id,operation_id)
);
create index save_operations_document on studybuddy.save_operations(owner_id,document_id,operation_id);
create index progress_mutations_document on studybuddy.progress_mutations(owner_id,document_id);
do $$ declare n text; begin
 foreach n in array array['deletions','deleted_operations','deleted_progress','upload_attempts'] loop
  execute format('alter table studybuddy.%I enable row level security',n);
  execute format('grant select,insert,update,delete on studybuddy.%I to authenticated',n);
  execute format('create policy owner_backend_all on studybuddy.%I to authenticated using(owner_id=(select auth.uid()) and (select studybuddy.backend_gate())) with check(owner_id=(select auth.uid()) and (select studybuddy.backend_gate()))',n);
 end loop;
end $$;
-- Deletion must erase the content-bearing replay requests before the FK parent.
grant delete on studybuddy.progress_mutations to authenticated;
create policy owner_backend_delete on studybuddy.progress_mutations for delete to authenticated
 using(owner_id=(select auth.uid()) and (select studybuddy.backend_gate()));

-- Content-free outcomes use Save's seven-day retry window. Uncertain deleting
-- records have no expiry and are never purged by this maintenance function.
create function studybuddy.purge_deletion_tombstones_admin() returns void
language plpgsql security invoker set search_path='' as $$ begin
 delete from studybuddy.deleted_progress where completed_at<clock_timestamp()-interval '7 days';
 delete from studybuddy.deleted_operations where completed_at<clock_timestamp()-interval '7 days';
 delete from studybuddy.deletions where status='deleted' and completed_at<clock_timestamp()-interval '7 days';
end $$;
revoke all on function studybuddy.purge_deletion_tombstones_admin() from public,anon,authenticated;
select cron.schedule('studybuddy-deletion-tombstones','17 * * * *','select studybuddy.purge_deletion_tombstones_admin()');

-- Serialize admission and deletion even when the document row does not exist.
-- Existing Save/expiry/storage finalization lock operation BEFORE document.
create function studybuddy.document_mutex(did uuid) returns void
language plpgsql security invoker set search_path='' as $$ begin
 if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
 perform pg_advisory_xact_lock(hashtextextended(auth.uid()::text||did::text,34));
end $$;

-- Move old implementations out of exposed public; wrappers share one fence.
do $$ declare a text; begin
 foreach a in array array['get','admit','attempt','verified','commit','cancel','pending'] loop
  execute format('alter function public.sb_save_%s_v1(jsonb) set schema studybuddy',a);
 end loop;
end $$;
create function studybuddy.save_dispatch(a text,payload jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$
declare did uuid; result jsonb;
begin
 if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
 if a not in ('get','admit','attempt','verified','commit','cancel') then return jsonb_build_object('error','save_mismatch'); end if;
 if a='admit' then did:=(payload->'snapshot'->>'documentId')::uuid;
 else select document_id into did from studybuddy.save_operations where owner_id=auth.uid() and operation_id=(payload->>'operationId')::uuid; end if;
 if did is not null then perform studybuddy.document_mutex(did); end if;
 if exists(select 1 from studybuddy.deleted_operations where owner_id=auth.uid() and operation_id=(payload->>'operationId')::uuid) or
    exists(select 1 from studybuddy.deletions where owner_id=auth.uid() and document_id=did) then
   return jsonb_build_object('error','save_conflict');
 end if;
 execute format('select studybuddy.sb_save_%s_v1($1)',a) into result using payload;
 return result;
end $$;
do $$ declare a text; begin
 foreach a in array array['get','admit','attempt','verified','commit','cancel'] loop
  execute format('create function public.sb_save_%1$s_v1(payload jsonb) returns jsonb language sql security invoker set search_path='''' as $fn$ select studybuddy.save_dispatch(%2$L,payload) $fn$',a,a);
 end loop;
end $$;
-- Pending recovery must not expose obsolete Save outcomes for deleting items.
create function public.sb_save_pending_v1(payload jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$ declare result jsonb; begin
 if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
 result:=studybuddy.sb_save_pending_v1(payload);
 return jsonb_set(result,'{operations}',coalesce((select jsonb_agg(x) from jsonb_array_elements(result->'operations') x
   where not exists(select 1 from studybuddy.deletions d where d.owner_id=auth.uid() and d.document_id=(x->>'documentId')::uuid)),'[]'));
end $$;

-- Register EVERY physical request before dispatch. A lost response leaves an
-- unsettled intent indefinitely; a different successful retry cannot settle it.
create or replace function public.sb_save_attempt_v1(payload jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$
declare result jsonb; uid uuid:=gen_random_uuid();
begin
 result:=studybuddy.save_dispatch('attempt',payload);
 if result ? 'error' then return result; end if;
 insert into studybuddy.upload_attempts(owner_id,operation_id,upload_id)
 values(auth.uid(),(payload->>'operationId')::uuid,uid);
 return result||jsonb_build_object('uploadId',uid);
end $$;
create function public.sb_save_upload_settled_v1(payload jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$
declare o studybuddy.save_operations;
begin
 if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
 -- Also accepted after deletion fenced the operation: the exact response
 -- can arrive late, but cannot re-enable upload, verification or commit.
 select * into o from studybuddy.save_operations where owner_id=auth.uid() and operation_id=(payload->>'operationId')::uuid for update;
 if not found or o.digest is distinct from payload->>'digest' then return jsonb_build_object('error','save_unknown'); end if;
 update studybuddy.upload_attempts set settled=true where owner_id=auth.uid() and operation_id=o.operation_id and upload_id=(payload->>'uploadId')::uuid;
 if not found then return jsonb_build_object('error','save_unknown'); end if;
 update studybuddy.save_objects f set write_unknown=f.legacy_unknown or exists(select 1 from studybuddy.upload_attempts a
  where a.owner_id=f.owner_id and a.operation_id=f.operation_id and not a.settled)
 where f.owner_id=auth.uid() and f.operation_id=o.operation_id;
 return jsonb_build_object('status','settled');
end $$;

create function public.sb_save_delete_v1(payload jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$
declare own uuid:=auth.uid(); did uuid:=(payload->>'documentId')::uuid; oid uuid:=(payload->>'operationId')::uuid;
 prior studybuddy.deletions; d studybuddy.documents;
begin
 if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
 if payload->>'schemaVersion' is distinct from '1.0' or (select count(*) from jsonb_object_keys(payload))<>3 then
  return jsonb_build_object('error','delete_mismatch'); end if;
 -- Bind the deletion identity before taking a document-specific lock. Two
 -- different documents must never race past the same unbound operation ID.
 perform pg_advisory_xact_lock(hashtextextended(own::text||oid::text,35));
 perform studybuddy.document_mutex(did);
 -- Owner-bound identity, independent of browser/session lifetime.
 select * into prior from studybuddy.deletions where owner_id=own and operation_id=oid;
 if found and prior.document_id<>did then return jsonb_build_object('error','delete_mismatch'); end if;
 if found and prior.status='deleted' then
  return jsonb_build_object('schemaVersion','1.0','status','deleted','documentId',did,'operationId',oid); end if;
 -- Same order as Save/expiry: operations in UUID order, THEN document.
 perform 1 from studybuddy.save_operations where owner_id=own and document_id=did order by operation_id for update;
 select * into d from studybuddy.documents where owner_id=own and document_id=did for update;
 if not found then return jsonb_build_object('error','document_unknown'); end if;
 if exists(select 1 from studybuddy.deletions where owner_id=own and document_id=did and operation_id<>oid) then
  return jsonb_build_object('error','delete_mismatch'); end if;
 insert into studybuddy.deletions(owner_id,operation_id,document_id,status) values(own,oid,did,'deleting') on conflict do nothing;
 update studybuddy.documents set lifecycle='deleting' where owner_id=own and document_id=did;
 -- Ready operation identity/outcome is immutable: DELETE it only at finish.
 update studybuddy.save_operations set status='cancelled',snapshot=null where owner_id=own and document_id=did and status='pending';
 update studybuddy.save_operations set snapshot=null where owner_id=own and document_id=did and snapshot is not null;
 update studybuddy.save_objects f set upload_enabled=false,cleanup_needed=true from studybuddy.save_operations o
  where f.owner_id=own and o.owner_id=f.owner_id and o.operation_id=f.operation_id and o.document_id=did;
 return jsonb_build_object('schemaVersion','1.0','status','deleting','documentId',did,'operationId',oid,
  'objects',coalesce((select jsonb_agg(jsonb_build_object('objectKey',f.object_key,'writeUnknown',f.write_unknown,'removalVerified',f.removal_verified))
   from studybuddy.save_objects f join studybuddy.save_operations o using(owner_id,operation_id)
   where f.owner_id=own and o.document_id=did),'[]'));
end $$;

create function public.sb_save_delete_complete_v1(payload jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$
declare own uuid:=auth.uid(); did uuid:=(payload->>'documentId')::uuid; oid uuid:=(payload->>'operationId')::uuid;
 fenced jsonb;
begin
 fenced:=public.sb_save_delete_v1(payload-'removedKeys');
 if fenced ? 'error' or fenced->>'status'='deleted' then return fenced; end if;
 update studybuddy.save_objects f set removal_verified=true from studybuddy.save_operations o
  where f.owner_id=own and o.owner_id=f.owner_id and o.operation_id=f.operation_id and o.document_id=did
   and not f.write_unknown and not f.upload_enabled and payload->'removedKeys' ? f.object_key;
 if exists(select 1 from studybuddy.save_objects f join studybuddy.save_operations o using(owner_id,operation_id)
  where f.owner_id=own and o.document_id=did and (f.write_unknown or not f.removal_verified)) then
  return jsonb_build_object('schemaVersion','1.0','status','deleting','documentId',did,'operationId',oid); end if;
 insert into studybuddy.deleted_operations(owner_id,operation_id,document_id)
  select owner_id,operation_id,document_id from studybuddy.save_operations where owner_id=own and document_id=did on conflict do nothing;
 insert into studybuddy.deleted_progress(owner_id,mutation_id,document_id)
  select owner_id,mutation_id,document_id from studybuddy.progress_mutations where owner_id=own and document_id=did on conflict do nothing;
 delete from studybuddy.progress_mutations where owner_id=own and document_id=did;
 delete from studybuddy.upload_attempts a using studybuddy.save_operations o
  where a.owner_id=own and o.owner_id=a.owner_id and o.operation_id=a.operation_id and o.document_id=did;
 delete from studybuddy.save_objects f using studybuddy.save_operations o
  where f.owner_id=own and o.owner_id=f.owner_id and o.operation_id=f.operation_id and o.document_id=did;
 delete from studybuddy.save_operations where owner_id=own and document_id=did;
 -- Child source/bundle/progress FK cascades in this same transaction.
 delete from studybuddy.documents where owner_id=own and document_id=did;
 update studybuddy.deletions set status='deleted',completed_at=clock_timestamp() where owner_id=own and operation_id=oid;
 return jsonb_build_object('schemaVersion','1.0','status','deleted','documentId',did,'operationId',oid);
end $$;
create function public.sb_save_deletions_v1(payload jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$ begin
 if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
 return (with candidates as (select x.operation_id,x.document_id,d.title from studybuddy.deletions x
  join studybuddy.documents d using(owner_id,document_id) where x.owner_id=auth.uid() and x.status='deleting'
   and (payload->>'cursor' is null or x.operation_id>(payload->>'cursor')::uuid) order by x.operation_id limit 51),
 page as (select * from candidates order by operation_id limit 50)
 select jsonb_build_object('schemaVersion','1.0','deletions',coalesce((select jsonb_agg(jsonb_build_object(
  'documentId',document_id,'operationId',operation_id,'title',title,'status','deleting') order by operation_id) from page),'[]'),
  'nextCursor',case when (select count(*) from candidates)>50 then (select operation_id from page order by operation_id desc limit 1) else null end));
end $$;

alter function public.sb_save_progress_write_v1(jsonb) set schema studybuddy;
create function public.sb_save_progress_write_v1(payload jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$ begin
 if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
 if not studybuddy.progress_request_valid(payload,true) then return jsonb_build_object('error','progress_mismatch'); end if;
 if exists(select 1 from studybuddy.deleted_progress where owner_id=auth.uid() and mutation_id=(payload->>'mutationId')::uuid) then
  return jsonb_build_object('error','document_unknown'); end if;
 return studybuddy.sb_save_progress_write_v1(payload);
end $$;

create or replace function studybuddy.storage_write_allowed(key text) returns boolean
language plpgsql security invoker set search_path='' as $$ declare o studybuddy.save_operations; d studybuddy.documents; begin
 if not studybuddy.backend_gate() then return false; end if;
 select op.* into o from studybuddy.save_operations op join studybuddy.save_objects f using(owner_id,operation_id)
  where op.owner_id=auth.uid() and f.object_key=key for update of op;
 if not found then return false; end if;
 select * into d from studybuddy.documents where owner_id=auth.uid() and document_id=o.document_id for share;
 return found and d.lifecycle<>'deleting' and o.status='pending' and o.expires_at>clock_timestamp() and exists(
  select 1 from studybuddy.save_objects where owner_id=auth.uid() and operation_id=o.operation_id and upload_enabled);
end $$;
-- Cleanup S3 reads are internal and require an owned, fenced durable key.
alter function studybuddy.storage_read_allowed(text) rename to storage_read_before_deletion;
create function studybuddy.storage_read_allowed(key text) returns boolean
language sql stable security invoker set search_path='' as $$
 select studybuddy.storage_read_before_deletion(key) or (studybuddy.backend_gate()
  and storage.allow_only_operation('s3.object.get')
  and coalesce(nullif(current_setting('request.headers',true),'')::jsonb->>'x-studybuddy-operation','')='cleanup'
  and exists(select 1 from studybuddy.save_objects f join studybuddy.save_operations o using(owner_id,operation_id)
   join studybuddy.documents d using(owner_id,document_id) where f.owner_id=auth.uid() and f.object_key=key
    and d.lifecycle='deleting' and not f.upload_enabled and f.cleanup_needed));
$$;
-- Rebind policies: renaming a function preserves its OID in old expressions.
alter policy studybuddy_read on storage.objects using(bucket_id='studybuddy-sources' and studybuddy.storage_read_allowed(name));
alter policy studybuddy_cleanup on storage.objects using(bucket_id='studybuddy-sources' and studybuddy.storage_read_allowed(name) and storage.allow_any_operation(array['object.delete','object.delete_many']));

do $$ declare f record; begin
 for f in select p.oid::regprocedure as signature from pg_proc p join pg_namespace n on n.oid=p.pronamespace
  where (n.nspname='public' and p.proname like 'sb_save_%') or
  (n.nspname='studybuddy' and p.proname in ('document_mutex','save_dispatch','sb_save_get_v1','sb_save_admit_v1','sb_save_attempt_v1','sb_save_verified_v1','sb_save_commit_v1','sb_save_cancel_v1','sb_save_pending_v1','sb_save_progress_write_v1','storage_read_before_deletion','storage_read_allowed')) loop
  execute format('revoke all on function %s from public,anon',f.signature);
  execute format('grant execute on function %s to authenticated',f.signature);
 end loop;
end $$;
commit;
