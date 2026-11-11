---
title: Study Buddy implementation backlog
status: final
stepsCompleted: [step-01-validate-prerequisites, step-02-design-epics, step-03-create-stories, step-04-final-validation]
updated: 2026-11-11
inputDocuments:
  - prds/prd-G79-hansen-2026-09-26/prd.md
  - architecture/architecture-G79-hansen-2026-11-01/ARCHITECTURE-SPINE.md
  - ux-designs/ux-G79-hansen-2026-11-01/DESIGN.md
  - ux-designs/ux-G79-hansen-2026-11-01/EXPERIENCE.md
---

# Study Buddy - Epic Breakdown

## Overview

User delegation on 2026-11-11 authorizes architecture reconciliation, backlog, sprint planning and the first runnable FastAPI demo. It does not authorize paid services, public deployment or claiming live functionality is finished. Requirements below retain the PRD IDs. An incremental demo does not complete live requirements. Epics are ordered; stories depend only on earlier stories. Exact delivery deadline remains unconfirmed; approximately 15 December, with a target core completion around 1 December, is a planning assumption rather than a promise.

## Requirements Inventory

### Functional Requirements

FR-1: Accept exactly one pasted-text, text-file or text-based PDF source; preserve physical pages and explain unreadable/partly readable PDFs; no OCR/table/figure interpretation.
FR-2: Optional subject; independent Norwegian/English and short/detailed settings; defaults Norwegian/short; source remains factual authority.
FR-3: Produce a source-supported summary at the selected detail level.
FR-4: Produce supported concepts with explanations and the PRD coverage target.
FR-5: Flashcards reveal each answer only on request.
FR-6: Quiz reveals each answer only on request; no scoring or multiple choice in core.
FR-7: Attach paragraph/page references, preserving original physical pages.
FR-8: Supabase email/password signup/login/recovery/logout; protected reset, generic recovery response, server ownership, private UI cleared at logout; New session resets workspace only. Server restart requires re-login and retains saved data.
FR-9: One Generate action returns all four labelled outputs; tab/reveal/navigation/open never calls AI.
FR-10: Explicit Save persists source/settings/results under owner, never implicitly on upload/generation; survives restart and devices; replacing material needs Save again.
FR-11: Owner library lists title/date and opens saved source/results; independent card/quiz positions autosync only for saved generations. Reopen resumes positions with answers hidden. Stale devices must fetch latest progress; show pending/failed sync, never silently overwrite newer progress.
FR-12: Confirmed owner-only deletion removes source/results/files/progress and active view; failures retain visible retry/recovery status.

### NonFunctional Requirements

NFR-1: Before live generation, select five central concepts and source locations for each of three test documents. All sampled content must be supported, all sampled references correct, at least four of five concepts covered; record unsupported content, wrong references and omissions separately.
NFR-2: Empty/unreadable input rejected; failed generation preserves every input/setting with explicit retry; distinguish insufficiency from technical error; never display partial result as complete.
NFR-3: Maximum 30,000 Unicode code points and 40 physical PDF pages; reject rather than truncate. Keep secrets/private material out of Git/logs/static/cache; enforce ownership, expiry and provider data handling.
NFR-4: Credential-free local fixed-data demo, explicit demo/live distinction, README startup and live configuration instructions, secrets example without real credentials.
NFR-5: Four clear sections, adjacent references, labels, readable contrast, keyboard reveal/navigation and manual primary-flow verification.

### Additional Requirements

- AD-1–AD-9 in the architecture are the shared build contract. Use FastAPI plus plain HTML/CSS/JS; same origin, layered services/adapters, no separate frontend build or framework.
- Start from the official minimal FastAPI application, not a copied full-stack template. First story creates only demo files and dependencies; later stories introduce their own tables/entities.
- Typed Source/LearningBundle and versioned errors; one demo/live adapter boundary; demo accepts named fixtures only. Secrets remain on server. Never silently fall back from live to demo.
- User-scoped Supabase and owner RLS for all data/files; one-process in-memory sessions, PKCE recovery and restricted password update, CSRF/same-origin checks, configured expiry.
- Receipt-bound explicit save, revision checks, transactional RPC mutations, pending/ready/deleting operations and cleanup/retry for cross-service lifecycle; no fake transaction using separate inserts.
- Source/resource bounds, early physical-page PDF experiment; precise backend/dependency versions recorded in lockfile when installed.
- Live model/provider/budget/data-handling decision gates Story 2.5; hosting/region/email/cost and backup/cleanup gates Story 4.1. These remain backlog gates and do not block the local demo.

### UX Design Requirements

UX-DR1: Implement DESIGN tokens: light #f8fafc background, white surfaces, #172033 text, blue #315f91 accent, system fonts and readable existing text sizes; no sidebar/marketing layout.
UX-DR2: Compact material/settings region above results; whole region expanded initially/on error, collapsed only on success; Vis/rediger preserves all current state and focuses source control.
UX-DR3: Four accessible tabs (Sammendrag/Begreper/Flashcards/Quiz), roving focus and Arrow/Home/End handling; summary selected on generation.
UX-DR4: One practice item with count; separate card/quiz positions and per-item reveal sets; reference appears with answer; previous/next disabled at bounds and usable by keyboard.
UX-DR5: Labels, visible focus, polite status and useful validation; safe text rendering; usable at narrow width and 200% zoom; screen-reader checks before final acceptance.
UX-DR6: Norwegian UI and confirmed action/help text; discreet Demo – eksempeldata label; fixed examples distinct from arbitrary-source input.
UX-DR7: Authentication surfaces including signup/login/recovery and expired/error/link states, generic recovery messages, clearing private UI at logout/session failure.
UX-DR8: Save state, owner library with title/date/positions, empty state, open and named inline delete confirmation; reset never deletes saved records.
UX-DR9: Progress pending/error/conflict states, Hent siste fremdrift before stale writes, acknowledged positions restored with hidden answers on reopen.
UX-DR10: Busy disables duplicate Generate; error retains source/settings with retry; PDF coverage and insufficient-source notices; late responses ignored after reset/change/logout.

### FR Coverage Map

| Requirement | Stories completing live requirement (demo coverage is partial) |
| --- | --- |
| FR-1 | 1.2, 2.4, 2.5 |
| FR-2 | 2.4, 2.5 |
| FR-3, FR-4, FR-7, FR-9 | 2.5, 2.6 |
| FR-5, FR-6 | 1.1 (interaction), 2.5, 2.6 (live output) |
| FR-8 | 2.1, 2.2, 2.3 |
| FR-10 | 3.1, 3.2 |
| FR-11 | 3.2, 3.3 |
| FR-12 | 3.4 |
| NFR-1 | 2.6, 4.2 |
| NFR-2, NFR-3 | 1.2, 2.1–2.6, 3.1–3.4, 4.2 |
| NFR-4, NFR-5 | 1.1, 4.1, 4.2 |

## Epic List

1. **Try the complete study flow locally**: runnable fixed-data demo, plus early PDF feasibility evidence. No credentials needed.
2. **Study your own material privately**: account access, validated source extraction and real four-part generation. A live model decision is explicit before integration.
3. **Keep and resume your study material**: explicit owner save/open/delete and cross-device progress with safe conflict handling.
4. **Use and assess the finished app reliably**: hosted multi-device verification, reproducible local demo and final quality/accessibility evidence.

Epics 2–4 add different risk boundaries (external identity/model, durable storage, deployment/acceptance). Their shared UI changes are intentional, not a split by technical layers. Each works using only earlier epics. No optional scoring/export/mobile scope added.

## Epic 1: Try the complete study flow locally

An assessor can run and inspect the study interaction without cloud services. Covers NFR-4/5 and interaction portions of FR-3–FR-9; PDF experiment is feasibility evidence, not completed PDF support.

### Story 1.1: Run the four-part study demo

As an assessor, I want a local working example, so that I can inspect the study flow without credentials.

**Scope:** `app/main.py`, `app/api/demo.py`, `app/contracts/learning.py`, `app/services/demo.py`, `app/static/index.html`, `app/static/styles.css`, `app/static/app.js`, `pyproject.toml`, `uv.lock`, `README.md`, `tests/test_demo.py`, `tests/browser-demo.cjs`. AD-1/4/5/9; UX-DR1–6, UX-DR10. No template generator or database.

**Acceptance Criteria:**

**Given** a clean setup with uv and no service keys, **When** README startup is followed, **Then** FastAPI serves the same-origin study UI, labelled demo, with fixed material and a content-free health check.

**Given** a named demo fixture, **When** Generate is pressed, **Then** the browser obtains a validated four-part bundle from the demo API and collapses the whole material region after success; arbitrary text/files or language changes are never presented as genuinely processed.

**Given** results, **When** tabs/reveal/navigation are used, **Then** independent positions and per-item reveal state persist across tab changes, references appear with answers, and no further generation request occurs.

**Given** results or a pending response, **When** New session is pressed, **Then** workspace/results/reveals reset, the material region expands, and stale responses cannot repopulate it. Vis/rediger preserves state. Keyboard/focus and 390px/200% layout checks pass.

**Given** invalid demo input or a failed request, **When** the API/UI handles it, **Then** errors are understandable, input remains available with explicit retry and no fabricated success; private/live routes are not implemented as working demo shortcuts.

### Story 1.2: Verify physical PDF pages before integration

As a student, I want extraction limitations proven early, so that my references do not point to the wrong page.

**Scope:** `scripts/pdf_probe.py`, `tests/test_pdf_probe.py`, synthetic fixtures, `.docs/implementation-artifacts/pdf-experiment.md`. Depends on 1.1; AD-4; FR-1/7, NFR-3. Adopt candidate library only after experiment; lock tested version then.

**Acceptance Criteria:**

**Given** text on pages 1 and 3 with blank page 2 and image-only page 4, **When** the probe extracts text, **Then** original page positions survive and unreadable pages 2/4 are reported without OCR.

**Given** 40/41-page PDFs, 30,000/30,001 extracted code points, malformed/encrypted/oversized input and extraction timeout, **When** tested within bounded bytes/time/memory, **Then** limits reject safely without truncation and the report records observations and remaining limitations. No uploaded private fixture enters Git.

## Epic 2: Study your own material privately

Users can create an account and generate source-grounded material. Depends on Epic 1 only. Provider selection is a recorded gate before 2.5, not an invented model choice.

### Story 2.1: Sign up and sign in securely

As a student, I want my own account, so that private work is associated with my identity.

**Scope:** `app/api/auth.py`, `app/services/sessions.py`, `app/adapters/auth.py`, auth UI and `tests/test_auth.py`. FR-8, NFR-3; UX-DR7; AD-2/3. Configure Supabase test project/redirects without committing keys; no document tables yet.

**Acceptance Criteria:**

**Given** configured email/password Auth, **When** signup/confirmation/login succeeds, **Then** a validated user obtains an opaque HttpOnly same-origin cookie; tokens/passwords never enter browser storage or logs.

**Given** bad credentials, wrong callback binding, expired/replayed state or missing config, **When** submitted, **Then** no private session is created and understandable errors appear. Cookie-authenticated mutations require CSRF and same-origin protection; two browsers have isolated sessions.

**Given** private API responses, **When** returned, **Then** use no-store and prevent shared-cache exposure; never log tokens, source or generated content.

### Story 2.2: Recover a password through a restricted session

As a student, I want password recovery, so that I can regain account access.

**Scope:** auth adapter/routes, recovery UI and auth tests. Depends on 2.1. FR-8; UX-DR7; AD-3.

**Acceptance Criteria:**

**Given** any email, **When** recovery is requested, **Then** the response does not disclose account existence. A valid browser-bound PKCE callback creates a password-update-only session.

**Given** restricted, missing, expired, reused or wrong-browser recovery state, **When** document access or password change is attempted, **Then** only a valid restricted session may set a password, no document access is allowed, and errors explain restarting recovery. Successful update consumes the session and requires normal login.

### Story 2.3: End access on logout expiry and restart

As a student, I want predictable session endings, so that private material is not left accessible.

**Scope:** sessions/routes/UI and auth/browser tests. Depends on 2.2. FR-8; UX-DR7/10; AD-3.

**Acceptance Criteria:**

**Given** signed-in users on two devices, **When** logout, idle/absolute expiry or process restart ends a session, **Then** its private API access is denied, private UI is cleared with a sign-in-again action and old/late responses cannot restore it. Logout semantics and configured 30-minute idle/12-hour absolute defaults are tested; saved persistence is verified again in 3.2.

**Given** an unavailable identity provider, **When** logout is requested, **Then** local session denial/cookie clearing still completes and another device's independent session remains unaffected.

### Story 2.4: Validate and extract the active source

As a student, I want text/file/PDF input, so that my actual material supplies generation.

**Scope:** `app/api/sources.py`, `app/services/extraction.py`, `app/adapters/pdf.py`, source contracts, source UI and boundary tests. Depends on 1.2 and 2.3. FR-1/2/7; NFR-2/3; UX-DR2/5/10; AD-4.

**Acceptance Criteria:**

**Given** each input method, **When** accepted under authenticated access, **Then** only the active source supplies stable paragraph/page units and chosen subject/language/detail are retained. Empty, invalid encoding, unreadable or over-limit sources are rejected before model calls; exactly 30,000 Unicode code points/40 physical pages are accepted.

**Given** partial PDF text, **When** extracted, **Then** original physical pages remain and notices list unreadable pages; no text means no generation. Source changes invalidate old results/receipts and late responses. Private source is neither durably staged nor logged.

### Story 2.5: Generate all learning parts from the source

As a student, I want one action to generate all four parts, so that I can start practising my own material.

**Scope:** `app/api/generation.py`, `app/services/generation.py`, `app/adapters/model.py`, LearningBundle/receipt contracts, UI, adapter and failure tests. Depends on 2.4. FR-2–FR-7/9; NFR-2/3; UX-DR3/4/10; AD-4/5/6.

**Milestone gate:** record provider/model, quality/cost comparison, API access, budget ceiling, provider data handling and bounded timeout/output before implementing live calls. If unresolved, retain this story in backlog; do not substitute demo as live.

**Acceptance Criteria:**

**Given** a configured provider and validated source, **When** Generate is pressed once, **Then** one bounded request returns validated source-supported summary/concepts/cards/quiz or per-part insufficiency, in the selected output language and summary detail, with valid source IDs resolved by the server and a signed save receipt.

**Given** timeout, malformed schema, unknown references or provider error, **When** generation fails, **Then** every input/setting remains with explicit retry and no partial bundle/silent fallback; fanebytte/reveal/navigation never call AI. Source text remains transient until Save.

**Given** a current generation receipt, **When** source/settings/reset or a newer generation invalidates the workspace, **Then** bounded session/workspace receipt authority and ordered invalidation reject superseded receipts and late replies even before signature expiry; no durable unsaved snapshot is created.

### Story 2.6: Evaluate generated content against known sources

As a student, I want evidence of source fidelity, so that learning output can be checked rather than trusted blindly.

**Scope:** synthetic/public test inputs and `.docs/implementation-artifacts/content-evaluation.md`; generation fixes/tests as needed. Depends on 2.5. NFR-1, FR-3/4/7 and UX-DR10.

**Acceptance Criteria:**

**Given** three documents including text and PDF with five concepts/locations chosen before generation, **When** outputs are evaluated, **Then** sampled content is supported, sampled references are correct and at least four of five concepts are covered per document; unsupported content, wrong references and omissions are recorded separately and failures are fixed/rechecked. Conflicting subject context and insufficient material must not invent facts.

## Epic 3: Keep and resume your study material

Users retain explicitly saved source/results and resume privately across visits/devices. Depends on Epic 2. Tables are introduced with the feature that needs them.

### Story 3.1: Save a consistent private snapshot

As a student, I want an explicit Save action, so that only chosen material is retained.

**Scope:** `supabase/migrations/`, `app/api/documents.py`, `app/services/documents.py`, repository/storage adapters, save UI, RLS/lifecycle tests. FR-10, NFR-3; UX-DR8; AD-2/6/8.

**Acceptance Criteria:**

**Given** generated content and a valid owner/session-bound receipt, **When** Save is pressed, **Then** one idempotent pending operation leads to an owner-scoped ready source/settings/bundle/progress snapshot; missing/changed/expired receipt fails without persisting arbitrary client content.

**Given** failure/restart at upload, RPC commit or old-file cleanup, **When** the owner retries, **Then** durable operation state resumes without duplicate ready records or untracked files; success is shown only at ready. Transactional user-authenticated SECURITY INVOKER RPCs and RLS prevent cross-owner read/write. Replacement requires expected document revision and resets progress atomically.

**Given** the same operation ID replayed, **When** its immutable request digest differs, **Then** reject it; matching completed retries return the recorded outcome. First Save captures current valid practice positions; replacement Save resets positions for the new generation.

**Given** an explicitly admitted Save with immutable owner snapshot/digest, **When** the same owner reauthenticates after restart/receipt expiry within its seven-day admission lifetime, **Then** exact recovery uses that admitted operation plus fresh ownership/revision/lifecycle checks, not the expired receipt/session. Changed data, unknown/foreign admission or expired admission cannot commit; expired staging is erased and cleanup/replay cannot create content. Test lost commit replies and invalidation/admission races.

### Story 3.2: Open your private document library

As a student, I want My documents, so that saved work can be reopened without regenerating.

**Scope:** document list/open API, private file proxy, repository, library UI and two-account/restart tests. Depends on 3.1. FR-10/11; UX-DR8; AD-2/6/8.

**Acceptance Criteria:**

**Given** saved items, **When** listed/opened after browser/server restart and re-login or on another device, **Then** only the owner's ready items show safe title/date, stored source/settings/results and progress, with answers hidden and no AI request. Empty library explains Save.

**Given** another owner, changed identifiers, pending/deleting files or a missing session, **When** direct API/database/storage access is attempted, **Then** access is denied including file bytes. New session clears workspace without deleting saved records. Owner-only pending/recovery status remains discoverable.

### Story 3.3: Synchronize practice progress across devices

As a student, I want to continue where I stopped, so that switching devices does not lose my place.

**Scope:** progress RPC/migration, `app/api/progress.py`, service, sync UI and concurrent browser/RPC tests. Depends on 3.2. FR-11; UX-DR9; AD-7.

**Acceptance Criteria:**

**Given** a saved generation, **When** card/quiz positions change, **Then** independent valid item IDs autosave with acknowledged revision and pending/failure status; unsaved generations never persist. A second device resumes acknowledged positions with answers hidden.

**Given** two views of one generation, **When** a stale view writes after a newer acknowledgement, **Then** it cannot overwrite; show Fremdriften er endret på en annen enhet and Hent siste fremdrift before further writes. Backwards navigation after fresh load is allowed. Unknown retry outcomes, out-of-order responses and writes concurrent with replacement/deletion cannot restore old generations or overwrite newer revisions.

### Story 3.4: Delete saved material completely

As a student, I want named deletion confirmation, so that unwanted saved material is removed deliberately.

**Scope:** delete API/service/RPC, private storage cleanup, library confirmation and lifecycle tests. Depends on 3.3. FR-12; UX-DR8; AD-8.

**Acceptance Criteria:**

**Given** a saved item, **When** deletion is cancelled, **Then** nothing changes. **When** confirmed, **Then** deleting state blocks read/open/progress, removes file and rows, clears its active UI, and reports success only after all required removals.

**Given** storage/network failure or process crash, **When** retried by the owner, **Then** visible deleting/error state resumes idempotently without resurrection; another account cannot delete or read the item. Stale-operation cleanup and documented backup retention must be verified before real files.

**Given** current, old, provisional or uncertain in-flight uploaded objects, **When** deleting, **Then** track and reconcile all objects and wait for uncertain writes to quiesce before reporting success; retry cannot leave a late uploaded orphan.

## Epic 4: Use and assess the finished app reliably

Users can reach live private content from multiple devices and assessors can reproduce the demo. Depends on completed live Epics 2/3; this is a user availability/acceptance increment, not infrastructure-only work.

### Story 4.1: Reach the app securely from two devices

As a student, I want a hosted browser address, so that my PC and phone can reach the same private library.

**Scope:** deployment/config instructions, `.env.example`, README, health checks and operations evidence. FR-8/10/11; NFR-3/4; AD-9.

**Milestone gate:** verify and record hosting provider/region/plan/cost ceiling, Supabase region/quotas/email/redirects, HTTPS, backups/restore/deletion retention and cleanup procedure before provisioning or deployment. Paid/public actions need authorization specific to that action.

**Acceptance Criteria:**

**Given** an authorized configured deployment, **When** the same owner signs in on two devices, **Then** saved material/progress is available securely with one backend process, valid cookie/redirect settings and restart re-login behavior. Content-free health/error logs expose no material/tokens; owner isolation passes against real database/storage/API.

### Story 4.2: Verify the full release and assessor setup

As an assessor, I want reproducible instructions and evidence, so that I can evaluate the real scope and limitations.

**Scope:** README, browser/API/ownership tests, acceptance/evaluation reports and fixes. Depends on 4.1. All FRs/NFRs; UX-DR1–10.

**Acceptance Criteria:**

**Given** a clean checkout without keys, **When** README demo instructions run, **Then** the complete fixed-example flow works; live configuration/limits are documented separately with no real secrets. Private data never enters tracked files.

**Given** the live app, **When** all PRD checks, three-document evaluation, keyboard flow, 200% zoom/narrow-window and screen-reader walkthroughs run, **Then** evidence records observed outcomes and resolved failures, including two-account direct access, expiry/logout/restart, failure retry, explicit Save, cross-device conflicts and complete deletion. Optional EXT-1 remains excluded unless explicitly added after core acceptance.
