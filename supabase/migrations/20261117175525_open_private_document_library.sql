-- Story 3.2. Local verification only; hosted application requires approval.
begin;
create function public.sb_save_library_v1(payload jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$
begin
  if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
  return (with candidates as (
    select d.document_id,d.title,d.updated_at,d.revision,d.object_key,
      b.bundle,p.flashcard_id,p.quiz_id
    from studybuddy.documents d
    join studybuddy.bundles b using(owner_id,document_id,generation_id)
    join studybuddy.progress p using(owner_id,document_id,generation_id)
    where d.owner_id=auth.uid() and d.lifecycle='ready'
      and (payload->>'cursor' is null or d.document_id>(payload->>'cursor')::uuid)
    order by d.document_id limit 51
  ), page as (select * from candidates order by document_id limit 50)
  select jsonb_build_object('schemaVersion','1.0','items',coalesce((
    select jsonb_agg(jsonb_build_object('documentId',d.document_id,'title',d.title,
      'updatedAt',d.updated_at,'revision',d.revision,'hasOriginalFile',d.object_key is not null,
      'positions',jsonb_build_object(
        'flashcard',case when jsonb_array_length(d.bundle->'flashcards')>0 then jsonb_build_object(
          'ordinal',(select n from jsonb_array_elements(d.bundle->'flashcards') with ordinality as x(item,n) where item->>'id'=d.flashcard_id),
          'total',jsonb_array_length(d.bundle->'flashcards')) else null end,
        'quiz',case when jsonb_array_length(d.bundle->'quiz')>0 then jsonb_build_object(
          'ordinal',(select n from jsonb_array_elements(d.bundle->'quiz') with ordinality as x(item,n) where item->>'id'=d.quiz_id),
          'total',jsonb_array_length(d.bundle->'quiz')) else null end)) order by d.document_id) from page d),'[]'::jsonb),
    'nextCursor',case when (select count(*) from candidates)>50 then
      (select document_id from page order by document_id desc limit 1) else null end));
end $$;

-- Server-internal descriptor: FastAPI consumes it, never forwards it to clients.
create function public.sb_save_file_v1(payload jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$
begin
  if not studybuddy.backend_gate() then raise insufficient_privilege; end if;
  return coalesce((select jsonb_build_object('documentId',d.document_id,'generationId',d.generation_id,
    'revision',d.revision,'title',d.title,'objectKey',f.object_key,'fileHash',f.file_hash,
    'fileSize',f.file_size,'mediaType',f.media_type)
    from studybuddy.documents d join studybuddy.save_objects f on f.owner_id=d.owner_id and f.object_key=d.object_key
    where d.owner_id=auth.uid() and d.document_id=(payload->>'documentId')::uuid and d.lifecycle='ready'),
    jsonb_build_object('error','document_unknown'));
end $$;

revoke all on function public.sb_save_library_v1(jsonb),public.sb_save_file_v1(jsonb) from public,anon;
grant execute on function public.sb_save_library_v1(jsonb),public.sb_save_file_v1(jsonb) to authenticated;
commit;
