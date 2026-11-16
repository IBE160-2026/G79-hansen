# Story 3.1 Save acceptance

Local implementation re-derived on 16 November 2026. Hosted migration/bucket/verifier
changes to `studybuddy-test` remain unapproved. No hosted accounts, auth settings,
model calls, real model allowance files or existing secrets were used by the
implementation agent. All application/browser fixtures are synthetic.

## Final local result, 16 November 2026

Local implementation/review is complete. Hosted application and real-file gates
remain pending. Final checks: **529 pytest passed / one inherited skip / one
existing warning (92.30s)**; **25 Save browser scenarios**; actual local
**47 provider, 23 pgTAP, 18 SQL/cron/concurrency and 4 expiry-fairness checks**
passed. Schema lint/advisors and19 unsigned normal-server startup checks passed.
Shared browsers28/33/11 passed during re-derivation; unchanged auth/demo flows were
not rerun after the final Save-only corrections. Full details are in ignored
`test-results/save-*-final.log`; no real model inference was performed.

Three independent layers and a fresh three-layer loopback were triaged before
patching. All29 individual findings have verdicts in the spec. Initial15 caused
one non-frozen clarification/re-derivation; the later14 yielded11 corrections /
verification gaps and3 rejected claims (two false, one low impact requiring
unnecessary new preflight complexity). No findings were deferred. Final corrections
retain cleanup retry, refresh terminal rows, validate ready replay bytes, fence
late reload errors, skip locked operation/document pairs before the batch limit,
scope cleanup status, bound unused Storage responses and strengthen concurrency /
replacement/portable-tool evidence. Actual verified-duplicate upload probe returned
HTTP400, reconciled successfully and committed; the alleged failure was rejected.

The exact migration SHA-256 (UTF-8 with LF) is
`34256a4919de041f3ae2c8e67de71569d4257d9e113df803a858a30014fdf4fb`.
Review that migration, the bucket/grants/job below and the nonsecret verifier
before the separate hosted approval. Save remains disabled locally until setup
is approved; the existing auth/model configuration and real allowances are unchanged.

## Implementation and reproducible checks

- `app/contracts/documents.py`: strict owner-free DTOs, schema-versioned digest,
  exact snapshot/file/positions identity and Unicode title limit.
- `app/services/documents.py`, `app/api/documents.py`: replay-first admission,
  same-owner recovery, per-session/global no-queue limits, 16 MiB/five-second
  intake and 60-second owned work budget. HTTP wait expiry retains worker permits.
- `app/services/workspaces.py`: per-workspace asynchronous admission ordering;
  authentication/global locks never span external IO or the legacy validation yield.
- `app/adapters/documents.py`, `storage.py`: request-scoped user JWT/publishable
  key plus server-owned capability, bounded RPC/readback and immutable upload.
- CLI-created migration
  `supabase/migrations/20261115214610_save_consistent_private_snapshot.sql`:
  constrained owner entities, immutable operation trigger, protected hash
  configuration, invoker RPCs, owner+gate RLS and operation-aware private bucket.
- Secondary Norwegian Save/title/pending/retry/recovery/conflict controls preserve
  draft/results and clear private state on access end; no browser content storage.

Historical checks before review-loop re-derivation (not proof of current files):

| Check | Executed result |
| --- | --- |
| `uv run pytest tests/test_documents.py -q` | 27 passed; injected ports only, including restart discovery/CLI superseded cleanup and conflict staging erasure |
| `uv run pytest -q` | 506 passed, one inherited optional skip |
| `node tests/browser-documents.cjs` | 15 passed including exact-file resupply, explicit reload and ready superseded-file cleanup after page reload |
| `node tests/browser-sources.cjs` | 28 passed |
| `node tests/browser-auth.cjs` | 33 passed |
| `node tests/browser-demo.cjs` | 11 passed |

The existing Starlette/httpx TestClient deprecation warning remains. No tests
were used as a substitute for actual SQL/Storage acceptance.

Historical parent checks against the isolated actual local Supabase stack:

- CLI 3.1.0 official Linux ARM64 release verified against its release checksum;
  CLI-generated migration name, initialization and current help used.
- Exact latest migration reset succeeded against actual Postgres 17.
- `supabase/tests/save_protocol.test.sql`: 16 pgTAP assertions passed.
- `tests/save_provider_acceptance.py`: 37 actual API/RLS/Storage checks passed
  using two local synthetic owners. This includes actual Storage backend-header
  propagation, missing/wrong/retired gate and foreign-owner negatives, direct
  table/RPC isolation, ready/pending verification/sign denial, immutable upload,
  readback/commit/replacement/superseded deletion and expiry erasure/commit denial.
  That run also verified discovery of ready superseded-file cleanup; the later
  historical parent run reached 38 checks including conflict staging erasure.
- An upload was genuinely stalled mid HTTP request body while cancellation
  committed, then released: later metadata finalization was denied, metadata
  remained absent and unknown-write/cleanup records remained retained.
- Database advisors at warning threshold/error failure reported no issues.

These results establish observed local transaction and provider behavior. The
delayed upload check does not establish physical blob quiescence; cleanup stays
pending. The hosted project has not been changed.

## Fresh review-loop verification, 16 November 2026

| Check | Executed result |
| --- | --- |
| `.venv/Scripts/python.exe -m pytest tests/test_documents.py tests/test_generation.py -q` | 147 passed (33 document cases and 114 generation cases), including 6,000 short paragraphs, noninitial independent positions, seven-day completed discovery, lost ready reply/restart, object-free terminal cleanup and enabled/disabled configuration distinction |
| `node tests/browser-documents.cjs` | 23 passed; persisted noninitial item IDs in both sections, explicit reload at both noninitial positions with answers hidden, lost ready reply/restart, title correction/uncertain identity, discovery error/retry versus disabled configuration, stale root/page and stale authentication replies, object-free completion |
| `node tests/browser-sources.cjs` | 28 passed |
| `node tests/browser-auth.cjs` | 33 passed |
| `node tests/browser-demo.cjs` | 11 passed |

The parent completed the fresh full-suite and actual local SQL/Storage/scheduler acceptance: **514 passed, one inherited skip and one existing warning (50.19 seconds)**; **45 provider checks, 23 pgTAP assertions and 12 SQL/cron/concurrency checks passed**, with clean schema lint/advisors. The final fixture harness with separate timeout headroom also passed all12.
The final `completed_at` migration passed actual provider45 and pgTAP23 checks,
including safe pending title/lifetime projection, ready outcomes, object-free
completion/tombstones, cancellation title erasure and UUID pagination beyond 50
rows. The first derived migration passed provider42, pgTAP16 and concurrency/
scheduler12 checks with clean advisors; scheduler12 also passed bounded-job
hardening before the completion timestamp addition. The final scheduler and
full pytest passed as recorded above. One parallel fixture run failed before
its second expiry assertion without a retained SQL error category; no expired
publication was observed or claimed. Fixed-category diagnostics and separate
fixture timeout headroom were added. Both subsequent isolated scheduler/lock
runs passed all12; an unrecorded cause is not asserted.

The Story 2.6 baseline remains historical: 481 passed/one inherited skip and
28/33/11 browser checks. The prior implementation's 506/one skip, focused27,
15 Save browser scenarios, pgTAP16 and parent38 results remain historical above.

## Matrix evidence and limits

| Protocol row | Application/browser evidence | Real-provider evidence |
| --- | --- | --- |
| First Save | Exact ready snapshot/title/independent positions, no extra model call, duplicate suppression | Actual local commit/readback passed |
| Invalid authority | Receipt/source/bundle/positions/file/title/unknown fields rejected before admission | Actual local gate/grants negatives passed |
| Replay | Completed replay survives invalidation/old proof; changed digest fails; lost HTTP reply retains one operation | Actual local transaction replay passed |
| Replacement | New generation resets positions; stale revision preserves draft and offers reload/Save as new | Actual local replacement/superseded object checks passed |
| Recovery | Reconstructed app/fresh owner login resumes stored snapshot; foreign/unknown denied; exact-file resupply | Actual local two-owner operation isolation and expiry denial passed |
| Upload/cleanup | Registered uncertain writes, bounded byte hash, wrong bytes denied, expiry erasure, cleanup stays pending | Actual delayed upload cancellation/finalization fence passed; physical cleanup/retention remains separate |
| Concurrency/session | Owned workspace gate orders edit against admission; logout remains responsive; post-logout new admission denied; worker permits retained at wait deadline | Actual operation finalization fence passed |
| Direct access | Injected transports prove backend-selected headers only | Actual JWT/no/wrong/retired gate, foreign-owner, table/RPC/Storage negatives passed |

## Exact hosted review package

Review the complete migration above, its grants, policies and bucket restrictions
before approval. It creates only private bucket `studybuddy-sources`, limits
uploads to 10 MiB and `text/plain`/`application/pdf`, grants no Storage UPDATE,
list or signing path, and accepts only registered owner/operation keys. Pending
verification is a backend-only read path; exact ready files require owner and
backend gate. Cleanup DELETE is limited to disabled registered cleanup objects.

The exact same migration installs pg_cron and schedules the administrator-owned
`studybuddy-expire-staging-v1` job every minute. Its command sets a ten-second
statement timeout then invokes the unexposed SECURITY INVOKER
`studybuddy.expire_staging_admin(100)`. Public/anon/authenticated cannot execute
that maintenance function or access its health table. Batches skip locked
operations/targets, erase overdue pending staging/title, disable upload
finalization and preserve content-free identities and uncertain object records.
Ready rows and unexpired rows are preserved. Commit/recovery rejects expiry at
the exact deadline after locks; physical staging purge occurs on the next
successful maintenance batch. A disabled/failed job or overdue backlog is an
acceptance failure. This does not erase backups or establish blob quiescence.

Include job installation and monitoring in the separate hosted approval. The
following administrator-only, content-free queries are the health review:

```sql
select jobname, schedule, active, username, command from cron.job
where jobname = 'studybuddy-expire-staging-v1';
select status, start_time, end_time, return_message from cron.job_run_details
where jobid = (select jobid from cron.job
               where jobname = 'studybuddy-expire-staging-v1')
order by start_time desc limit 5;
select last_completed_at, expired_count,
       last_completed_at > clock_timestamp() - interval '2 minutes' as recent
from studybuddy.expiry_maintenance_health;
select count(*) as overdue_staging from studybuddy.save_operations
where status = 'pending' and expires_at <= clock_timestamp();
```

Require an active administrator job, a recent successful completion and no
unexplained overdue staging. Locked/backlogged rows delay purge and require
operational attention; scheduler health cannot be inferred from passing mocks.
Only pending recovery includes its private title; cancellation/conflict/expiry
scrubs initial pending titles. Completed outcomes remain discoverable for seven
days from completion; terminal operations with no registered object report
`cleanup_complete`, disappear from recovery and retain their ID/digest tombstone.

The parent completed the separately authorized exclusive key setup with restricted
Windows ACLs. The raw key remains in ignored `.save-backend-key`, outside `.env`,
Git, SQL and browser responses. This is the exact nonsecret verifier statement
for the separate hosted approval package; it has not been executed:

```sql
insert into studybuddy.backend_verifiers (key_id, verifier, active)
values ('save-v1', 'ade78cbee9327fdde5abb8d261974431d25741520ed2db3878c72508326be999', true);
```

Normal authenticated roles have SELECT only on this configuration table.
Save remains disabled until configuration is explicitly enabled after approval.

Retain the existing hosted Free plan, Paris region, users and auth settings.
Hosting, real course files, document backup/deletion retention, full library UI,
ongoing practice sync and user deletion remain separate acceptance/story gates.
Physical cleanup currently remains pending conservatively, including after a
DELETE response; recovery metadata is not removed while writes may be uncertain.
