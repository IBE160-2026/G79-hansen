---
title: Delete saved material completely
type: feature
created: 2026-11-18
status: done
route: dispatch
review_loop_iteration: 0
story_key: 3-4-delete-saved-material-completely
baseline_commit: b9f7158b86bc62b820de270edff6dbf131bbdd6b
context: [.docs/implementation-artifacts/epic-3-context.md]
---

<frozen-after-approval reason="human-owned intent; confirmation required by bmad-build checkpoint 1">

## Intent

Let the owner deliberately delete a saved document from Mine dokumenter. Name the document and explain that its source, learning material and progress are included. Cancel changes nothing. Confirmation fences access immediately; success requires completed removal rather than merely scheduling cleanup.

## Boundaries & Constraints

Reuse existing authentication, CSRF/session-view checks, bounded private document routes, user-JWT transport, backend gate and owner RLS. Keep Norwegian UI and no-store responses. No real model calls, new accounts, public deployment, paid services or unrelated hardening. First implement and verify locally with synthetic data; prepare any hosted migration for separate concrete approval.

Persist a deleting lifecycle and owner-bound retry identity. Serialize document file IO in the application and use compatible database lock ordering with Save, upload finalization, expiry and progress. Fence new admission, upload, commit, open, download and progress when deleting. Cancel pending saves and erase staged source/results. Enumerate current, superseded, provisional and uncertain object keys from durable records. Never infer physical upload quiescence from a successful DELETE, a missing metadata row, a timer or process-local lock alone. Retain retry/cleanup records while writes may still finish.

After verified object cleanup, remove source/bundle/progress, obsolete operation payloads and the document row transactionally. Preserve only content-free owner/document/operation tombstones and outcomes for the existing seven-day retry window; stale Save and progress requests cannot recreate deleted IDs. Respect the foreign keys and immutable-ready-operation trigger. Retain uncertain object records beyond that window until reconciled. Document backup/physical retention separately; existing real-file acceptance gates remain open until evidenced.

## I/O & Edge-Case Matrix

| Scenario | State | Expected behavior |
| --- | --- | --- |
| Cancel | Named inline confirmation | No API mutation; return focus to Delete |
| Confirm | Owned saved document | Disable duplicate submission, persist deleting, clear its active workspace and fence late responses |
| Failure/restart | Durable deleting state | Discoverable retry; no false success or resurrection |
| Lost response | Same owner and exact request | Replay/resume same deletion, including after fresh login |
| Foreign/unknown ID | Any direct endpoint | No content, keys, title or mutation authority disclosed |
| Concurrent Save/progress/read | Deletion starts | One safe lock order; no stale commit or bytes returned after lifecycle recheck |
| Delayed upload | Provisional or uncertain object | Keep cleanup pending until provider quiescence and removal are verified |
| Complete | Every required removal verified | Remove library entry; show success; exact retry remains safe |

</frozen-after-approval>

## Code Map

- `app/{contracts,api,services,adapters}/documents.py`: reuse strict DTOs, authenticated admission, bounded workers and allowlisted RPCs. Current cleanup deliberately never certifies quiescence.
- `app/adapters/storage.py`: HTTP200 DELETE alone cannot prove cleanup.
- `app/static/workspace.{js,html}`: library rows, savedTarget, progress/save/library epochs and private-state reset.
- Save migration `20261115214610`: lifecycle, noncascading operation FK, immutable ready trigger, write_unknown, upload/expiry locks. Admission must check tombstones before insert.
- Progress migration `20261117184855` and library/S3 migrations: preserve CAS, replay and uncached lifecycle checks.
- `tests/{test_documents.py,test_library.py,documents_browser_app.py,browser-library.cjs}`: reusable fixtures; provider helpers use SUREUbuntu.

## Tasks & Acceptance

- [x] Document contracts/API/service/adapters above: add delete/retry discovery, lifecycle orchestration and shared file-IO ordering.
- [x] `supabase/migrations/` (CLI-created): owner+gate invoker deletion RPCs, cleanup/tombstones, compatible locks and resurrection guards.
- [x] Workspace JS/HTML above: named confirmation/cancel, deleting/retry states, focus and active-document cleanup with response fencing.
- [x] `tests/test_deletion.py`, `tests/browser-deletion.cjs`, `supabase/tests/deletion_protocol.test.sql`, `tests/deletion_provider_acceptance.py`: matrix, actual ownership/storage, delayed upload and concurrent deletion.
- [x] `.docs/implementation-artifacts/deletion-acceptance.md`, `README.md`, sprint/spec and session/reflection records: executed evidence and retention gates.

Given an owned saved item, when deletion is cancelled, then its library entry, content and progress remain unchanged. When confirmed, then deleting blocks access and completed removal clears its active UI.

Given provider failure, process restart or a lost successful reply, when the owner retries, then deletion resumes/replays without recreating data or reporting premature completion.

Given current, old and provisional objects plus an uncertain delayed upload, when deletion runs, then all keys remain tracked until writes quiesce and removal is verified; another owner cannot read or delete them.

## Implementation Notes

Hosted activation approved with “ja godkjenner” on18 November. The reviewed
migration was applied as20261118172916 to existing studybuddy-test (Free/Paris).
Ordinary app restarted at port8000/worker25940. Hosted16, normal deletion22,
ordinary browser6 and normal progress16 passed; direct DB postcheck confirmed
only content-free tombstones/outcome remain for the new synthetic document.
Existing accounts reused; real model ledgers byte-identical. No public deploy.
The following local-only implementation notes are historical.

Local implementation completed 18 November: CLI-created migration
`20261118165334_delete_saved_material_completely.sql`; no hosted migration.
New uploads register exact durable attempt IDs. Only the terminal response for
that attempt settles it; legacy/lost/uncertain writes stay pending. File cleanup
requires an exact positive named remove receipt, no uncertain writes and a
fresh internal S3 check. HTTP200/empty lists/metadata absence alone never pass.
The matching local Storage v1.90.1 source awaits backend cleanup before its
positive result. Final cleanup deletes rows in FK order without mutating the
immutable ready outcome; content-free tombstones expire after seven days via
administrator-only maintenance. Uncertain records never expire automatically.
See `deletion-acceptance.md` for executed evidence and backup/physical gates.

The student approved the specification with “godkjenner” on 18 November. Continue the authorized local implementation and necessary synthetic tests. Respect CLAUDE.md: keep context and test/review rounds focused; credentials, model budgets and hosted state remain unchanged.

No intent gaps. Cross-layer footprint as listed above. Irreversibles: migrations and provider-data deletion; no hosted mutation during planning. Elevated Git inspection confirmed clean baseline; apparent fixture deletions were sandbox access errors.

## Spec Change Log

## Review Triage Log

One focused independent edge-case review plus parent diff/matrix audit; overlapping blind-hunter and separate verification-gap contexts were omitted to respect the student's token/time constraints.

| ID | Verdict | Route | Evidence |
| --- | --- | --- | --- |
| E1 | medium, resolved | patch | Captured ready replay now checks the fenced commit RPC after file IO; two passing regressions cover deleting and completed deletion. |
| P1 | medium, resolved | patch | Owner/operation advisory lock precedes document locking. Deterministic actual PostgreSQL concurrency test passed: second document stays ready and receives delete_mismatch. |
| P2 | medium, resolved | patch | Only successful current-view deletion discovery enables Slett; browser regressions for absent API404 and unavailable RPC503 preserve opening/library status. |

## Verification

- Baseline 18 November: `uv run pytest tests/test_documents.py tests/test_library.py tests/test_progress.py -q` — 89 passed in 5.99s; existing TestClient deprecation warning.
- After implementation: deletion Python/browser/pgTAP/provider races; affected Save/library/progress regressions once. Broaden for concrete shared-flow changes/failures.
- Keep provider outputs in ignored `test-results`; injected ports cannot prove SQL/Storage acceptance.
- 18 November final after review fixes: `uv run pytest tests/test_deletion.py tests/test_documents.py tests/test_library.py tests/test_progress.py -q` — 115 passed (existing TestClient warning), including 26 deletion tests.
- `node tests/browser-deletion.cjs` — 7 passed; affected browser regressions: Save25/library21/progress16 passed. Parent reran Save/library after the patches; progress16 remains the unchanged earlier run.
- Isolated local `supabase/tests/deletion_protocol.test.sql` — 40 pgTAP assertions passed, rolled back; includes seven-day pruning and indefinite uncertain-record retention.
- `SAVE_TEST_WSL_DISTRO=SUREUbuntu uv run python tests/deletion_provider_acceptance.py` — 15 passed with real local owner JWTs/Storage. Current+superseded files complete; delayed chunked upload during deletion is fenced and remains uncertain/retryable across service reconstruction.
- No real-file, independent physical-erasure or backup-retention acceptance is claimed. Lost provider removal acknowledgements require independent reconciliation and remain pending. Hosted synthetic integration passed after separate approval as recorded above.
- Parent final pgTAP rerun40 passed against the corrected local function. `SAVE_TEST_WSL_DISTRO=SUREUbuntu uv run python tests/deletion_identity_concurrency_acceptance.py` passed the deterministic identity race. No review finding deferred.
- Matrix audit: cancel/confirm/complete and lost reply/restart have browser coverage; foreign/unknown/auth contracts have Python/provider coverage; captured Save replay, in-flight file read and actual delayed upload cover lifecycle races; superseded/current removal and pgTAP cover transactional completion. All covering checks executed and passed.
