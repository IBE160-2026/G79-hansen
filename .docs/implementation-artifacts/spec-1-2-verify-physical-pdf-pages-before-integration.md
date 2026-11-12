---
title: Verify physical PDF pages before integration
type: feature
created: 2026-11-12
status: done
route: dispatch
story_key: 1-2-verify-physical-pdf-pages-before-integration
baseline_commit: a4310f6f1470d36304d6009dab10cced458f0653
review_loop_iteration: 0
context:
  - .docs/implementation-artifacts/epic-1-context.md
---

<frozen-after-approval reason="human-owned intent; awaiting the Build planning checkpoint">

## Intent

**Problem:** The fixed-example demo does not prove that PDF extraction preserves physical references or rejects excessive inputs safely.

**Approach:** Complete Story 1.2 with synthetic PDFs, an isolated probe, boundary tests and an evidence report. Evaluate pypdf 7.0.1 before adoption.

## Boundaries & Constraints

**Always:** Preserve one-based physical pages, including blank/image-only pages. Report unreadable pages and partial coverage. Reject above 40 pages, 30,000 Unicode code points or 10 MiB without truncation. Normalize CRLF/CR to LF; sum page text lengths without labels or added separators. Enforce provisional limits of 10 seconds and 512 MiB worker memory before parsing; report measured suitability. Fail closed if isolation is unavailable.

**Never:** Add upload routes, UI changes, AI/cloud calls, private fixtures, OCR, table/figure interpretation or PDF password entry. Story 1.1 remains pending student review.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
| --- | --- | --- | --- |
| Physical pages | Text on 1/3, blank 2, image-only 4 | Readable units at 1/3; unreadable list 2/4; partial-coverage notice | Never relabel page 3 as page 2 |
| No usable text | Blank/image-only document | No accepted source | Safe no-readable-text code |
| Page boundary | 40/41 pages, including blank pages | Accept 40 with readable text; reject 41 | No partial result |
| Character boundary | 30,000/30,001 extracted code points | Accept exact boundary; reject excess | No silent trimming |
| Byte boundary | Input at/above 10 MiB | At limit proceeds to validation; excess rejected before parsing | Bounded read, content-free error |
| Invalid input | Empty, malformed, non-PDF or encrypted PDF | Explicit rejection | No traceback, source or parser exception echoed |
| Worker failure | Timeout, excessive allocation, crash | Terminate/reap worker; return failure | No orphan or accepted partial result |
| Unsupported isolation | Memory cap unavailable | Refuse extraction | Explain unsupported environment safely |

</frozen-after-approval>

## Code Map

- `app/contracts/learning.py`: `SourceUnit` supports nonconsecutive ordered page locations. Blank pages belong in coverage metadata, not empty units.
- `tests/test_demo.py`: preserve existing API/contract checks and public boundaries.
- `pyproject.toml`, `uv.lock`, `.python-version`: Python 3.13.7; no PDF dependency yet.
- `.docs/planning-artifacts/epics.md`: Story 2.4 owns application integration.

## Tasks & Acceptance

**Execution:**
- [x] `pyproject.toml`, `uv.lock` — add `pdf-experiment` dependency group with the exact candidate. Adopt only after passing checks.
- [x] `scripts/pdf_probe.py` — implement importable probe and CLI, bounded read, isolated worker, enforced limits and cleanup. Return readable units with stable physical-page IDs, total pages, unreadable positions, character count and coverage notice. Default CLI JSON exposes counts, positions, status and resource observations only; no text, filenames or parser exceptions. Failures exit nonzero.
- [x] `tests/pdf_fixtures.py` — generate deterministic temporary PDFs: real image object, encryption, boundary cases and compressed-stream stress. Version generator source only.
- [x] `tests/test_pdf_probe.py` — cover every matrix row; exact counts, line endings and Unicode versus bytes. Exercise real timeout and memory enforcement with controlled worker workloads; verify cleanup and subsequent success. Distinguish containment tests from parser observations.
- [x] `.docs/implementation-artifacts/pdf-experiment.md` — record commands, platform, version, observed outcomes/resources, adoption decision and limitations. Identify synthetic-only coverage and untested platforms; require verification before hosting.
- [x] `README.md` — document experiment setup, invocation and limitations.

**Acceptance Criteria:**
- Given a clean checkout, when documented commands run, then boundary outcomes reproduce without cloud credentials or demo changes.
- Given rejection or worker failure, when inspecting the result, then no source is accepted, no content leaks and worker resources are released.
- Given experiment results, when Story 2.4 starts, then the report supplies tested limits and representation, or blocks adoption with recorded failures.

## Implementation Notes

2026-11-12: The student approved implementation with “kjør” after the planning checkpoint. The pre-existing planning/context/reflection changes belong to this workflow and are preserved. The frozen block remains unchanged. Initial baseline remains the full revision recorded during planning.

Implemented the optional locked pypdf group, Windows Job Object worker, safe summary CLI, deterministic synthetic fixtures, matrix tests and evidence report. The parent identified and corrected short-read byte-limit accounting before review. Worker launch uses the base interpreter because the Windows venv redirector conflicts with the one-process job limit. No application files/routes changed.

## Spec Change Log

## Review Triage Log

Three independent layers reviewed the complete baseline diff. Each finding is classified before grouping; duplicate outcomes share one patch.

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| B1: mixed text/image pages lack limitation notice | medium | When every page has text, coverage_notice is null even though images are ignored. Patch the existing notice value and add a mixed-page assertion. |
| B2: input reading precedes the worker deadline | low | True for a stalled caller-provided stream or remote file. The documented ten-second extraction deadline begins at worker creation; this local experiment documents input reading separately. Reject additional I/O watchdog complexity for an uncommon local-experiment case; upload transport deadlines remain later integration work. |
| B3: alternate environment can import another pypdf version | false | The supported setup and every documented command use the exact optional dependency and uv lockfile. An independently modified environment violates that setup; no claim of validating arbitrary interpreters is made. The report records the actual tested version. |
| B4: isolation initialization OSError has wrong code | low | The shared OSError handler classifies setup failures as worker_failed. Direct correction: map initialization errors to isolation_unavailable, keeping process/runtime failures distinct; test that path. |
| B5: stress test permits invalid_pdf | false | This test explicitly measures containment, not successful extraction of the stress stream. The report records both rejection and timeout, and limits adoption accordingly; ordinary valid-document tests separately require exact success. Allowing documented safe rejection is the intended observation contract. |
| B6: allocation test is a single oversize allocation | false | The code installs and queries an OS process/job committed-memory cap, with no application per-allocation policy that could diverge for gradual allocations. The real oversize allocation tests OS refusal; no specific gradual-allocation defect was demonstrated. |
| B7: no late-page parser-failure regression | medium | Initial malformed-input tests fail before a readable prefix exists. Add a two-page failure through the real worker; same patch as V1. |
| B8: ordinary measurement rows lack executable observation output | low | Tests reproduce inputs/outcomes but JUnit initially retains only containment/stress measurements. Add content-free properties to existing ordinary cases and identify them in the report. |
| B9: approval issue and sprint status are stale | false | The diff is captured during review, before workflow finalization. The approval was recorded; issue closure and sprint transition are explicitly finalization work. The final tracking files will reflect completion. |
| V1: late-page failure could be hidden as partial coverage | medium | Pre-verified regression gap: blank/image pages and malformed-header tests cannot detect acceptance after a later parser error. Add the real two-page regression; shared B7/V1 patch. |

The edge-case layer returned no findings. No intent change, spec redesign or deferred defect was identified. B1/B4/B7/B8/V1 receive direct patches; B2 is rejected under the low-impact/complexity rule, with the existing I/O limitation retained.

Resolution: B1 now always exposes the extracted-text-only limitation; B4 distinguishes setup OSError from process-start failure. The B7/V1 fixture has readable page 1 and an unterminated text literal on page 2, verified to raise PdfStreamError in the locked parser; the worker rejects the whole source and is reaped. B8 adds four content-free ordinary-case JUnit properties. The implementation agent's focused patch verification passed 11 tests. Parent final verification follows below.

## Design Notes

The [pypdf documentation](https://pypdf.readthedocs.io/en/7.0.1/user/extract-text.html) warns of large extraction allocations: byte limits alone are insufficient. Contain the worker before decoding. Python's [`resource`](https://docs.python.org/3.13/library/resource.html) is Unix-only; choose supported Windows containment here. The report determines adoption readiness.

## Verification

- `uv sync --locked --group pdf-experiment` — reproducible experiment dependencies.
- `uv run --group pdf-experiment pytest` — PDF matrix and existing API tests pass.
- `uv run --group pdf-experiment python scripts/pdf_probe.py --help` — documented CLI is discoverable.
- `git diff --check` — no whitespace errors.
- Inspect outputs for leaks and report accuracy.

Parent verification 2026-11-12: full suite 58 passed, 1 skipped, 1 existing TestClient/httpx deprecation warning in 41.10 seconds. The sole skip checks a real unsupported OS; executed Windows isolation-setup/assignment/uncapped-entry tests cover the failure behavior here. Every matrix row has an executed passing covering test. The implementation's locked sync, help and documented synthetic CLI example passed. Evidence and measured limitations: [PDF experiment](pdf-experiment.md). Full source comparison confirms no `app/` changes. Independent review follows.

Final parent verification after review patches: **62 passed, 1 skipped**, one existing TestClient/httpx warning, in 43.04 seconds; `test-results/pdf-final-verification.xml` contains the current observations. Locked sync, CLI help and diff checks pass. No unresolved implementation finding or deferred defect remains. The experiment is complete for the tested Windows host with synthetic inputs; target-host and representative-document verification remain integration prerequisites. Sprint status is review for student inspection, independently of this completed build workflow.
