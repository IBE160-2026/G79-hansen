# Story 2.5 generation acceptance

## Scope and historical evidence

This record separates offline protocol/UX verification from live model behavior.
The inherited Story 2.4 evidence remains 306 Python passes, one skip, and
19/33/11 source/auth/demo browser scenarios. Those counts are historical, not a
claim about this implementation. No source, generated prose, signed token,
credential or filename is recorded here.

The implementation adds ordered, metadata-only workspace authority; source
acceptance proofs; a single bounded model request; complete server-side item
validation/reference resolution; a signed generation receipt and future Save
admission mutex; a durable content-free USD 5 reservation ledger; and private
four-tab learning/practice UI. Save/library/database/deployment remain excluded.

## Executed offline checks, 15 November 2026

- `uv sync --locked --group pdf-experiment`: passed (43 resolved / 42 installed packages audited).
- First full `uv run --group pdf-experiment pytest -q --tb=short`: **372 passed, one inherited skip**, 83.97 seconds. The final post-hardening run is recorded below.
- Focused generation protocol matrix: **75 passed**, 12.30 seconds, including Windows write-through ledger replacement, persisted maximum-four live-check count, strict wire schema and receipt expiry after mutex admission.
- Original source browser regression: **19 passed**.
- Expanded `node tests/browser-sources.cjs`: **27 passed** (19 inherited plus 8 generation scenarios).
- Full post-hardening `uv run --group pdf-experiment pytest -q --tb=short`: **381 passed, one inherited skip**, 80.23 seconds.
- Final full post-session-race-fix run: **383 passed, one inherited skip**, 84.79 seconds.
- `node tests/browser-auth.cjs`: **33 passed** (test-only auth adapter).
- `node tests/browser-demo.cjs`: **11 passed**.
- `git diff --check`: passed; Git reports normal LF/CRLF checkout notices.
- `uv run python -m scripts.generation_smoke --help`: passed without inference.
- Visually inspected `test-results/generation-320.png`; generated tabs, practice question, reveal/navigation and visible focus fit the 320px flow. Browser assertions also checked the 200% layout.

One intermediate full run returned an unexpected safe 401 in the inherited
UTF-8 BOM source-file case (379 passed, one failed, one skipped). The complete
63-test extraction rerun passed, followed by a full 381-pass run. Investigation
identified a pre-existing session validation race: the worker can resolve its
shared Future successfully before its owner coroutine resumes; per-request
portal shutdown then cancelled that owner and incorrectly terminated the live
session. Cleanup now preserves already-completed success while denying unfinished
validation. A deterministic barrier regression checks both cancellation phases;
all 12 focused auth validation checks passed. No source/auth expectation was
weakened. The final full post-fix result is the 383-pass run above.

The only Python warning is the existing Starlette TestClient/httpx deprecation.
The inherited skip is retained; no new generation test is skipped.

## Matrix coverage

| Matrix row | Executed coverage |
| --- | --- |
| Generate | Paste/text-file/PDF adapters, all four parts, English/detailed settings, physical-page gaps, complete insufficiency, signed proofs/receipts and Save validation in `tests/test_generation.py`; browser primary-action/double-click/atomic-display checks. |
| Failure | Unknown references, invalid/blank/oversized prose, wrong types/counts, duplicate refs, refused/truncated/malformed provider envelopes, request/response limits, compressed envelope rejection, provider/transport failure and timeout; browser file/settings preservation and explicit retry. |
| Authority | Tampered source/settings/identity/coverage/proof, cross-session receipts, replay/high-water acknowledgements, out-of-order extraction, in-flight generation invalidation and future Save mutex race; browser failed invalidation and uncancellable late edit/reset replies. |
| Session | Logout, denial, expiry, rotation, restart and proof expiry; metadata cleanup and late model-result rejection; browser pagehide/relogin/logout/late reply and inherited auth lifecycle checks. |
| Resources | Per-session/global no-queue saturation, independent revocation, streamed/body/deadline limits, cancelled waiter cleanup, timeout-resistant adapter, missing/corrupt/exhausted budget, concurrent reservations, restart retention and unexpected-usage blocking. |
| Practice | Independent flashcard/quiz positions/reveals, hidden answer/reference pairs, safe text, keyboard tabs/navigation, insufficiency without fabricated practice controls and no model calls for navigation; 320px and 200% reflow. |

## Live smoke boundary

The implementation agent executed **zero** live inference calls and initialized
no live ledger. Synthetic test ledgers use isolated temporary paths. The parent
subsequently initialized the approved ignored ledger once and executed exactly
the four approved calls after its independent offline checks below.

After offline checks pass, the approved maximum is four self-authored synthetic
calls: Norwegian/short, English/detailed, insufficient evidence and a contained
PDF with readable physical pages 1 and 3 plus unreadable pages 2 and 4. Each call
reserves USD 0.05 before dispatch; the ledger persists both reservations and a
maximum-four live-check counter. No retry or uncertain-charge refund occurs.
Record only actual model identity, latency, token usage, estimated standard-rate
cost, section counts and resolved reference locations. The live ledger is ignored
and is never automatically initialized/reset by the app or smoke script.

### Parent verification and executed live checks

Parent locked sync passed. `pytest --junitxml=test-results/generation-parent-verification.xml`:
**383 passed, one inherited skip, one existing Starlette warning**, 83.05s.
All **183 auth, 63 source and 75 generation** cases passed without skips; the
only skip remains the existing optional PDF-platform case. Parent browsers:
**27 source/generation, 33 auth and 11 demo / 21 demo requests** passed.
The parent read the complete staged baseline diff including new files, corrected
one trailing-whitespace issue caught only after staging, inspected both 320px
and 200% generated views, and verified the approved block/hash and prior
Story 2.3/2.4 specs/source evidence unchanged. No provider key appears in the
staged diff; `.env` remains ignored.

All four live calls returned HTTP 200, exact model `gpt-6-luna`, completed
message output and validated four-part contracts/reference mappings. Only
self-authored water-phase statements or punctuation were sent. No account,
email, password, original file or source filename was sent to the model.

| Case | Input / output tokens | Model latency | Estimated USD | Section counts (summary/concepts/cards/quiz) | Resolved references |
| --- | --- | --- | --- | --- | --- |
| nb/short | 662 / 315 | 6.640s | 0.0002237 | 1/2/2/2 | Avsnitt 1, 2 |
| en/detailed | 663 / 397 | 4.461s | 0.0002648 | 1/4/4/4 | Avsnitt 1, 2 |
| Insufficient punctuation | 623 / 90 | 3.370s | 0.0001073 | 0/0/0/0, all four explanations present | None |
| Contained PDF with gaps | 662 / 303 | 6.647s | 0.0002177 | 1/2/2/1 | Side 1, 3; unreadable physical pages 2, 4 |

Actual inference calls: **4**. Estimated standard-rate usage total:
**USD 0.0008135**, before tax; this is calculated from returned usage, not an
invoice. Durable reservations: **USD 0.20** against the USD 5 ceiling; remaining
reservation allowance USD 4.80. The ledger's automated live-check count is now
four: **no further automated inference is authorized by this smoke allowance**.
No retry/refund/reset occurred. A launcher invocation failed before executing
the script; it made no HTTP request and consumed no reservation. The corrected
launcher then executed each named case once. Content-free parent diagnostics
recorded HTTP status and output types only, never raw provider errors/content.
Ignored observations are in `test-results/generation-parent-live.json`.

These checks establish live protocol compatibility and observed insufficiency/
reference behavior for the four controlled inputs. Selected language/detail
were submitted; general language/style/factual quality remains Story 2.6.

## Final review corrections and parent verification

Three independent review layers supplied twelve individually triaged findings;
the edge follow-up supplied one additional filesystem/deadline finding. All
thirteen were corrected within the approved intent, with no deferred findings.
The final patch moves budget filesystem work to two bounded workers with no
queue, retains actual-work admission during cancellation/cleanup and rechecks
session/workspace/deadline authority after reservation before network dispatch.
Other corrections cover durable anomalous-usage blocking, safe usage metadata
from rejected envelopes, independent HTTP deadlines, warning allowance, partial
insufficiency, language attributes, reversible controls, Enter submission and
exact second/mixed-unit references across all four sections.

The parent's final full run after all code changes, recorded in
`test-results/generation-parent-verification-final.xml`, passed **422 tests**
with **one inherited platform skip**, 90.163s. All **183 auth, 63 source and
114 generation** tests passed without skips; PDF contributes 32 passes/one skip
and demo 30 passes. Final browsers passed **28 source/generation, 33 auth and
11 demo scenarios / 21 demo requests**. Both final 320px/200% views were inspected.
Whitespace checks passed. The approved frozen block and historical Story 2.3/2.4
specifications/source evidence remain unchanged.

The normal local server was restarted with existing ignored auth/key, explicit
model activation and the existing ledger, one worker (PID 30048). **Ten unsigned
startup checks** passed: health, workspace, JavaScript, route registration,
private headers/status, denied unauthenticated mutations, inaccessible private
files and unchanged ledger. No login, provider request or inference was needed;
the student must log in again following restart. A first checker invocation
stopped before HTTP because it used an incorrect configuration property name;
the corrected checker passed all ten checks. The ledger still holds exactly
four attempts/four live checks/USD 0.20 reserved. These final offline/startup
checks do not claim a post-patch live rerun; the four historical observations
above remain the complete automated live evidence.

## Separate acceptance gates

A structurally valid response/reference is not proof of factual support. Full
three-document evaluation (five preselected concepts/locations per document,
supported content, correct references, at least four concepts covered), any
quality correction and recheck belong to Story 2.6. Language/style and actual
insufficiency fidelity must be observed separately from schema validation.

The actual contained Windows PDF path is exercised with synthetic PDFs. A
representative real PDF and primary-flow screen-reader review remain separate
acceptance gates. PDF isolation on a hosted target, deployment concurrency,
network deadlines, provider project limits and hosted session handling require
target-platform verification. No production/platform or general fidelity claim
follows from local smoke checks. No account, funding, hosted setting or deployment
was changed by this work.
