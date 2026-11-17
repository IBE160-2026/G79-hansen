-- Hosted authenticated downloads perform a metadata preflight. Preserve every
-- owner/backend/lifecycle/verification condition; signed/list/public info stay denied.
begin;
create or replace function studybuddy.storage_read_allowed(key text) returns boolean language sql stable security invoker set search_path='' as $$
  select studybuddy.backend_gate() and (
    (storage.allow_any_operation(array['object.get_authenticated','object.get_authenticated_info']) and (
      exists(select 1 from studybuddy.documents d where d.owner_id=auth.uid() and d.lifecycle='ready' and d.object_key=key)
      or (coalesce(nullif(current_setting('request.headers',true),'')::jsonb->>'x-studybuddy-operation','')='verify'
        and exists(select 1 from studybuddy.save_operations o join studybuddy.save_objects f using(owner_id,operation_id)
          where o.owner_id=auth.uid() and o.status='pending' and o.expires_at>clock_timestamp() and f.object_key=key))))
    or (storage.allow_any_operation(array['object.delete','object.delete_many']) and exists(
      select 1 from studybuddy.save_objects f where f.owner_id=auth.uid() and f.object_key=key and f.cleanup_needed and not f.upload_enabled
        and not exists(select 1 from studybuddy.documents d where d.owner_id=f.owner_id and d.lifecycle='ready' and d.object_key=f.object_key))));
$$;
commit;
