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

## Open Questions

1. Accept PC + free Funnel public HTTPS, with PC-on availability, or choose another zero-fee public host requiring new platform investigation? The installed Tailscale is online; plan entitlement and existing mappings still need verification.
2. Accept daily encrypted DB plus object backup, maximum seven-day retention and a 15 January 2027 shutdown review? Name an existing separate backup medium; otherwise real private files remain gated. No automatic deletion of the shared test project.
3. Assessor access: separately authorize an individual test account, or select a free SMTP arrangement for ordinary registration/recovery? Built-in email only serves team addresses and has a small shared quota. Never share credentials in Git or assume assessor email authorization.

## Code Map

- `app/main.py`: reuse `/health`, request protection and access-log query redaction.
- `app/config.py`, `.env.example`: exact HTTPS origin, Secure-cookie selection, server-only configuration.
- `app/api/auth.py`, `app/services/sessions.py`: callback/browser binding, expiry/restart; shared email admission is deferred work.
- `scripts/pdf_probe.py`, `app/adapters/pdf.py`: existing Windows Job Object isolation avoids a Linux rewrite.
- `app/services/model_budget.py`: durable monotonic journal and blocked latch; existing local state must not be initialized anew.
- `.docs/implementation-artifacts/deletion-acceptance.md`, `deferred-work.md`: retain evidence and outstanding gates.

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

## Spec Change Log

## Review Triage Log

## Verification

Planning: inspect source/provider docs and read-only connection state; `git diff --check`. No code tests needed for this draft. Implementation: focused auth checks plus actual PC/mobile/external-browser evidence; no broad repeated provider suites without new evidence. Reuse existing Story 3 results with their documented limits.
