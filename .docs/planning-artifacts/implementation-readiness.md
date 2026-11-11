# Implementation readiness — 2026-11-11

**PASS for the recorded incremental plan and Story 1.1 implementation.** This is planning readiness, not proof that the application/live integrations are complete. The first runnable demo is the authorized implementation scope for this session.

## Evidence and traceability

- Final [architecture](architecture/architecture-G79-hansen-2026-11-01/ARCHITECTURE-SPINE.md), [PRD](prds/prd-G79-hansen-2026-09-26/prd.md), and UX [DESIGN](ux-designs/ux-G79-hansen-2026-11-01/DESIGN.md)/[EXPERIENCE](ux-designs/ux-G79-hansen-2026-11-01/EXPERIENCE.md) exist and agree on adopted user behavior. Independent architecture review resolutions and deterministic lint are in the architecture review summary; these are document-level checks.
- [Epics](epics.md) contain four user-value increments and 14 stories. All FR-1–FR-12, NFR-1–NFR-5 and UX-DR1–UX-DR10 trace into scope/acceptance criteria. Demo coverage is explicitly partial for live requirements.
- The sprint generator parsed all four numbered epic headings and all 14 story headings. Its two warnings refer to the template's document title and generic "Epic List" section, not omitted work; no story is dropped and no illegal/orphan status is reported.
- Epic order is runnable demo → own-source study → saved private library → multi-device release acceptance. Stories depend only on earlier stories. The early PDF experiment precedes extraction integration. Accounts precede private source/real generation. Storage tables appear only with Save, not in demo setup.
- Story 1.1 uses the official minimal FastAPI application pattern, matching the architecture rather than importing an unrelated starter. It has a concrete file map and spec with API/browser verification.
- Current scope includes explicit Save, automatic progress for saved generations, hidden answers on reopening, restart re-login, and stale-view fetch-before-write. First Save captures positions; replacing a generation resets them. Logout still denies local access during provider outage; operation replay/deletion uncertainty requirements are captured in affected stories.
- Shared UI files occur in multiple epics because identity/model/storage/deployment have separate risk and feedback boundaries; epics are not artificial backend/frontend layers.

## Recorded milestone gates

These decisions have owners and revisit points, and affected stories stay in backlog until their gate closes:

| Gate | Owner | Required before |
| --- | --- | --- |
| PDF extraction fidelity and byte/time/memory evidence; tested adapter version | Student + builder | Story 2.4, via experiment 1.2 |
| Model/provider/API, cost ceiling, data handling and request limits | Student + assistant | Story 2.5 real integration |
| Supabase project/redirect/email configuration and owner-isolation test environment | Student + builder | Story 2.1 integration; no real account has been created here |
| Hosting/region/plan/cost, HTTPS, backups/restore/retention, stale cleanup | Student + assistant | Story 4.1 deployment; no paid/public action authorized here |
| Browser/screen-reader, real ownership/lifecycle and live content quality checks | Student + builder | Story 4.2 final application acceptance |
| Exact submission date | Student | Final delivery scheduling; provisional targets are not promises |

No unresolved gate is hidden inside Story 1.1. Its local fixed-fixture behavior requires no external service and introduces no database or migration.
