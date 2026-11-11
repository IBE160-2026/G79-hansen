# Architecture handoff - AI Study Buddy

The PRD defines required behavior. The following implementation choices remain open; none prevents starting UX or architecture. Owner: student, supported by assistant.

| Choice | Required decision and revisit point |
| --- | --- |
| Stack and PDF library | Use the user-selected Python/FastAPI plus HTML/CSS/JavaScript in one project with hosted live mode and a locally runnable fixed-data demo, with a PDF library that preserves physical page positions. Decide before affected stories are implemented. |
| Provider/model and access | Choose one provider/model, obtain API access, set a test budget and check provider data handling before live integration. Codex sign-in is not evidence of an application API key. |
| AI request strategy | Decide prompt/output structure, one or multiple calls for the four sections, validation, request timeouts and retry behavior. Preserve the PRD's single Generate action and source-grounding requirements. |
| Resource controls | Set upload-byte and request/output limits, character-count convention and text-decoding behavior. Respect the agreed 40-page/30,000-character limits; record any adjustments justified by tests. |
| Session lifecycle | Define expiry, disconnect/restart behavior and cleanup with owner-scoped saved documents/results and no shared private-content caches. Use selected Supabase Auth, Postgres and private Storage; define account/session configuration, owner-based database/storage policies, deletion consistency and progress-write rules before affected implementation. Implement the exact New session reset and prevent stale outputs after source changes. |
| Credentials and demo fixtures | Keep secrets server-side and out of Git; provide an example configuration without credentials. Keep fixed demo data distinct from live source material. |

Delivery follow-up: the student confirms the exact deadline (currently approximately 15 December 2026) and checks the actual assessment guidance before final scheduling/submission. This is not an architecture blocker. Target core completion around 1 December.

The optional automatically marked multiple-choice quiz remains deferred until core acceptance passes and inclusion is explicitly recorded. The 2026-11-10 user scope decision adds login and owner-only saved documents/results, library, reopening and deletion. This supersedes previous no-persistence assumptions. User selected explicit Save; no auto-save on upload/generation. Cross-visit card/quiz position resumption is required. Decide account/library UX, progress-write timing and reopened reveal-state handling before affected implementation. Do not auto-save an unsaved document merely to track progress.

## Adopted service selection - 2026-11-10

Supabase Auth owns identity; Postgres stores owner-linked document metadata, source text where appropriate, generated learning parts and progress; private Storage holds uploaded document files. Keep table and object access owner-scoped using database/storage policies and enforce authorization for FastAPI operations. Privileged secrets and private files never become frontend/static assets. Email/password with signup, login, recovery and logout is selected. Exact schema, SDK versions, token/cookie/session handling, email confirmation/recovery redirects, region, hosting, quotas/budget and migrations remain architecture configuration decisions. No cloud resources have been provisioned by this document update.

Documentation verified: https://supabase.com/docs/guides/auth ; https://supabase.com/docs/guides/storage/buckets/fundamentals ; https://supabase.com/docs/guides/database/postgres/row-level-security .
