-- Story 3.1. Local first; separate approval is required before hosted application.
begin;
create schema if not exists studybuddy;
revoke all on schema studybuddy from public, anon;
grant usage on schema studybuddy to authenticated;
alter default privileges in schema studybuddy revoke all on tables from public, anon;
alter default privileges in schema studybuddy revoke execute on functions from public, anon;

create table studybuddy.backend_verifiers (
  key_id text primary key, verifier text not null check (verifier ~ '^[0-9a-f]{64}$'), active boolean not null default true
);
alter table studybuddy.backend_verifiers enable row level security;
grant select on studybuddy.backend_verifiers to authenticated;
create policy verifier_read on studybuddy.backend_verifiers for select to authenticated using (true);
-- Only database administration may INSERT/UPDATE/DELETE verifiers. No raw key is stored.
create function studybuddy.backend_gate() returns boolean language sql stable security invoker
set search_path = '' as $$
  select auth.uid() is not null and exists (
    select 1 from studybuddy.backend_verifiers v where v.active and v.verifier =
      encode(extensions.digest(convert_to(coalesce(nullif(current_setting('request.headers', true), '')::jsonb
             ->> 'x-studybuddy-backend', ''), 'UTF8'), 'sha256'), 'hex'));
$$;
revoke all on function studybuddy.backend_gate() from public, anon;
grant execute on function studybuddy.backend_gate() to authenticated;

create table studybuddy.documents (
  owner_id uuid not null references auth.users(id), document_id uuid not null,
  generation_id uuid not null, title text not null check (length(title) between 1 and 160),
  lifecycle text not null check (lifecycle in ('pending','ready','deleting')),
  revision bigint not null default 0 check (revision >= 0), object_key text,
  updated_at timestamptz not null default now(), primary key (owner_id,document_id),
  unique(owner_id, document_id, generation_id), unique(document_id)
);
create table studybuddy.contents (
  owner_id uuid not null, document_id uuid not null, generation_id uuid not null,
  acceptance jsonb not null, primary key(owner_id,document_id),
  foreign key(owner_id,document_id,generation_id) references studybuddy.documents(owner_id,document_id,generation_id)
    on update cascade on delete cascade
);
create table studybuddy.bundles (
  owner_id uuid not null, document_id uuid not null, generation_id uuid not null,
  bundle jsonb not null check (jsonb_typeof(bundle) = 'object'), primary key(owner_id,document_id),
  foreign key(owner_id,document_id,generation_id) references studybuddy.documents(owner_id,document_id,generation_id)
    on update cascade on delete cascade,
  check ((bundle->>'generationId')::uuid = generation_id)
);
create table studybuddy.progress (
  owner_id uuid not null, document_id uuid not null, generation_id uuid not null,
  flashcard_id text, quiz_id text, revision bigint not null default 1 check (revision > 0),
  primary key(owner_id,document_id),
  foreign key(owner_id,document_id,generation_id) references studybuddy.documents(owner_id,document_id,generation_id)
    on update cascade on delete cascade
);
create table studybuddy.save_operations (
  owner_id uuid not null references auth.users(id), operation_id uuid not null, document_id uuid not null,
  generation_id uuid not null, digest text not null check(digest ~ '^[0-9a-f]{64}$'),
  snapshot jsonb, expected_revision bigint check(expected_revision > 0),
  status text not null default 'pending' check(status in ('pending','ready','expired','conflict','cancelled')),
  admitted_at timestamptz not null default now(), expires_at timestamptz not null default now() + interval '7 days',
  outcome jsonb, completed_at timestamptz, primary key(owner_id,operation_id), unique(operation_id),
  foreign key(owner_id,document_id) references studybuddy.documents(owner_id,document_id),
  check (expires_at = admitted_at + interval '7 days'),
  check (snapshot is null or ((snapshot->>'ownerId')::uuid=owner_id and
    (snapshot->>'documentId')::uuid=document_id and (snapshot->>'generationId')::uuid=generation_id))
);
create table studybuddy.save_objects (
  owner_id uuid not null, operation_id uuid not null, object_key text not null unique,
  file_hash text not null check(file_hash ~ '^[0-9a-f]{64}$'), file_size bigint not null check(file_size between 0 and 10485760),
  media_type text not null check(media_type in ('text/plain','application/pdf')),
  attempts integer not null default 0, verified boolean not null default false,
  upload_enabled boolean not null default true, cleanup_needed boolean not null default false,
  -- Intentionally retained until the actual provider proves physical quiescence.
  write_unknown boolean not null default false,
  primary key(owner_id,operation_id), foreign key(owner_id,operation_id)
    references studybuddy.save_operations(owner_id,operation_id)
);
create index save_pending_expiry on studybuddy.save_operations(expires_at) where status='pending';
create index documents_owner_ready on studybuddy.documents(owner_id,updated_at desc) where lifecycle='ready';
create index save_cleanup on studybuddy.save_objects(owner_id) where cleanup_needed or write_unknown;

create function studybuddy.immutable_save_identity() returns trigger language plpgsql security invoker set search_path='' as $$
begin
  if new.owner_id<>old.owner_id or new.operation_id<>old.operation_id or new.document_id<>old.document_id or
    new.generation_id<>old.generation_id or new.digest<>old.digest or new.admitted_at<>old.admitted_at or new.expires_at<>old.expires_at or
    new.expected_revision is distinct from old.expected_revision or (new.snapshot is not null and new.snapshot is distinct from old.snapshot) or
    (old.status='ready' and (new.status<>'ready' or new.outcome is distinct from old.outcome or new.completed_at is distinct from old.completed_at)) then
    raise exception 'immutable_save_identity' using errcode='23000';
  end if;
  return new;
end $$;
create trigger save_identity before update on studybuddy.save_operations for each row execute function studybuddy.immutable_save_identity();

-- The gate is present in every mutation policy. No permissive owner-only alternative exists.
do $$ declare name text; begin
  foreach name in array array['documents','contents','bundles','progress','save_operations','save_objects'] loop
    execute format('alter table studybuddy.%I enable row level security',name);
    execute format('grant select,insert,update,delete on studybuddy.%I to authenticated',name);
    execute format('create policy owner_backend_select on studybuddy.%I for select to authenticated using (owner_id = (select auth.uid()) and (select studybuddy.backend_gate()))',name);
    execute format('create policy owner_backend_insert on studybuddy.%I for insert to authenticated with check (owner_id = (select auth.uid()) and (select studybuddy.backend_gate()))',name);
    execute format('create policy owner_backend_update on studybuddy.%I for update to authenticated using (owner_id = (select auth.uid()) and (select studybuddy.backend_gate())) with check (owner_id = (select auth.uid()) and (select studybuddy.backend_gate()))',name);
    execute format('create policy owner_backend_delete on studybuddy.%I for delete to authenticated using (owner_id = (select auth.uid()) and (select studybuddy.backend_gate()))',name);
  end loop;
end $$;

create function studybuddy.operation_json(o studybuddy.save_operations) returns jsonb language sql stable security invoker
set search_path = '' as $$
  select jsonb_build_object('operationId',o.operation_id,'documentId',o.document_id,'digest',o.digest,
    'status',o.status,'expiresAt',o.expires_at,'snapshot',o.snapshot,'outcome',o.outcome,
    'objectKey',f.object_key,'mediaType',f.media_type,'fileHash',f.file_hash,'fileSize',f.file_size) from (select 1) q
    left join studybuddy.save_objects f on f.owner_id=o.owner_id and f.operation_id=o.operation_id;
$$;

-- Called with an operation lock; document locking and wall-clock recheck make
-- expiry exact even when admission/commit waited behind another transaction.
create function studybuddy.expire_operation(own uuid, oid uuid) returns boolean language plpgsql security invoker set search_path='' as $$
declare o studybuddy.save_operations;
begin
  select * into o from studybuddy.save_operations where owner_id=own and operation_id=oid for update;
  if not found or o.status<>'pending' then return false; end if;
  perform 1 from studybuddy.documents where owner_id=own and document_id=o.document_id for update;
  if o.expires_at <= clock_timestamp() then
    update studybuddy.save_objects set upload_enabled=false,cleanup_needed=true where owner_id=o.owner_id and operation_id=o.operation_id;
    update studybuddy.save_operations set status='expired',snapshot=null where owner_id=o.owner_id and operation_id=o.operation_id;
    update studybuddy.documents set title='Utløpt lagring' where owner_id=o.owner_id and document_id=o.document_id and lifecycle='pending';
    return true;
  end if;
  return false;
end $$;

create function studybuddy.expire_operations() returns void language plpgsql security invoker set search_path='' as $$
declare o studybuddy.save_operations;
begin
  for o in select op.* from studybuddy.save_operations op
      join studybuddy.documents d using(owner_id,document_id)
      where op.owner_id=auth.uid() and op.status='pending' and op.expires_at<=clock_timestamp()
      order by op.expires_at,op.operation_id limit 100 for update of op,d skip locked loop
    perform studybuddy.expire_operation(o.owner_id,o.operation_id);
  end loop;
end $$;

-- Administrator-only, unexposed, bounded all-owner maintenance. No user token
-- or ordinary-operation service key is involved. Health records contain no content.
create table studybuddy.expiry_maintenance_health (
  singleton boolean primary key default true check(singleton),
  last_completed_at timestamptz not null, expired_count integer not null
);
revoke all on studybuddy.expiry_maintenance_health from public,anon,authenticated;
create function studybuddy.expire_staging_admin(batch_size integer default 100) returns integer
language plpgsql security invoker set search_path='' as $$
declare o studybuddy.save_operations; erased integer:=0;
begin
  if batch_size<1 or batch_size>100 then raise exception 'invalid_batch_size'; end if;
  perform set_config('lock_timeout','2s',true);
  perform set_config('statement_timeout','10s',true);
  -- LockRows skips either locked row before LIMIT counts an eligible pair.
  -- A blocked target cannot consume the batch or delay an unrelated replay.
  for o in select op.* from studybuddy.save_operations op
      join studybuddy.documents d using(owner_id,document_id)
      where op.status='pending' and op.expires_at<=clock_timestamp()
      order by op.expires_at,op.operation_id limit batch_size for update of op,d skip locked loop
    if studybuddy.expire_operation(o.owner_id,o.operation_id) then erased:=erased+1; end if;
  end loop;
  insert into studybuddy.expiry_maintenance_health values(true,clock_timestamp(),erased)
    on conflict(singleton) do update set last_completed_at=excluded.last_completed_at,expired_count=excluded.expired_count;
  return erased;
end $$;

create function public.sb_save_get_v1(payload jsonb) returns jsonb language plpgsql security invoker set search_path='' as $$
declare o studybuddy.save_operations;
begin
  if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
  perform studybuddy.expire_operations();
  select * into o from studybuddy.save_operations where owner_id=auth.uid() and operation_id=(payload->>'operationId')::uuid;
  if not found then return jsonb_build_object('operation',null); end if;
  if payload ? 'digest' and payload->>'digest' <> o.digest then return jsonb_build_object('error','save_mismatch'); end if;
  return jsonb_build_object('operation',studybuddy.operation_json(o));
end $$;

create function public.sb_save_admit_v1(payload jsonb) returns jsonb language plpgsql security invoker set search_path='' as $$
declare s jsonb:=payload->'snapshot'; o studybuddy.save_operations; d studybuddy.documents;
  own uuid:=auth.uid(); oid uuid:=(payload->>'operationId')::uuid; did uuid:=(s->>'documentId')::uuid;
  gid uuid:=(s->>'generationId')::uuid; expected bigint:=(s->>'expectedRevision')::bigint;
begin
  if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
  -- Per-operation advisory lock gives concurrent first admission one immutable identity.
  perform pg_advisory_xact_lock(hashtextextended(oid::text,0));
  select * into o from studybuddy.save_operations where owner_id=own and operation_id=oid;
  if found then
    if o.digest<>payload->>'digest' then return jsonb_build_object('error','save_mismatch'); end if;
    return jsonb_build_object('operation',studybuddy.operation_json(o));
  end if;
  if (s->>'ownerId')::uuid<>own or s->>'schemaVersion'<>'1.0' or
      s->'bundle'->'source'<>s->'acceptance'->'source' or s->'bundle'->'settings'<>s->'acceptance'->'settings' or
      (s->'bundle'->>'generationId')::uuid<>gid then return jsonb_build_object('error','save_mismatch'); end if;
  select * into d from studybuddy.documents where owner_id=own and document_id=did for update;
  if expected is null then
    if found then return jsonb_build_object('error','save_conflict'); end if;
    insert into studybuddy.documents(owner_id,document_id,generation_id,title,lifecycle) values(own,did,gid,s->>'title','pending');
  elsif not found or d.lifecycle<>'ready' or d.revision<>expected then return jsonb_build_object('error','save_conflict');
  end if;
  insert into studybuddy.save_operations(owner_id,operation_id,document_id,generation_id,digest,snapshot,expected_revision)
    values(own,oid,did,gid,payload->>'digest',s,expected) returning * into o;
  if s->>'fileHash' is not null then
    insert into studybuddy.save_objects(owner_id,operation_id,object_key,file_hash,file_size,media_type)
      values(own,oid,own::text||'/'||did::text||'/'||gid::text||'/'||oid::text,
      s->>'fileHash',(s->>'fileSize')::bigint,case when s->'acceptance'->>'kind'='pdf' then 'application/pdf' else 'text/plain' end);
  end if;
  return jsonb_build_object('operation',studybuddy.operation_json(o));
end $$;

create function public.sb_save_attempt_v1(payload jsonb) returns jsonb language plpgsql security invoker set search_path='' as $$
declare o studybuddy.save_operations;
begin
  if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
  perform studybuddy.expire_operations();
  select * into o from studybuddy.save_operations where owner_id=auth.uid() and operation_id=(payload->>'operationId')::uuid for update;
  if not found then return jsonb_build_object('error','save_unknown'); end if;
  if o.digest<>payload->>'digest' then return jsonb_build_object('error','save_mismatch'); end if;
  if o.status<>'pending' or studybuddy.expire_operation(o.owner_id,o.operation_id) then return jsonb_build_object('error','save_expired'); end if;
  update studybuddy.save_objects set attempts=attempts+1,write_unknown=true where owner_id=auth.uid() and operation_id=o.operation_id and upload_enabled;
  return jsonb_build_object('status','pending');
end $$;

create function public.sb_save_verified_v1(payload jsonb) returns jsonb language plpgsql security invoker set search_path='' as $$
declare o studybuddy.save_operations;
begin
  if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
  perform studybuddy.expire_operations();
  select * into o from studybuddy.save_operations where owner_id=auth.uid() and operation_id=(payload->>'operationId')::uuid for update;
  if not found then return jsonb_build_object('error','save_unknown'); end if;
  if o.digest<>payload->>'digest' then return jsonb_build_object('error','save_mismatch'); end if;
  if o.status<>'pending' or studybuddy.expire_operation(o.owner_id,o.operation_id) then return jsonb_build_object('error','save_expired'); end if;
  update studybuddy.save_objects set verified=true,upload_enabled=false where owner_id=auth.uid() and operation_id=o.operation_id;
  return jsonb_build_object('status','pending');
end $$;

create function public.sb_save_commit_v1(payload jsonb) returns jsonb language plpgsql security invoker set search_path='' as $$
declare o studybuddy.save_operations; d studybuddy.documents; f studybuddy.save_objects; s jsonb; result jsonb; rev bigint;
begin
  if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
  perform studybuddy.expire_operations();
  select * into o from studybuddy.save_operations where owner_id=auth.uid() and operation_id=(payload->>'operationId')::uuid for update;
  if not found then return jsonb_build_object('error','save_unknown'); end if;
  if o.digest<>payload->>'digest' then return jsonb_build_object('error','save_mismatch'); end if;
  if o.status='ready' then return o.outcome; end if;
  if o.status='expired' then return jsonb_build_object('error','save_expired'); end if;
  if o.status<>'pending' then return jsonb_build_object('error','save_conflict'); end if;
  select * into d from studybuddy.documents where owner_id=auth.uid() and document_id=o.document_id for update;
  -- Never use transaction-start now() here: either row lock may have waited
  -- across expiry. Erase/fence in this same transaction before publication.
  if studybuddy.expire_operation(o.owner_id,o.operation_id) then return jsonb_build_object('error','save_expired'); end if;
  if not found or d.lifecycle='deleting' or (o.expected_revision is not null and
    (d.lifecycle<>'ready' or d.revision<>o.expected_revision)) or (o.expected_revision is null and d.lifecycle<>'pending') then
    update studybuddy.save_operations set status='conflict',snapshot=null where owner_id=auth.uid() and operation_id=o.operation_id;
    update studybuddy.save_objects set upload_enabled=false,cleanup_needed=true where owner_id=auth.uid() and operation_id=o.operation_id;
    update studybuddy.documents set title='Avsluttet lagring' where owner_id=auth.uid() and document_id=o.document_id and lifecycle='pending';
    return jsonb_build_object('error','save_conflict');
  end if;
  select * into f from studybuddy.save_objects where owner_id=auth.uid() and operation_id=o.operation_id;
  if found and not f.verified then return jsonb_build_object('error','file_required'); end if;
  s:=o.snapshot; rev:=d.revision+1;
  if (s->'positions'->>'flashcardId' is not null and not exists(select 1 from jsonb_array_elements(s->'bundle'->'flashcards') x where x->>'id'=s->'positions'->>'flashcardId')) or
     (s->'positions'->>'quizId' is not null and not exists(select 1 from jsonb_array_elements(s->'bundle'->'quiz') x where x->>'id'=s->'positions'->>'quizId')) then
    return jsonb_build_object('error','save_mismatch');
  end if;
  update studybuddy.save_objects set cleanup_needed=true,upload_enabled=false where owner_id=auth.uid() and object_key=d.object_key and object_key is distinct from f.object_key;
  -- Delete dependent old generation first, then install the complete new generation in this transaction.
  delete from studybuddy.progress where owner_id=auth.uid() and document_id=d.document_id;
  delete from studybuddy.bundles where owner_id=auth.uid() and document_id=d.document_id;
  delete from studybuddy.contents where owner_id=auth.uid() and document_id=d.document_id;
  update studybuddy.documents set generation_id=o.generation_id,title=s->>'title',lifecycle='ready',revision=rev,object_key=f.object_key,updated_at=now()
    where owner_id=auth.uid() and document_id=d.document_id;
  insert into studybuddy.contents values(auth.uid(),d.document_id,o.generation_id,s->'acceptance');
  insert into studybuddy.bundles values(auth.uid(),d.document_id,o.generation_id,s->'bundle');
  insert into studybuddy.progress(owner_id,document_id,generation_id,flashcard_id,quiz_id) values
    (auth.uid(),d.document_id,o.generation_id,s->'positions'->>'flashcardId',s->'positions'->>'quizId');
  result:=jsonb_build_object('schemaVersion','1.0','status','ready','operationId',o.operation_id,'documentId',d.document_id,
    'generationId',o.generation_id,'revision',rev,'digest',o.digest,'cleanupStatus',case when exists(
    select 1 from studybuddy.save_objects obj join studybuddy.save_operations prior using(owner_id,operation_id)
    where obj.owner_id=auth.uid() and prior.document_id=o.document_id
      and (obj.operation_id=o.operation_id or obj.cleanup_needed)
      and (obj.cleanup_needed or obj.write_unknown)) then 'pending' else 'complete' end);
  update studybuddy.save_operations set status='ready',snapshot=null,outcome=result,completed_at=clock_timestamp() where owner_id=auth.uid() and operation_id=o.operation_id;
  return result;
end $$;

create function public.sb_save_pending_v1(payload jsonb) returns jsonb language plpgsql security invoker set search_path='' as $$
begin
  if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
  perform studybuddy.expire_operations();
  return (with candidates as (select op.*,exists(select 1 from studybuddy.save_objects f where
      f.owner_id=op.owner_id and f.operation_id=op.operation_id and f.cleanup_needed and not f.upload_enabled) as cleanup
    from studybuddy.save_operations op where owner_id=auth.uid() and
    (status='pending' or (status='ready' and completed_at>clock_timestamp()-interval '7 days') or exists(select 1 from studybuddy.save_objects f where f.owner_id=op.owner_id
      and f.operation_id=op.operation_id and f.cleanup_needed and not f.upload_enabled))
    and (payload->>'cursor' is null or operation_id>(payload->>'cursor')::uuid) order by operation_id limit 51),
    page as (select * from candidates order by operation_id limit 50)
    select jsonb_build_object('schemaVersion','1.0','operations',coalesce((select jsonb_agg(jsonb_build_object(
    'operationId',o.operation_id,'documentId',o.document_id,'digest',o.digest,'status',o.status,
    'admittedAt',o.admitted_at,'expiresAt',o.expires_at,
    'title',case when o.status='pending' then o.snapshot->>'title' else null end,
    'recoveryState',case when o.cleanup then 'cleanup_only' when o.status='ready' then 'ready' else 'pending' end,
    'cleanupOnly',o.cleanup,
    'outcome',case when o.status='ready' and not o.cleanup then o.outcome else null end,
    'requiresFile',o.status='pending' and exists(select 1 from studybuddy.save_objects f where f.owner_id=o.owner_id and f.operation_id=o.operation_id))
    order by o.operation_id) from page o),'[]'::jsonb),'nextCursor',case when (select count(*) from candidates)>50 then
      (select operation_id from page order by operation_id desc limit 1) else null end));
end $$;

create function public.sb_save_cancel_v1(payload jsonb) returns jsonb language plpgsql security invoker set search_path='' as $$
declare o studybuddy.save_operations; keys jsonb;
begin
  if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
  select * into o from studybuddy.save_operations where owner_id=auth.uid() and operation_id=(payload->>'operationId')::uuid for update;
  if not found then return jsonb_build_object('error','save_unknown'); end if;
  if o.status='ready' then
    select coalesce(jsonb_agg(f.object_key),'[]'::jsonb) into keys
    from studybuddy.save_objects f join studybuddy.save_operations op using(owner_id,operation_id)
    where f.owner_id=auth.uid() and op.document_id=o.document_id and f.cleanup_needed and not f.upload_enabled
      and not exists(select 1 from studybuddy.documents d where d.owner_id=f.owner_id and d.lifecycle='ready' and d.object_key=f.object_key);
  else
    perform 1 from studybuddy.documents where owner_id=auth.uid() and document_id=o.document_id for update;
    update studybuddy.save_objects set upload_enabled=false,cleanup_needed=true where owner_id=auth.uid() and operation_id=o.operation_id;
    update studybuddy.save_operations set status=case when expires_at<=clock_timestamp() then 'expired' else 'cancelled' end,snapshot=null
      where owner_id=auth.uid() and operation_id=o.operation_id;
    update studybuddy.documents set title='Avsluttet lagring' where owner_id=auth.uid() and document_id=o.document_id and lifecycle='pending';
    select coalesce(jsonb_agg(object_key),'[]'::jsonb) into keys from studybuddy.save_objects where owner_id=auth.uid() and operation_id=o.operation_id;
  end if;
  -- Only a missing registered object proves object-free completion. A successful
  -- DELETE alone never settles uncertain physical writes.
  return jsonb_build_object('cleanupKeys',keys,'cleanupStatus',case when jsonb_array_length(keys)=0 then 'cleanup_complete' else 'cleanup_pending' end);
end $$;

create function public.sb_save_reload_v1(payload jsonb) returns jsonb language plpgsql security invoker set search_path='' as $$
begin
  if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
  return coalesce((select jsonb_build_object('schemaVersion','1.0','status','ready','documentId',d.document_id,
    'generationId',d.generation_id,'revision',d.revision,'title',d.title,'acceptance',c.acceptance,'bundle',b.bundle,
    'positions',jsonb_build_object('flashcardId',p.flashcard_id,'quizId',p.quiz_id)) from studybuddy.documents d
    join studybuddy.contents c using(owner_id,document_id,generation_id) join studybuddy.bundles b using(owner_id,document_id,generation_id)
    join studybuddy.progress p using(owner_id,document_id,generation_id)
    where d.owner_id=auth.uid() and d.document_id=(payload->>'documentId')::uuid and d.lifecycle='ready'),jsonb_build_object('error','save_unknown'));
end $$;

-- Storage finalization takes the operation lock. Cancel/expiry conflicts with it.
create function studybuddy.storage_write_allowed(key text) returns boolean language plpgsql security invoker set search_path='' as $$
declare o studybuddy.save_operations;
begin
  if not studybuddy.backend_gate() then return false; end if;
  select op.* into o from studybuddy.save_operations op join studybuddy.save_objects f using(owner_id,operation_id)
    where op.owner_id=auth.uid() and f.object_key=key for update of op;
  return found and o.status='pending' and o.expires_at>clock_timestamp() and exists(
    select 1 from studybuddy.save_objects where owner_id=auth.uid() and operation_id=o.operation_id and upload_enabled);
end $$;
create function studybuddy.storage_read_allowed(key text) returns boolean language sql stable security invoker set search_path='' as $$
  select studybuddy.backend_gate() and (
    (storage.allow_only_operation('object.get_authenticated') and (
      exists(select 1 from studybuddy.documents d where d.owner_id=auth.uid() and d.lifecycle='ready' and d.object_key=key)
      or (coalesce(nullif(current_setting('request.headers',true),'')::jsonb->>'x-studybuddy-operation','')='verify'
        and exists(select 1 from studybuddy.save_operations o join studybuddy.save_objects f using(owner_id,operation_id)
          where o.owner_id=auth.uid() and o.status='pending' and o.expires_at>clock_timestamp() and f.object_key=key))))
    or (storage.allow_any_operation(array['object.delete','object.delete_many']) and exists(
      select 1 from studybuddy.save_objects f where f.owner_id=auth.uid() and f.object_key=key and f.cleanup_needed and not f.upload_enabled
        and not exists(select 1 from studybuddy.documents d where d.owner_id=f.owner_id and d.lifecycle='ready' and d.object_key=f.object_key))));
$$;
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
  values('studybuddy-sources','studybuddy-sources',false,10485760,array['text/plain','application/pdf']);
create policy studybuddy_upload on storage.objects for insert to authenticated with check (
  bucket_id='studybuddy-sources' and storage.allow_only_operation('object.upload') and studybuddy.storage_write_allowed(name));
create policy studybuddy_read on storage.objects for select to authenticated using (
  bucket_id='studybuddy-sources' and studybuddy.storage_read_allowed(name));
create policy studybuddy_cleanup on storage.objects for delete to authenticated using (
  bucket_id='studybuddy-sources' and studybuddy.storage_read_allowed(name) and storage.allow_any_operation(array['object.delete','object.delete_many']));
-- No UPDATE policy: immutable keys cannot be overwritten/moved/upserted.

revoke all on all functions in schema studybuddy from public,anon;
grant execute on all functions in schema studybuddy to authenticated;
revoke all on function studybuddy.expire_staging_admin(integer) from public,anon,authenticated;
-- Failure/disablement is a retention acceptance failure, observable via the
-- health row and cron.job_run_details. Hosted installation needs final approval.
create extension if not exists pg_cron;
select cron.schedule('studybuddy-expire-staging-v1','* * * * *',
  'set statement_timeout = ''10s''; select studybuddy.expire_staging_admin(100)');
do $$ declare f record; begin
  for f in select oid::regprocedure as signature from pg_proc where pronamespace='public'::regnamespace and proname like 'sb_save_%_v1' loop
    execute format('revoke all on function %s from public,anon',f.signature);
    execute format('grant execute on function %s to authenticated',f.signature);
  end loop;
end $$;
commit;
