---
title: 'Product Brief: AI Study Buddy'
status: pending-assessment-criteria
created: 2026-09-26
updated: 2026-09-26
---

# AI Study Buddy

## Purpose and agreed scope

An individual IBE160 project at Høyskolen i Molde, built with BMAD in VS Code. One beginner, a December deadline and moderate time investment make feasibility the priority. The goal is a solid assessed student project, not a commercial product.

The agreed audience is students across subjects. The problem is extracting the main points from course material and turning them into practice: summaries and key concepts provide an overview; flashcards and quizzes help students start practising. This is the chosen problem focus, not a validated research finding.

Build a working text-to-summary prototype first, then the remaining learning functions, and integrate PDF last. Run a small PDF extraction/page-number experiment early to discover limitations. Detailed tasks and technical proposals are in the [development plan](development-plan.md).

## Required final capabilities

These come from the supplied assignment and remain in scope:

| Area | Requirement |
| --- | --- |
| Input | Uploaded lecture notes, slides or course material in PDF/text format; course code/subject, desired detail level and language/preferences. |
| Output | Summaries, key concepts, flashcards, quiz questions and answers, and references to sources/pages. |
| Security/login | Required if user material is stored or shared. |
| Commerce | No online buying or selling. |
| Decisions to document | LLM and confidence level, summary granularity, handling of tables/figures, and local versus cloud processing. |

Early prototypes do not satisfy the complete assignment. PDF and source references are required in the final delivery.

## Proposed minimal implementation

All choices in this section are proposals, not expressly approved decisions: one screen and one document at a time; short/detailed summaries; Norwegian/English output; concepts with brief explanations; simple flashcards and quiz answers revealed on request; no fixed item counts or automatic marking. Use paragraph references for text and page references for PDFs.

Propose temporary sessions without saved history or sharing. Defer libraries, exports, spaced repetition, scoring, multiple-choice options, multiple-document analysis, advanced preferences and mobile apps. These deferrals remain subject to the assessment criteria; conditional login cannot be dropped as an extra.

## Agreed quality goals

Evaluate three documents. Identify five central concepts and their source locations in each before generation. All checked content must be supported by the source, all checked references must be correct, and at least four of the five concepts must appear in each generated concept list. These are agreed project goals, not lecturer-supplied criteria or guarantees for arbitrary inputs.

## Open constraints and safeguards

The assessment rubric has been requested; the exact December deadline, required technology and AI access/budget remain unknown. Review the rubric with the user before proposing any cut that could affect assessment. Confirm with the lecturer whether text-based PDFs/slide exports, no table/figure interpretation, source-based uncertainty handling and temporary sessions satisfy the assignment. These are proposed limitations, not waivers of requirements.

Keep documentation short but preserve whatever evidence the rubric requires. The [PRD draft](../../prds/prd-G79-hansen-2026-09-26/prd.md) is the next BMAD step; finalize it after the necessary assessment clarifications.
