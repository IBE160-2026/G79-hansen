# Story 3.4: delete saved material completely

Local implementation evidence, 18 November 2026. Hosted migration and real-file
retention acceptance remain separate approvals/gates. No hosted changes, real
model calls, credentials or real study files were used.

## Implemented protocol

Mine dokumenter offers a named inline confirmation explaining source, learning
material and progress. Avbryt sends no mutation and restores Delete focus.
Confirmation fences late browser responses, clears the active saved workspace,
persists `deleting`, disables duplicate submission and exposes explicit retry.
Pending deletions are discoverable after fresh login/restart, separately from
ready library entries and obsolete Save recovery.

Strict owner-free DTOs reuse authentication, CSRF/session-view checks, bounded
admission/workers, user-JWT transport, backend gate, owner RLS and no-store.
File upload/read/delete/cleanup share an application file-IO mutex; deletion
persists the database fence before waiting. Database admission/deletion share
an owner/document advisory mutex and lock Save operations before the document,
compatible with commit, expiry and upload finalization. Progress uses the
document row lock and cannot publish into deleting/missing generations.

Every new physical upload registers a unique durable attempt before dispatch.
Only its own terminal provider response can settle that attempt. Lost upload
responses, process death and existing `write_unknown` records remain uncertain;
successful later retries do not settle earlier attempts. Deletion enumerates
all current, superseded and provisional keys from durable Save records, cancels
pending Save, erases staged snapshots and disables upload/commit/read/progress.

Completion requires an exact positive named Storage remove receipt in the
requested bucket, no uncertain writes and a fresh internal S3 absence check.
HTTP200 alone, an empty removal list, metadata absence, a timer or a local lock
cannot certify completion. Per-key acknowledged cleanup is recorded durably.
Final removal transaction respects object/operation/progress-mutation FKs and
the immutable-ready trigger, then cascades source/bundle/progress/document.
Only content-free owner/document/operation/mutation identities remain for the
seven-day retry window. Hourly administrator-only pruning never expires a
deleting document or uncertain object/attempt records. Expired stale receipts
cannot readmit deleted content after the retry window.

## Executed checks

| Evidence | Result |
| --- | --- |
| Existing affected Python baseline before implementation | 89 passed |
| Deletion Python tests, including two review regressions | 26 passed |
| Final combined deletion + Save/library/progress Python regression | 115 passed |
| `node tests/browser-deletion.cjs` | 7 passed |
| Save browser regression after review fixes | 25 passed |
| Library browser regression | 21 passed |
| Progress browser regression | 16 passed |
| `supabase/tests/deletion_protocol.test.sql` in isolated local PostgreSQL | 40 assertions passed, rolled back |
| `SAVE_TEST_WSL_DISTRO=SUREUbuntu uv run python tests/deletion_provider_acceptance.py` | 15 passed |
| `SAVE_TEST_WSL_DISTRO=SUREUbuntu uv run python tests/deletion_identity_concurrency_acceptance.py` | Passed deterministic actual PostgreSQL identity race |

One independent edge-case review and parent diff/matrix audit found three issues;
all were fixed with focused regressions: cached ready Save replay now rechecks
the deletion fence; concurrent deletion identity reuse cannot fence a different
document; missing deletion API/RPC leaves library opening available and Slett
disabled. Parent final checks passed Python115, Save25/library21 and pgTAP40.
Earlier progress16 and actual provider15 remain the relevant unchanged evidence.
No review finding was deferred.

The actual provider runner uses two temporary accounts, owner JWTs and the
named `studybuddy-save-local` stack only. It verifies foreign RPC/Storage denial,
current/superseded object removal, obsolete operation deletion, exact retry from
a fresh service, resurrection guards and a chunked HTTP upload held while
deletion runs. That upload cannot finalize after the fence; its unsettled
attempt survives restart/retry and prevents false success. Late Save/progress
are denied. Temporary fixture rows/accounts are removed in `finally`.

The local Storage image is `public.ecr.aws/supabase/storage-api:v1.90.1`.
Provider semantics were checked against the
[official remove documentation](https://supabase.com/docs/guides/storage/management/delete-objects)
and the matching
[tagged deleteObjects implementation](https://github.com/supabase/storage/blob/v1.90.1/src/storage/object.ts).
`deleteObjects` awaits `cleanupDeletedObjects` before returning the positive
named result; the cleanup awaits backend object deletion. This is operational
removal evidence for these acknowledged objects, not a backup erasure claim.
S3 404 is used only together with that acknowledgement and write quiescence.

## Remaining gates and conservative recovery

- Migration `20261118165334_delete_saved_material_completely.sql` is prepared
  for separate concrete hosted approval. The hosted browser must not use the
  new deletion API before that migration is applied.
- Legacy uncertain uploads, lost provider remove acknowledgements, orphaned
  physical blobs and provider failures without terminal evidence remain
  deleting/retryable. No timer or automatic record purge turns them into
  success. Independent provider reconciliation is still required for these
  existing real-file acceptance gates.
- Database backups/PITR, object versioning/replicas/provider backups, their
  retention periods and independently measured physical erasure have not been
  accepted. Application deletion does not claim immediate backup destruction.
- Local synthetic ownership/Storage/race evidence does not establish hosted,
  production multi-device or real-file acceptance. Historical broad Save
  provider timing instability remains outside this focused run.
- Existing TestClient/httpx deprecation warning remains unchanged.

Raw pgTAP output and the summarized local run record are under ignored
`test-results/`; no provider payloads, secrets or private source material are
committed.
