# PDF extraction experiment — Story 1.2

Date: 2026-11-12. Platform: Windows 11, build 10.0.26300, x64; CPython 3.13.7;
candidate and locked experiment dependency: **pypdf 7.0.1**. No cloud credentials,
private fixtures, OCR or application routes were used. Story 1.1 remains pending
student review.

## Decision

Adopt the exact candidate **for this isolated local experiment on the tested Windows
host**, subject to the completed verification below. Keep it in the optional
`pdf-experiment` dependency group; it is not an application runtime dependency.
The experiment supplies a representation and provisional limits for Story 2.4.
Hosting/integration remains gated on verification of the actual deployment platform,
its worker containment and end-to-end input handling. This report does not establish
arbitrary-document quality or production security.

## Reproduce

From a clean checkout, install uv, then run in PowerShell from the repository root:

```powershell
uv sync --locked --group pdf-experiment
uv run --group pdf-experiment pytest -q --junitxml=test-results/pdf-probe.xml
uv run --group pdf-experiment python scripts/pdf_probe.py --help
New-Item -ItemType Directory -Force test-results | Out-Null
uv run --group pdf-experiment python tests/pdf_fixtures.py test-results/synthetic.pdf
uv run --group pdf-experiment python scripts/pdf_probe.py test-results/synthetic.pdf
git diff --check
```

uv selects Python 3.13.7 from `.python-version`; initial dependency installation needs
network access. Extraction/tests need no remote service. Generated PDF/XML files stay
under ignored `test-results/` or pytest temporary directories. Only generator source
is versioned. Synthetic bytes, including encrypted fixtures, are reproducible.
The deterministic RC4 fixture tests rejection only and is not an encryption recommendation.

## Representation and rules

The importable `probe_pdf(path)` / `probe_stream(binary_stream)` return a `ProbeResult`.
An accepted result has ordered `PageUnit` values with `id="pdf-page-N"`, `kind="page"`,
one-based physical `location=N` and canonical extracted text. They conform to the
existing `SourceUnit` contract without changing it. IDs are stable within a source,
not globally unique document identifiers. Original documents/accepted representations
must receive source identity at later integration.

For text on physical pages 1/3, blank page 2 and a real PDF image object on page 4,
units retain locations 1/3, `total_pages=4`, `unreadable_pages=(2,4)` and a partial
coverage notice identifying those positions. Whitespace-only pages contain no usable
text and produce no source unit. When all pages contain text, a fixed notice still
states that coverage is limited to extracted text and images are not interpreted,
including mixed text/image pages. Extraction/parser exceptions reject the entire source;
coverage metadata does not conceal parser failures. If all pages lack usable text,
the result is `no_readable_text` and no source is accepted.

CRLF and CR become LF before counting. The count sums the length of every extracted
page string, including whitespace, without page labels or inserted separators. Text
is not stripped or silently shortened. Python string length counts Unicode code
points: the tests distinguish an emoji from its four UTF-8 bytes/two UTF-16 code units.

40 physical pages, 30,000 canonical code points and 10,485,760 bytes are inclusive
ceilings. 41 pages, 30,001 code points and 10,485,761 bytes are rejected without any
accepted prefix. Input reading repeats bounded reads through EOF or ceiling+1,
including streams that return short reads; bytes beyond the ceiling never enter the
parser. Empty/non-PDF/malformed/encrypted inputs and unavailable paths have fixed safe
codes. The CLI prints counts, positions, safe status/messages and resource observations;
it has no source-text output mode and returns a nonzero exit status on rejection.

## Containment

Before sending any PDF bytes, the parent creates a Windows Job Object, configures
512 MiB **process and job committed-memory** caps, limits the job to one process,
enables kill-on-close, starts a gated worker and assigns it to the job. The worker
verifies its own current job limits after the stdin gate and before importing pypdf.
No PDF decoding or parsing occurs before that verification. It uses the base Python
interpreter directly because the Windows venv redirector otherwise needs a second
process; `-I` ignores ambient Python path/user packages and the selected environment's
site-packages is added after the gate.

The parent starts a monotonic 10-second deadline before worker creation. Startup,
input transfer and parsing count against it; bounded local file reading precedes it.
Timeout, worker crash, parse failure and memory allocation failure release the worker
and accept no partial result. The parent terminates the job, kills any worker that
failed assignment, waits for the process and closes process pipes/job handles on all
paths. The single-process cap prevents descendants. Cleanup may add milliseconds
beyond the work deadline. The cap concerns worker committed virtual memory, not RSS
or the parent/application's total memory; the parent also holds bounded input/JSON.

There is no polling-only memory fallback. Unsupported OS, unavailable job creation
or failed assignment returns `isolation_unavailable`. The importable API and CLI do
not echo source, paths, tracebacks or pypdf diagnostics. Direct hidden worker entry
also refuses to parse outside a suitably capped job.

This design uses documented [Windows Job Object management](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
and [committed-memory limits/peak accounting](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information).
[pypdf's extraction documentation](https://pypdf.readthedocs.io/en/7.0.1/user/extract-text.html)
warns that a small compressed file may expand into substantial extraction allocations;
that is why a byte ceiling alone is insufficient. Python's
[`resource` module](https://docs.python.org/3.13/library/resource.html) is Unix-only.

## Observations

The following content-free measurements are historical observations from the importable
probe on this host, not newly rerun values or guarantees. Times and peak committed bytes
vary with load and process startup.

The documented JUnit command re-emits current observations in
`test-results/pdf-probe.xml`. Within each `testcase`, read the JSON in
`properties/property[@name='pdf_observation']/@value` for the physical-page,
accepted 40-page, accepted 30,000-character and exact-byte tests. Each contains
`inputBytes` plus `public_summary()` fields, including resource measurements, with no
source text or filenames. The character test includes a blank middle page, so its
fixture size/page count differs from the historical two-page Unicode row below.
Existing `containment_result` and `compressed_stream_result` properties contain the
controlled-worker and parser-stress observations.

| Synthetic input | Input bytes | Outcome | Elapsed seconds | Peak worker committed bytes |
| --- | ---: | --- | ---: | ---: |
| Text pages 1/3, blank 2, image-only 4 | 2,623 | accepted; 4 physical pages; 10 characters; gaps 2/4 | 0.3974 | 33,120,256 |
| 40 pages with 39 blank pages | 5,913 | accepted; all physical pages counted | 0.5743 | 33,181,696 |
| 30,000 Unicode code points over two pages | 61,929 | accepted; exact text preserved | 0.5495 | 34,471,936 |
| Valid PDF padded to exact 10 MiB | 10,485,760 | accepted after validation | 3.1619 | 54,173,696 |
| Compressed 6 MB stream: 1,500,000 `q Q` operator pairs | 7,021 | timeout, no accepted units, worker reaped | 10.0147 | 258,351,104 |
| Controlled allocation of 513 MiB in a 512 MiB job | gate only | `memory_limit`, no units, worker reaped | 0.4093 | 32,223,232 |
| Controlled process exit 17 | gate only | `worker_failed`, no units, worker reaped | 0.4557 | 32,305,152 |

The allocation test requests a single committed buffer exceeding the cap. Its low
peak is expected: the OS refuses that allocation instead of committing 513 MiB.
It proves enforcement, not a measured pypdf memory requirement. The controlled sleep
workload separately proves parent timeout enforcement at the default 10-second limit.
Tests verify a subsequent successful extraction after timeout, allocation failure,
crash and compressed-stream stress.

The compressed-stream case is a **parser observation**, distinct from controlled
containment workloads. A concurrent run instead safely returned `invalid_pdf` at
8.8827 seconds with a 316,436,480-byte peak. Parser outcomes may vary with resources;
neither observation is evidence that compressed inputs are harmless or fully readable.
The test permits safe rejection/timeout/memory failure or an exact, complete success;
it always requires worker cleanup and successful subsequent extraction.

## Verification and limits

`uv sync --locked --group pdf-experiment` succeeded. The final parent verification after
review patches returned **62 passed, 1 skipped** in 43.04 seconds, including the unchanged
demo suite (`test-results/pdf-final-verification.xml`). An earlier implementation run
returned 58 passed, 1 skipped in 44.52 seconds before the additional review regressions.
`git diff --check` passed. The pre-existing FastAPI/Starlette test-client deprecation
warning is unrelated to PDF extraction. JUnit properties retain content-free containment
and compressed-stream observations in the ignored report.
The documented help, fixture-generation command and CLI example also passed: the CLI
reported physical pages 1/3, unreadable 2/4, 4 total pages and 36 code points without
text or filenames. After changing only JUnit observation recording to remove a format
warning, `uv run --group pdf-experiment pytest tests/test_pdf_probe.py -q -k 'containment_workloads or compressed_stream' --junitxml=test-results/pdf-containment.xml`
passed all 4 selected tests in 23.95 seconds without warnings.

Three independent review layers were triaged in the [build specification](spec-1-2-verify-physical-pdf-pages-before-integration.md).
Direct patches added a notice for mixed text/image pages, a distinct isolation-setup
error mapping, a real parser failure on page 2 after readable page 1, and ordinary-case
JUnit observations. The focused patch run passed 11 selected tests before the final
full parent run. No implementation defect was deferred. Reading a caller-provided
stream still precedes the worker deadline; any future upload/remote transport must
have its own I/O deadline.

The executed matrix covers all frozen-spec rows: physical page gaps with a real image
object; no usable text; 40/41 pages; 30,000/30,001 Unicode code points; line normalization;
exact/excess byte inputs; short reads; empty/non-PDF/malformed/encrypted input; real
timeout, allocation failure and crash; cleanup/recovery; unavailable isolation;
and content-free CLI success/failure. Existing API/contract tests remain unchanged.
One platform-specific test is intentionally skipped on Windows: it asserts refusal
on a real unsupported OS. Executed setup/assignment failure tests and a direct uncapped
worker test establish fail-closed behavior here; the skip is not sole coverage of a
required matrix row.

Only synthetic PDFs were tested. Complex layouts/fonts, scanned documents, real-world
damaged files and extraction correctness against rendered pages have not been assessed.
The generator's ToUnicode mappings test counting and preservation, not typography or
reading order. No OCR, table/figure interpretation or PDF password workflow is provided.
Strict parser failures reject the whole document, even if an earlier page was readable.

Linux/macOS, Windows Server, containers, CI runners, low-memory machines and the final
hosting environment are untested and unsupported by the current containment adapter.
Reverify nested-job compatibility, limits, cleanup, leakage and representative permitted
documents on the target host before Story 2.4 deployment. Full application upload,
authentication/storage, server concurrency limits and hosting are outside this story.
