-- Story 3.3. Local only; parent integrates the reviewed test-project migration.
begin;
create table studybuddy.progress_mutations (
  owner_id uuid not null references auth.users(id), mutation_id uuid not null,
  document_id uuid not null, generation_id uuid not null,
  request jsonb not null, outcome jsonb not null, admitted_at timestamptz not null default clock_timestamp(),
  primary key(owner_id,mutation_id),
  foreign key(owner_id,document_id) references studybuddy.documents(owner_id,document_id)
  -- No generation FK: replacement must preserve old request identity/outcome.
);
alter table studybuddy.progress_mutations enable row level security;
grant select,insert on studybuddy.progress_mutations to authenticated;
create policy owner_backend_select on studybuddy.progress_mutations for select to authenticated
 using(owner_id=(select auth.uid()) and (select studybuddy.backend_gate()));
create policy owner_backend_insert on studybuddy.progress_mutations for insert to authenticated
 with check(owner_id=(select auth.uid()) and (select studybuddy.backend_gate()));

create function studybuddy.progress_request_valid(payload jsonb, writing boolean) returns boolean
language plpgsql immutable security invoker set search_path='' as $$
declare uuid_pattern text:='^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$';
begin
  if jsonb_typeof(payload) is distinct from 'object' then return false; end if;
  if (select count(*) from jsonb_object_keys(payload)) <> (case when writing then 6 else 3 end) or
      payload->>'schemaVersion' is distinct from '1.0' or
      coalesce(payload->>'documentId','') !~ uuid_pattern or coalesce(payload->>'generationId','') !~ uuid_pattern then return false; end if;
  if not writing then return payload ?& array['schemaVersion','documentId','generationId']; end if;
  if not (payload ?& array['schemaVersion','documentId','generationId','mutationId','expectedProgressRevision','positions']) or
     coalesce(payload->>'mutationId','') !~ uuid_pattern or
     jsonb_typeof(payload->'expectedProgressRevision') is distinct from 'number' or
     coalesce(payload->>'expectedProgressRevision','') !~ '^[0-9]{1,16}$' or
     (payload->>'expectedProgressRevision')::numeric not between 1 and 9007199254740990 or
     jsonb_typeof(payload->'positions') is distinct from 'object' then return false; end if;
  if (select count(*) from jsonb_object_keys(payload->'positions')) <> 2 or
     not ((payload->'positions') ?& array['flashcardId','quizId']) then return false; end if;
  return (jsonb_typeof(payload->'positions'->'flashcardId') in ('string','null') and
          coalesce(length(payload->'positions'->>'flashcardId'),0)<=100 and
          jsonb_typeof(payload->'positions'->'quizId') in ('string','null') and
          coalesce(length(payload->'positions'->>'quizId'),0)<=100);
end $$;

create function public.sb_save_progress_read_v1(payload jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$
declare d studybuddy.documents; p studybuddy.progress;
begin
  if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
  if not studybuddy.progress_request_valid(payload,false) then return jsonb_build_object('error','progress_mismatch'); end if;
  -- This lock also fences replacement/deletion while reading both IDs/revision.
  select * into d from studybuddy.documents where owner_id=auth.uid() and document_id=(payload->>'documentId')::uuid for share;
  if not found or d.lifecycle<>'ready' then return jsonb_build_object('error','document_unknown'); end if;
  if d.generation_id<>(payload->>'generationId')::uuid then return jsonb_build_object('error','progress_generation'); end if;
  select * into p from studybuddy.progress where owner_id=auth.uid() and document_id=d.document_id and generation_id=d.generation_id;
  if not found then return jsonb_build_object('error','document_unknown'); end if;
  return jsonb_build_object('schemaVersion','1.0','documentId',d.document_id,'generationId',d.generation_id,
    'progressRevision',p.revision,'positions',jsonb_build_object('flashcardId',p.flashcard_id,'quizId',p.quiz_id));
end $$;

create function public.sb_save_progress_write_v1(payload jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$
declare d studybuddy.documents; p studybuddy.progress; b jsonb; prior studybuddy.progress_mutations;
  result jsonb; own uuid:=auth.uid(); mid uuid;
begin
  if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
  if not studybuddy.progress_request_valid(payload,true) then return jsonb_build_object('error','progress_mismatch'); end if;
  mid:=(payload->>'mutationId')::uuid;
  -- Serializes reuse across different documents as well as same-document retries.
  perform pg_advisory_xact_lock(hashtextextended(own::text||mid::text,1));
  select * into d from studybuddy.documents where owner_id=own and document_id=(payload->>'documentId')::uuid for update;
  if not found or d.lifecycle<>'ready' then return jsonb_build_object('error','document_unknown'); end if;
  if d.generation_id<>(payload->>'generationId')::uuid then return jsonb_build_object('error','progress_generation'); end if;
  select bundle into b from studybuddy.bundles where owner_id=own and document_id=d.document_id and generation_id=d.generation_id;
  if not found then return jsonb_build_object('error','document_unknown'); end if;
  if (case when jsonb_array_length(b->'flashcards')=0 then payload->'positions'->>'flashcardId' is not null
      else not exists(select 1 from jsonb_array_elements(b->'flashcards') x where x->>'id'=payload->'positions'->>'flashcardId') end) or
     (case when jsonb_array_length(b->'quiz')=0 then payload->'positions'->>'quizId' is not null
      else not exists(select 1 from jsonb_array_elements(b->'quiz') x where x->>'id'=payload->'positions'->>'quizId') end) then
    return jsonb_build_object('error','progress_mismatch');
  end if;
  select * into prior from studybuddy.progress_mutations where owner_id=own and mutation_id=mid;
  if found then
    if prior.request<>payload then return jsonb_build_object('error','progress_mismatch'); end if;
    return prior.outcome;
  end if;
  select * into p from studybuddy.progress where owner_id=own and document_id=d.document_id and generation_id=d.generation_id;
  if not found then return jsonb_build_object('error','document_unknown'); end if;
  if p.revision<>(payload->>'expectedProgressRevision')::bigint then
    result:=jsonb_build_object('error','progress_conflict');
  else
    update studybuddy.progress set flashcard_id=payload->'positions'->>'flashcardId',quiz_id=payload->'positions'->>'quizId',revision=revision+1
      where owner_id=own and document_id=d.document_id returning * into p;
    result:=jsonb_build_object('schemaVersion','1.0','documentId',d.document_id,'generationId',d.generation_id,
      'progressRevision',p.revision,'positions',jsonb_build_object('flashcardId',p.flashcard_id,'quizId',p.quiz_id));
  end if;
  insert into studybuddy.progress_mutations(owner_id,mutation_id,document_id,generation_id,request,outcome)
    values(own,mid,d.document_id,d.generation_id,payload,result);
  return result;
end $$;

revoke all on function studybuddy.progress_request_valid(jsonb,boolean),public.sb_save_progress_read_v1(jsonb),public.sb_save_progress_write_v1(jsonb) from public,anon;
grant execute on function studybuddy.progress_request_valid(jsonb,boolean),public.sb_save_progress_read_v1(jsonb),public.sb_save_progress_write_v1(jsonb) to authenticated;

-- The acknowledged Save outcome always records initial progress revision 1.
-- Replay never reads/adopts subsequent practice progress.
create or replace function public.sb_save_commit_v1(payload jsonb) returns jsonb language plpgsql security invoker set search_path='' as $$
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
    'generationId',o.generation_id,'revision',rev,'progressRevision',1,'digest',o.digest,'cleanupStatus',case when exists(
    select 1 from studybuddy.save_objects obj join studybuddy.save_operations prior using(owner_id,operation_id)
    where obj.owner_id=auth.uid() and prior.document_id=o.document_id
      and (obj.operation_id=o.operation_id or obj.cleanup_needed)
      and (obj.cleanup_needed or obj.write_unknown)) then 'pending' else 'complete' end);
  update studybuddy.save_operations set status='ready',snapshot=null,outcome=result,completed_at=clock_timestamp() where owner_id=auth.uid() and operation_id=o.operation_id;
  return result;
end $$;

create or replace function public.sb_save_reload_v1(payload jsonb) returns jsonb language plpgsql security invoker set search_path='' as $$
begin
  if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
  return coalesce((select jsonb_build_object('schemaVersion','1.0','status','ready','documentId',d.document_id,
    'generationId',d.generation_id,'revision',d.revision,'progressRevision',p.revision,'title',d.title,'acceptance',c.acceptance,'bundle',b.bundle,
    'positions',jsonb_build_object('flashcardId',p.flashcard_id,'quizId',p.quiz_id)) from studybuddy.documents d
    join studybuddy.contents c using(owner_id,document_id,generation_id) join studybuddy.bundles b using(owner_id,document_id,generation_id)
    join studybuddy.progress p using(owner_id,document_id,generation_id)
    where d.owner_id=auth.uid() and d.document_id=(payload->>'documentId')::uuid and d.lifecycle='ready'),jsonb_build_object('error','save_unknown'));
end $$;

commit;
