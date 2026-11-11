---
title: 'PRD: AI Study Buddy'
status: draft
created: 2026-09-26
updated: 2026-11-10
---

# AI Study Buddy — short PRD

## Goal and boundaries

Implement the [product brief](../../briefs/brief-G79-hansen-2026-09-26/brief.md) as a manageable individual student project due approximately 15 December 2026 (exact date unconfirmed). Target core completion around 1 December to reserve two weeks for testing and corrections. Students across subjects should get an overview of their own material and start practising. The primary design scenario is a student preparing for a test with about 40 lecture slides. This is an illustrative scenario, not validated research. The core remains non-commercial; one optional extension is tracked separately below.

The functional capabilities below come from the assignment. Acceptance checks below define project completion; they do not replace the lecturer's assessment rubric. The [development plan](../../briefs/brief-G79-hansen-2026-09-26/development-plan.md) holds task order and unapproved technical proposals, including an early PDF experiment and later PDF integration.

## Delivery and build sequence

The live application must support access to the same private saved content from multiple devices through a hosted browser application. Python/FastAPI serves the HTML/CSS/JavaScript interface. Supabase Auth, Postgres and private Storage are selected for accounts, saved content/progress and uploaded files. Keep a locally runnable example-data demo that the assessor starts from README without cloud credentials. Begin with a clearly labelled demo mode that works without API credentials. Demo mode is the first development increment, not a substitute for the final live AI capabilities. Select the AI provider/model, establish API access and review data handling and budget before integrating real generation. Choose the hosting provider and configuration in architecture before deployment; provider selection does not imply that deployment or paid subscriptions have occurred.

## Functional requirements

### Inputs

| ID | Required capability | Acceptance check |
| --- | --- | --- |
| FR-1 | Accept pasted text, one uploaded text file or one uploaded text-based PDF, using exactly one input method at a time. | Each of the three input methods enters the same learning flow. Only the selected method supplies source material; inactive pasted text or uploads are not combined with it. Support text-based slide exports. Exclude OCR and table/figure interpretation. For a partly readable PDF, process readable pages, list the original page numbers without readable text and explain that results cover only extracted text. Preserve original physical page numbers in references. If no page has readable text, do not generate; ask for a text-based PDF or pasted text. |
| FR-2 | Accept optional course code/subject, detail level and language/preferences. | Generation succeeds with course code/subject left blank. If supplied, use it only as context: all factual content and answers must remain supported by the active source material. Default to Norwegian and a short summary. Before generation, the student may select English and/or a detailed summary independently. The chosen language applies to summary, key concepts, flashcards and quiz, including their answers and explanations; summary detail controls the summary. |

**Input acceptance check:** generate from pasted text, a text file and a text-based PDF separately. Switch methods with material still present in the previous method and verify only the active source is used. Do not display previous outputs as results for the newly selected source; new generation starts with flashcard and quiz answers hidden. Empty active input is rejected even if an inactive method contains material.

**Settings acceptance check:** a new session defaults to Norwegian and a short summary. Generate with Norwegian/English and short/detailed choices independently; verify all four learning sections and their answers use the selected language, and the summary reflects the selected detail level.

**PDF coverage acceptance check:** use a PDF with readable text on pages 1 and 3, a blank page 2 and an image-only page 4. Verify pages 2 and 4 are listed as having no readable text, results clearly state they cover extracted text only, and references to page 3 remain page 3. For a PDF with no readable text on any page, verify no generation request is made and the message asks for a text-based PDF or pasted text.

**Context acceptance check:** generate with a blank subject field, then with a relevant subject and a deliberately conflicting subject. Generation must remain available without the field and must not introduce facts or answers from outside the supplied material.

### Learning outputs

| ID | Required capability | Acceptance check |
| --- | --- | --- |
| FR-3 | Generate a summary. | Summary points accurately describe supplied material at the selected detail level. |
| FR-4 | Generate key concepts. | A visible concept list includes source-supported explanations and meets the agreed coverage target below. |
| FR-5 | Generate flashcards. | Question/answer pairs are present; each answer is hidden initially and revealed only when the student requests it. |
| FR-6 | Generate quiz questions and answers. | Questions are visible while answers are initially hidden; reveal each answer only on student request. Core v1 uses plain questions without automatic grading. |
| FR-7 | Provide source/page references. | Summary points, concepts and learning items refer to supporting text paragraphs or PDF pages. Page references preserve the original physical page position. |

### Login and workspace reset

**FR-8:** Use Supabase Auth with email and password: Create account, Log in, Forgot password and Log out. Password recovery must lead to a protected password-update step after a valid recovery link; configure confirmation/recovery redirects for each environment. Do not reveal account existence in reset responses. V1 includes login because user material and generated learning material are stored. Require authentication and enforce ownership on the server for list, read, generation-on-saved-source and delete actions. A user must never access another user's documents/results by changing an identifier. Logout ends access and clears active private content from the interface.

New session clears active pasted text/upload, subject, results and revealed-answer state and restores Norwegian/short. It starts a new workspace; it does not delete saved documents. Saved-document deletion is a separate explicit action under FR-12. Explain this distinction in the interface.

**Acceptance checks:** unauthenticated requests cannot list/read/delete private material. With two accounts, user B cannot list/open/delete user A's material, including direct requests with A's identifiers. After logout, protected requests are denied and the private workspace is cleared. New session restores defaults while previously saved material remains available only to its owner.

### Combined generation flow

**FR-9:** One press of Generate creates the summary, key concepts, flashcards and quiz together for the current document and selected settings. The student does not choose a single learning function before generation. Show the four outputs in clearly labelled sections. Flashcard and quiz answers remain hidden after generation until explicitly revealed. This describes user-visible behavior, not the number of API calls.

**Acceptance check:** supply a known document, select settings and press Generate once. Verify all four sections appear for that document, with supporting references. Verify no flashcard or quiz answer is visible initially and that requesting one answer reveals that answer. Repeat with new material and verify answers start hidden again.

### Saved documents and learning material

| ID | Required capability | Acceptance check |
| --- | --- | --- |
| FR-10 | Persist the user's uploaded course document or pasted source and its generated learning material under that user's ownership only after an explicit Save action. Generation alone never persists the workspace. | Saved source, subject/settings and all four generated parts with references remain available after browser/server restart and when the same owner signs in on another device; reopening a saved result does not call the AI again. Record whether results are complete or generation failed; never present an incomplete set as complete. |
| FR-11 | Provide My documents with an owner-only list and open action. | Show an understandable title/file name and date. Open restores the corresponding source/settings and saved learning content, with original paragraph/page references, and resumes the last flashcard and quiz-question positions independently; do not mix results or progress from another source or owner. |
| FR-12 | Allow the owner to delete a saved document and its associated learning material. | A clear deletion action removes the item from the owner's list and prevents subsequent direct retrieval of source/results. Deleting an active item also clears its active view. A failed deletion keeps the item visible with an understandable retry message. Other users cannot delete it. |

Explicit Save is selected. Saving stores the source, settings and currently generated learning material together; New session does not delete saved items. Email/password account creation and password recovery are selected. Provider configuration, hosting and the technical mechanism for saving progress remain open. The user requires continuing at the last flashcard and quiz question when a saved document is reopened, including across visits. Owner: student with assistant; resolve UX behavior before finalizing revised UX and implementation details in architecture before affected stories. Persistence of progress across tab changes remains required; Cross-visit card and quiz positions must persist independently per saved document and owner. New session does not erase that saved progress. Decide progress-write timing in architecture without introducing automatic persistence of unsaved source/results. Document/library sharing, CV-specific processing and advanced folders/search remain outside this change.

### Scope and source sufficiency

Online buying/selling, export, spaced repetition, multiple-document analysis and mobile apps are outside v1. OCR and table/figure interpretation are also excluded. No fixed item count, scoring or export is required in v1. Adapt the number of key concepts, flashcards and quiz questions to the source material. Generate only source-supported items; if the material is too short or incomplete for a learning section, explain the limitation in that section rather than inventing content. All four sections remain visible, with supported content or an explanation of insufficient material.

## Quality and checks

- **NFR-1 — agreed content goals:** use three documents, identifying five central concepts and source locations per document before generation. All checked generated content must be supported, all checked references correct, and at least four of five concepts included. Record errors and fixes. Counter-checks: record unsupported content, incorrect references and missing concepts separately; coverage must never be improved by adding unsupported items. These sample checks do not prove accuracy for all material or improved grades.
- **NFR-2 - error behavior:** reject empty/unreadable input with an understandable correction message. A generation failure preserves source material, subject, language and detail settings; show an understandable error and a Try again button that retries those inputs without re-entry. Never present incomplete generation as a complete result. Explain insufficient source material instead of inventing content.
- **NFR-3 - input limits and data handling:** accept at most 40 physical PDF pages and 30,000 source-text characters. The character limit applies to pasted text, text files and total PDF-extracted text; PDFs must meet both limits. If either limit is exceeded, reject before live AI requests and ask for a shorter excerpt; never truncate automatically. These provisional limits can change after testing if the decision is recorded. Keep credentials, private documents, database files and generated private learning material out of Git and logs. Store private content only through the owner-scoped persistence layer; never expose it through static file serving or shared caches. Define authenticated-session expiry/logout and review provider data handling before live use.

**Input-limit acceptance check:** verify 30,000 characters are accepted and 30,001 rejected for pasted text, text-file content and PDF-extracted text. Verify a 40-page PDF within the character limit is accepted and a 41-page PDF is rejected even with little text. Count blank/image-only pages toward the physical page limit. For oversized inputs, verify a clear shorter-excerpt message, no silent truncation and no live AI request.

**Insufficient-material acceptance check:** use a short factual excerpt and incomplete material. Verify every generated item is supported, item counts can be lower than for richer material, and sections that cannot be generated show an understandable explanation instead of invented concepts, questions or answers. An insufficient-material explanation is distinct from a technical generation failure.

**Failure acceptance check:** simulate a failed generation after supplying material and non-default settings. Verify the source and every setting remain available, an understandable error and Try again button appear, and retry uses the same source/settings. After a successful retry, all four sections appear with flashcard and quiz answers initially hidden.

Test each small task as described in the development plan. The final check includes every required output for text and PDF; working text-only increments do not constitute assignment completion. Balance concept coverage against factual support: do not add unsupported concepts merely to reach the target.

## Demo, usability and optional extension

- **NFR-4 - demo and setup:** run locally without a key using clearly labelled fixed example material and responses. Demo mode does not generate answers for arbitrary uploads. Verify startup and the complete example flow without credentials. README explains demo/live modes, limitations and the assessor's own API key; provide an example secrets file without real secrets.
- **NFR-5 - usability:** show summary, key concepts, flashcards and quiz in clearly labelled sections after one Generate action; show paragraph/page references beside their content. Use labelled inputs, readable contrast and keyboard-operable answer reveal; manually check the primary study flow.
- **EXT-1 - optional, after core acceptance:** multiple-choice quiz with automatic marking and source-supported explanations. Check correct/incorrect answers, score calculation and explanation references if included. Login and saved documents are now required core features under FR-8 and FR-10 through FR-12; this quiz extension remains optional. Record inclusion explicitly before implementing.

## Deferred decisions and architecture handoff

| Owner | Decision | Revisit point |
| --- | --- | --- |
| Student | Confirm approximately 15 December deadline and required delivery/process evidence. | Before final delivery scheduling; plan core completion around 1 December. |
| Student, supported by assistant | Provider/model, API access/budget, request limits and cloud data handling; adjust agreed document limits only if testing justifies a recorded change. | Before live AI integration; do not upload student content before this check. |
| Student, supported by assistant | PDF library, hosting provider, account/session configuration and progress-write mechanism; Supabase Auth/Postgres/private Storage are selected; Python/FastAPI with HTML/CSS/JavaScript is selected. | Before implementing affected tasks and finalizing architecture. |

The 2026-11-10 storage/login scope change reopens this PRD and the affected UX surfaces. Architecture can proceed, but revised authentication/library UX must be settled before their stories are finalized. The decisions above have explicit owners and revisit points; technical implementation details are collected in [the architecture handoff](addendum.md). Final status means the requirements are ready for downstream planning, not that the application is implemented or tested.

## Completion and terminology

V1 is complete when all required FR/NFR acceptance checks pass, including the three-document live-generation quality evaluation and startup from README in key-free demo mode. Record observed results and corrections in the development/test log. EXT-1 is optional and cannot compensate for failed core checks.

A source is the single active pasted text or uploaded file. A PDF page means its original physical position, including blank pages. A source reference identifies a supporting paragraph for text or physical page for PDF. A session is an authenticated interaction; active workspace state is distinct from owner-scoped saved documents and results. Demo mode uses fixed example material/responses; live mode generates from the student's active source using the selected provider.

## Scope revision - 2026-11-10

The user explicitly requests login, saved documents/results, My documents, open/delete and cross-user access checks in v1. This supersedes the earlier temporary-only/no-database plan. The prior finalization/review reports describe the earlier scope and do not validate this revision. New work adds account/session management, persistence, ownership checks, library UX and restart/deletion tests. Reassess delivery scheduling after architecture; do not silently drop existing core quality goals. No public hosting or paid service is approved by this requirements change.

**Explicit-save acceptance check:** generate without pressing Save, reload and verify no new saved item was created. Press Save and verify the source/settings/results reopen from My documents after restart. New session preserves previously saved items. Changing or regenerating content must not overwrite a saved item without another explicit save action.

**Resume acceptance check (2026-11-10):** save a document, navigate to different flashcard and quiz positions, leave and reopen it, including after browser/server restart. Both positions must resume independently. Another saved document and another account must not inherit those positions. New session starts an empty workspace but must not erase the saved document or its progress. A fresh generation starts a new set with initial positions; do not apply old indices blindly to regenerated items. Progress-write timing and reopened revealed-answer handling remain architecture/UX details.

**Multi-device acceptance check:** user A saves a document and advances card/quiz positions on device 1, then signs in as A on device 2 and reopens the same content/progress. User B on either device must be unable to list/read/update/delete A's records or private files, including direct database/storage/API requests. Local demo mode remains runnable without Supabase or model credentials. Supabase tables and private Storage require owner-scoped access rules; selecting Supabase does not replace these checks.

**Authentication acceptance check:** create an account with email/password, complete any required confirmation, log in, log out and request password recovery. Only a valid recovery session may update the password. Expired/invalid links show a recovery action; wrong credentials show an understandable error without opening private content. Recovery responses do not disclose whether an email has an account. Demo mode must not send real emails or create real accounts.
