# Architecture handoff — AI Study Buddy

Updated 2026-11-11. The [PRD](prd.md), [DESIGN](../../ux-designs/ux-G79-hansen-2026-11-01/DESIGN.md) and [EXPERIENCE](../../ux-designs/ux-G79-hansen-2026-11-01/EXPERIENCE.md) define the reconciled product baseline. The [architecture spine](../../architecture/architecture-G79-hansen-2026-11-01/ARCHITECTURE-SPINE.md) fixes shared implementation contracts. These documents are ready for story planning, not proof of implemented features.

## Fixed contracts

- Python/FastAPI serves ordinary HTML/CSS/JavaScript and same-origin APIs. Keep the approved prototype composition; use a clearly labelled synthetic demo without external keys first.
- Supabase Auth owns email/password signup/login/recovery. Postgres and private Storage isolate each owner's records/files; FastAPI also checks ownership. Normal operations use user-scoped tokens, never a service-role bypass.
- One-process backend login state lives in memory; restart requires login again without losing saved documents or acknowledged progress. Opaque secure cookies, same-origin/CSRF checks, local-scope logout and no-store private responses are governed by AD-3. Initial expiry is 30 minutes idle / 12 hours absolute. Recovery links require the initiating browser and a password-update-only session; normal login follows recovery.
- Explicit Save stores source/settings/generated material; upload/generation alone never persists it. New session clears only active work. Signed generation receipts are checked against a bounded session/workspace registry, invalidated by source/settings/reset/new-generation actions, and used only to admit an explicit Save. After admission, an immutable owner-scoped staged operation can resume under a fresh login within 7 days, without requiring the expired receipt; cleanup/replay cannot stage new content. Revisioned idempotent save/delete operations preserve consistent snapshots and file/database lifecycle.
- Saved flashcard/quiz positions update automatically and independently. Reopening restores positions with answers hidden. Tab changes within the current visit retain revealed answers. Outdated writes cannot overwrite newer progress; Hent siste fremdrift reloads current progress before more writes. AD-7 fixes revision, locking, mutation IDs and bounded retry. Show pending/failed sync; cross-device continuity guarantees acknowledged updates only.
- One Generate action produces all four sections from one canonical source. Stable physical page/paragraph references, 40-page/30,000-character limits, no truncation/OCR, source insufficiency and honest failure/retry remain required.

## Milestone gates

| Owner | Decision/check | Required before |
| --- | --- | --- |
| Builder + student | pypdf candidate experiment: distinct first/third pages, blank middle, image-only input, bounded extraction; validate the 10 MiB initial upload ceiling and worker limits. | PDF integration; does not block fixed demo. |
| Student + builder | Model/provider/API access, request limits, data handling and cost ceiling; then three-document factual/reference/concept checks. | Live AI integration. |
| Student + builder | Hosting provider/region/quotas/cost, Supabase project/email/redirect configuration, backup and deletion retention. Render remains a candidate. | Provisioning/deployment or real private data. |
| Builder | Tested dependency lockfile, migrations/RLS, negative two-user/API/file tests, restart, failure/lifecycle and browser/accessibility checks. | Each affected feature's acceptance; demo alone proves none of these. |
| Student | Confirm actual deadline (currently approximately 15 December 2026), delivery/process evidence and schedule, preserving correction time. | Final delivery scheduling. |

No paid service, public deployment, cloud resource or real private upload is authorized by this document. Optional multiple-choice marking remains deferred until core acceptance and an explicit inclusion decision. Secrets, private data, provider responses and tokens stay out of Git/logs/static assets.
