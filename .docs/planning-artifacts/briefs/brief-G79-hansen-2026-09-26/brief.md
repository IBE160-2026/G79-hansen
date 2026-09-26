---
title: 'Product Brief: AI Study Buddy'
status: ready-for-planning
created: 2026-09-26
updated: 2026-09-26
---

# AI Study Buddy

## Purpose

AI Study Buddy helps students process course material by generating summaries, flashcards, and quiz questions from uploaded notes. It provides practical study support while giving students experience with AI for text processing.

The application is an IBE160 project at Høyskolen i Molde, developed using BMAD in VS Code. The assignment specifies a simple difficulty level. This brief separates assignment requirements, agreed product decisions and quality goals, and proposed implementation choices. It is ready for requirements planning; implementation proposals remain open to revision.

## Confirmed assignment requirements

| Area | Requirement |
| --- | --- |
| Users | Students processing and studying course material. |
| Uploaded material | Lecture notes, slides, and course material in PDF or text format. |
| Additional inputs | Course code or subject, desired detail level, language and preferences. |
| Study outputs | Summaries, flashcards, quiz questions and answers, and key concepts. |
| Source references | Pointers to the sources or pages supporting the generated material. |
| Security and login | Required if the user's material is stored or shared. |
| Online commerce | No online buying or selling. |

The assignment leaves these decisions open: LLM selection and confidence level, summary granularity, treatment of tables and figures, and local versus cloud processing. It does not prescribe a web app, a particular model, fixed numbers of cards or questions, or the absence of accounts.

## Target audience and study problem

The target audience is students across subjects, not a specific course, programme, or cohort. The user confirmed this broad audience. The first version serves students who bring their own notes or course material and want to turn it into study aids.

The agreed problem focus is that students have lecture notes and course material but may find it difficult to identify the main points and turn the material into concrete practice activities. AI Study Buddy prioritizes helping them get an overview and start practising: summaries and key concepts provide the overview, while flashcards and quizzes support practice.

The user selected this problem focus for the product. It remains a hypothesis to investigate with students, not a finding established through user research.

## Student experience

A student uploads course material, enters the course or subject, and chooses the desired detail level and language preferences. The application generates a summary, key concepts, flashcards, and quiz questions with answers. Source references let the student return to the original material to check the generated content.

The intended benefit is a convenient route from course material to study and practice. Time savings and improved learning outcomes have not been measured.

## Proposed first version

These are recommendations for a manageable student project, not additional assignment requirements:

- Build a browser-based application that processes one document per study session.
- Accept uploaded text-based PDFs and text files; optionally support pasting text. Explain clearly when scanned pages or visual content cannot be processed.
- Offer Norwegian and English output and short or detailed summaries as initial options.
- Include a dedicated list of key concepts in every study set. Each concept has a short explanation grounded in the uploaded material and a source reference. Key concepts are an assignment requirement; this presentation is proposed.
- Generate five flashcards and five multiple-choice questions when the material supports that many distinct items. Reveal flashcard answers on request and show quiz answers with explanations after submission.
- Attach PDF page references or numbered text-section references to generated content. Explain insufficient source support instead of inventing missing information.
- Show generation progress and useful messages for unsupported, empty, unreadable, or oversized input and generation failures.
- Keep uploads and results temporary, without saved history or sharing. Define what ends a session and how temporary data is removed. Confirm this design before deciding whether accounts are needed under the assignment's conditional login requirement.
- Defer scanned-document recognition, table and figure interpretation, multiple-document synthesis, exports, and spaced repetition unless the lecturer requires them.

## Decisions to resolve before implementation

| Decision | Current proposal or open question |
| --- | --- |
| LLM and confidence level | Select a model after checking access, output quality, and budget. Define what confidence means and how uncertainty is communicated; do not treat an unvalidated percentage as a reliability measure. |
| Summary granularity | Start with short and detailed summaries; define their length and coverage in the requirements. |
| Tables and figures | Start with extractable text and identify omitted visual content. Confirm whether the demonstration must handle tables or figures. |
| Local versus cloud | Compare feasible options before selecting one. If using a cloud service, establish data handling and cost; temporary app storage does not establish provider retention behavior. |
| Storage, sharing, and login | Temporary sessions are proposed. If material is stored or shared, include the required security and login. |
| Platform and implementation | A web app is proposed. Programming language, framework, upload limits, and session cleanup remain to be specified. |
| Project constraints | Confirm the deadline, grading rubric, available development time, and any required technology or AI-service access. |

## Agreed project quality goals

The following goals are agreed for the first version. They are the project's own evaluation criteria, not additional assignment requirements or the lecturer's grading rubric.

Evaluate generated material using three documents. Before generation, identify five central concepts and their supporting source locations in each document. Check generated content against the source; these sample-based checks do not guarantee correctness for arbitrary material.

| Quality area | Agreed criterion |
| --- | --- |
| Factual support | All checked content is supported by the uploaded material, without contradictions or invented facts. |
| Reference accuracy | All checked references point to the correct source locations and support the associated content. A valid page number alone is insufficient. |
| Key-concept coverage | Each document's generated key-concept list includes at least four of the five concepts identified before generation. |

## Proposed evaluation procedure

The details below are proposals for applying and extending the agreed goals. They remain subject to refinement during requirements planning.

Choose short documents with sufficient material, covering lecture notes, slides, and course text, with at least one text-based PDF and one text file. Run each document twice and record results. Review every generated summary claim, concept explanation, flashcard answer, and quiz answer against its reference. Correct failures and rerun affected samples before the demonstration.

| Quality area | Proposed acceptance criterion |
| --- | --- |
| Required outputs | Every run produces a summary, a dedicated key-concept list, flashcards, quiz questions and answers, and source references. Where the source supports it, the proposed five cards and five questions are present. |
| Quiz quality | Each multiple-choice question has exactly one defensible correct option, an explanation supported by the source, and feedback that matches the submitted answer. Answers remain hidden until submission. |
| Preferences | Exercise both proposed languages and detail levels. Output follows the selected language, except for necessary subject terms; the detailed summary covers at least the short summary's main ideas and adds supported explanation. |
| Insufficient material and errors | Empty input, an unreadable PDF, and a simulated AI-service failure each produce an understandable message and a retry or replacement-upload action. Sparse input produces fewer items with an explanation rather than invented filler. |
| Storage and access | Verify the agreed session cleanup behavior. If storage or sharing is implemented, verify that unauthenticated users cannot access retained material and one user cannot access another user's private material. |
| Usability | Two students studying different subjects each upload material, use the summary and key-concept list to identify three main points supported by the source, check a concept's reference, reveal a flashcard answer, and complete a quiz without facilitator intervention. Both must complete the tasks; record obstacles and ask whether the study set helped them get an overview and start practising. Record opinions separately from task completion. This small sample does not establish usefulness across all subjects. |

The audience, problem focus, and goals in the preceding section are agreed product decisions. Additional test procedures and participant selection remain proposals. None of these checks establishes improved grades.

## Next step

Use this brief to create detailed requirements and acceptance criteria. Resolve the open decisions before treating the proposed implementation choices as agreed scope.
