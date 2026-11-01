---
title: 'PRD: AI Study Buddy'
status: final
created: 2026-09-26
updated: 2026-11-01
---

# AI Study Buddy — short PRD

## Goal and boundaries

Implement the [product brief](../../briefs/brief-G79-hansen-2026-09-26/brief.md) as a manageable individual student project due approximately 15 December 2026 (exact date unconfirmed). Target core completion around 1 December to reserve two weeks for testing and corrections. Students across subjects should get an overview of their own material and start practising. The primary design scenario is a student preparing for a test with about 40 lecture slides. This is an illustrative scenario, not validated research. The core remains non-commercial; one optional extension is tracked separately below.

The functional capabilities below come from the assignment. Acceptance checks below define project completion; they do not replace the lecturer's assessment rubric. The [development plan](../../briefs/brief-G79-hansen-2026-09-26/development-plan.md) holds task order and unapproved technical proposals, including an early PDF experiment and later PDF integration.

## Delivery and build sequence

The first version runs locally in a browser. The assessor starts it using README instructions. Begin with a clearly labelled demo mode that works without API credentials. Demo mode is the first development increment, not a substitute for the final live AI capabilities. Select the AI provider/model, establish API access and review data handling and budget before integrating real generation. No public hosting is required.

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

### Session reset and conditional access

**FR-8:** If persistent storage or sharing is introduced later, security/login and checks against unauthorized access become required. V1 uses temporary sessions with no persistent storage, history or sharing, so login is not included. This is a design decision based on the conditional assignment requirement and lecturer feedback. The New session action clears pasted text, the uploaded file, course code/subject and all generated results, including revealed-answer state. It resets language to Norwegian and summary detail to short; avoid application caches, logs and disk storage of student content. Document session expiry/cleanup behavior before implementation. Provider handling must be checked separately before live use.

**Reset acceptance check:** enter pasted text, upload a file, fill in the subject, select English/detailed, generate results and reveal answers. Press New session. Verify both input methods are empty, subject and all results are cleared, no revealed answers remain, and Norwegian/short are restored. Generating immediately afterward must report empty input rather than reuse previous material.

### Combined generation flow

**FR-9:** One press of Generate creates the summary, key concepts, flashcards and quiz together for the current document and selected settings. The student does not choose a single learning function before generation. Show the four outputs in clearly labelled sections. Flashcard and quiz answers remain hidden after generation until explicitly revealed. This describes user-visible behavior, not the number of API calls.

**Acceptance check:** supply a known document, select settings and press Generate once. Verify all four sections appear for that document, with supporting references. Verify no flashcard or quiz answer is visible initially and that requesting one answer reveals that answer. Repeat with new material and verify answers start hidden again.

### Scope and source sufficiency

Online buying/selling, saved libraries, export, spaced repetition, multiple-document analysis and mobile apps are outside v1. OCR and table/figure interpretation are also excluded. No fixed item count, scoring or export is required in v1. Adapt the number of key concepts, flashcards and quiz questions to the source material. Generate only source-supported items; if the material is too short or incomplete for a learning section, explain the limitation in that section rather than inventing content. All four sections remain visible, with supported content or an explanation of insufficient material.

## Quality and checks

- **NFR-1 — agreed content goals:** use three documents, identifying five central concepts and source locations per document before generation. All checked generated content must be supported, all checked references correct, and at least four of five concepts included. Record errors and fixes. Counter-checks: record unsupported content, incorrect references and missing concepts separately; coverage must never be improved by adding unsupported items. These sample checks do not prove accuracy for all material or improved grades.
- **NFR-2 - error behavior:** reject empty/unreadable input with an understandable correction message. A generation failure preserves source material, subject, language and detail settings; show an understandable error and a Try again button that retries those inputs without re-entry. Never present incomplete generation as a complete result. Explain insufficient source material instead of inventing content.
- **NFR-3 - input limits and data handling:** accept at most 40 physical PDF pages and 30,000 source-text characters. The character limit applies to pasted text, text files and total PDF-extracted text; PDFs must meet both limits. If either limit is exceeded, reject before live AI requests and ask for a shorter excerpt; never truncate automatically. These provisional limits can change after testing if the decision is recorded. Keep credentials and student material out of Git, logs, persistent storage and shared application caches. Define session expiry/cleanup and review provider data handling before live use.

**Input-limit acceptance check:** verify 30,000 characters are accepted and 30,001 rejected for pasted text, text-file content and PDF-extracted text. Verify a 40-page PDF within the character limit is accepted and a 41-page PDF is rejected even with little text. Count blank/image-only pages toward the physical page limit. For oversized inputs, verify a clear shorter-excerpt message, no silent truncation and no live AI request.

**Insufficient-material acceptance check:** use a short factual excerpt and incomplete material. Verify every generated item is supported, item counts can be lower than for richer material, and sections that cannot be generated show an understandable explanation instead of invented concepts, questions or answers. An insufficient-material explanation is distinct from a technical generation failure.

**Failure acceptance check:** simulate a failed generation after supplying material and non-default settings. Verify the source and every setting remain available, an understandable error and Try again button appear, and retry uses the same source/settings. After a successful retry, all four sections appear with flashcard and quiz answers initially hidden.

Test each small task as described in the development plan. The final check includes every required output for text and PDF; working text-only increments do not constitute assignment completion. Balance concept coverage against factual support: do not add unsupported concepts merely to reach the target.

## Demo, usability and optional extension

- **NFR-4 - demo and setup:** run locally without a key using clearly labelled fixed example material and responses. Demo mode does not generate answers for arbitrary uploads. Verify startup and the complete example flow without credentials. README explains demo/live modes, limitations and the assessor's own API key; provide an example secrets file without real secrets.
- **NFR-5 - usability:** show summary, key concepts, flashcards and quiz in clearly labelled sections after one Generate action; show paragraph/page references beside their content. Use labelled inputs, readable contrast and keyboard-operable answer reveal; manually check the primary study flow.
- **EXT-1 - optional, after core acceptance:** multiple-choice quiz with automatic marking and source-supported explanations. Check correct/incorrect answers, score calculation and explanation references if included. No saved sessions or login are added. Record inclusion explicitly before implementing.

## Deferred decisions and architecture handoff

| Owner | Decision | Revisit point |
| --- | --- | --- |
| Student | Confirm approximately 15 December deadline and required delivery/process evidence. | Before final delivery scheduling; plan core completion around 1 December. |
| Student, supported by assistant | Provider/model, API access/budget, request limits and cloud data handling; adjust agreed document limits only if testing justifies a recorded change. | Before live AI integration; do not upload student content before this check. |
| Student, supported by assistant | Final stack/PDF library and session expiry/cleanup implementation. | Before implementing affected tasks and finalizing architecture. |

No unresolved product requirement blocks UX or architecture. The decisions above have explicit owners and revisit points; technical implementation details are collected in [the architecture handoff](addendum.md). Final status means the requirements are ready for downstream planning, not that the application is implemented or tested.

## Completion and terminology

V1 is complete when all required FR/NFR acceptance checks pass, including the three-document live-generation quality evaluation and startup from README in key-free demo mode. Record observed results and corrections in the development/test log. EXT-1 is optional and cannot compensate for failed core checks.

A source is the single active pasted text or uploaded file. A PDF page means its original physical position, including blank pages. A source reference identifies a supporting paragraph for text or physical page for PDF. A session is temporary application state without saved history. Demo mode uses fixed example material/responses; live mode generates from the student's active source using the selected provider.
