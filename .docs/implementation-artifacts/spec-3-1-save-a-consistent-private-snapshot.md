---
title: Save a consistent private snapshot
type: feature
created: 2026-11-15
status: draft
route: dispatch
story_key: 3-1-save-a-consistent-private-snapshot
baseline_commit: 15987b9dc74859b8272883af85e2a404ea0af89c
review_loop_iteration: 0
context: [.docs/implementation-artifacts/epic-3-context.md, .docs/implementation-artifacts/save-protocol-3-1.md]
---

<frozen-after-approval reason="human-owned intent; concrete plan approval pending">

## Intent

**Problem:** Generated material disappears with the page/session; there is no explicit private Save or recoverable durable operation.

**Approach:** Save the validated source, settings, four-part bundle, optional original file and independent practice positions as one owner snapshot. Use durable admission, immutable operation identity and transactional commit so exact retries survive failures/relogin/restart without duplicate documents or stale replacement.

## Boundaries & Constraints

**Always:** Only explicit Save admits persistence. Preserve existing receipt/hash/authority, authentication, source limits and late-response fences. Owner comes from validated identity. Use user-token SECURITY INVOKER RPCs, RLS, short transactions and the backend-origin gate in the protocol; no ordinary-operation service key. Expose ready data only; keep pending snapshots private. Preserve inputs/results on failure. First Save captures valid independent item IDs; replacement resets progress. Retain admitted recovery seven days, then erase staging and permit cleanup only.

**Never:** Autosave unsaved content, new model calls, new hosted accounts/emails/password changes, paid services/deploy, credentials/content in logs or browser storage, overwriting ready files before commit, automatic conflict rebasing, or claiming mock tests prove database isolation. Full library UI, ongoing progress sync and user deletion remain Stories 3.2–3.4.

## I/O & Edge-Case Matrix

| Scenario | Given / when | Then / safe failure |
| --- | --- | --- |
| First Save | Given current generation/file/receipt, when clicked | One immutable owner operation; source/settings/bundle/file/progress become ready atomically; no AI |
| Invalid authority | Given missing/changed/expired/superseded proof or wrong file/positions | Reject before durable new admission; preserve draft and explain fresh generation when required |
| Replay | Given known owner operation, when retried | Identical completed outcome before old receipt/revision checks; changed digest fails; no duplicate mutation |
| Replacement | Given expected revision and new generation | Atomic revision/bundle/progress replacement; stale/deleting target conflicts; preserve draft, explicit reload or Save as new |
| Recovery | Given admitted operation and fresh same-owner login | Resume exact snapshot/registered file within seven days without old receipt; foreign/unknown/expired admission cannot commit |
| Upload/cleanup | Given failure, timeout, restart or lost reply | Registered keys and uncertain writes remain discoverable; reconcile exact bytes, retain cleanup records; never false ready/clean success |
| Concurrency/session | Given edit/reset/logout/expiry during Save | Ordered admission versus invalidation, responsive logout, no late display revival or unapproved new admission |
| Direct access | Given user JWT without backend gate, foreign owner or pending object | RPC/table/storage mutation or private content access denied; backend gate never bypasses owner/lifecycle checks |

</frozen-after-approval>

## Delivery and Authorization

Approval starts local implementation/testing. Present exact migration, bucket policies and nonsecret verifier for separate final approval before hosted changes to `studybuddy-test`. Preserve Free/Paris/users/settings. No new model budget. Docker is installed but stopped; CLI is absent. Prepare pinned tooling after approval; unavailable SQL/Storage testing remains pending, never replaced by mock acceptance.

## Code Map

- `app/services/workspaces.py::validate_save`: reuse checks, but replace its global-lock-across-yield integration with an owned per-workspace admission gate; never await remote IO under auth/global locks.
- `app/services/receipts.py`: preserve canonical/signature formats. `app/api/private.py`: reuse authentication, Origin/CSRF/session-view and bounded decoding.
- `app/adapters/auth.py::Identity`, `services/sessions.py`: reuse validated owner/user JWT and lifecycle. Add separate request-scoped document/storage clients; auth client yields auth only.
- `app/static/workspace.js`: reuse accepted/bundle/receipt, independent positions, invalidation and access clearing; add separate Save state without calling generation submit.

## Tasks & Acceptance

**Execution:**
- [ ] `supabase/config.toml`, `supabase/migrations/`, `supabase/tests/` — initialize pinned CLI via help; generate migration names with CLI; implement constrained owner documents/content/bundles/progress, immutable save operations/object records, gate verifier, RPCs and exact ready-object policies; test real local transactions/RLS.
- [ ] `app/contracts/documents.py` — strict Save/recovery/status/reload DTOs, schema-versioned digest including title/positions, exact file identity and safe lifecycle errors.
- [ ] `app/services/workspaces.py`, `api/workspaces.py`, `services/documents.py`, `scripts/save_cleanup.py` — ordered admission/invalidation, replay-first recovery, owned IO, expiry, commit and registered-key cleanup; no global lock around network calls.
- [ ] `app/adapters/documents.py`, `storage.py` — bounded user-token clients, backend-owned gate header, no overwrite, bounded readback verification, upload uncertainty and registered-key cleanup; no reusable signed URLs.
- [ ] `scripts/save_backend_key.py`, `app/config.py`, `main.py`, `.env.example`, `.gitignore` — disabled-by-default Save, exclusive ignored key setup printing hash only, injected ports and private routes; never expose raw key or alter existing secrets.
- [ ] `app/api/documents.py` — admission, retry, owner pending-status/cleanup and minimal current-target reload; bounded intake, work deadline, admission and cleanup ownership per protocol.
- [ ] `app/static/workspace.html`, `workspace.js`, `styles.css` — secondary Lagre, optional 160-code-point title, saved/pending/retry state, recovery/file resupply and conflict choices; preserve workspace, capture positions once, clear private state on access end.
- [ ] `tests/test_documents.py`, `tests/documents_browser_app.py`, `tests/browser-documents.cjs` — injected-model lifecycle/failure matrix, invalidation races, restart recovery, lost replies and no extra model calls; genuine local SQL/storage two-owner negative tests remain mandatory.
- [ ] `README.md`, `save-acceptance.md`, architecture implementation note — document operation, backend-origin gate, exact executed evidence, pre-hosted review package and remaining real-file/provider/hosting gates.

**Acceptance Criteria:**
- Given local verification, when implementation is reviewed, then every matrix row has executed evidence; pending/ready claims reflect actual database/storage state, and no never-admitted snapshot persists.
- Given approved hosted application later, when existing-user synthetic checks run, then direct RPC/table/storage isolation and recovery pass without new accounts, model calls or auth-setting changes. Until then label hosted acceptance pending.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

Run document/generation tests, real local SQL/RLS/Storage checks, Save/recovery/reflow/keyboard browsers and final full pytest. Repeat existing browsers for shared UI/session changes. Verify owner/gate negatives and exact migration/grants/advisors before hosted approval. Preserve historical 481 passed/one skip and 28/33/11 browsers as baseline.
