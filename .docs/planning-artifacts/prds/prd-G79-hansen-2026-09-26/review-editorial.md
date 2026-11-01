# PRD editorial review

These documents help the student, assessor and downstream planning agents understand the required study flow and carry unresolved implementation decisions into architecture. Model: Strategic/Context (Pyramid); reader: humans; baseline: Microsoft Writing Style Guide. Preserve the direct, test-oriented wording and stable requirement IDs.

Reviewed structure first, then prose. Measured with word_metrics.py: PRD 2,005 words; architecture handoff 286 words. The relevant PRD sections are Conditional access requirement (250 words) and Combined generation flow (111 words).

| Pass | Original Text | Revised Text | Changes |
| --- | --- | --- | --- |
| structure | PRD: Conditional access requirement contains the reset behavior and an unrelated paragraph starting 'Online buying/selling, saved libraries...' | MOVE that paragraph to a Scope exclusions and source sufficiency subsection; rename Conditional access requirement to Session reset and conditional access. | Makes session behavior findable and separates exclusions from access control. Estimated word impact: +5 words for headings; preserves requirements. |
| structure | PRD: FR-9 appears before FR-8. | MOVE Session reset and conditional access before Combined generation flow, keeping FR IDs unchanged. | Stable IDs remain intact and readers encounter FR-8 before FR-9. Word impact: 0. |
| prose | PRD: 'Online buying/selling, saved libraries, export, spaced repetition, multiple-document analysis and mobile apps are outside v1. OCR and table/figure interpretation are also excluded. Online buying/selling is excluded by the assignment. No fixed item count, scoring or export is required in v1.' | 'Online buying/selling is excluded by the assignment. Saved libraries, export, spaced repetition, multiple-document analysis, mobile apps, OCR and table/figure interpretation are outside v1. Core v1 has no scoring or fixed item counts.' | Removes repeated exclusions without changing the optional scoring extension. Estimated saving: 11 words. |

Architecture handoff: no structural or prose changes required. Keep its decision table and revisit points.

Three recommendations; estimated net reduction 6 words (0.3% of PRD), grounded in measured section totals. No comprehension trade-off. The roughly two-page aim is exceeded by the accumulated acceptance checks, but cutting confirmed behavior would hurt downstream use; no expansion is recommended. No editorial issue blocks UX or architecture.
