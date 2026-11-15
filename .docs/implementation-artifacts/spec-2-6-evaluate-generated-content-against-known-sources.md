---
title: Evaluate generated content against known sources
type: feature
created: 2026-11-15
status: done
route: dispatch
story_key: 2-6-evaluate-generated-content-against-known-sources
baseline_commit: dec0683dca9888aa04fcb0635d6e10421c7d71e6
review_loop_iteration: 0
context: [.docs/implementation-artifacts/epic-2-context.md, .docs/implementation-artifacts/content-evaluation.md]
---

<frozen-after-approval reason="student approved plan and eight additional evaluation attempts on 2026-11-15">

## Intent

**Problem:** Story 2.5 proves bounded generation and reference identity, but not factual support or coverage of important source concepts.

**Approach:** Pre-register three distinct self-authored sources and five concepts/locations each, generate through the production extraction/model/resolution components, and assess actual content against those sources. Separately test misleading subject context and insufficient evidence. Correct observed defects and recheck within an explicitly approved allowance.

**Approved decision (2026-11-15):** After explanation of five initial cases and up to three rechecks, the student replied “ok greit”. Approve this plan and at most eight additional automated evaluation attempts, each reserving USD 0.05, at most USD 0.40 additional within the existing USD 5 ceiling. Preserve the exhausted four-smoke allowance and existing provider/model/data/bounds decisions. No purchases or hosted changes.

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

## Code Map

- `app/services/extraction.py`: reuse `prepare`, `extract_text`, `extract_pdf_result`; actual PDF uses contained `app/adapters/pdf.py::extract_pdf`.
- `app/adapters/model.py`: reuse `request_bytes`, `OpenAIModel`, safe usage accounting and existing instructions. `app/services/generation.py::resolve` maps canonical references; identity is not factual support.
- `app/services/model_budget.py`: existing USD 5 durable accounting and anomaly latch stay authoritative; keep `liveChecks=4` and its smoke enforcement unchanged.
- `scripts/generation_smoke.py`: historical smoke only, do not extend or rerun. New evaluation runner accepts fixed synthetic cases only, never arbitrary files or app credentials beyond the existing model configuration.
- `tests/test_generation.py`, `tests/pdf_fixtures.py`: reuse injected transport/contract patterns; old encoded-font PDF is extraction evidence, not proof of visible glyph fidelity.

## Tasks & Acceptance

**Execution:**
- [x] `tests/content_fixtures.py` — encode the exact registered corpus, fixed settings and fifteen concept/location expectations; generate a genuinely readable, ordinary-font PDF and verify physical pages before inference.
- [x] `scripts/content_evaluation.py` — default offline preflight; explicit live opt-in, one selected case per invocation, 60s deadline, bounded adapter/resolver and numeric-only safe errors. Persist only whitelisted synthetic evidence, excluding credentials, receipts and raw provider envelopes.
- [x] `scripts/content_evaluation.py` — implement one fixed-path, content-free, exclusive-created evaluation allowance `.model-budget-evaluation-2-6.json` after approval; maximum eight attempts across restarts. Durably consume it before the existing global reservation; never compensate/refund either on uncertain failure. Do not initialize the global ledger or change smoke counters. Concurrent invocations fail safely under a nonblocking lock.
- [x] `tests/test_content_evaluation.py` — test fixture locations, corrupt/missing/exhausted grant, concurrent/restarted attempts, no opt-in/no dispatch, grant/global reservation ordering and failure accounting using temporary paths and injected transport only. Verify the four-smoke limit still rejects a fifth smoke.
- [x] `.docs/implementation-artifacts/content-evaluation.md`, `content-evaluation-evidence/` — retain fixture/implementation revisions, settings, latency/usage/cost, projected synthetic outputs and item-level support/reference judgments; score concept coverage and record failure categories/corrections separately.
- [x] `app/adapters/model.py`, `tests/test_generation.py` — change instructions/behavior only for an observed quality defect, add focused regression and recheck affected live cases; if shared instructions change, all five cases require final-version evidence before claiming acceptance.
- [x] `README.md` — link offline/live evaluation operation and clearly state what the controlled corpus establishes and which real-document/platform gates remain open.

**Acceptance Criteria:**
- Given completed evaluation, when acceptance is recorded, then all three documents individually meet 4/5 coverage, all audited claims/references pass, both negative cases pass and no required final-version evidence is missing.
- Given exhausted allowance, technical failure or an unresolved defect, when reporting status, then preserve evidence and mark acceptance incomplete instead of inventing a pass or silently increasing costs.

## Implementation Notes

Parent owns real model execution and semantic assessment after independent offline verification. The implementation agent must not read `.env`, initialize/read/write actual budget or grant files, or perform live/provider requests; it implements the runner and exercises temporary ledgers/injected transports only. It returns with live evidence/report tasks explicitly pending for the parent. Commit/fingerprint the registered corpus before the first live attempt. This is a continuation of the existing rendered build, not a new planning run.

Parent read the complete baseline diff and completed 453 passing tests/one inherited skip (45.43s), offline preflight and five-page PDF visual/text comparison. Registered corpus/runner were committed before all five authorized live cases. Semantic audits checked 59 items/70 references; A/B/C each cover 5/5 concepts, D rejects conflicting subject facts and E explains all four empty sections. No quality defect required prompt/application changes or rechecks. Five of eight evaluation attempts consumed, USD 0.25 additional reserved; original smoke count remains four and global reservation USD 0.45. See the report for raw projected outputs, exact support excerpts, costs and unchanged acceptance gates. A pre-live deadline refinement and PDF binary attribute preserve the approved bounds/fixture bytes.

## Spec Change Log

## Review Triage Log

Three independent layers reported before triage: blind review supplied twelve findings, verification review supplied two trusted gaps, edge review supplied none. Each finding is graded separately; no intent gap, frozen-block change or deferral is needed.

| ID | Verdict | Route | Verified evidence / smallest correction |
| --- | --- | --- | --- |
| B1 | medium | patch | The existing collision regression spends both allowances before discovering an existing destination. Preflight that destination under the grant lock before provider/global reservation; preserve existing evidence and never retry. |
| B2 | medium | patch | write_json_exclusive writes directly to its final name; interruption can expose truncated final evidence. Publish a fully flushed temporary file atomically without replacing an existing result. |
| B3 | medium | patch | Evidence writes fsync the file but omit durable directory publication, unlike the existing budget replacement. Make publication durable using the existing Windows/POSIX patterns while preserving no-overwrite behavior. |
| B4 | medium | patch | register creates the final directory before either required write, so a failed PDF/JSON write leaves an unretryable partial directory. Publish complete registration atomically and clean only its owned temporary directory on failure. |
| B5 | low | patch | verify_registration reads unbounded local files before its length check. Bound reads before allocation for JSON and the fixed synthetic PDF; a direct guard avoids memory exhaustion after local artifact corruption. |
| B6 | false | reject | The claimed strict 60-second process-exit guarantee is not the generation contract: owned filesystem/transport cleanup may outlast a generation deadline. The original deadline is checked before/after reservation, bounds provider waiting and is checked after resolution; the executed slow-reservation regression proves no late dispatch. No CLI wall-clock exit promise or late validated generation is established by this finding. |
| B7 | medium | patch | Error 9 alone cannot distinguish pre-dispatch expiry from an uncertain provider timeout. Record booleans for completed global reservation and provider attempt start; the latter is not proof of upstream receipt/billing. |
| B8 | low | patch | The broad exception branch labels an unexpected runner failure with whichever provider/output stage was active. Separate expected model/budget/validation/cancellation cases from safe internal error 10, without exception text. |
| B9 | medium | patch | The preregistration Git commit preserves the approved rubric, but the runtime fingerprint excludes it and therefore cannot detect a subsequent rule edit. Include the stable rubric prose in registration hashes, excluding mutable results/status tables; preserve the old registration and its pre-live commit evidence. |
| B10 | medium | patch | Parent completeness/hash checks passed, but no committed regression enforces assessment links/excerpts against observations. Add an offline consistency test for hashes, every item/reference, exact excerpts and coverage IDs; this checks evidence integrity, not semantic truth. |
| B11 | medium | patch | The concurrency test uses separate instances/threads, while the documented CLI uses processes. Add an isolated subprocess lock/release test, including owned child termination, with temporary ledgers only. |
| B12 | medium | patch | The explicit CancelledError path has no regression. Cancel an injected transport after entry and assert consumed allowances, safe retained evidence and released grant ownership. |
| V1 | medium | patch | Trusted broken-verification gap: the projection test checks section/reference keys but no supplied textual fields, so omitted practice answers still pass. Assert every textual field in returned and persisted projections. |
| V2 | medium | patch | Trusted regression gap: successful main --live case/phase forwarding never reaches the tested real runner. Parametrize all selected cases with temporary grants and injected transport, checking request content and persisted case/phase. |

All surviving findings were independent corrections/test gaps within the approved evaluation boundary. The same implementation agent applied all thirteen patches; B6 was rejected, and nothing deferred. Parent read the patched runner/tests/docs and completed final verification: **481 passed/one inherited skip**, 46.99s, including **59 evaluation controls**. Offline registration and original artifact hashes passed. The new rubric-aware registration is offline-only; historical five-call evidence, corpus, request bodies, prompt, production code and actual allowance counts remain unchanged. No further inference was performed.

## Verification

Offline: `uv run --group pdf-experiment pytest tests/test_content_evaluation.py tests/test_generation.py -q`; runner offline preflight; PDF render/text comparison; `git diff --check`. After code fixes, run the affected suite and one final full pytest run. Browser suites repeat only if UI/session behavior changes. Live: execute only the approved named cases/rechecks and account for every attempted call. BMAD review precedes completion. Existing 422 passes/one skip and 28/33/11 browser scenarios remain historical baseline, not new results.
