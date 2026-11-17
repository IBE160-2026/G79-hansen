---
title: Save a consistent private snapshot
type: feature
created: 2026-11-15
status: done
route: dispatch
story_key: 3-1-save-a-consistent-private-snapshot
baseline_commit: 15987b9dc74859b8272883af85e2a404ea0af89c
review_loop_iteration: 1
context: [.docs/implementation-artifacts/epic-3-context.md, .docs/implementation-artifacts/save-protocol-3-1.md, .docs/implementation-artifacts/save-review-requirements-3-1.md]
---

<frozen-after-approval reason="student approved the concrete plan on 2026-11-15; hosted application requires separate final approval">

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
- [x] `supabase/config.toml`, `supabase/migrations/`, `supabase/tests/` — initialize pinned CLI via help; generate migration names with CLI; implement constrained owner documents/content/bundles/progress, immutable save operations/object records, gate verifier, RPCs and exact ready-object policies; test real local transactions/RLS.
- [x] `app/contracts/documents.py` — strict Save/recovery/status/reload DTOs, schema-versioned digest including title/positions, exact file identity and safe lifecycle errors.
- [x] `app/services/workspaces.py`, `api/workspaces.py`, `services/documents.py`, `scripts/save_cleanup.py` — ordered admission/invalidation, replay-first recovery, owned IO, expiry, commit and registered-key cleanup; no global lock around network calls.
- [x] `app/adapters/documents.py`, `storage.py` — bounded user-token clients, backend-owned gate header, no overwrite, bounded readback verification, upload uncertainty and registered-key cleanup; no reusable signed URLs.
- [x] `scripts/save_backend_key.py`, `app/config.py`, `main.py`, `.env.example`, `.gitignore` — disabled-by-default Save, exclusive ignored key setup printing hash only, injected ports and private routes; never expose raw key or alter existing secrets.
- [x] `app/api/documents.py` — admission, retry, owner pending-status/cleanup and minimal current-target reload; bounded intake, work deadline, admission and cleanup ownership per protocol.
- [x] `app/static/workspace.html`, `workspace.js`, `styles.css` — secondary Lagre, optional 160-code-point title, saved/pending/retry state, recovery/file resupply and conflict choices; preserve workspace, capture positions once, clear private state on access end.
- [x] `tests/test_documents.py`, `tests/documents_browser_app.py`, `tests/browser-documents.cjs` — injected-model lifecycle/failure matrix, invalidation races, restart recovery, lost replies and no extra model calls; genuine local SQL/storage two-owner negative tests remain mandatory.
- [x] `README.md`, `save-acceptance.md`, architecture implementation note — document operation, backend-origin gate, exact executed evidence, pre-hosted review package and remaining real-file/provider/hosting gates.

**Acceptance Criteria:**
- Given local verification, when implementation is reviewed, then every matrix row has executed evidence; pending/ready claims reflect actual database/storage state, and no never-admitted snapshot persists.
- Given approved hosted application later, when existing-user synthetic checks run, then direct RPC/table/storage isolation and recovery pass without new accounts, model calls or auth-setting changes. Until then label hosted acceptance pending.

## Implementation Notes

Approval recorded after rereading this file: student said “godkjenn og fortsett” on 2026-11-15. Local implementation/testing only; hosted migration/configuration remains unapproved. Parent prepares the local Docker/CLI runtime, then hands its verified connection/commands to the implementation agent. The agent implements against injected ports while setup proceeds; it must not use the existing hosted project, read `.env`, touch real model allowance files, call models or create real keys. Parent owns actual local integration verification and later key setup. Preserve baseline and frozen intent; do not rerender/replan this continuing build.

## Spec Change Log

### 2026-11-16 — review loop 1

The frozen intent is unchanged. B8/B9/B10 exposed insufficient non-frozen detail for object-free cleanup completion, automatic expiry for absent owners and useful recovery identities. Added [review requirements](save-review-requirements-3-1.md) as implementation context: explicit bounded recovery states, safe title/time projection, an admin-only database expiry job, and verification requirements. The previous implementation is reverted before re-derivation; positive preservation instructions and a local ignored source snapshot are described there. Avoid perpetual empty cleanup, indefinite private staging for absent owners and indistinguishable recovery actions. Preserve existing receipt/owner authority, atomic snapshots, no global IO locks, actual provider fencing, all historical evidence and disabled hosted integration. Patch findings below also survive this loopback.

## Review Triage Log

| ID | Verdict | Route | Evidence |
| --- | --- | --- | --- |
| B1 | high | patch | commit calls expire_operations before waiting for its operation/document locks and never compares clock_timestamp with expires_at after those locks; a queued expired action can publish. Add the post-lock deadline check using the existing expiry failure. |
| B2 | medium | patch | discovery filters out ready operations without cleanup, and the browser keeps operation IDs only in page memory; a lost commit reply followed by restart cannot discover success. Include recent completed outcomes using existing owner/status identities and render confirmed completion. |
| B3 | medium | patch | cancel nulls operation.snapshot but never changes documents.title for an initial pending document. Scrub that pending title at cancellation without touching a ready document. |
| B4 | medium | patch | browser only checks title length before freezing; server rejects whitespace/control titles as invalid_input, while saveControls then disables the title due to saveAttempt. Validate before freezing and release only definitively unadmitted invalid attempts. |
| B5 | low | patch | a ready generation disables Save but clears saveAttempt, enabling its title input. Disable title editing for that saved generation until a new generation can be saved. |
| B6 | medium | patch | discoverSaves catches all failures and schedules no retry on ordinary observations; transient failure hides operations until another initial/success trigger. Reuse existing status/retry controls for visible discovery failure, while configured-disabled Save stays unobtrusive. |
| B7 | medium | patch | discoverSaves checks session view only; same-session responses can clear a newer list, and stale pagination can append old actions. Add a discovery epoch/sequence fence, separate from workspace reset. |
| B8 | medium | bad_spec | cleanup always returns cleanup_pending and discovery retains all cancelled/expired operations even without a save_objects row; there is no possible provider uncertainty to settle. Specify object-free completion and hide only completed recovery rows while retaining content-free identity tombstones. |
| B9 | high | bad_spec | expiry runs only inside owner RPCs or the owner-token CLI; no scheduled all-owner erasure exists, so an absent owner's staged source/settings/bundle and initial title remain indefinitely. Add an admin-only automatic database expiry mechanism, strict deadline rejection and explicit physical-purge scheduling/health evidence; hosted scheduling remains unapproved. |
| B10 | medium | bad_spec | pending metadata omits title/admission time and the UI ignores expiresAt, so several pending saves have identical descriptions. Specify safely rendered owner-only pending title and times, with scrubbed terminal labels. |
| B11 | low | patch | README current-behavior paragraphs still describe Save/database as future work despite the new configured implementation. Correct these direct contradictions, retaining historical test facts and hosted-disabled status. |
| E1 | medium | patch | Save duplicates source units in acceptance and bundle but inherits collect's 10,100 structures/50,100 members limits; legitimate 6,000 short paragraphs pass source/generation intake but fail Save. Give Save a separately derived bounded structural budget without relaxing other routes. |
| E2 | high | patch | independently verified the same operation/document lock-wait expiry gap at commit; no post-lock clock check exists. Same root cause/fix as B1, retained as an individual verdict. |
| V1 | medium | patch | pre-verified gap: browser advances a flashcard but persistence assertion only checks different section IDs, while API/provider fixtures use first positions. Assert actual persisted noninitial independent item IDs. |
| V2 | medium | patch | pre-verified gap: reload test checks source/hidden answers but never noninitial displayed practice positions; removing restoration still passes. Exercise and assert restored independent positions in both sections. |


### Review after loop 1, 2026-11-16

All three fresh layers reported before triage. Each item is judged separately;
R1-B5/R1-B6 share post-selection target locking and are one SQL patch group.
No intent/spec loopback is needed: surviving corrections preserve the existing
API/identity/lifecycle and add focused evidence for demonstrated states.

| ID | Verdict | Route | Evidence |
| --- | --- | --- | --- |
| R1-B1 | medium | patch | cleanup_pending replaces row children, removing its only retry action. Retain the registered cleanup button and update its message while pending. |
| R1-B2 | medium | patch | retry errors only append text, so expired/conflicted pending rows retain Fortsett lagring. Refresh terminal recovery state to cleanup or object-free completion. |
| R1-B3 | false | rejected | Actual local probe after verified_v1: duplicate upload returned HTTP400, which upload explicitly accepts for reconciliation; adapter upload returned normally, readback succeeded and commit reached ready. The claimed denied-duplicate failure does not occur on the accepted provider. |
| R1-B4 | low | rejected | A stale admitted recovery may upload before the final CAS check, but commit still rejects stale/deleting targets and registers cleanup; the approved protocol expressly rechecks revision at commit. This is avoidable bounded IO, not invalid publication. A new locked preflight adds state/API complexity for an uncommon redundant transfer. |
| R1-B5 | high | patch | Admin selects LIMIT100 before checking document locks; 100 expired operations for a busy target can consume every batch and delay unrelated unlocked expiry. Select and skip locked operation/document pairs before the limit. |
| R1-B6 | medium | patch | Owner expire_operations skips operation locks but then waits on each unrelated document, before get/pending/completed replay. Use the same nonblocking pair selection for unrelated maintenance, retaining exact selected-operation deadline checks. |
| R1-B7 | low | patch | Commit cleanupStatus scans every owner file, even unrelated documents; a paste Save can inherit unrelated upload uncertainty. Restrict the existing calculation to this document's registered operations. |
| R1-B8 | false | rejected | The protocol requires a minimum seven-day outcome/tombstone lifetime and forbids recreating retired IDs; it does not prescribe a metadata maximum. Erased, unexposed content-free identities intentionally remain. Compaction that must recreate an equivalent permanent retired-ID record is not a missing user behavior. |
| R1-B9 | medium | patch | upload/delete call buffered HTTP helpers; BudgetTransport enforces time, not bytes. Stream/cap or ignore unused bounded response bodies, closing them on every result. |
| R1-B10 | medium | patch | Actual CAS checks are sequential; the real SQL runner only races expiry, not two replacements or commit/cancel. Add genuine concurrent SQL actors and assert one CAS winner and coherent ready-or-cancelled snapshots. |
| R1-B11 | low | patch | The explicit provider runner hardcodes checkout/distro/CLI, so another checkout cannot reproduce it. Derive checkout paths and allow narrow local test-tool settings while preserving fixed local project/container validation and no hosted target. |
| R1-E1 | medium | patch | finish returns ready before checking supplied bytes; retry uses the recorded digest independently, so changed contentBase64 gets ready success. Project retained file hash/size to the service and validate optional bytes before replay, preserving byte-free replay without old proof. |
| R1-E2 | low | patch | Reload success checks epoch, but its catch checks session view only; same-session edits can receive an obsolete reload error. Apply the existing epoch fence to that catch. |
| R1-V1 | medium | patch | Pre-verified gap: replacing items[0] with items[-1] passed all33 document tests because replacement fixture sections have one item. Use multiple items and assert both persisted first IDs. |

## Verification

Run document/generation tests, real local SQL/RLS/Storage checks, Save/recovery/reflow/keyboard browsers and final full pytest. Repeat existing browsers for shared UI/session changes. Verify owner/gate negatives and exact migration/grants/advisors before hosted approval. Preserve historical 481 passed/one skip and 28/33/11 browsers as baseline.

Parent verification after loop 1: complete baseline diff and re-derived delta read; 514 pytest passed/one inherited skip/one existing warning (50.19s), 23 Save browsers and28/33/11 shared browsers passed, actual provider45/pgTAP23/SQL-cron12 passed. Lint/advisors clean. Final physical-file/backup and hosted gates remain unexecuted. Fresh three-layer review follows.

Final patch verification: 529 passed/one inherited skip/one existing warning (92.30s); Save browser25; actual provider47, pgTAP23, SQL/cron/concurrency18 and expiry-fairness4 passed. Schema lint/advisors and19 unsigned configured startup checks passed. No new model calls/allowance mutations, hosted change or deployment. All29 review findings individually triaged, no deferred findings; physical-file/backup and hosted approval gates remain separate.

### Hosted acceptance correction — 17 November 2026

Hosted schema/bucket/verifier/cron were already installed, contrary to the older
status narrative above. An existing interrupted acceptance and a fresh read-only
probe demonstrated JWT-keyed REST CDN caching bypassing the backend/pending-read
marker after a successful internal file read. Local correction preserves the
frozen ownership/explicit-Save semantics: uncached S3 session-token GET with the
same user JWT and public legacy anon key, existing gate and lifecycle checks;
deny REST reads/metadata and retain registered cleanup. Botocore supplies standard
SigV4 signing. The exact migration and separate hosted approval scope are in
`save-acceptance.md`. Final focused checks: Python51, browser25, pgTAP15 and real
local provider50 passed. No new inference or hosted mutation in this session.

The student subsequently approved the exact hosted package with “ja godkjenner”.
Migration `20261117173439` applied the approved additional SQL; hosted32 and
normal-server30 passed, and normal local Save is enabled. Model allowances remain
byte-identical. Earlier physical-file/retention/release acceptance limits remain.
