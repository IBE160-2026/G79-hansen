---
title: 'Product Brief: AI Study Buddy'
status: revised
created: 2026-09-26
updated: 2026-11-01
---

# AI Study Buddy

## Executive summary

AI Study Buddy helps students turn their own course material into an overview and concrete practice. A student supplies text or a text-based PDF, selects subject, language and detail level, and receives a summary, key concepts, flashcards and quiz questions with source references.

This is an individual IBE160 project at Høyskolen i Molde, built with BMAD. One beginner, a December deadline and moderate time investment make feasibility the priority. The goal is a solid assessed student project, not a commercial product.

## Problem and primary user

The audience remains students across subjects. The primary design scenario is a student preparing for a test who has a lecture export of about 40 slides and struggles to identify the main points and start practising. Reading alone does not give the student ready-made practice questions or an easy way to check where an answer came from. This is an illustrative scenario, not validated user research.

## Solution and differentiation

Use one screen and one document per session. The defaults are Norwegian and a short summary. Before generation, the student can independently choose English and/or a detailed summary. The language choice applies to all four learning sections, including answers. The student then presses Generate once to create all four learning sections together: summary, key concepts, flashcards and quiz. Flashcard and quiz answers are initially hidden and revealed only on request. Text references identify paragraphs; PDF references identify physical pages.

A general chatbot can perform similar tasks. This app's value is a repeatable study flow, a consistent output format and source references without the student composing a new prompt for every task. References help students check answers; they do not guarantee correctness.

## Required final capabilities

| Area | Requirement |
| --- | --- |
| Input | Pasted text, one uploaded text file or one text-based PDF (including slide exports), using one input method at a time; optional course code/subject (context only), detail level and language. All factual output must be supported by the supplied material. |
| Output | Summaries, explained key concepts, flashcards, quiz questions and answers, all with supporting paragraph/page references. |
| Security/login | Required if user material is persistently stored or shared; neither is part of v1. |
| Commerce | No online buying or selling. |
| AI behavior | Use source-supported answers; state when information is insufficient rather than inventing content or a numerical confidence score. |

## Scope and decisions

- Use temporary sessions without saved history, sharing or accounts. This keeps v1 manageable and follows the assignment's conditional login requirement. Do not persist or log student material; New session clears pasted text, uploaded file, course/subject and all results, and restores Norwegian/short defaults. Define session expiry/cleanup in the architecture, preserving the PRD reset and no-persistence requirements.
- Support text-based PDFs only, preserving physical page numbers. No OCR or interpretation of tables/figures: these require additional extraction and validation beyond this project's scope. Process readable pages and list original page numbers without readable text. State that results cover extracted text only and retain original physical page references. If no page has readable text, ask for a text-based PDF or pasted text instead of generating.
- Build text-to-summary first, remaining learning functions next, and integrate PDF last. Run an early PDF extraction/page-number experiment to expose limitations.
- Keep simple answer reveal. Adapt concept, flashcard and quiz counts to the material; generate only source-supported items. If material is too short or incomplete, explain the limitation in the affected section rather than invent content. Defer libraries, export, spaced repetition, multiple-document analysis and mobile apps.
- Keep LLM provider/model and budget open until before live integration. Choose one provider, document cloud data handling, and set request limits before sending course material. Initial document limits are 40 physical PDF pages and 30,000 characters, including PDF-extracted text. Exceeding either limit requires a shorter excerpt; never truncate automatically. Adjust limits only after testing and record changes. No paid subscription or public deployment is authorized by this brief.

These scope decisions respond to the [lecturer feedback](tilbakemelding-product-brief.md). They replace the earlier pending-approval proposals without claiming approval of technical details the lecturer did not assess.

## Success criteria and delivery evidence

Evaluate three documents, including text and PDF. Identify five central concepts and their source locations in each before generation. All checked generated content must be supported by the source, all checked references must be correct, and at least four of the five concepts must appear in each concept list. Record results and fixes. These are sample-based project goals, not guarantees for arbitrary inputs or improved grades.

Provide a readable, accessible interface with clear sections for each output, visible references, answer-reveal controls and understandable errors. Failed generation preserves material and settings and offers a Try again button. Keep a development log showing checks and corrections to AI suggestions. Put test documents in a dedicated folder and document setup, use and limitations in README.

Provide a clearly labelled demo mode with fixed example material and saved responses, runnable without an API key or paid account. Explain that it demonstrates the flow and does not generate answers for arbitrary documents. README must also explain live mode with the assessor's own key and an example secrets file without real credentials.

## Optional extension and vision

After every required capability and the quality checks pass, prioritize one optional extension: multiple-choice quiz with automatic marking and source-supported explanations. Record the decision to include it in the PRD and test it; it is not required for v1 completion. Do not add saved sessions or login in the same extension.

Longer term, the app could support repetition over time and help students revisit difficult concepts. This gives direction without expanding v1.

## Next steps and remaining constraints

The [development plan](development-plan.md) records task order; the [PRD](../../prds/prd-G79-hansen-2026-09-26/prd.md) defines acceptance checks. Finalize provider/model, budget, request limits and technical choices before affected implementation work. Confirm the exact December deadline and consult the actual assessment guidance for delivery evidence; the supplied feedback is not a substitute for the full rubric. Planning can proceed with the decisions above.
