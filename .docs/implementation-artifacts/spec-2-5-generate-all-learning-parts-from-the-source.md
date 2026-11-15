---
title: Generate all learning parts from the source
type: feature
created: 2026-11-15
status: done
route: dispatch
story_key: 2-5-generate-all-learning-parts-from-the-source
baseline_commit: 5737bbf45902f3621fc90ecb8ab62e09eecbf100
review_loop_iteration: 0
context: [.docs/implementation-artifacts/epic-2-context.md, .docs/implementation-artifacts/model-decision-2-5.md, .docs/implementation-artifacts/generation-protocol-2-5.md]
---

<frozen-after-approval reason="student approved the plan and recommendations on 2026-11-15; API setup is required before implementation">

## Intent

**Problem:** The workspace previews sources but cannot generate learning material.

**Approach:** One action validates the current source if necessary, then makes one bounded model request producing all four learning sections and a signed generation receipt.

**Approved decisions (2026-11-15):** OpenAI `gpt-6-luna`, Standard, reasoning `none`; USD 5 total usage ceiling with USD 0.05 reservations and at most four automated synthetic live checks; global processing, `store:false`, explicit cache mode without breakpoints, no training opt-in, normally up to 30-day provider abuse retention with exceptions; permitted nonsensitive material only. Generation: 60s server deadline, 70s browser wait after extraction, 8,000 output tokens, 256 KiB provider response and protocol item limits. Funding/taxes remain separate; no automatic purchases. The student needs API setup help; local credentials/billing/model access are not yet established.

## Boundaries & Constraints

**Always:** Resolve all five model gates before implementation. Preserve Story 2.4's limits, physical references, coverage, transient inputs and authentication fences. Verify signed source acceptance before dispatch. Resolve references and assign identities server-side. Validate the whole output before publishing; explain insufficient evidence per section. Source/subject are untrusted data; subject never supplies facts. Preserve every input/setting on technical failure. Use ordered invalidation and bounded metadata-only workspace authority; signature validity alone never authorizes Save. Keep private payloads/receipts out of logs, storage, caches and demo transport.

**Never:** Demo fallback, hidden retries, AI calls on navigation, durable unsaved content, Save/library/database work, OCR, account/email/password operations, hosted changes, funding or deployment. Preserve prior approvals and test history.

## I/O & Edge-Case Matrix

| Scenario | Given / when | Then / safe failure |
| --- | --- | --- |
| Generate | Given accepted paste/file/PDF and selected settings, when clicked once | One model call; four validated sections or per-section insufficiency; server-resolved paragraph/physical-page references, coverage and receipt |
| Failure | Given refusal, timeout, malformed/truncated/oversized output, unknown reference or provider failure | No partial bundle/receipt; retain text/file/settings, expand controls and offer explicit retry |
| Authority | Given changed source/settings, reset, newer generation or late reply | Revoke old authority; ordered acknowledgements and completion fences prevent revival, including before signature expiry |
| Session | Given logout, expiry, denial, rotation, restart or pagehide | Clear private display; reject old proof/receipt and late completion; fresh access cannot restore old drafts |
| Resources | Given duplicate/saturated/slow/disconnected request or exhausted budget | Bound admission/read/transport/cleanup; reject safely before charge where possible; retain uncertain charge reservations |
| Practice | Given complete/insufficient parts, when tabs/reveal/navigation/edit visibility are used | Independent positions/reveals, no AI calls, safe text rendering and accessible empty states |

</frozen-after-approval>

## Readiness Gate

Resolved 2026-11-15 12:14: student reports billing ready; ignored local key is present and authenticated GET `/v1/models/gpt-6-luna` returned 200 with the expected model ID. No inference was called and no secret emitted. Existing plan approval stands; proceed without another approval. The frozen block's setup statement records the earlier state. No automatic accounts, funding or hosted changes.

## Code Map

- `app/api/sources.py`, `app/services/extraction.py`: bounded extraction and canonical units; add acceptance proof without retaining source content.
- `app/api/auth.py`, `app/services/sessions.py`: reuse protected/current_session/authenticated_async/live_session/session_view_matches; preserve non-touching status and logout retry.
- `app/contracts/learning.py`: existing bundle/reference/insufficiency validation; keep demo contract compatible.
- `app/static/workspace.js`, `app.js`: extend workspace observation/invalidation fences; reuse demo rendering algorithms without its fixture bootstrap.

## Tasks & Acceptance

**Execution:**
- [x] `app/contracts/generation.py`, `sources.py`, `learning.py` — strict acceptance/generation/receipt DTOs, bounded model output and canonical hashing contract.
- [x] `app/services/workspaces.py`, `receipts.py`, `app/api/workspaces.py` — implement shared authority/mutex, monotonic invalidation, source proof and generation receipts per protocol; expose reusable future Save validation only.
- [x] `app/api/sources.py`, `app/services/sessions.py` — integrate proof issuance and lifecycle cleanup; old extraction/authority guarantees remain.
- [x] `app/adapters/model.py`, `app/services/generation.py`, `app/api/generation.py` — one bounded structured request, complete validation, reference resolution and atomic fenced publication.
- [x] `app/services/model_budget.py`, `scripts/model_budget.py`, `.gitignore` — persist content-free reservations, explicit one-time initialization, fail closed on missing/corrupt/exhausted ledger; no restart reset.
- [x] `app/config.py`, `main.py`, `.env.example`, `pyproject.toml`, `uv.lock` — disabled-by-default model settings, injectable adapter/authority, private errors/headers and direct locked HTTP dependency.
- [x] `app/static/workspace.html`, `workspace.js`, `styles.css` — one primary action, optional preview, four tabs, collapsed controls, retry and ordered invalidation; preserve selected files on errors.
- [x] `tests/test_generation.py`, `test_sources.py`, `test_auth.py`, `sources_browser_app.py`, `browser-sources.cjs` — cover every matrix row with synthetic adapters, source-proof tampering, cross-session receipts, cancellation, budget restart and invalidation races.
- [x] `README.md`, `.docs/implementation-artifacts/generation-acceptance.md` — record executed checks and separate live fidelity, representative-PDF and target-platform gates.

**Acceptance Criteria:**
- Given no model configuration, when demo or workspace opens, then demo stays credential-free and private generation fails clearly without a fabricated result.
- Given passing offline checks and explicitly approved live access, when up to four synthetic smoke calls run, then record actual usage/latency/reference observations; full three-document quality acceptance remains Story 2.6.

## Implementation Notes

2026-11-15: Resumed the existing build after API setup; no rerender or replanning. Spec reread from disk; approved-block SHA-256 (UTF-8/LF including markers) remains `2b453bfa703d032fc54784412a7239b435ed4be9954e5f820f3e4fb563395301`. Preserved baseline. Model metadata access verified without inference; billing is student-reported. Price/cache docs rechecked unchanged. Live smoke checks remain bounded by the approved four-call limit and follow passing offline checks; no credentials/content in diagnostics.

Implementation agent completed production/UI and synthetic regressions. Parent read the complete baseline diff including new files and checked all nine tasks/six matrix rows against executed evidence. Existing LearningBundle validation is reused unchanged; bounded live DTOs validate before it. A credential-leaking draft session claim was replaced by a non-authorizing hash binding before tests/live. A deterministic regression fixed a pre-existing auth validation-owner cancellation window exposed by the larger suite; pre-success cancellation still revokes authority.

Parent locked sync passed; full suite **383 passed/one inherited skip**, 83.05s, including **183 auth/63 source/75 generation** without skips. Browsers **27 source/generation, 33 auth, 11 demo/21 demo requests** passed. Both 320px/200% images inspected. Staged whitespace corrected; no key in diff; prior approved source/logout blocks unchanged. All four authorized synthetic live cases returned 200/completed/exact model and validated bundles, including insufficiency and physical PDF references 1/3 with unreadable 2/4. Actual estimated usage USD **0.0008135**, durable reservations USD **0.20**. Live-check allowance exhausted at four; no further automated inference. See [acceptance evidence](generation-acceptance.md); quality acceptance remains Story 2.6.

## Spec Change Log

## Review Triage Log

All three independent layers reported before triage. Findings are graded separately before grouping. Parent probes used injected adapters and temporary ledgers only; no further live inference.

| ID | Verdict | Route | Evidence / smallest correction |
| --- | --- | --- | --- |
| B1 | medium | patch | Parent reproduced both an already-cancelled and expired-deadline generate call making one synthetic model call/reservation. Check cancellation/deadline before reservation and again before network dispatch. |
| B2 | high | patch | Parent reproduced Windows contention raising PermissionError before lock error normalization; unexpected usage left blocked=false and a subsequent reservation succeeded. Persist fail-closed blocking despite contention, normalize lock errors and prevent later dispatch across instances/restart. |
| B3 | high | patch | Parent injected an incomplete HTTP-200 envelope reporting 266,241 input tokens: API failed safely but ledger blocked remained false. Observe reported usage before completion/schema/model rejection; propagate only safe usage metadata, never provider content. |
| B4 | medium | patch | Parent configured a 20ms deadline and a briefly cancellation-resistant adapter: HTTP 504 arrived after 207ms. Bound the HTTP waiter independently; retain actual-work admission until cleanup and fence all late publication. |
| B5 | medium | patch | Request schema allows eight model warnings while server rejects extraction notices plus warnings above eight. Supply the remaining warning allowance for accepted sources so a schema-valid PDF response is not rejected for hidden server notices. |
| B6 | medium | patch | ModelOutput permits items plus an insufficiency explanation; renderLearning only displays explanations for empty arrays. Show accepted per-section qualifications with nonempty items too. |
| B7 | medium | patch | Generated English inherits document lang=nb; there are no output language attributes. Mark generated prose with the selected language and retain nb for Norwegian controls/reference metadata. |
| B8 | low | patch | materialOpen(true) hides the only disclosure control and its click handler only opens. Provide a reversible existing toggle without clearing results or invoking AI. |
| B9 | medium | patch | Primary generation is type=button; secondary extraction is the form submit action. Enter in the subject field therefore only checks the source. Make generation the primary submit and keep explicit source checking separate. |
| B10 | low | patch | README line 42 still says generation comes later; protocol/setup/model documents retain operative pre-implementation wording. Label historical planning passages and update current guidance without altering prior evidence. |
| E1 | medium | patch (B1) | Independent edge trace finds synchronous preflight/reservation can consume the deadline before dispatch. Same missing before-dispatch deadline check as B1; preserve this extra trigger in its regression. |
| V1 | medium | patch | Trusted verification review found every provider-reference assertion uses u1; replacing resolution with units[u1] still passed all 75 generation tests. Add exact u2 and mixed u1/u2 canonical ID/physical-page assertions across all four sections. |

Grouping: only B1/E1 share one root. B2/B3 protect distinct anomaly paths and remain separate. All findings are concrete corrections inside the approved intent; no new public surface, unresolved intent, frozen-spec amendment or deferral is needed. The same implementation agent applied the patches; the parent completed full offline verification. The four-call live allowance remains exhausted.

Follow-up edge review after patches found one additional concrete issue:

| ID | Verdict | Route | Evidence / smallest correction |
| --- | --- | --- | --- |
| F1 | medium | patch | A temporary-ledger probe with a 50ms HTTP deadline and 300ms reservation stall replied only after 350ms because filesystem calls run on the event loop; invalidation also waits. Offload owned budget filesystem work under bounded admission, retain permits until the worker actually ends, and recheck deadline/cancellation plus current session/workspace before network dispatch after the new await. |

All thirteen findings are resolved. Budget I/O now uses two bounded workers without a queue; cancellation retains ownership until actual cleanup, and pre-dispatch checks reject expired/revoked source authority after the await. Six new regressions cover stalled reservation/usage observation, responsive invalidation, logout/expiry during reservation and repeated cancellation without worker-slot release. The parent read the patch and completed the full verification below. No finding was deferred and the approved block is unchanged.

## Design Notes

Approved implementation is complete. Normal local use is enabled with the existing ignored credentials and durable ledger; the four automated smoke calls are exhausted. No further automated live inference or budget reset was performed.

## Verification

`uv sync --locked --group pdf-experiment`; `uv run --group pdf-experiment pytest`; `node tests/browser-sources.cjs`; `node tests/browser-auth.cjs`; `node tests/browser-demo.cjs`; `git diff --check`. Require all existing regressions plus the new matrix. Inspect 320px/200% layout and keyboard flow; retain broader screen-reader/hosting gates. Record actual new results separately from the inherited 306 passed/one skip and 19/33/11 browser scenarios.

Final parent run after all review patches: **422 passed, one inherited platform skip**, 90.163s; **183 auth, 63 source and 114 generation** tests passed without skips. Final browsers: **28 source/generation, 33 auth and 11 demo / 21 demo requests** passed. Both final reflow images were inspected. Normal local server restarted with existing ignored auth/key and one worker (PID 30048); **10 unsigned startup checks** passed with no inference and no budget change. New login is required after restart. Historical live observations above precede the review patches; no post-patch live retest is claimed. Broader content quality remains Story 2.6.
