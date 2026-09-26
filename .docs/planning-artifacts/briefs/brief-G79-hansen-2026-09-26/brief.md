---
title: 'Product Brief: AI Study Buddy'
status: ready-for-planning
created: 2026-09-26
updated: 2026-09-26
---

# AI Study Buddy

## Purpose and priority

AI Study Buddy is an IBE160 project at Høyskolen i Molde, developed using BMAD in VS Code. It helps students get an overview of their course material and start practising, while learning how AI can support text processing.

The developer is a beginner. Feasibility and a small working application take priority over extra features. The agreed audience is students across subjects. The problem focus is difficulty extracting main points from notes and turning them into practice activities; this is the chosen product direction, not a finding validated through student research.

Assignment requirements below remain mandatory for the finished version. The build sequence is agreed; implementation choices are proposals. Early increments are deliberately incomplete and must not be presented as satisfying the whole assignment.

## Assignment requirements and simplest planned coverage

| Requirement | Planned coverage in the finished version |
| --- | --- |
| Uploaded lecture notes, slides, or course material in PDF/text format | Upload one text file or one text-based PDF at a time. PDF support comes last, but remains in the delivery scope. Slides are supported as text-based PDF exports. See teacher clarifications below for other formats. |
| Course code or subject | One text input, used as context for generation. No course catalogue. |
| Desired detail level | A simple short/detailed choice for summaries. |
| Language/preferences | A simple output-language choice, initially Norwegian/English, and the detail choice. Additional preferences are not specified; clarify if the lecturer expects more. |
| Summaries | A readable summary of the supplied material. |
| Key concepts | A list of concepts with brief source-supported explanations. |
| Flashcards | Simple question/answer pairs with a reveal-answer control. |
| Quiz questions and answers | A short list of questions with answers revealed on request. No automatic marking is needed for the proposed version. |
| Source/page references | Numbered paragraphs for text and page numbers for PDFs, attached to summary points, concepts and learning items. No embedded PDF viewer. |
| Security/login if material is stored or shared | Propose no saved history or sharing, with material processed only during the active session. Confirm the interpretation with the lecturer; if the design counts as storage, add the required security/login or agree a revised design. |
| No online buying or selling | No commerce features. |

## Small build increments

Finish and check one increment before starting the next. The checks below are proposed completion checks, not additional assignment requirements.

| Step | Build | Check before continuing |
| --- | --- | --- |
| 1. Text to summary | Paste a short text, press Generate, and display a summary. Use one AI model. Add a busy indicator and a clear message for empty input or failed generation. | A known sample produces a source-supported summary; empty input and a failed request produce understandable messages. This is a prototype, not the final submission. |
| 2. Text input and source references | Add text-file upload, course/subject, short/detailed and output-language inputs. Number source paragraphs and retain the numbering through generation. Add paragraph references to summary points. | Upload a text file, exercise the choices, and manually follow summary references back to the supporting paragraphs. |
| 3. Key concepts | Add a list of key concepts, brief explanations and paragraph references. | Apply the agreed concept-coverage goal to the text samples. |
| 4. Flashcards | Add question/answer pairs and a reveal-answer control, using the same source and reference scheme. | Questions and answers are supported by their cited paragraphs, and answers can be revealed. |
| 5. Quiz | Add quiz questions and answers with references. Use plain questions and revealed model answers; no scoring or multiple-choice generation. | A student can attempt each question, reveal its answer and check the source. |
| 6. PDF support and final check | Extract text from one text-based PDF, preserve original page numbers, and feed it into the existing learning functions. Add a clear message for PDFs with no usable text. | All required outputs work with a text file and a PDF. References use PDF page numbers correctly. Complete the agreed three-document quality check. |

## Keep implementation small

Propose one screen, one document at a time, and a single AI integration. Reuse the extracted text across functions. Do not require a fixed count of cards or questions: produce a small set supported by the material rather than inventing filler. Set a modest input-size limit before implementation and tell the student when material exceeds it.

Choose one language/framework familiar from the course before coding. Do not add a database, vector search, multiple AI agents, separate frontend/backend projects, a local model installation, or public deployment unless needed for a confirmed requirement. If a cloud API is chosen, credentials belong on the server, not in browser code. A small server-rendered application is one possible implementation; the stack remains open.

## Decisions and teacher clarifications

The assignment names these decision points; keeping them simple does not remove them:

- **LLM and confidence:** choose one accessible model after checking course rules and cost. Proposed confidence handling is source references and explicit insufficient-source messages, without an unvalidated numerical score. Clarify with the lecturer if a numerical confidence measure is expected.
- **Summary granularity:** propose short/detailed; define simple length targets during requirements planning.
- **Tables and figures:** propose text-only processing without interpreting visuals or complex tables, with visible limitations. Clarify this limitation with the lecturer before treating it as sufficient for the assignment.
- **Local versus cloud:** choose one processing route based on available course tools, setup effort, access and cost. No automatic fallback or provider switching. Confirm cloud data handling if selected.
- **Storage/login:** propose no persistence or sharing; define session end, temporary-data cleanup and content logging before implementation. Temporary processing is not a blanket exemption from the conditional login requirement. Clarify with the lecturer whether this design satisfies it.
- **Input scope:** scanned PDFs, native slide files and image-only material are outside the proposed implementation. Confirm this interpretation with the lecturer. PDF support itself is scheduled for the last increment, not removed.

The deadline, assessment rubric and required course technology remain unknown. If time is insufficient, seek teacher agreement before removing any assignment requirement, including PDF support, source references or a learning output.

## Deferred extras

Saved libraries, sharing, export, spaced repetition, score tracking, automatic grading, multiple-choice options, fixed item counts, multiple-document analysis, advanced preferences, PDF viewers and mobile apps are not needed for this proposed version. Accounts are conditional on the storage/sharing decision, not an optional extra when that condition applies.

Extra usability studies and repeated runs of every sample are optional follow-up work. They are not delivery gates. No claim of improved grades or measured time savings is made.

## Agreed quality goals

These are project decisions, separate from the lecturer's requirements. Keep the previously agreed final check with three documents, including text and PDF input once PDF support exists. Before generation, identify five central concepts and supporting source locations per document.

| Area | Agreed goal |
| --- | --- |
| Factual support | All checked generated content is supported by the supplied material, without contradictions or invented facts. |
| References | All checked references identify the correct source location and support the associated content. |
| Key concepts | At least four of the five preselected concepts appear in each document's generated concept list. |

Review the small test outputs manually and record failures and fixes. These checks measure the tested samples, not guaranteed accuracy for all material. Verify that the final version also produces every required output and handles unusable input and failed generation clearly.

## Next step

Create a small PRD around these increments. Resolve only the decisions needed for the next increment, while tracking teacher clarifications and preserving all final-delivery requirements.
