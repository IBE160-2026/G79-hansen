# Epic 4 Context: Use and assess the finished app reliably

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Make the private live study flow reachable from multiple devices and give assessors reproducible setup instructions and evidence of the required behavior. Deliver a feasible, understandable IBE160 school project by 15 December 2026. Hosted availability and final acceptance must be demonstrated independently of the local fixed-example demo.

## Stories

- Story 4.1: Reach the app securely from two devices
- Story 4.2: Verify the full release and assessor setup

## Requirements & Constraints

- Before provisioning or deployment, record and resolve provider, region, plan, cost ceiling, Supabase region/quotas, email delivery, redirect configuration, HTTPS, backup/restore, deletion retention and cleanup. Paid resources and public deployment require authorization for the specific action. A proposed hosting choice is not approval.
- Live access must work from PC and phone for the same account. Saved source/settings/results and acknowledged card/quiz progress survive browser/server restart and reopen without a model request. Another account must fail direct database, Storage and API list/read/write/delete attempts against those records and files.
- Verify explicit Save, replacement, failure recovery and deletion against real database/storage/API. Upload or generation alone must not persist a private workspace. New session clears active work while preserving saved items. Pending/deleting work remains recoverable and must never appear successfully saved/deleted prematurely.
- Document backup retention and prove uncertain-upload reconciliation, stale-operation cleanup and physical-file handling before using real private material. Do not promise immediate erasure from provider backups. Keep synthetic fixtures and development accounts separate from real student content.
- Keep private documents, generated content, passwords, tokens, keys and database/file dumps out of Git, logs, public static routes and shared caches. Health/error evidence must be content-free.
- Preserve required text-file and text-based PDF support, physical page references, coverage warnings and enforced limits; validate extraction containment/resource limits on the actual deployment platform. Text-only availability does not establish full assignment completion. No OCR or table/figure interpretation is required.
- A clean checkout must run the complete labelled fixed-example demo from README without Supabase/model credentials. Explain live setup, limits and use of the assessor's own API key separately; example environment files contain placeholders only.
- Final evidence covers required functional/security behavior, the registered three-document quality evaluation, understandable failure states and manual accessibility checks. Existing sample quality results do not prove accuracy for arbitrary material. Optional multiple-choice scoring remains excluded unless explicitly added after core acceptance.

## Technical Decisions

- Retain one same-origin FastAPI application serving plain HTML/CSS/JavaScript and API routes, with Supabase Auth/Postgres/private Storage. Avoid a separate frontend deployment or extra services without a demonstrated need. One Render Python web service in Europe is a proposal whose exact region/plan/cost still needs agreement.
- Run one backend process for v1. Login state remains in bounded server memory; restart/redeploy invalidates application sessions and requires login again. Saved data and acknowledged progress remain in Supabase. Simultaneous sessions on different devices are supported; logout affects the initiating device.
- Use HTTPS with opaque HttpOnly, SameSite=Lax, Secure session cookies. Cookie mutations require same-origin and CSRF checks. Keep provider tokens on the backend, validate sessions on every private request and use request-scoped user credentials with owner policies. Ordinary document operations never use privileged provider credentials.
- Configure confirmation/recovery redirect allowlists for each environment. PKCE callback exchange is bound to the initiating browser, purpose, state and expiry. Restart-invalidated, expired, reused or wrong-browser links require a new attempt; recovery cannot expose documents and requires normal login after password change.
- Preserve owner/document/generation identities and revision/idempotency protocols across retries, conflicts and lifecycle changes. File/database work uses pending/ready/deleting coordination. Do not remove cleanup authority while an uncertain upload could still complete. Retain minimal content-free operation outcomes/tombstones for seven days without removing still-needed object recovery records.
- Version configuration, migrations and deployment instructions, while keeping secrets and backups outside version control. Add a content-free health endpoint and use safe error codes/request IDs/timing rather than raw provider bodies or request content.

## UX & Interaction Patterns

- Keep Norwegian labels, readable contrast, persistent input labels, visible keyboard focus and keyboard-operated answer reveal. Verify primary flows with keyboard and screen reader, narrow-window reflow and 200% zoom. Source inspection alone does not establish accessibility conformance.
- Reopening saved content restores independent acknowledged card/quiz positions with answers hidden. Tab switches preserve reveals during the current visit. A stale device must show a progress conflict and require fetching current progress before further writes; network uncertainty shows pending/failed sync rather than success.
- Invalid sessions clear private UI and offer login again. Recovery links explain the same-browser requirement. Deletion confirmation names the document and associated material; cancellation changes nothing, and failed deletion stays visible with retry.

## Cross-Story Dependencies

Epic 4 relies on live authentication, generation, private persistence, progress and deletion from Epics 2/3; unresolved acceptance gates remain visible rather than being inferred complete from implementation. Story 4.1 establishes authorized hosting and real multi-device evidence. Story 4.2 builds on that deployment to verify the complete release and assessor setup. Keep local demo reproducibility available throughout.
