---
title: Synchronize practice progress across devices
type: feature
created: 2026-11-17
status: done
route: dispatch
review_loop_iteration: 0
story_key: 3-3-synchronize-practice-progress-across-devices
baseline_commit: f7178fbaf10d022215c75a57afe6e31a4aa089a9
context: [.docs/implementation-artifacts/epic-3-context.md]
---

<frozen-after-approval reason="student requested the agreed next story with ta neste steg; implementation and necessary existing-test-project integration authorized">

## Intent

Automatically persist independent flashcard/quiz positions for an already-saved generation. Another authenticated visit resumes acknowledged progress with answers hidden. Prevent a stale view from overwriting newer progress.

## Boundaries & Constraints

Reuse existing FastAPI/plain-JS, sessions/CSRF/session-view checks, backend gate, user-JWT RPC transport, owner RLS and ready lifecycle. Stable item IDs, not indices. Never autosave source/settings/results or unsaved generations. No model calls, new accounts, paid services, deletion UI or public deployment. Implementation agent stays local; parent integrates the reviewed migration into the existing test project and restarts/verifies the local app.

Atomic writes lock the document row shared with Save/replacement/deletion, validate owner/ready/current generation and both item IDs, and compare the independent progress revision. Durable owner-bound mutation IDs bind the exact canonical request and recorded outcome. Identical admitted retries replay without updating again; changed payload reuse fails. Enforce current ready generation before replay and replay before checking the old expected progress revision. Old generations/deleting/unknown targets never recreate rows. Keep replay records through restart; reference owner/document without cascading old-generation identity when Save replaces it.

Browser writes serialize and coalesce navigation. Freeze mutation ID/payload until its outcome is known. One automatic retry for uncertain transport, same ID/payload; then explicit retry/refetch. A conflict blocks writes until a successful explicit fresh fetch; never silently rebase stale intent. Fetch restores positions and hides answers; failure keeps the conflict. A changed generation requires reopening the saved document. Fence responses/timers by session/document/generation and active-workspace epoch; preserve tab reveals during ordinary navigation. Only acknowledged progress is guaranteed after leaving/restart.

## I/O & Edge-Case Matrix

| Scenario | State | Expected behavior |
|---|---|---|
| Saved navigation | Valid current generation | Both IDs sync with acknowledged revision; pending/saved/failure status |
| Unsaved/edited/new result | No matching saved generation | No progress write or implicit content Save |
| Rapid navigation | Request in flight | One serialized write then latest coalesced intent; retain current visible position |
| Lost reply | Mutation may have committed | Retry exact ID once; one revision advance, then explicit recovery |
| ID reuse | Changed request | Reject without mutation |
| Two views | Both read revisionN | One wins; stale view cannot overwrite; show “Fremdriften er endret på en annen enhet” |
| Refresh conflict | Explicit “Hent siste fremdrift” | Restore latest IDs/revision with hidden answers; failed fetch remains blocked |
| Fresh navigation | After successful refresh | Backwards navigation is valid; new revision/ID |
| Lifecycle | Replacement/deletion races, wrong owner/generation/item/session | Reject; no resurrection or leaked private metadata |
| Late completion | Reset/edit/open/logout/new owner | Ignore old response and queued work |
| Restart/other visit | Same authenticated owner | Reopen acknowledged positions/revision, answers hidden, zero inference |
| Empty section | No cards or quiz | Corresponding ID null; no 1-of-0 or invented progress |

</frozen-after-approval>

## Code Map

- `app/static/workspace.js`: savedTarget, positions, Save success, openDocument, generation/reset/session cleanup and practice navigation; library epochs must not silently discard valid same-document acknowledgments.
- `app/{api,contracts,services}/documents.py`, `adapters/documents.py`: bounded private pipeline, strict owner-free DTOs, backend-gated user-JWT RPC transport and admission pattern.
- `app/main.py`, `api/private.py`: router/state wiring, private no-store headers and safe errors.
- `supabase/migrations/20261115214610_save_consistent_private_snapshot.sql`: progress revision starts at1; Save locks document and replaces progress atomically. Existing reload needs atomic progress revision alongside positions. Latest library RPC reads current positions.
- `tests/test_documents.py`, `documents_browser_app.py`, `browser-{documents,library}.cjs`: synthetic ports and browser fixtures. `tests/library_provider_acceptance.py` has guarded local stack helpers; SAVE_TEST_WSL_DISTRO=SUREUbuntu. Do not repeat its broad failing predecessor to diagnose unrelated gaps.

## Tasks & Acceptance

- [x] Add strict bounded progress read/write DTOs/API (`app/api/progress.py`) and service using existing auth/transport. Mutations cannot accept owner IDs or caller-selected RPC names.
- [x] CLI-create invoker/RLS migration with durable request-bound replay records, document lock/CAS/membership/lifecycle checks, and atomic reload progressRevision. Initial Save starts revision1; stale Save replay must not silently adopt a newer revision.
- [x] Add serialized/coalesced JS autosync, visible statuses, exact retry, conflict/refetch blocking and cleanup/late-response fences. Preserve Save/library and ordinary tab/reveal behavior.
- [x] Add meaningful focused Python/browser/pgTAP and real local concurrent-RPC verification, including one actual same-revision race and lost successful reply. Only synthetic models/accounts local; no hosted changes by implementation agent.
- [x] Update concise acceptance record, README and sprint/spec tasks with exact executed results and any unresolved limits.

Given two authenticated views of one saved generation, when one acknowledges progress, then the other's old revision cannot overwrite it; explicit fetch is required before further persistence. Opening on a fresh visit restores acknowledged IDs without inference.

## Implementation Notes

18 November completion: reviewed implementation integrated into the existing test
project (hosted migration20261118142904); local app restarted on port8000,
worker10088. The stop/resume notes below are historical. Spec done/sprint review;
Story3.4 deletion is next. No new hosted accounts, real inference or deployment.

18 November: the student explicitly resumed with “kan vi fortsette”. Continue
the preserved edits and original baseline. The historical stop below is revoked;
finish local verification/review and then the authorized existing-test-project
integration. Reuse the implementation agent; keep additional contexts/checks focused.

Session stopped at the student's explicit request on17 November (4% remaining
five-hour allowance). Implementation agent was interrupted. Work is partial and
unreviewed: preserve current edits and resume them, not a new implementation.
Last executed baseline was66 document/library Python tests; no completed progress
acceptance is claimed. No hosted progress migration or normal-server restart.
Contract: POST /api/v1/progress/read and /write; write uses mutationId,
expectedProgressRevision and both positions; success returns progressRevision.
Migration file20261117184855 exists locally. Next: inspect the partial backend/JS,
finish progress-specific tests/SQL concurrency and one focused review before integration.

Decide routine implementation details autonomously within these constraints. Keep context/output small, capture full logs under ignored test-results, and run targeted checks. Existing hosted account credentials/configuration/budgets must remain untouched by the implementation agent. No production deadline increases for a test harness.

## Spec Change Log

## Review Triage Log

One focused edge-case review was used, with the parent auditing test evidence;
the broad forced-finding and separate gap-review contexts were omitted to respect
the student's five-hour allowance.

| ID | Verdict | Route | Evidence |
|---|---|---|---|
| E1 | medium, resolved | patch | Replacement retry reset intervening navigation/answers because its navigation counter was recaptured. Original-attempt private metadata now survives exact retries outside the wire payload and clears with the attempt lifecycle. Replacement-retry regression passed in final Save25 run. |

## Verification

18 November final: progress Python23, progress browser16, Save25/library21,
pgTAP36, real local RPC20, hosted23 and restarted normal-server16 passed.
Document/library Python66 remains the historical baseline. The extra old Save SQL
rerun was interrupted by infrastructure failure, not counted as a pass. User-approved
SUREUbuntu restart restored local services. Model budget files stayed byte-identical.
Exact commands/results and separate acceptance limits are recorded in
`progress-acceptance.md`. No hosted changes by the implementation agent.

Focused progress Python/browser/actual SQL concurrency; affected Save/library browsers. Broaden only for shared behavior changed by this story. Baseline: focused Python74, library21/Save25/source28, local SQL23+23/provider17, hosted library25/normal34. Historical broad provider failures remain unproven; never relabel them green.
