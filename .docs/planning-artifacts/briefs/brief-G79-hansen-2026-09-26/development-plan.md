# AI Study Buddy — development plan

Build order and the early PDF experiment are user-approved. Local browser delivery, README startup and demo-first development are user-approved. Task boundaries, final technology and detailed checks below remain proposals. Final scope and quality goals are in [the brief](brief.md); its revised scope decisions apply here too. Temporary sessions and text-based PDFs are settled; provider/model, budget and final stack remain open.

## Small tasks and checks

Finish one task and record its result before continuing. Adapt concept, flashcard and quiz counts to the source; test short/incomplete material and require an explanation in any section that cannot be supported, rather than invented content. Build fixed responses into a labelled demo mode with supplied example material, usable without an API key. Demo mode does not generate answers for arbitrary uploads. Use separate real AI calls for content checks. Experiments are not completed product features.

| Order | Small task | Observable check |
| --- | --- | --- |
| 1a | Text box, Generate button and summary display using a fixed response. | The submitted text follows the expected flow; empty input is rejected. |
| 1b | Connect one model to generate a summary. | A short known text produces a supported summary. |
| 1c | Busy state and failed-request message. | A simulated generation failure preserves material and every setting, shows an understandable error and Try again button, and retries with the same inputs. A successful retry shows all four sections with answers initially hidden once those features exist. |
| 2 | Early standalone PDF experiment, before further feature work. | Extract a three-page PDF with distinct text on the first and third pages and a blank middle page. Preserve physical page positions; the last page remains page 3. Compare extracted text with the PDF. Try an image-only page and report absent usable text. Record findings and limitations, not an OCR solution. |
| 3a | Text-file upload alongside pasted text, with one active input method. | A sample file yields expected text; switching methods uses only the active source and invalidates previous results. Empty active input is rejected even if inactive input exists. |
| 3b | Optional course/subject, language and detail inputs. | Generation works with a blank subject; defaults are Norwegian/short. Allow English and detailed summary independently; all four sections and answers use the chosen language and the summary follows the detail setting. Relevant or conflicting course context must not introduce facts unsupported by the source. |
| 3c | Number text paragraphs and attach summary references. | Each checked reference identifies the supporting paragraph. |
| 4 | Key concepts, brief explanations and references. | Apply the agreed four-of-five concept check. |
| 5 | Flashcards with answer reveal. | Reveal works and each answer is supported by its reference. |
| 6 | Quiz questions and answer reveal. | A student can attempt a question before revealing the supported answer. No scoring or multiple-choice work. |
| 6b | Combine all four learning outputs under one Generate action in clearly labelled sections. | One press produces all sections for the same document/settings; flashcard and quiz answers start hidden, including after regeneration. |
| 7a | Integrate PDF extraction into the same text-processing flow. | Pasted text, text-file and PDF inputs each produce every required output; exactly one source is active at a time. |
| 7b | Preserve PDF page references and handle unreadable input. | References preserve original physical PDF pages. Process readable pages while listing pages without readable text and stating results cover extracted text only. An entirely unreadable PDF triggers no generation and asks for a text-based PDF or pasted text. |
| 8 | Final three-document quality check and requirements check. | Record factual support, reference accuracy and concept coverage; fix failures. Include text and PDF. Verify New session clears pasted text, uploaded file, subject, all results and answer-reveal state, and restores Norwegian/short; check no student content is persisted or logged. Verify demo startup without credentials and document the live setup. |

If the early PDF experiment fails, investigate its cause before leaving the task; do not silently omit PDF or add OCR. Document limitations clearly; support text-based PDFs without OCR or table/figure interpretation, as decided in the brief.

## Technical proposal — not yet approved

If course rules allow it: one locally run Python/Streamlit app, one cloud model API, and one PDF extraction library. Keep interface, extraction and AI functions in the same project; no separate frontend project, database, vector search or agent framework. Streamlit supports [file uploads](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader) and [session state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state). Keep API credentials server-side and out of Git using [secrets management](https://docs.streamlit.io/develop/concepts/connections/secrets-management).

Provider and PDF library remain open. Initial input limits are 40 physical PDF pages and 30,000 characters for pasted text, text-file content or total PDF-extracted text. PDFs must meet both limits; blank/image-only pages count toward the page limit. Reject oversized input before live AI calls, ask for a shorter excerpt and never truncate automatically. Check exact boundaries and record any limit changes justified by testing. A locally running app using a cloud model still sends text to that service. Define session cleanup and avoid caching/logging student content; implement the temporary-session decision with explicit reset, defined expiry/cleanup and no persistent history or sharing. Check provider data handling separately before live use. No paid service or public deployment is approved.

## Work rhythm and evidence — proposals

Use one small task per work session and a small commit after checking it; no hourly estimate is promised. Use approximately 15 December 2026 as the provisional deadline, with core completion around 1 December to reserve two weeks for fixes and submission. Confirm the exact deadline before final scheduling. Reassess pace after the first working summary.

Keep a setup/use README, the brief and short PRD, and a compact development/test log covering results and relevant AI/BMAD decisions. Additional reports, reflection or testing are included if the assessment rubric requires them. Do not duplicate the same evidence across documents.

## Delivery and optional extension

Before live integration, choose the provider/model and budget, set request limits, enforce the agreed document limits and record cloud data handling. Keep test material in a dedicated folder and saved demo responses separate from live output. README covers setup, demo/live modes, example secrets without real keys and PDF limitations. Check readable contrast, labelled inputs, keyboard use, output sections and reference visibility.

Only after all core checks pass, consider EXT-1: multiple-choice quiz with automatic marking and source-supported explanations. Record inclusion in the PRD and verify answer handling, score calculation and source references. Preserve the final two-week correction buffer; defer the extension if it threatens required delivery. Longer-term repetition features remain outside this plan.
