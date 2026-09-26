---
title: 'Product Brief: AI Study Buddy'
status: draft
created: 2026-09-26
updated: 2026-09-26
---

# AI Study Buddy

## Purpose

AI Study Buddy helps students process course material by generating summaries, flashcards, and quiz questions from uploaded notes. It provides practical study support while giving students experience with AI for text processing.

The application is an IBE160 project at Høyskolen i Molde, developed using BMAD in VS Code. The assignment specifies a simple difficulty level. This brief separates confirmed assignment requirements from proposed implementation choices; the proposed choices remain open to revision.

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

## Student experience

A student uploads course material, enters the course or subject, and chooses the desired detail level and language preferences. The application generates a summary, key concepts, flashcards, and quiz questions with answers. Source references let the student return to the original material to check the generated content.

The intended benefit is a convenient route from course material to study and practice. Time savings and improved learning outcomes have not been measured.

## Proposed first version

These are recommendations for a manageable student project, not additional assignment requirements:

- Build a browser-based application that processes one document per study session.
- Accept uploaded text-based PDFs and text files; optionally support pasting text. Explain clearly when scanned pages or visual content cannot be processed.
- Offer Norwegian and English output and short or detailed summaries as initial options.
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

## Proposed demonstration and success criteria

These checks are proposed for evaluating the application; they are not the lecturer's grading rubric:

- Complete the upload-to-practice flow using a text-based PDF and a text file, including course, detail-level, and language inputs.
- Confirm that the application produces every required output: summaries, flashcards, quiz questions and answers, key concepts, and source references.
- Manually compare generated claims and answers with their cited source locations. Correct unsupported claims and incorrect references before the demonstration.
- Demonstrate the proposed card and quiz interactions, a clear response to unreadable input, and recovery from an AI-service failure.
- Verify the chosen storage behavior and, if storage or sharing is included, the security and login behavior.
- Ask two fellow students to complete a study session and record obstacles and perceived usefulness. Treat this as exploratory feedback, not evidence of improved grades.

## Next step

Use this brief to create detailed requirements and acceptance criteria. Resolve the open decisions before treating the proposed implementation choices as agreed scope.
