---
title: 'Product Brief: AI Study Buddy'
status: draft
created: 2026-09-26
updated: 2026-09-26
---

# AI Study Buddy

## Purpose

AI Study Buddy helps students turn their own course material into summaries, flashcards, and quizzes with references back to the source. It is a simple IBE160 project at Høyskolen i Molde, developed using BMAD in VS Code, and an opportunity to learn how AI supports text processing.

This is a complete first draft for user review. The assignment establishes the concept and output types. Items marked **[ASSUMPTION]** are proposed choices, not confirmed requirements or lecturer expectations.

## Users and problem

**[ASSUMPTION]** The first users are fellow students preparing for a lecture recap or an exam. They have notes but need help identifying the main ideas and turning passive reading into practice. Creating study aids manually is the problem hypothesis; no interviews or evidence of time savings have been collected.

The intended benefit is a short route from course material to active practice, with a way to check the generated content. Improved grades or learning outcomes are not established claims.

## Proposed student experience

**[ASSUMPTION]** A browser-based application supports one document and one study session at a time:

1. Upload a text-based PDF or paste plain text. Optionally enter the course code or subject.
2. Choose Norwegian or English and a short or detailed summary.
3. Generate a study set: a summary with key concepts, five flashcards, and five multiple-choice questions, where the source contains enough material.
4. Read the summary, reveal flashcard answers, and answer quiz questions before seeing the correct answer and explanation.
5. Check PDF page references or numbered text sections for summary points, flashcards, and quiz answers. Start a new session when finished.

**[ASSUMPTION]** Outputs use only the supplied material. If it cannot support a requested answer or enough distinct questions, the app explains the limitation instead of filling gaps. Source references enable checking; they do not guarantee correctness.

## First-version scope

**[ASSUMPTION]** The first release includes the flow above, a visible generation state, and useful messages for unsupported files, unreadable or empty input, oversized input, and generation failures. Exact upload limits will be defined before implementation.

**[ASSUMPTION]** The app does not retain uploads or study sets beyond the active session and has no accounts, saved history, sharing, or database of student material. Temporary server data must have a defined cleanup policy. The assignment requires security/login if material is stored or shared; adding either feature reopens that decision.

**[ASSUMPTION]** Scanned PDFs, image interpretation, table extraction, multiple-document synthesis, exports, spaced repetition, and mobile apps are deferred. Text-based slides are supported only when their text can be extracted reliably; omitted visual content must be made clear. Online buying and selling are excluded by the assignment.

## AI and delivery choices

**[ASSUMPTION]** Use one cloud LLM through a backend, with credentials kept off the client. This depends on course rules, available access, cost, and provider data handling. Temporary storage in our app does not imply that a provider retains nothing. Provider and model selection remain open; no paid service is approved by this brief.

**[ASSUMPTION]** Do not display a numeric confidence score without a validated basis. Instead, show source references and identify insufficient source support. Keep the initial implementation focused on text; choose the programming language and framework during technical planning.

## Proposed demonstration and success criteria

These **[ASSUMPTION]** targets are project checks, not the lecturer's grading rubric:

- Complete the upload-to-practice flow on three short sample documents with sufficient material, including a text-based PDF and plain text, covering Norwegian and English output.
- For each sample, manually check five summary points, five flashcards, and five quiz answers against their cited pages or sections. Correct unsupported claims and incorrect references before the demonstration.
- Ensure quiz answers stay hidden until the student submits, and that feedback matches the selected answer.
- Demonstrate a clear response to an unreadable input and an AI-service failure, followed by a successful retry or replacement upload.
- Have two fellow students complete a session without guidance and record any obstacles and whether they find the study aids useful. This is exploratory feedback, not proof of learning effectiveness.

## Context and next decisions

Comparable workflows already exist: Google describes document-based flashcards, quizzes, and source-linked explanations in [NotebookLM](https://blog.google/innovation-and-ai/models-and-research/google-labs/notebooklm-student-features/). The project makes no novelty claim; its purpose is a focused learning aid and a manageable exercise in developing and evaluating AI software.

Before implementation, confirm the deadline, lecturer's assessment and technology requirements, available development time, API budget/access, and whether temporary sessions meet the assignment. These are open constraints, not reasons to delay reviewing this draft. The next planning artifact should turn the agreed scope into precise requirements and acceptance criteria.
