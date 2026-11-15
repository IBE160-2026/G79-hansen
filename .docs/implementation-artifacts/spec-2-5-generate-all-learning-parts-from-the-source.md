---
title: Generate all learning parts from the source
type: feature
created: 2026-11-15
status: draft
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

Approval recorded; do not request again. The student answered “Trenger hjelp med oppsett”. Keep draft/backlog until local key, billing and model access are established. Follow `model-setup-2-5.md`; no implementation/inference yet. Never paste secrets into chat or automatically create accounts, fund or change hosted settings.

## Code Map

- `app/api/sources.py`, `app/services/extraction.py`: bounded extraction and canonical units; add acceptance proof without retaining source content.
- `app/api/auth.py`, `app/services/sessions.py`: reuse protected/current_session/authenticated_async/live_session/session_view_matches; preserve non-touching status and logout retry.
- `app/contracts/learning.py`: existing bundle/reference/insufficiency validation; keep demo contract compatible.
- `app/static/workspace.js`, `app.js`: extend workspace observation/invalidation fences; reuse demo rendering algorithms without its fixture bootstrap.

## Tasks & Acceptance

**Execution:**
- [ ] `app/contracts/generation.py`, `sources.py`, `learning.py` — strict acceptance/generation/receipt DTOs, bounded model output and canonical hashing contract.
- [ ] `app/services/workspaces.py`, `receipts.py`, `app/api/workspaces.py` — implement shared authority/mutex, monotonic invalidation, source proof and generation receipts per protocol; expose reusable future Save validation only.
- [ ] `app/api/sources.py`, `app/services/sessions.py` — integrate proof issuance and lifecycle cleanup; old extraction/authority guarantees remain.
- [ ] `app/adapters/model.py`, `app/services/generation.py`, `app/api/generation.py` — one bounded structured request, complete validation, reference resolution and atomic fenced publication.
- [ ] `app/services/model_budget.py`, `scripts/model_budget.py`, `.gitignore` — persist content-free reservations, explicit one-time initialization, fail closed on missing/corrupt/exhausted ledger; no restart reset.
- [ ] `app/config.py`, `main.py`, `.env.example`, `pyproject.toml`, `uv.lock` — disabled-by-default model settings, injectable adapter/authority, private errors/headers and direct locked HTTP dependency.
- [ ] `app/static/workspace.html`, `workspace.js`, `styles.css` — one primary action, optional preview, four tabs, collapsed controls, retry and ordered invalidation; preserve selected files on errors.
- [ ] `tests/test_generation.py`, `test_sources.py`, `test_auth.py`, `sources_browser_app.py`, `browser-sources.cjs` — cover every matrix row with synthetic adapters, source-proof tampering, cross-session receipts, cancellation, budget restart and invalidation races.
- [ ] `README.md`, `.docs/implementation-artifacts/generation-acceptance.md` — record executed checks and separate live fidelity, representative-PDF and target-platform gates.

**Acceptance Criteria:**
- Given no model configuration, when demo or workspace opens, then demo stays credential-free and private generation fails clearly without a fabricated result.
- Given passing offline checks and explicitly approved live access, when up to four synthetic smoke calls run, then record actual usage/latency/reference observations; full three-document quality acceptance remains Story 2.6.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

Documentation only; external transfers and charges remain gated.

## Verification

`uv sync --locked --group pdf-experiment`; `uv run --group pdf-experiment pytest`; `node tests/browser-sources.cjs`; `node tests/browser-auth.cjs`; `node tests/browser-demo.cjs`; `git diff --check`. Require all existing regressions plus the new matrix. Inspect 320px/200% layout and keyboard flow; retain broader screen-reader/hosting gates. Record actual new results separately from the inherited 306 passed/one skip and 19/33/11 browser scenarios.
