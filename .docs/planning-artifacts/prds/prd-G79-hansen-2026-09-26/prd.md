---
title: 'PRD: AI Study Buddy'
status: draft
created: 2026-09-26
updated: 2026-09-26
---

# AI Study Buddy — short PRD

## Goal and boundaries

Implement the [product brief](../../briefs/brief-G79-hansen-2026-09-26/brief.md) as a manageable individual student project due in December. Students across subjects should get an overview of their own material and start practising. No commercial ambition or new features are introduced here.

The functional capabilities below come from the assignment. Acceptance checks are proposed ways to demonstrate them; they are not the lecturer's rubric. The [development plan](../../briefs/brief-G79-hansen-2026-09-26/development-plan.md) holds task order and unapproved technical proposals, including an early PDF experiment and later PDF integration.

## Functional requirements

### Inputs

| ID | Required capability | Proposed acceptance check |
| --- | --- | --- |
| FR-1 | Upload lecture notes, slides or course material in PDF/text format. | A text file and text-based PDF each enter the same learning flow. Confirm supported slide exports and scanned/visual limitations with the lecturer. |
| FR-2 | Accept course code/subject, detail level and language/preferences. | Generation respects supplied settings. Short/detailed and Norwegian/English are proposed initial choices; confirm whether other preferences are required. |

### Learning outputs

| ID | Required capability | Proposed acceptance check |
| --- | --- | --- |
| FR-3 | Generate a summary. | Summary points accurately describe supplied material at the selected detail level. |
| FR-4 | Generate key concepts. | A visible concept list includes source-supported explanations and meets the agreed coverage target below. |
| FR-5 | Generate flashcards. | Question/answer pairs are present; the proposed interface reveals each answer on request. |
| FR-6 | Generate quiz questions and answers. | A student can attempt questions and reveal the corresponding answers. Plain questions without automatic grading are proposed. |
| FR-7 | Provide source/page references. | Summary points, concepts and learning items refer to supporting text paragraphs or PDF pages. Page references preserve the original physical page position. |

### Conditional access requirement

**FR-8:** If user material is stored or shared, provide the required security/login. Verify unauthenticated access is blocked and one user cannot access another user's private material. Temporary sessions without persistence/sharing are proposed, not an approved exemption; resolve the lecturer's interpretation before finalizing access requirements.

Online buying/selling is excluded by the assignment. No fixed item count, scoring, export or extra learning function is added.

## Quality and checks

- **NFR-1 — agreed content goals:** use three documents, identifying five central concepts and source locations per document before generation. All checked generated content must be supported, all checked references correct, and at least four of five concepts included. Record errors and fixes. These sample checks do not prove accuracy for all material or improved grades.
- **NFR-2 — proposed error behavior:** empty or unreadable input and a failed AI request produce understandable messages with a retry/replacement action. Insufficient material must not be filled with invented facts or questions.
- **NFR-3 — proposed data handling:** define input limits, session end and cleanup; keep credentials and student content out of repository/logs. If a cloud model is selected, establish its data handling before use.

Test each small task as described in the development plan. The final check includes every required output for text and PDF; working text-only increments do not constitute assignment completion. Balance concept coverage against factual support: do not add unsupported concepts merely to reach the target.

## Open decisions before finalization

| Owner | Decision | Revisit point |
| --- | --- | --- |
| Student with lecturer | Assessment rubric, exact deadline, required technology and process/test evidence. | Before final scope approval or any assessment-affecting cut. |
| Student with lecturer | Temporary storage/login interpretation; acceptable PDF/slide/table/figure limitations; expected confidence handling and preferences. | Before final acceptance criteria and architecture. |
| Student, supported by assistant | Stack, local/cloud processing, model access/budget, summary targets, input limits and cleanup. | Before implementing affected tasks; technical proposals remain in the development plan. |

This is the next BMAD planning artifact, not a finalized PRD. Review the missing assessment criteria first, then finalize only the necessary requirements and create a small architecture decision document. Preserve the existing scope throughout.
