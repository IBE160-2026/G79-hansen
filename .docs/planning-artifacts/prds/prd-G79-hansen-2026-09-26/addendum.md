# Architecture handoff - AI Study Buddy

The PRD defines required behavior. The following implementation choices remain open; none prevents starting UX or architecture. Owner: student, supported by assistant.

| Choice | Required decision and revisit point |
| --- | --- |
| Stack and PDF library | Confirm the proposed single Python/Streamlit application or document an alternative, with a PDF library that preserves physical page positions. Decide before affected stories are implemented. |
| Provider/model and access | Choose one provider/model, obtain API access, set a test budget and check provider data handling before live integration. Codex sign-in is not evidence of an application API key. |
| AI request strategy | Decide prompt/output structure, one or multiple calls for the four sections, validation, request timeouts and retry behavior. Preserve the PRD's single Generate action and source-grounding requirements. |
| Resource controls | Set upload-byte and request/output limits, character-count convention and text-decoding behavior. Respect the agreed 40-page/30,000-character limits; record any adjustments justified by tests. |
| Session lifecycle | Define expiry, disconnect/restart behavior and cleanup without persistent student content or shared caches. Implement the exact New session reset and prevent stale outputs after source changes. |
| Credentials and demo fixtures | Keep secrets server-side and out of Git; provide an example configuration without credentials. Keep fixed demo data distinct from live source material. |

Delivery follow-up: the student confirms the exact deadline (currently approximately 15 December 2026) and checks the actual assessment guidance before final scheduling/submission. This is not an architecture blocker. Target core completion around 1 December.

The optional automatically marked multiple-choice quiz remains deferred until core acceptance passes and inclusion is explicitly recorded. No additional feature is authorized by this handoff.
