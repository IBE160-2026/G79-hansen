---
title: Reach the app securely from two devices
type: feature
created: 2026-11-18
status: draft
route: dispatch
review_loop_iteration: 0
story_key: 4-1-reach-the-app-securely-from-two-devices
baseline_commit: 7f22a28d7e93ee6ea09e989f04496f26a3bdde48
context: [.docs/implementation-artifacts/epic-4-context.md, .docs/implementation-artifacts/hosting-plan-4-1.md]
---

<frozen-after-approval reason="human-owned intent; hosting choices remain unapproved">

## Intent

Make StudyBuddy reachable from PC, mobile and an assessor's ordinary browser. The student requires zero new hosting fees, prefers this Windows PC and requires access for people outside their private network. Reuse the active Supabase Free test project in Paris; Story 3.4 is already activated. Submission: 15 December 2026, IBE160 at Molde University College.

Propose this PC plus Tailscale Funnel, using existing infrastructure and Windows PDF containment. A paid Render service and private-only Tailscale Serve do not meet the clarified intent. Provider/region/cost/HTTPS/backup/deletion choices must be settled before external activation.

## Boundaries & Constraints

One backend process, loopback only, same-origin API/UI, HTTPS secure cookies, owner-scoped credentials and existing RLS. Saved content persists in Supabase; restart ends application sessions. Preserve source/PDF limits, budget journals, cleanup authority and seven-day content-free outcomes. Current physical retention and earlier acceptance gates remain open. Never reset budgets, invoke a real model for these checks, expose repository directories, enable router forwarding, create another Supabase project or enable paid services. Public availability does not grant access to private documents.

PC hosting entails student-managed availability. Funnel and TLS/redirect changes require specific authorization after local preparation. Existing Tailscale configuration may serve other work: inspect narrowly and preserve unrelated mappings. No configuration or application code has changed during planning.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure |
| --- | --- | --- | --- |
| Two devices | Same owner, separate browsers | Same library and acknowledged progress | Existing conflict/retry rules |
| Foreign access | Other account, substituted IDs | API/DB/Storage deny access | No content in errors/logs |
| Restart/sleep | Host unavailable or restarted | Outage is clear; fresh login after restart | Saved data/budget survive |
| Recovery | Wrong-browser/replayed link | Restricted callback rejects it | No private access |
| Backup restore | Snapshot predates deletion/spend | Reapply deletion, retain highest spend/block | Keep service closed on doubt |

</frozen-after-approval>

## Confirmed preparation decisions — 18 November continuation

Student selected this Windows PC, free public Funnel access, existing Supabase Free/Paris and same-PC backup in `C:\StudyBuddy-Backup` through submission, accepting PC-loss risk. Assessor gets an individual account; email is explicitly deferred. These authorize local preparation, not public activation, email sending or account creation. See `hosting-local-preparation-4-1.md` for route ownership and the bounded execution sequence.

## Open Questions

1. Assessor email and account provisioning authorization are deferred by the student. Resume this question when the address is available; do not ask again during independent local preparation.
2. A 15 January 2027 shutdown review remains a proposal. Schedule review on that date or agree another date before release; never automatically delete the shared project.

## Code Map

- `app/main.py`: reuse `/health`, request protection and access-log query redaction.
- `app/config.py`, `.env.example`: exact HTTPS origin, Secure-cookie selection, server-only configuration.
- `app/api/auth.py`, `app/services/sessions.py`: callback/browser binding, expiry/restart; shared email admission is deferred work.
- `scripts/pdf_probe.py`, `app/adapters/pdf.py`: existing Windows Job Object isolation avoids a Linux rewrite.
- `app/services/model_budget.py`: durable monotonic journal and blocked latch; existing local state must not be initialized anew.
- `.docs/implementation-artifacts/deletion-acceptance.md`, `deferred-work.md`: retain evidence and outstanding gates.
- `hosting-local-preparation-4-1.md`: existing 443/8765 football and 8443/3000 SURE mappings are private Serve routes; preserve both. Separate 10000 is the candidate for StudyBuddy, pending fresh conflict checks.

## Tasks & Acceptance

**Execution after decisions:**

- [ ] `hosting-plan-4-1.md` -- record answers and exact authorized scope.
- [ ] `app/api/auth.py`, `app/services/sessions.py` -- bounded shared signup/recovery admission before public exposure; configure agreed assessor access.
- [ ] `.env.example`, `README.md`, `scripts/start-hosted.ps1` -- document and prepare one-process Windows startup, persistent server-only state, sanitized logs and safe stop; do not automatically publish.
- [ ] `scripts/backup-studybuddy.ps1`, `hosting-plan-4-1.md` -- implement agreed encrypted backup/retention and isolated restore procedure without budget rollback or document resurrection.
- [ ] `tests/test_auth.py`, `tests/browser-auth.cjs` -- focused admission/config regressions; reuse existing ownership checks rather than duplicate them.
- [ ] `.docs/implementation-artifacts/hosting-acceptance.md` -- after specific activation approval, record Funnel origin, redirects, fresh real-device login, isolation, restart and cleanup evidence; preserve incomplete acceptance gates.

**Acceptance Criteria:**

- Given resolved hosting decisions and completed local controls, when activation is explicitly approved, then only the intended app port becomes publicly reachable over HTTPS without new hosting fees.
- Given two physical devices and an authorized assessor account, when they use ordinary browsers, then private live access, restart and ownership behavior match the matrix without requiring assessor Tailscale installation.
- Given synthetic data, when backup/restore and deletion are exercised, then evidence distinguishes active removal, retained copies and unresolved physical retention; logs contain no private material.

## Implementation Notes

18 November: authorized local email subtask completed in [spec-4-1-local-email-admission.md](spec-4-1-local-email-admission.md), with 221 offline auth/admission tests and review gaps closed. Durable shared 2-global/1-recipient rolling-hour reservations; unsafe/unconfigured state stops dispatch. No production journal/configuration or server restart. Email implementation is complete locally; assessor provisioning, startup, backup and public acceptance remain unchecked above.

Later continuation: [local startup subtask](spec-4-1-local-hosted-startup.md) complete/reviewed with99 focused checks. `scripts/start-hosted.ps1`, preflight and placeholder hosted environment are prepared. Parent startup/configuration task above remains unchecked because actual private hosted configuration and runtime startup are still unexecuted; backup/account/public acceptance remain pending. No existing runtime state or routes changed.

Later backup continuation: [local prepared-bundle component](spec-4-1-local-backup-bundle.md) complete/reviewed with 62 focused checks, including real Windows crypto. Actual root ACL restricted, root still empty. Student has no established export password/access. Parent backup task remains unchecked: full live capture, consistency, scheduling, actual isolated PostgreSQL/Storage import and monotonic/deletion reconciliation are still unproven. No password/account/provider/runtime/public change.

## Spec Change Log

## Review Triage Log

## Verification

Planning: inspect source/provider docs and read-only connection state; `git diff --check`. No code tests needed for this draft. Implementation: focused auth checks plus actual PC/mobile/external-browser evidence; no broad repeated provider suites without new evidence. Reuse existing Story 3 results with their documented limits.

18 November continuation: read-only local route/process/task ownership established; backup folder empty. Assessor access choice recorded. No app-code change, tests, model calls, backup execution or activation. The earlier frozen proposal is preserved verbatim; confirmed decisions above supersede its unapproved-choice wording for local preparation only.
