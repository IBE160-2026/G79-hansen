# Story 3.4: delete saved material completely

Implementation and existing-test-project integration evidence, 18 November 2026.
The student explicitly approved hosted activation with “ja godkjenner”. Migration
`20261118172916` is applied in `studybuddy-test` (Free/Paris); the ordinary app
was restarted on port8000, worker25940. No real model calls, new accounts or real
study files were used. Real-file backup/physical-retention acceptance remains open.

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

## Existing test-project activation

The reviewed local migration `20261118165334_delete_saved_material_completely.sql`
was applied unchanged as hosted version `20261118172916`. Schema inspection
confirmed owner RLS on all four new tables, invoker deletion functions, anonymous
denial and the administrator-only active tombstone cleanup job. Security advisors
showed only the previously recorded leaked-password-protection warning; Auth
settings were unchanged.

- Actual hosted preparation saved and replaced one new synthetic text file,
  with an injected synthetic model and an isolated temporary budget. Existing
  authorized accounts were reused. Resumed hosted acceptance: **16 passed**.
- A simulated cleanup failure before any Storage delete persisted the deleting
  identity; ordinary app restart/fresh login resumed it. Normal-server deletion:
  **22 passed**, including actual current/superseded removal, exact retry,
  identity binding, foreign denial and no-store responses.
- Direct database postcheck: document/source/bundle/progress/progress-request/
  Save-operation/object/upload-attempt counts were all zero for this run; two
  content-free Save tombstones and the deleted outcome remained.
- Ordinary-server browser: **6 passed** for enabled deletion, named confirmation,
  cancellation without a delete request, preserved existing synthetic entry,
  focus, script-error absence and unchanged model allowance.
- Existing ordinary-server progress regression: **16 passed** after integration,
  including normal ready-document reading and cross-owner denial. Both real
  model ledgers remained byte-identical throughout.

The first hosted harness stopped because it required403 for a stale view;
the existing contract correctly returns401. The corrected harness resumed the
same synthetic document without creating more files. The first browser probe
clicked the library during initial pending-Save discovery and met the existing
per-session429 guard; waiting for startup discovery produced the final six passes.
Production limits were unchanged. Ignored scripts/results are
`test-results/hosted-deletion-*`, `normal-deletion-*` and `normal-progress-*`.

## Remaining gates and conservative recovery

- Legacy uncertain uploads, lost provider remove acknowledgements, orphaned
  physical blobs and provider failures without terminal evidence remain
  deleting/retryable. No timer or automatic record purge turns them into
  success. Independent provider reconciliation is still required for these
  existing real-file acceptance gates.
- Database backups/PITR, object versioning/replicas/provider backups, their
  retention periods and independently measured physical erasure have not been
  accepted. Application deletion does not claim immediate backup destruction.
- Local and hosted synthetic evidence does not establish public hosting, two
  physical devices or real-file acceptance. Historical broad Save provider
  timing instability remains outside this focused run.
- Existing TestClient/httpx deprecation warning remains unchanged.

Raw pgTAP output and the summarized local run record are under ignored
`test-results/`; no provider payloads, secrets or private source material are
committed.
