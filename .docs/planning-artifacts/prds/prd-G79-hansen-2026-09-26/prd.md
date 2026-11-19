---
title: 'PRD: AI Study Buddy'
status: final
created: 2026-09-26
updated: 2026-11-19
---

# AI Study Buddy — product requirements

## Goal and boundaries

Implement the [product brief](../../briefs/brief-G79-hansen-2026-09-26/brief.md) as a manageable individual IBE160 project at Molde University College. The complete assignment is due **15 December2026**. Target a working core by1 December and an application/README/report package by8 December, leaving9–14 December as correction buffer. The core remains non-commercial.

The capabilities combine the supplied brief and student-approved scope. These project checks do not replace the full assignment or assessment rubric, which still require a final delivery check. The [development plan](../../briefs/brief-G79-hansen-2026-09-26/development-plan.md) records the build sequence; current delivery priorities below supersede older deployment proposals.

### Product hypothesis and user

A student preparing for a test has a lecture export of about40 slides and needs an overview and a way to practise. StudyBuddy aims to provide a repeatable, source-referenced study flow without composing a new chatbot prompt for every task. Its value hypothesis is that the fixed four-part format and visible references make starting and checking practice easier; improved learning, speed or grades have not been established. This is the illustrative scenario from the accepted brief, not validated user research.

### UJ-1 — From lecture material to checked revision

This journey structures the already selected source/generate/practise flow; it introduces no new features.

| Step | Student action and observable outcome | Requirements |
| --- | --- | --- |
| 1 | Provide one readable text/PDF excerpt; choose language/detail or keep defaults. Invalid/oversized input gives a correction message before a model request. | FR-1, FR-2; NFR-2, NFR-3 |
| 2 | Press Generate once; receive four labelled sections with source references or an explicit insufficiency explanation. | FR-3–FR-7, FR-9; NFR-1 |
| 3 | Read the summary, check a reference, practise cards/quiz and reveal answers deliberately. Positions remain independent. | FR-5–FR-7, NFR-5 |
| 4 | In configured live mode, explicitly Save and later reopen the same owner's work; delete it deliberately when no longer wanted. | FR-8, FR-10–FR-12 |

Value is observable when the student can locate the supporting source and complete the practice flow. Content quality is checked against NFR-1, not inferred from a successful API response.

### Glossary

| Term | Meaning |
| --- | --- |
| Source | The one active pasted text, text file or text-based PDF; inactive inputs are not combined. |
| Source reference | Supporting paragraph or original physical PDF page, including original page numbering. |
| Workspace | Current source, settings, generated results and practice state; unsaved work has no durability guarantee. |
| Login session | Authenticated access for one browser; distinct from the workspace and the New session UI action. |
| New session | Clear active work and restore defaults; keep previously saved documents. |
| Generation | One complete result for a source/settings combination; regeneration does not overwrite a saved item implicitly. |
| Saved document | Owner-linked source, settings, learning results, saved progress and original file where applicable. |
| Demo | Fixed synthetic source/responses without account or model credentials; it does not process arbitrary uploads. |

### Delivery priorities and fallback

| Priority | Scope | Delivery rule |
| --- | --- | --- |
| Must | FR-1–FR-7, FR-9 and NFR-1–NFR-5: supported text/PDF flow, four learning parts, content checks, honest failures, key-free setup and usable UI. | Core by1 December; remaining evidence/README/report by8 December. |
| Retain completed extension | Existing FR-8, FR-10–FR-12 and implemented progress/conflict handling. | Keep functionality and safety controls; reuse evidence and fix actual defects. Do not rebuild storage or add new sync features. Open acceptance boundaries remain explicit. |
| If time, with separate decision | Public HTTPS/physical two-device deployment and EXT-1 multiple-choice marking. | Optional/deferred; no implied authorization or claim that deployment acceptance passed. |

If core checks still fail on1 December, stop optional expansion and prioritize core correction, reproducible setup and the report. Do not silently remove implemented features, lower source-quality goals or weaken ownership to meet the date. No new features after1 December;9–14 December is correction buffer.

## Delivery and build sequence

Local school delivery is the accepted19 November priority. The assessor must be able to start the fixed demo from README without private keys or paid accounts. Existing live source/generation/account/library features are retained and documented separately; demo evidence does not establish live acceptance. Public hosting/physical two-device checks are optional and deferred. Technology and operating mechanisms belong in the [architecture handoff](addendum.md); the unrelated `architecture/technology.md` example is not the StudyBuddy implementation contract.

## Functional requirements

### Inputs

| ID | Required capability | Acceptance check |
| --- | --- | --- |
| FR-1 | Accept pasted text, one uploaded text file or one uploaded text-based PDF, using exactly one input method at a time. | Each of the three input methods enters the same learning flow. Only the selected method supplies source material; inactive pasted text or uploads are not combined with it. Support text-based slide exports. Exclude OCR and table/figure interpretation. For a partly readable PDF, process readable pages, list the original page numbers without readable text and explain that results cover only extracted text. Preserve original physical page numbers in references. If no page has readable text, do not generate; ask for a text-based PDF or pasted text. |
| FR-2 | Accept optional course code/subject, detail level and language/preferences. | Generation succeeds with course code/subject left blank. If supplied, use it only as context: all factual content and answers must remain supported by the active source material. Default to Norwegian and a short summary. Before generation, the student may select English and/or a detailed summary independently. The chosen language applies to summary, key concepts, flashcards and quiz, including their answers and explanations; summary detail controls the summary. |

Detailed input/settings/PDF/context boundary cases are preserved in the
[acceptance handoff](addendum.md#boundary-and-workflow-acceptance-cases).

### Learning outputs

| ID | Required capability | Acceptance check |
| --- | --- | --- |
| FR-3 | Generate a source-supported summary. | Each checked point has at least one supporting reference and no claim absent from the source; verify all points on the three NFR-1 documents, at the selected detail level. |
| FR-4 | Generate explained key concepts. | On each of the three NFR-1 documents, cover at least four of the five concepts selected before generation; every checked explanation/reference is source-supported. Richer inputs need no fixed global item count. |
| FR-5 | Generate flashcards. | Question/answer pairs are present; each answer is hidden initially and revealed only when the student requests it. |
| FR-6 | Generate quiz questions and answers. | Questions are visible while answers are initially hidden; reveal each answer only on student request. Core v1 uses plain questions without automatic grading. |
| FR-7 | Provide source/page references. | Summary points, concepts and learning items refer to supporting text paragraphs or PDF pages. Page references preserve the original physical page position. |

### Login and workspace reset

**FR-8** remains the stable umbrella ID for existing architecture/stories. Its acceptance responsibilities are:

| Sub-ID | Capability and consequence | Acceptance |
| --- | --- | --- |
| FR-8a | Create account, confirm if required, log in and log out. | Wrong credentials deny private access; logout clears private UI/access, including uncertain provider outcomes. Other devices remain signed in. |
| FR-8b | Recover a password through a valid restricted recovery session. | Invalid/expired links cannot update it; recovery is not ordinary login and never reveals whether an account exists. Configure the correct confirmation/recovery redirect per environment. |
| FR-8c | Enforce authenticated ownership for every private operation. | User B cannot list/read/generate from/update/delete user A's records/files through UI, changed IDs or direct API/database/storage access. Unauthenticated requests are denied. |

New session clears active pasted text/upload, subject, results and revealed-answer state and restores Norwegian/short. It starts a new workspace; it does not delete saved documents. Saved-document deletion is a separate explicit action under FR-12. Explain this distinction in the interface.

**Acceptance checks:** unauthenticated requests cannot list/read/delete private material. With two accounts, user B cannot list/open/delete user A's material, including direct requests with A's identifiers. After logout, protected requests are denied and the private workspace is cleared, including when provider revocation fails or times out. Other devices remain signed in. New session restores defaults while previously saved material remains available only to its owner.

### Combined generation flow

**FR-9:** One press of Generate creates the summary, key concepts, flashcards and quiz together for the current document and selected settings. The student does not choose a single learning function before generation. Show the four outputs in clearly labelled sections. Flashcard and quiz answers remain hidden after generation until explicitly revealed. This describes user-visible behavior, not the number of API calls.

**Acceptance check:** supply a known document, select settings and press Generate once. Verify all four sections appear for that document, with supporting references. Verify no flashcard or quiz answer is visible initially and that requesting one answer reveals that answer. Repeat with new material and verify answers start hidden again.

### Saved documents and learning material

| ID | Required capability | Acceptance check |
| --- | --- | --- |
| FR-10 | Persist the user's uploaded course document or pasted source and its generated learning material under that user's ownership only after an explicit Save action. Generation alone never persists the workspace. | Saved source, subject/settings and all four generated parts with references remain available after browser/server restart and when the same owner signs in on another device; reopening a saved result does not call the AI again. Record whether results are complete or generation failed; never present an incomplete set as complete. |
| FR-11 | Provide My documents with an owner-only list and open action. | Show an understandable title/file name and date. Open restores the corresponding source/settings and saved learning content, with original paragraph/page references, and resumes the last flashcard and quiz-question positions independently; do not mix results or progress from another source or owner. |
| FR-12 | Allow the owner to delete a saved document and its associated learning material. | A clear deletion action removes the item from the owner's list and prevents subsequent direct retrieval of source/results. Deleting an active item also clears its active view. A failed deletion keeps the item visible with an understandable retry message. Other users cannot delete it. |

Explicit Save stores source, settings and current generated material together; upload/generation alone never saves it. New session preserves saved items. Changing or regenerating content requires another explicit Save. For already-saved generations, flashcard and quiz positions update automatically and independently; unsaved progress remains browser-only. Reopen restores acknowledged positions with answers hidden, while tab changes within one visit retain revealed answers. Stale views must fetch current progress before writing; pending/failed synchronization is visible. Technical recovery, revision and operation contracts are in the architecture handoff.

Detailed restart/progress-conflict cases are preserved in the
[acceptance handoff](addendum.md#boundary-and-workflow-acceptance-cases).

### Scope and source sufficiency

Online buying/selling, export, spaced repetition, multiple-document analysis and mobile apps are outside v1. OCR and table/figure interpretation are also excluded. No fixed item count, scoring or export is required in v1. Adapt the number of key concepts, flashcards and quiz questions to the source material. Generate only source-supported items; if the material is too short or incomplete for a learning section, explain the limitation in that section rather than inventing content. All four sections remain visible, with supported content or an explanation of insufficient material.

## Quality and checks

- **NFR-1 — agreed content goals:** use three documents, identifying five central concepts and source locations per document before generation. All checked generated content must be supported, all checked references correct, and at least four of five concepts included. Record errors and fixes. Counter-checks: record unsupported content, incorrect references and missing concepts separately; coverage must never be improved by adding unsupported items. These sample checks do not prove accuracy for all material or improved grades.
- **NFR-2 - error behavior:** reject empty/unreadable input with an understandable correction message. A generation failure preserves source material, subject, language and detail settings; show an understandable error and a Try again button that retries those inputs without re-entry. Never present incomplete generation as a complete result. Explain insufficient source material instead of inventing content.
- **NFR-3 - input limits and data handling:** accept at most 40 physical PDF pages and 30,000 source-text characters. The character limit applies to pasted text, text files and total PDF-extracted text; PDFs must meet both limits. If either limit is exceeded, reject before live AI requests and ask for a shorter excerpt; never truncate automatically. These provisional limits can change after testing if the decision is recorded. Keep credentials, private documents, database files and generated private learning material out of Git and logs. Store private content only through the owner-scoped persistence layer; never expose it through static file serving or shared caches. Define authenticated-session expiry/logout and review provider data handling before live use.

Detailed input-limit/insufficiency/retry cases are preserved in the
[acceptance handoff](addendum.md#boundary-and-workflow-acceptance-cases).

Test each small task as described in the development plan. The final check includes every required output for text and PDF; working text-only increments do not constitute assignment completion. Balance concept coverage against factual support: do not add unsupported concepts merely to reach the target.

## Demo, usability and optional extension

### Existing live limits and unsupported output (NFR-2, NFR-3)

Live generation uses the selected OpenAI `gpt-6-luna` integration with an
application reservation budget of **USD5 for the lifetime of its preserved
journal**, reserving **USD0.05 per admitted attempt** (at most100 attempts).
Uncertain attempts are not refunded and restart must not reset the journal.
This application allowance is not a guarantee about the provider account's
entire invoice. At budget denial, do not dispatch; retain material and show
«Budsjettet er utilgjengelig eller brukt opp. Materialet er beholdt.»

Admit at most **one generation per login session and two in total per backend
process** at once; excess requests receive a wait/retry message, not a hidden
queue or automatic model retry. Generation has a60-second request deadline.
These are the existing implemented limits, not a new per-hour quota.

Missing/unknown source references or invalid output structure reject the whole
generation without publishing a partial success. A valid empty learning
section carries an explicit insufficient-material explanation. Structurally
valid references do not prove semantic correctness: every checked factual
claim still needs the NFR-1 source comparison. This avoids mislabeling a
technical validation failure as insufficient course material.

Evidence and cost evaluation are recorded in
[generation](../../../implementation-artifacts/spec-2-5-generate-all-learning-parts-from-the-source.md)
and [registered content evaluation](../../../implementation-artifacts/content-evaluation.md).

- **NFR-4 - demo and setup:** run locally without a key using clearly labelled fixed example material and responses. Demo mode does not generate answers for arbitrary uploads. Verify startup and the complete example flow without credentials. README explains demo/live modes, limitations and the assessor's own API key; provide an example secrets file without real secrets.
- **NFR-5 - usability:** show summary, key concepts, flashcards and quiz in clearly labelled sections after one Generate action; show paragraph/page references beside their content. Use labelled inputs, readable contrast and keyboard-operable answer reveal; manually check the primary study flow.
- **EXT-1 - optional, after core acceptance:** multiple-choice quiz with automatic marking and source-supported explanations. Check correct/incorrect answers, score calculation and explanation references if included. Login and saved documents are now required core features under FR-8 and FR-10 through FR-12; this quiz extension remains optional. Record inclusion explicitly before implementing.

## Decisions and remaining handoff

| Owner | Decision | Revisit point |
| --- | --- | --- |
| Student | Confirmed hard deadline15 December2026; core target1 December, full package8 December. Full assignment/rubric reconciliation and own report text remain. | Complete delivery checks before8 December target. |
| Student + builder | OpenAI/gpt-6-luna, existing USD5 application allowance, request limits and pypdf7.0.1 are selected/implemented; registered content evaluation exists. No new evaluation calls authorized here. | Revisit only for a concrete defect or separately agreed scope change. Preserve budget/safety boundaries. |
| Student + builder | Existing Supabase Free/Paris retained. Public HTTPS/physical-device deployment and further backup automation are optional/deferred. Preserve known email/PDF/real-data acceptance limits. | Before any later public deployment or use of real private material; separate approval still required. |

The table distinguishes selected decisions from remaining delivery checks. The [architecture handoff](addendum.md) preserves technical contracts; the [delivery checklist](../../../implementation-artifacts/delivery-checklist-2026-11-19.md) records actual evidence and open limits. PRD final status means requirements readiness, not a claim that every implementation/release check has passed.

## Completion and terminology

**Delivery revision19 November2026, accepted by the student:** Prioritize the
locally runnable school submission. Public hosting/Funnel and acceptance on two
physical devices are optional/deferred, not completed release claims. Retain
implemented Supabase login, Save/library/progress/deletion, persistence and owner
isolation; do not rewrite storage. Multi-device checks below remain the target
for any later hosted delivery. For this local submission verify separate
sessions, persistence, stale-update handling and cross-user access using existing
evidence plus focused checks where needed. Continue with synthetic test data;
complete backup/restore and public-operation gates remain prerequisites for
real private data/public deployment, not claims established by the demo.
Story4.2 assessor setup can proceed without Story4.1. No new optional features.
Working-core target1 December; submission package target8 December; hard deadline
15 December2026, including report/README. See
[accepted delivery scope](../../../implementation-artifacts/leveranseavgrensning-2026-11-19.md).

V1 is complete when all required FR/NFR acceptance checks pass, including the three-document live-generation quality evaluation and startup from README in key-free demo mode. Record observed results and corrections in the development/test log. EXT-1 is optional and cannot compensate for failed core checks.

Use the glossary above: login session, workspace and the New session action are distinct. PDF references retain original physical positions, including blank pages. Demo and live evidence must remain distinguishable.

## Change log and detailed acceptance

- 10 November: user selected account, explicit Save, library and deletion.
- 11 November: independent saved progress and conflict/refetch behavior adopted.
- 19 November: local submission prioritized; implemented features retained,
  public hosting optional, deadline confirmed. Lecturer feedback reconciled.

Detailed save/recovery/ownership continuity cases moved unchanged to the
[architecture handoff](addendum.md#detailed-live-acceptance-continuity-moved19-november2026).
They preserve technical depth without mixing it into the product narrative.
