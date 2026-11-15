---
title: Evaluate generated content against known sources
type: feature
created: 2026-11-15
status: draft
route: dispatch
story_key: 2-6-evaluate-generated-content-against-known-sources
baseline_commit: dec0683dca9888aa04fcb0635d6e10421c7d71e6
review_loop_iteration: 0
context: [.docs/implementation-artifacts/epic-2-context.md, .docs/implementation-artifacts/content-evaluation.md]
---

<frozen-after-approval reason="human-owned intent; approval and new live allowance are pending">

## Intent

**Problem:** Story 2.5 proves bounded generation and reference identity, but not factual support or coverage of important source concepts.

**Approach:** Pre-register three distinct self-authored sources and five concepts/locations each, generate through the production extraction/model/resolution components, and assess actual content against those sources. Separately test misleading subject context and insufficient evidence. Correct observed defects and recheck within an explicitly approved allowance.

## Boundaries & Constraints

**Always:** Preserve Story 2.5's model/data/output/deadline controls, receipts, authority, transient user data and historical evidence. Freeze the corpus and rubric before inference. Audit all returned items semantically; keyword matches and synthetic adapters cannot establish live quality. Keep unsupported claims, wrong references and omissions separate. Record both failures and corrections without replacing initial results.

**Never:** Run live calls before new approval, reset the actual budget, increase the USD 5 global ceiling, reuse the exhausted four-call smoke allowance, hidden retries, automatic model switching, model-as-judge calls, private course material, real account/email/password operations, hosted changes, deployment or unrelated features.

## I/O & Edge-Case Matrix

| Scenario | Given / when | Then / failure handling |
| --- | --- | --- |
| Three sources | Given registered paste, UTF-8 file and readable PDF, when generated | All four sections checked; at least 4/5 concepts covered per document, all checked claims supported and references substantively correct; record each failure |
| PDF locations | Given readable physical pages 1/3/5 and blank 2/4, when extracted and cited | Visible text matches extraction, physical references preserved; no facts attributed to blank pages |
| Subject conflict | Given source A and conflicting subject, when generated | Source facts prevail; conflicting assertions do not appear as learning facts |
| Insufficiency | Given readable punctuation without factual evidence, when generated | No invented items; four empty sections with specific insufficiency explanations |
| Costs/errors | Given approved evaluation grant and existing global ledger, when dispatch attempted | Consume grant and durable global reservation first; failed/uncertain attempts count; stop on exhausted/corrupt/blocked state, with no retry/refund |
| Recheck | Given an observed defect, when a minimal fix is made | Add synthetic regression, preserve before/after evidence, rerun affected cases within allowance; unresolved failures remain explicit |

</frozen-after-approval>

## Open Questions

1. Approve the concrete plan and new live allowance: recommended **up to eight additional evaluation attempts**, five initial cases plus at most three explicit rechecks, reserving at most **USD 0.40 additional within the existing USD 5 ceiling**; or approve offline preparation only, leaving live quality acceptance pending. This permission is separate from Story 2.5's exhausted four smoke checks. Existing provider/model/data/bounds approvals remain unchanged.

## Code Map

- `app/services/extraction.py`: reuse `prepare`, `extract_text`, `extract_pdf_result`; actual PDF uses contained `app/adapters/pdf.py::extract_pdf`.
- `app/adapters/model.py`: reuse `request_bytes`, `OpenAIModel`, safe usage accounting and existing instructions. `app/services/generation.py::resolve` maps canonical references; identity is not factual support.
- `app/services/model_budget.py`: existing USD 5 durable accounting and anomaly latch stay authoritative; keep `liveChecks=4` and its smoke enforcement unchanged.
- `scripts/generation_smoke.py`: historical smoke only, do not extend or rerun. New evaluation runner accepts fixed synthetic cases only, never arbitrary files or app credentials beyond the existing model configuration.
- `tests/test_generation.py`, `tests/pdf_fixtures.py`: reuse injected transport/contract patterns; old encoded-font PDF is extraction evidence, not proof of visible glyph fidelity.

## Tasks & Acceptance

**Execution:**
- [ ] `tests/content_fixtures.py` — encode the exact registered corpus, fixed settings and fifteen concept/location expectations; generate a genuinely readable, ordinary-font PDF and verify physical pages before inference.
- [ ] `scripts/content_evaluation.py` — default offline preflight; explicit live opt-in, one selected case per invocation, 60s deadline, bounded adapter/resolver and numeric-only safe errors. Persist only whitelisted synthetic evidence, excluding credentials, receipts and raw provider envelopes.
- [ ] `scripts/content_evaluation.py` — implement one fixed-path, content-free, exclusive-created evaluation allowance `.model-budget-evaluation-2-6.json` after approval; maximum eight attempts across restarts. Durably consume it before the existing global reservation; never compensate/refund either on uncertain failure. Do not initialize the global ledger or change smoke counters. Concurrent invocations fail safely under a nonblocking lock.
- [ ] `tests/test_content_evaluation.py` — test fixture locations, corrupt/missing/exhausted grant, concurrent/restarted attempts, no opt-in/no dispatch, grant/global reservation ordering and failure accounting using temporary paths and injected transport only. Verify the four-smoke limit still rejects a fifth smoke.
- [ ] `.docs/implementation-artifacts/content-evaluation.md`, `content-evaluation-evidence/` — retain fixture/implementation revisions, settings, latency/usage/cost, projected synthetic outputs and item-level support/reference judgments; score concept coverage and record failure categories/corrections separately.
- [ ] `app/adapters/model.py`, `tests/test_generation.py` — change instructions/behavior only for an observed quality defect, add focused regression and recheck affected live cases; if shared instructions change, all five cases require final-version evidence before claiming acceptance.
- [ ] `README.md` — link offline/live evaluation operation and clearly state what the controlled corpus establishes and which real-document/platform gates remain open.

**Acceptance Criteria:**
- Given completed evaluation, when acceptance is recorded, then all three documents individually meet 4/5 coverage, all audited claims/references pass, both negative cases pass and no required final-version evidence is missing.
- Given exhausted allowance, technical failure or an unresolved defect, when reporting status, then preserve evidence and mark acceptance incomplete instead of inventing a pass or silently increasing costs.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

Offline: `uv run --group pdf-experiment pytest tests/test_content_evaluation.py tests/test_generation.py -q`; runner offline preflight; PDF render/text comparison; `git diff --check`. After code fixes, run the affected suite and one final full pytest run. Browser suites repeat only if UI/session behavior changes. Live: execute only the approved named cases/rechecks and account for every attempted call. BMAD review precedes completion. Existing 422 passes/one skip and 28/33/11 browser scenarios remain historical baseline, not new results.
