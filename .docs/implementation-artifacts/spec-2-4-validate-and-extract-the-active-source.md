---
title: Validate and extract the active source
type: feature
created: 2026-11-15
status: draft
route: dispatch
story_key: 2-4-validate-and-extract-the-active-source
baseline_commit: 2fd75fb7eb22965a5288635dde21751ade10cfb0
review_loop_iteration: 0
context: [.docs/implementation-artifacts/epic-2-context.md, .docs/implementation-artifacts/pdf-experiment.md]
---

<frozen-after-approval reason="human-owned intent; awaiting approval">

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
- [ ] `app/contracts/sources.py` — strict envelope/response using Source/Settings; no filenames/client owner IDs. Return source/settings/kind, characterCount, totalPages/unreadablePages/warnings and echoed clientRevision.
- [ ] `app/adapters/pdf.py`, `pyproject.toml`, `uv.lock` — wrap probe; promote pinned pypdf 7.0.1 to runtime, preserve experiment commands/tests. No web-process parsing.
- [ ] `app/services/extraction.py` — strict UTF-8/BOM/base64 decoding, canonical paragraphs, fresh source identity and PDF coverage. Preserve accepted unit content; count full canonical text including whitespace.
- [ ] `app/api/sources.py`, `app/api/auth.py`, `app/services/sessions.py`, `app/main.py` — protected POST `/api/v1/sources/extract`, bounded admission/body/cancellation, final atomic live-session check and safe fixed errors. Add non-authorizing per-session sessionViewId to normal status; require matching X-Session-View before source body work. Only successful work touches idle.
- [ ] `app/static/workspace.html`, `workspace.js`, `styles.css`, `index.html`, `account.html`, `app/main.py` — `/workspace` navigation, input/settings, preview/coverage and “Kontroller materiale”; explain generation is pending. Safe rendering, retry, focus and stale/session clearing.
- [ ] `tests/test_sources.py`, `sources_browser_app.py`, `browser-sources.cjs` — matrix regressions with synthetic data, actual contained PDF integration, cross-browser/session races, control preservation, privacy, keyboard and 320px/200% reflow; preserve all existing suites.
- [ ] `README.md`, `.docs/implementation-artifacts/source-acceptance.md` — commands/contracts, executed evidence and remaining real-document/target-host gates.

**Acceptance Criteria:**
- Given no authentication configuration, when the fixed demo runs, then it remains credential-free and never receives private material.
- Given accepted private material, when inspected, then previews identify their actual paragraphs/pages; no learning output or persistence is implied.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

Strict JSON: schemaVersion, kind (paste/text-file/pdf), settings, clientRevision and exactly one of text/contentBase64. Strict base64 avoids multipart disk spooling. Independently cap wire bytes at 14 MiB, decoded files at 10 MiB; five-second body deadline includes chunked/short reads.

Admit two requests globally/one per session before body collection, one isolated PDF worker globally; no queue. Hold permits through actual cleanup despite cancellation; independent worker limiter. Recheck the same live session after awaits/before success; no server-side source retention. Generation receipts/workspace authority follow in 2.5.

Non-touching status, elapsed-time-adjusted deadlines and authoritative fan-signal observation clear ended access. sessionViewId changes clear old drafts even after same-account relogin; it grants no access. pagehide clears private state; restoration revalidates.

Windows containment remains required; [pypdf guidance](https://pypdf.readthedocs.io/en/7.0.1/user/extract-text.html) explains memory risk. No irreversible operations; footprint spans contracts/API/service/UI/tests and existing wiring/dependencies/docs.

## Verification

- `uv sync --locked --group pdf-experiment`; `uv run --group pdf-experiment pytest` — all suites pass; only the existing optional platform skip is acceptable, not an unexecuted required PDF row.
- `node tests/browser-sources.cjs`; `node tests/browser-auth.cjs`; `node tests/browser-demo.cjs` — all pass without real account/email/password operations.
- `git diff --check` — clean. Record actual Windows worker cleanup/bounds and compare extracted known fixture text with rendered pages; do not claim arbitrary-document or deployment acceptance.
