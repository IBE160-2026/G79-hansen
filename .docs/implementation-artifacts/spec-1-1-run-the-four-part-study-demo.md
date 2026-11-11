---
title: Run the four-part study demo
type: feature
created: 2026-11-11
status: done
route: dispatch
story_key: 1-1-run-the-four-part-study-demo
baseline_commit: 34f546d0006ea63f2cd2aa30b0e9bd5ffe5c0b73
review_loop_iteration: 0
context:
  - .docs/planning-artifacts/architecture/architecture-G79-hansen-2026-11-01/ARCHITECTURE-SPINE.md
---

<frozen-after-approval reason="user delegated the first runnable demo and implementation plan on 2026-11-11">

## Intent

**Problem:** Study Buddy currently consists of planning and a standalone UX prototype. An assessor cannot start a Python application and exercise a real browser/API flow.

**Approach:** Build one local FastAPI application serving the approved plain HTML/CSS/JavaScript study layout. A clearly labelled fixed-data demo adapter returns all four learning sections from a named fixture. This is Story 1.1 only; later stories supply live input/AI, accounts and durable storage.

## Boundaries & Constraints

**Always:** Same origin; versioned typed source/result contract; discreet Demo – eksempeldata label; visible fixed source; summary/concepts/cards/quiz with references; whole material region expanded initially/on errors and collapsed after success. Independent practice positions and per-item reveal state survive tab switches. Reset invalidates pending responses. Local startup requires no cloud secrets. Keep existing UX prototype as a historical reference and preserve its readable sizes/colors/composition.

**Never:** Accept arbitrary source as if processed by AI, provision cloud services, add paid calls, enable a fake live backend, persist private data or expose repository files through static serving. Save/auth/library remain clearly described future work, not presented as working live capabilities.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
| --- | --- | --- | --- |
| Generate | named memory fixture | one API response with four sections and stable reference IDs | busy state prevents duplicate submission |
| Unsupported input | custom source, unknown fixture or unknown fields | reject; no model/data writes | understandable 422 error |
| Practice | reveal, tabs, previous/next | no API request; separate positions/reveal sets | disabled bounds, no 1 of 0 |
| Reset while pending | New session before response | expanded empty workspace, late response ignored | abort/sequence guard |
| Network failure | fetch rejects/non-OK | preserve fixture/settings, expanded source and retry | never fabricate success |

</frozen-after-approval>

## Code Map

- `.docs/planning-artifacts/ux-designs/ux-G79-hansen-2026-11-01/.working/key-study.html`: visual/interaction reference; do not copy simulated auth/persistence as real functionality.
- `.docs/planning-artifacts/ux-designs/ux-G79-hansen-2026-11-01/{DESIGN,EXPERIENCE}.md`: accepted tokens/behavior; 960px content, 16px body, responsive controls.
- No existing application/package/test setup. `app/`, `tests/`, `pyproject.toml`, `uv.lock` are new. `.gitignore` already excludes environments/cache/secrets.

## Tasks & Acceptance

**Execution:**
- [x] `pyproject.toml`, `uv.lock`, `.python-version` — establish Python3.13/FastAPI runtime and locked test tools.
- [x] `app/contracts/learning.py`, `app/services/demo.py` — named fixture plus shared typed source/bundle models, validated references, no arbitrary-input generation.
- [x] `app/main.py`, `app/api/demo.py` — serve explicit public assets, demo fixture/generate API and health endpoint; no private file mount.
- [x] `app/static/index.html`, `styles.css`, `app.js` — reproduce accepted layout, accessible tabs/reveal, fixed source disclosure, status/retry/reset and stale-response guard.
- [x] `tests/test_demo.py`, `tests/browser-demo.cjs` — test API rejection/contract and browser flow including reset race/network failure.
- [x] `README.md`, `.env.example` — clean startup/demo/test instructions, actual limitations and future live configuration boundary.

**Acceptance Criteria:**
- Given no external credentials, when README startup runs, then a browser can complete all four fixed-example sections and a health request succeeds.
- Given practice state, when changing tabs or reopening the material panel, then positions/reveals and source remain intact with no generation call; reference is hidden with its answer.
- Given keyboard-only navigation and narrow/200% viewport, when exercising controls, then focus/labels/counts remain usable without horizontal overflow.
- Given failed or reset generation, when its response arrives, then source/settings remain or reset state wins and no stale success appears.

## Implementation Notes

User authorized the complete planning/demo sequence, including routine reversible setup. Earlier uncommitted changes belong to this same authorized session and are preserved. No irreversible work or unresolved user-visible choices are needed for this demo.

## Spec Change Log

## Review Triage Log

Three independent layers reviewed the full baseline diff on 2026-11-11. Findings are classified individually below; repeated root causes share one fix. Runtime changes use the existing failed-request/retry and validation paths. No intent change or external action is required.

| ID / layer | Verdict | Evidence and route |
| --- | --- | --- |
| B1 blind — unbounded fetch | medium | Both fetches have reset cancellation but no timeout; a connected stalled request remains busy. Patch both existing transport paths with bounded failure and browser checks. |
| B2 blind — warnings not rendered | false | Current named fixture's service always emits empty warnings and accepts no arbitrary source/model payload; no warning can be hidden in this increment. Later PDF/live notice work is explicit in Stories 2.4/2.5. |
| B3 blind — blank source unit | false | No PDF route exists in this increment. Physical page positions can be preserved by readable units at locations 1/3 without accepting an empty text unit; extraction/coverage representation is gated by 1.2/2.4. No current accepted input fails. |
| B4 blind — empty insufficiency | low | Browser accepts an empty string where Python rejects it. Directly correct existing browser predicate and add semantic rejection coverage. |
| B5 blind — malformed fixture ready | medium | Version/ID/units-length check can accept malformed unit/settings objects before generation fails. Patch the fixed-fixture shape check and startup failure/retry tests. |
| B6 blind — sprint/spec mismatch | low | Generator initially left Epic 1 backlog during its started story; sync epic/story at final completion. No application behavior affected. |
| B7 blind — pending-save recovery | medium | Final architecture has ambiguous new-session/expired-receipt recovery authority. Clarify operation recovery versus new writes before affected live stories. Documentation patch; demo unaffected. |
| B8 blind — superseded receipt | medium | Signed expiry alone cannot reject an old still-valid receipt after newer generation. Record bounded session current-generation/receipt identity and invalidation. Documentation patch; demo has no save receipt. |
| B9 blind — initial fixture checks absent | medium | Existing browser tests start only after successful fixture loading. Add fresh-page failure/retry and delayed-initial-response reset scenarios. Shared test fix with V1. |
| B10 blind — failed spawn cleanup | low | A spawn error need not emit exit, and cleanup currently waits for exit. Directly skip exit wait if no PID was created. |
| E1 edge — stalled fetch | medium | Same demonstrated pending-request root cause as B1; covered by the same bounded transport failure patch and tests. |
| V1 verification — fixture recovery gap | medium | Pre-verified gap: redirecting fixture retry incorrectly to generate would pass current tests. Add initial fixture-failure/retry coverage; same root as B9. |
| V2 verification — semantic bundle gap | medium | Pre-verified gap: removing source/settings checks still passes tests that supply only 503/invalid JSON/empty object. Add complete mismatched source/settings/reference bundles and assert failure. |

## Verification

Final result 2026-11-11: locked setup passed; 30 pytest cases passed, with one upstream TestClient/httpx deprecation warning. After review patches, parent reran all 11 real Edge browser scenarios (21 generation requests), including actual 15-second startup/generation timeouts, fixture retry, reset races, complete semantic corruptions and 320/390/480px + 200% layout zoom. Screenshot inspection passed. No full manual screen-reader/native browser zoom/WCAG audit claimed. All I/O matrix rows have executed passing coverage. Findings B1/B4/B5/B9/B10/E1/V1/V2 were patched; B7/B8 were clarified in the architecture's receipt-admission resolution; B6 is reconciled in sprint status. B2/B3 have the refutations above. No unresolved implementation finding remains for this demo. Sprint status is review for the student's walkthrough; build status done records completed implementation/verification, not full v1 acceptance.

- `uv sync --locked` — dependency installation succeeds from lockfile.
- `uv run pytest` — API contracts, rejection, public boundary and fixture references pass.
- `node tests/browser-demo.cjs` — real browser journey, API call counts, reset race, retry and responsive checks pass against local uvicorn.
- `git diff --check` — no whitespace errors.
