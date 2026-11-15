# Source validation and extraction — Story 2.4

The authenticated `/workspace` accepts one pasted-text, UTF-8 text-file or
text-based PDF source and previews its canonical paragraphs/physical pages.
`/` and `/api/v1/demo/*` remain a separate fixed-data demo. No model call,
learning output, receipt, Save/library or durable staging is implemented here.

## Run and verify

```powershell
uv sync --locked --group pdf-experiment
uv run --group pdf-experiment pytest --junitxml=test-results/source-parent-verification.xml
node tests/browser-sources.cjs
node tests/browser-auth.cjs
node tests/browser-demo.cjs
git diff --check
```

The exact runtime PDF dependency is pypdf 7.0.1; the existing optional experiment
group and CLI still work. Normal configured loopback startup remains
`uv run --env-file .env uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1`.
Load only the existing ignored configuration; no account, email or hosted setting
change is part of these tests. `/workspace` offers login when ordinary authority
is absent; recovery grants cannot authorize source processing.

## Request and result

`POST /api/v1/sources/extract` requires exact Origin, browser-bound CSRF,
the ordinary session cookie and `X-Session-View` matching the non-authorizing
`sessionViewId` from normal auth status. The view ID alone grants no authority.
Rotation changes it even for the same account, clearing old drafts. Status remains
non-touching; only successful extraction touches idle.

The strict UTF-8 JSON envelope contains `schemaVersion: "1.0"`,
`kind: "paste" | "text-file" | "pdf"`, `settings`, `clientRevision` and exactly
one active field: `text` for paste, or strict canonical `contentBase64` for files.
Unknown/duplicate fields, client owners/filenames, invalid encoding/scalars,
binary text controls and whitespace-only sources are rejected safely.
No multipart/disk spool is used. Study settings retain the existing
`language` nb/en, `detail` short/detailed and optional `subject` contract.

Success returns a schema-versioned Source with a fresh ID, stable paragraph/page
unit IDs/locations, retained settings, kind, characterCount, totalPages,
unreadablePages, warnings and echoed clientRevision. Plain text normalizes
CRLF/CR to LF before counting the entire input, including whitespace and paragraph
separators. Empty separator blocks do not become source units. PDF counts all
physical pages, including blank/image-only positions; readable units keep their
original physical numbers. Every PDF includes the text-only limitation, with an
explicit unreadable-page list for partial coverage. Entirely unreadable,
encrypted or failed parsing accepts no prefix.

Ceilings are inclusive: 30,000 canonical Unicode code points, 40 physical pages,
10 MiB decoded file bytes. The independently bounded JSON wire ceiling is 14 MiB,
including base64/envelope overhead. Body reads have a five-second deadline and
enforce actual streamed bytes, including chunked/short reads. Oversized sources
are rejected wholly, never truncated.

Before JSON object construction, an envelope-aware lexical pass rejects arrays,
nesting deeper than two objects and more than 16 members. Quoted source text and
escaped quotes are preserved. Parsing/validation and source preparation run under
an independent two-permit thread limiter, rather than blocking the event loop or
queuing behind unrelated shared-pool work. These structural bounds complement
the byte ceiling; they do not add accepted fields to the strict envelope.

Two requests globally/one per ordinary session are admitted before body
collection, with no queue. One PDF worker globally uses its own thread limiter;
its existing Windows Job Object has a 512 MiB committed-memory cap and ten-second
startup/transfer/parser budget. Cancellation does not release capacity before
the owned work finishes and its worker is reaped. Logout/rotation/expiry fences
are checked after awaited input/extraction and before success. Errors contain
only fixed code/message/requestId; private payloads and parser diagnostics are
excluded. Workspace/source responses carry no-store/no-referrer headers.

The browser keeps source state only in the current page. Edits/reset discard
accepted previews and stale replies; technical retry preserves active input,
file and settings. Logout/expiry/denial, changed sessionViewId and pagehide clear
private text/file/subject/preview; restoration revalidates. Passive checks preserve
controls/focus and do not renew idle. No browser credential/source storage is added.
Concurrent observations share work; extraction then obtains a fresh status check.
Termination invalidates even cancellation-resistant old observations. Workspace
logout retains retry intent across page restoration and gives token acquisition
plus POST one 15-second deadline. Repeated clicks do not start duplicate attempts.
Oversized pasted text is counted canonically before serialization/upload.

## Executed evidence

Initial parent focused run on Windows 11 / CPython 3.13.7:
`pytest tests/test_sources.py -q --junitxml=test-results/source-focused.xml`
passed **59 cases**, including nine real contained PDF API integration cases.
`node tests/browser-sources.cjs` passed **13 scenarios** with a real browser and
test-only identity adapter. All source/account content in these checks is
synthetic; no genuine account/email/password operations occur.

The parent also authored a simple three-page PDF with ordinary visible Helvetica
text on physical pages 1/3 and blank page 2. Poppler 25.07 rendered all pages;
all three PNGs were visually inspected. Through the actual source API, extracted
text matched those visible lines exactly, totalPages was 3, unreadablePages [2],
and readable locations [1,3]. API privacy headers and admission cleanup passed.
Content-free booleans are in ignored `test-results/source-parent-render-check.json`.
The contained probe recorded workerReaped=true, peak committed memory 33,910,784
bytes and elapsed 1.0708 seconds for that same known document. These measurements
are observations, not performance guarantees. The renderer reported missing
unneeded Symbol/ArialUnicode fallbacks; the inspected Helvetica pages were legible.

Poppler was unpacked only under ignored test-results from the Windows package
with SHA-256 `435e6265738470b7ae6498b8a298a4025bacb9349656207ef54d0f069687ce57`,
matching the package manifest; no machine-wide install or app dependency change.
ReportLab was used only as a temporary uv tool for this known synthetic document.

### Final verification after review

Locked sync passed. Full parent pytest run completed **306 passed, one unchanged
optional platform skip**, in 77.74s, with one existing Starlette warning. All
**181 auth and 63 source cases** passed, including all nine real-contained PDF API
cases. Final browsers: **19 source**, **33 auth**, **11 demo / 21 generation
requests** passed. Evidence is in ignored `test-results/source-parent-verification-final.xml`.
The parent inspected the 320px and 200% workspace images without clipping or
overflow. Exact PDF unit text is now asserted in committed API/browser regressions.

Three independent review layers returned 11 blind findings, two edge findings
and two pre-verified test gaps. Each was triaged separately; overlapping roots
were grouped only afterward. Confirmed code/test/doc issues were corrected;
the proposed extra shutdown hook was rejected because no worker escape/leak was
shown and existing body/contained-worker cleanup already bounds the owned work.
No finding was deferred. A read-only follow-up of the patches found no additional
concrete defect. The frozen approved intent is unchanged.

The normal configured server's old worker 11748 was identified by its project
uvicorn command before replacement. New worker **45744** (launcher 45572) runs
one process on `127.0.0.1:8000` using the existing ignored `.env`. **8/8 unsigned
startup/security checks** passed; ignored `test-results/source-main-server-result.json`
contains content-free booleans. These checks do not establish genuine hosted
source acceptance. No real account/email/password operation was performed for
this story. Restart ends prior sessions; sign in again before using `/workspace`.

## Acceptance limits

This establishes integrated upload/authentication/UI/resource behavior on the
tested Windows host with known synthetic inputs. Existing PDF containment and
stress tests remain relevant evidence; it is not acceptance of arbitrary course
documents, layouts/fonts, scanned/OCR content or reading order. Representative
permitted real-document comparisons remain a separate gate. Unsupported OS/job
containment fails closed; Linux/macOS/container/final hosting limits, cleanup and
privacy must be verified before deployment. No production deployment, storage
durability or full manual screen-reader/assistive-technology audit is claimed.
Prior Story 2.1/2.2 email/link/template gates remain open; do not automatically
send email, create accounts or repeat the successful password change.
