# AI Study Buddy — development plan

Build order and the early PDF experiment are user-approved. Task boundaries, checks, technology and timing below are proposals. Final scope and quality goals are in [the brief](brief.md); its assessment safeguards apply here too.

## Small tasks and checks

Finish one task and record its result before continuing. Use fixed responses for interface checks and separate real AI calls for content checks. Experiments are not completed product features.

| Order | Small task | Observable check |
| --- | --- | --- |
| 1a | Text box, Generate button and summary display using a fixed response. | The submitted text follows the expected flow; empty input is rejected. |
| 1b | Connect one model to generate a summary. | A short known text produces a supported summary. |
| 1c | Busy state and failed-request message. | A simulated failure allows retry without losing the input. |
| 2 | Early standalone PDF experiment, before further feature work. | Extract a three-page PDF with distinct text on the first and third pages and a blank middle page. Preserve physical page positions; the last page remains page 3. Compare extracted text with the PDF. Try an image-only page and report absent usable text. Record findings and limitations, not an OCR solution. |
| 3a | Text-file upload. | A sample file yields the expected text; unusable input gets a clear message. |
| 3b | Course/subject, language and detail inputs. | Output uses the chosen language and detail; course context does not invent source facts. |
| 3c | Number text paragraphs and attach summary references. | Each checked reference identifies the supporting paragraph. |
| 4 | Key concepts, brief explanations and references. | Apply the agreed four-of-five concept check. |
| 5 | Flashcards with answer reveal. | Reveal works and each answer is supported by its reference. |
| 6 | Quiz questions and answer reveal. | A student can attempt a question before revealing the supported answer. No scoring or multiple-choice work. |
| 7a | Integrate PDF extraction into the same text-processing flow. | Text and PDF inputs both produce every required output. |
| 7b | Preserve PDF page references and handle unreadable input. | References match physical PDF pages, including blank-page offsets; unusable PDFs produce an actionable message. |
| 8 | Final three-document quality check and requirements check. | Record factual support, reference accuracy and concept coverage; fix failures. Include text and PDF. Check applicable security/login obligations. |

If the early PDF experiment fails, investigate its cause before leaving the task; do not silently omit PDF or add OCR. Bring any assessment-affecting limitation to the user/lecturer.

## Technical proposal — not yet approved

If course rules allow it: one locally run Python/Streamlit app, one cloud model API, and one PDF extraction library. Keep interface, extraction and AI functions in the same project; no separate frontend project, database, vector search or agent framework. Streamlit supports [file uploads](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader) and [session state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state). Keep API credentials server-side and out of Git using [secrets management](https://docs.streamlit.io/develop/concepts/connections/secrets-management).

Provider, PDF library and input-size limits remain open. A locally running app using a cloud model still sends text to that service. Define session cleanup and avoid caching/logging student content; confirm storage/login interpretation before adopting the temporary-session proposal. No paid service or public deployment is approved.

## Work rhythm and evidence — proposals

Use one small task per work session and a small commit after checking it; no hourly estimate is promised. Aim to finish required features two weeks before the exact December deadline, reserving that time for fixes and submission. Reassess pace after the first working summary.

Keep a setup/use README, the brief and short PRD, and a compact development/test log covering results and relevant AI/BMAD decisions. Additional reports, reflection or testing are included if the assessment rubric requires them. Do not duplicate the same evidence across documents.
