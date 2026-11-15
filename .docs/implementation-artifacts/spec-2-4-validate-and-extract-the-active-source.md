---
title: Validate and extract the active source
type: feature
created: 2026-11-15
status: done
route: dispatch
story_key: 2-4-validate-and-extract-the-active-source
baseline_commit: 2fd75fb7eb22965a5288635dde21751ade10cfb0
review_loop_iteration: 0
context: [.docs/implementation-artifacts/epic-2-context.md, .docs/implementation-artifacts/pdf-experiment.md]
---

<frozen-after-approval reason="approved by the student on 2026-11-15: godkjenn og fortsett">

## Intent

**Problem:** Students can authenticate but cannot use their own material.

**Approach:** Add authenticated paste/text-file/PDF input, canonical paragraph/page previews and retained settings. Live generation follows in 2.5.

## Boundaries & Constraints

**Always:** One active input only. Normalize CRLF/CR to LF before counting; reject rather than truncate above 30,000 Unicode code points, 40 physical PDF pages or 10 MiB decoded file bytes. Preserve physical page gaps and explain partial coverage. Validate ordinary authority and Origin/CSRF before body/parser work; fence success against logout, rotation and expiry. Bound upload time, admission and parser resources; fail closed without isolation. Private responses are no-store; sources/settings stay transient, outside logs/storage/static/cache. Changes/reset invalidate accepted results and stale replies; ended access clears private inputs/display. Preserve account recovery, fixed demo, Free/Paris and existing acceptance evidence.

**Never:** OCR, image/table interpretation, encrypted-PDF passwords, model calls, fabricated learning results, receipts/Save/library/database changes, hosted settings, account/email/password operations, costs or deployment. Unsupported platforms do not parse PDFs without containment.

## I/O & Edge-Case Matrix

| Scenario | Given / when | Then / safe failure |
| --- | --- | --- |
| Text | Given paste or UTF-8 file (optional BOM), when accepted | Nonempty blank-line-separated paragraphs, stable unit IDs/locations, settings retained; reject invalid encoding/scalars, binary controls or whitespace-only input |
| Limits | Given exact/excess character, physical-page or byte ceilings | Exact accepted; excess rejected wholly, including blank/image pages; count canonical text before labels/separators |
| PDF | Given readable/partial/image-only/encrypted/malformed PDF | Original physical locations and unreadable-page list; fixed text-only notice; no readable text/parser failure accepts no source |
| Transport/resources | Given slow/oversized/chunked/disconnected input, saturation or failed worker | Bounded rejection, no disk spool/partial acceptance, worker cleanup and released admission; subsequent request works |
| Authority/races | Given foreign browser/CSRF, recovery-only authority, provider denial, logout/expiry/rotation during read/extraction | Safe denial without private payload; stale replies cannot restore changed/reset/ended workspace |
| Interaction | Given source/settings edits, retry, reset or page restoration | Changes invalidate preview; retry retains input/settings; reset clears source/file/subject and restores nb/short; ended/restarted access requires login |

</frozen-after-approval>

## Code Map

- `app/contracts/learning.py`: reuse Source/SourceUnit/Settings.
- `scripts/pdf_probe.py`: reuse probe_stream/ProbeResult and isolated worker behind adapter; preserve CLI/tests, 512 MiB Job Object and ten-second deadline.
- `app/api/auth.py`, `app/services/sessions.py`: reuse protected/current_session/authenticated_async and live-session fences; preserve generation cookies/non-touching status.
- `app/static/app.js`, `account.js`: reuse rendering, sequence/abort/retry/lifetime patterns; preserve demo transport/selectors.

## Tasks & Acceptance

**Execution:**
- [x] `app/contracts/sources.py` — strict envelope/response using Source/Settings; no filenames/client owner IDs. Return source/settings/kind, characterCount, totalPages/unreadablePages/warnings and echoed clientRevision.
- [x] `app/adapters/pdf.py`, `pyproject.toml`, `uv.lock` — wrap probe; promote pinned pypdf 7.0.1 to runtime, preserve experiment commands/tests. No web-process parsing.
- [x] `app/services/extraction.py` — strict UTF-8/BOM/base64 decoding, canonical paragraphs, fresh source identity and PDF coverage. Preserve accepted unit content; count full canonical text including whitespace.
- [x] `app/api/sources.py`, `app/api/auth.py`, `app/services/sessions.py`, `app/main.py` — protected POST `/api/v1/sources/extract`, bounded admission/body/cancellation, final atomic live-session check and safe fixed errors. Add non-authorizing per-session sessionViewId to normal status; require matching X-Session-View before source body work. Only successful work touches idle.
- [x] `app/static/workspace.html`, `workspace.js`, `styles.css`, `index.html`, `account.html`, `app/main.py` — `/workspace` navigation, input/settings, preview/coverage and “Kontroller materiale”; explain generation is pending. Safe rendering, retry, focus and stale/session clearing.
- [x] `tests/test_sources.py`, `sources_browser_app.py`, `browser-sources.cjs` — matrix regressions with synthetic data, actual contained PDF integration, cross-browser/session races, control preservation, privacy, keyboard and 320px/200% reflow; preserve all existing suites.
- [x] `README.md`, `.docs/implementation-artifacts/source-acceptance.md` — commands/contracts, executed evidence and remaining real-document/target-host gates.

**Acceptance Criteria:**
- Given no authentication configuration, when the fixed demo runs, then it remains credential-free and never receives private material.
- Given accepted private material, when inspected, then previews identify their actual paragraphs/pages; no learning output or persistence is implied.

## Implementation Notes

2026-11-15: Student approved with “godkjenn og fortsett”; the frozen block is locked, SHA-256 `bba17495533b217d96a9c382c43a59714338a307aec8b0df249d2ec10b7d6914`. Existing baseline preserved. The isolated implementation agent wrote production/UI and focused/browser tests but stopped at an account usage limit before final reporting/docs. After the student said “fortsett”, the parent completed acceptance docs, inspected the actual patch and ran all verification independently. No account/email/password or hosted setting operations were performed. Windows contained extraction and transient JSON/base64 admission reuse the approved design; live generation remains later work.

## Spec Change Log

## Review Triage Log

All three independent layers reported before triage. Findings are graded individually below before grouping. The implementation agent cannot be continued after its usage-limit failure; the parent applies patches within the approved intent.

| ID | Verdict | Route | Evidence / correction |
| --- | --- | --- | --- |
| B1 | medium | patch | collect builds arbitrary JSON graphs on the event loop before strict validation. A 60,011-byte request with 20,000 empty objects allocated over 1.4 MiB; the 14 MiB wire allowance magnifies this pressure. Constrain structural depth/members/arrays before object construction and use independently limited workers for parsing/preparation. |
| B2 | medium | patch | A focus/visibility observation supersedes submit's final observe; its false result silently discards successful extraction with no retry. Edge reviewer reproduced it. Coordinate observations and require a fresh authoritative check after extraction. |
| B3 | medium | patch | endAccess clears extraction state but leaves authSequence/authActive current; a held old authenticated snapshot can reopen the form after a source 401. Invalidate/abort auth observations at termination. |
| B4 | medium | patch | Retry's token-acquisition fetch has no signal/deadline once csrf was cleared; stalled status leaves logoutPending forever. Bound the complete status+POST attempt. |
| B5 | medium | patch | pagehide/endAccess hides Retry while logoutPending survives; restored observe returns immediately, leaving no logout retry action. Preserve explicit pending intent and restore an enabled retry, with stale logout completions fenced. |
| B6 | false | reject | No escaped/unbounded shutdown worker was demonstrated. Cancelled HTTP waiters intentionally leave owned work; body reads time out and the existing probe owns a hard-deadline Job Object with terminate/reap in finally. Absence of an extra lifespan hook alone does not establish a leak; do not add unsupported lifecycle complexity. |
| B7 | low | patch | Oversized paste is serialized/uploaded before server rejection. Common long-course-text input can be rejected locally by canonical code-point count, preserving the draft and avoiding that allocation/request. |
| B8 | medium | patch | Browser logout coverage only clicks account.js, leaving workspace.js's separate button/retry untested. Add acknowledged success, failed POST/retry, repeated-click and restoration cases. |
| B9 | low | patch | Current issues entry still says awaiting approval/backlog. Update during finalization to executed implementation/review evidence; no app defect. |
| B10 | low | patch | README's older auth scope says private documents are absent while the new workspace processes them transiently. Correct the old scope wording. |
| B11 | low | patch | Earlier encoding cleanup changed an existing question mark into “å” in a reflection prompt. Restore the question without altering student reflections. |
| E1 | medium | patch (B2) | Independently reproduced the post-extraction observation race: hidden preview/retry and stuck checking status after a successful extraction. Same root as B2. |
| E2 | medium | patch (B4) | Independently traced unbounded status acquisition during logout retry. Same root as B4. |
| V1 | medium | patch | Trusted regression gap: API/browser PDF tests assert lengths/locations but not exact text, so uppercasing would pass. Add explicit expected physical-page/text pairs. Parent's one-off rendered comparison is evidence, not a committed regression. |
| V2 | medium | patch (B8) | Trusted regression gap: removing the workspace logout click listener would pass all prior browser tests. Add direct workspace logout and failed transport/retry assertions. |

Grouping: B2/E1, B4/E2 and B8/V2 share their respective roots; all other surviving findings stay separate. No intent gaps or frozen-spec changes are needed. B6 is rejected; no findings are deferred.

Resolution: B1 now rejects unsupported JSON structure before allocation and parses/prepares with its own two-permit limiter. B2/B3 coordinate observations, force a fresh final check and invalidate old auth generations on termination. B4/B5 bound the entire logout attempt, suppress duplicates and preserve pending retry across restoration with stale completion fencing. B7 checks canonical paste length before upload. B8/V2 add direct acknowledged workspace logout, failed POST/retry, repeated-click, timeout and restoration coverage. V1 adds exact physical-page/text assertions through both API and browser. B9 is closed in final session tracking; B10/B11 correct the documented scope/reflection punctuation. The independent edge reviewer inspected the patches and found no further concrete defects (read-only; no separate test execution). No new deferral or intent change.

## Design Notes

Strict JSON: schemaVersion, kind (paste/text-file/pdf), settings, clientRevision and exactly one of text/contentBase64. Strict base64 avoids multipart disk spooling. Independently cap wire bytes at 14 MiB, decoded files at 10 MiB; five-second body deadline includes chunked/short reads.

Admit two requests globally/one per session before body collection, one isolated PDF worker globally; no queue. Hold permits through actual cleanup despite cancellation; independent worker limiter. Recheck the same live session after awaits/before success; no server-side source retention. Generation receipts/workspace authority follow in 2.5.

Non-touching status, elapsed-time-adjusted deadlines and authoritative fan-signal observation clear ended access. sessionViewId changes clear old drafts even after same-account relogin; it grants no access. pagehide clears private state; restoration revalidates.

Windows containment remains required; [pypdf guidance](https://pypdf.readthedocs.io/en/7.0.1/user/extract-text.html) explains memory risk. No irreversible operations; footprint spans contracts/API/service/UI/tests and existing wiring/dependencies/docs.

## Verification

- `uv sync --locked --group pdf-experiment`; `uv run --group pdf-experiment pytest` — all suites pass; only the existing optional platform skip is acceptable, not an unexecuted required PDF row.
- `node tests/browser-sources.cjs`; `node tests/browser-auth.cjs`; `node tests/browser-demo.cjs` — all pass without real account/email/password operations.
- `git diff --check` — clean. Record actual Windows worker cleanup/bounds and compare extracted known fixture text with rendered pages; do not claim arbitrary-document or deployment acceptance.


### Parent verification before independent review

`uv sync --locked --group pdf-experiment` passed. Full `pytest --junitxml=test-results/source-parent-verification.xml`: **302 passed, 1 unchanged optional platform skip**, 44.14s; all **181 auth and 59 source cases** passed without skips. Source browser **13**, auth browser **33**, demo browser **11 / 21 generation requests** passed. The parent compared a self-authored three-page PDF's exact API extraction with all Poppler-rendered pages: readable 1/3, blank 2, correct text/coverage and worker/admission cleanup. This is controlled synthetic/render evidence, not acceptance of arbitrary course PDFs or future hosting.

| Frozen matrix row | Executed passing evidence |
| --- | --- |
| Text | canonical paragraphs/settings/fresh IDs; character/scalar and UTF-8/BOM tests; paragraph/file browser scenarios |
| Limits | character/scalar boundaries; decoded/wire ceilings; nine actual contained PDF integration cases; existing PDF probe physical-page/byte/Unicode boundary cases |
| PDF | actual contained integration (partial, empty, encrypted, malformed, exact/excess pages/chars/bytes); existing late-page parser-failure/cleanup tests; real browser physical gaps; parent rendered known-document comparison |
| Transport/resources | short/chunked body reads, deadline/disconnect recovery; global/session/PDF admission and cancellation; worker failure/retry; real probe timeout/memory/crash/cleanup suite |
| Authority/races | Origin/CSRF/view rejection before body; recovery-only/view-alone denial; provider denial; logout/rotation/expiry during body and worker; stale edited/reset/relogin browser replies |
| Interaction | settings and technical retry retention; file/method selection; edit/reset; same-account relogin; pagehide/restoration; sibling logout; provider denial/expiry/restart; privacy and reflow/focus browser cases |

All planned files/tasks are present; fixed demo and account recovery regressions passed. Independent review/triage follows; no final acceptance is claimed at this checkpoint.

### Final parent verification after review corrections — 2026-11-15

- Locked dependency sync passed. `uv run --group pdf-experiment pytest --junitxml=test-results/source-parent-verification-final.xml`: **306 passed, one unchanged optional PDF platform skip**, 77.74s; all **181 auth and 63 source cases** passed, including all nine required real-contained PDF integration cases. One existing Starlette warning remains.
- `node tests/browser-sources.cjs`: **19 passed**; `node tests/browser-auth.cjs`: **33 passed**; `node tests/browser-demo.cjs`: **11 passed / 21 generation requests**.
- The final regressions assert exact PDF text/location pairs, reject structural JSON before object construction, verify parser/preparation thread separation from the occupied default limiter, and reproduce observation overlap/stale success, direct workspace logout, duplicate suppression, bounded token retry, page restoration and local canonical paste boundaries.
- Parent inspected 320px/200% workspace images with no overflow/clipping and visually compared all three rendered pages of a self-authored known PDF with exact extraction via the source API. This remains synthetic/render evidence, not arbitrary real-course-document acceptance.
- Reviewed normal server PID 11748 ownership, replaced it with worker **45744** (launcher 45572), existing ignored `.env`, one worker, `127.0.0.1:8000`. **8/8 unsigned startup/security checks** passed: health, workspace/private headers/new JS, unprotected and ordinary-authority denial, configured unsigned status and no environment-file exposure. No genuine account/email/password operation was run for Story 2.4. Isolated browser servers are stopped.
- `git diff --check` passed. Frozen approved block remains SHA-256 `bba17495533b217d96a9c382c43a59714338a307aec8b0df249d2ec10b7d6914`.

Build implementation/review is complete; sprint Story 2.4 is review for final human/product acceptance. Source/PDF limits, Windows-only containment and existing representative-document/target-host/email gates are retained in [source acceptance](source-acceptance.md). No hosted settings, persistence, model integration, costs or deployment were introduced.
