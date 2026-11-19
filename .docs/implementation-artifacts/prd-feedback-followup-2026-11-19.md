# PRD feedback follow-up — 19 November2026

Source: [lecturer feedback dated12 November](../planning-artifacts/prds/prd-G79-hansen-2026-09-26/tilbakemelding-prd.md).
It assessed the11 November PRD, before later implementation and delivery
decisions. This response does not replace the full assignment/assessment rubric.

## What required action

| Feedback | Reconciliation and local correction | Current state |
| --- | --- | --- |
| 4.1 Semester scope and fallback | PRD now prioritizes must-have study flow/quality/demo, retains implemented account/library/progress/deletion without expansion, and keeps public hosting/physical two-device checks and EXT-1 optional. Core1 December, full package8 December, hard deadline15 December; stop optional expansion if core is late. | Addressed without removing working features or safety controls. |
| 4.2 User, thesis, journey and glossary | Added a product hypothesis, UJ-1 structured from the accepted lecture-excerpt study flow, and a glossary distinguishing login session/workspace/New session/source/saved document. Scenario is explicitly illustrative, not claimed user research or measured learning benefit. | Addressed in PRD. |
| 4.3 Testable FR-3/4/8 | Summary checks require supported claims/references on the three evaluation documents; concepts target at least4 of5 preselected concepts per document. FR-8 remains the stable umbrella with8a account/logout,8b recovery and8c ownership checks. | Addressed; no renumbering of existing top-level IDs or new feature work. |
| 4.4 Cost/call limits and unsupported output | Existing code already has USD5 preserved lifetime application reservations, USD0.05 per admitted attempt, at most100 attempts, one concurrent generation per login session/two per process and a60s deadline. Documented denial behavior, whole-result rejection of invalid references/structure and explicit source insufficiency. Semantic correctness still needs source assessment. | Clarified to match existing code. The suggested3/hour was an example, not an adopted new quota. No ledger reset, budget change or model call. |
| 4.5 Mixed architecture/history | Kept user-visible capability/acceptance summaries in PRD; moved detailed boundary/restart/save/recovery cases unchanged to the architecture handoff and reduced revision history. Updated stale milestone wording to selected/implemented versus still unverified. | Addressed; preserved detailed acceptance continuity. |

The incoming [technology reference](../planning-artifacts/architecture/technology.md)
describes Pytagoras Website V2, not this app. It does not add commerce,
Next.js/Redis, another hosting vendor or automatic live mock fallback to
StudyBuddy. The adopted architecture spine stays in force.

One bounded independent source reconciliation found no lost accepted
requirements after three stale-status/document-residue corrections. Its
[source map](../planning-artifacts/prds/prd-G79-hansen-2026-09-26/reconcile-lecturer-feedback-2026-11-12.md)
records the finding history. Additional reviewer agents/market research were
skipped under the student's short-work preference; structure/prose were
polished locally. No application code or infrastructure changed.

## Necessary delivery work still open

1. Reconcile the **full assignment and assessment rubric**, which are not
   supplied by this formative feedback. Do not invent criteria or promise grades.
2. Finish the remaining **manual quality/accessibility check**. Guided actual
   Narrator use of the fixed demo was user-confirmed19 November; see its
   [scoped results](screen-reader-check-2026-11-19.md). Keep honest boundaries
   for the untested private workspace/PDF/auth/error flows and other platforms.
   Reuse prior source/content/access evidence; run only checks for concrete gaps.
3. Complete the **student's own reflections and final report/package**.
   The [report draft](../../.reflection-doc/refleksjonsrapport-utkast.md) remains
   factual scaffolding with personal sections to fill. The student has been
   asked for their learning and what they would simplify.

Public hosting and full operational backup remain optional/deferred. Do not
reopen them as new required work because the feedback lists infrastructure
examples. Follow the [delivery checklist](delivery-checklist-2026-11-19.md).
