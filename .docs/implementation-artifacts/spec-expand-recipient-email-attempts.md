---
title: 'Allow a second authentication email attempt without resetting history'
type: 'feature'
created: '2026-11-21'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: a22c11d72f9478508fdf8f92763d3fa55f5a5a4b
context: [CLAUDE.md]
---

<frozen-after-approval reason="Student approved the proposed 2-per-recipient/2-global policy and implementation/activation on21 November2026">

## Intent

The student cannot retry signup while preparing a second account for the owner-
isolation test and asks to increase attempts. The current shared signup/recovery
gate permits one reservation per normalized recipient and two globally in a
rolling hour. At10:50 the journal held one reservation from10:34:51, expiring
at11:34:51 local time. Provide a bounded second attempt while retaining durable
history. Approved policy: **two per normalized recipient and two globally per
rolling hour**, shared by signup/recovery. Existing reservations still count.

## Boundaries & Constraints

Always preserve journal secret, timestamps, last-seen clock and model budget.
Signup/recovery share durable limits across browsers/restarts; uncertain
dispatch consumes its reservation. Keep bounded storage/concurrency, fail-closed
validation, generic errors and existing authentication. Store keyed digests only.
Upgrade explicitly and transactionally.

Never reset/refund history, expose secrets or weaken authentication. No agent
email/model calls, new accounts, dependencies, Supabase/SMTP changes or paid
services. Restart only the checked StudyBuddy worker after verification.

## I/O & Edge-Case Matrix

| Scenario | State | Expected behavior | Failure |
| --- | --- | --- | --- |
| Recipient retry | One existing signup/recovery reservation | A second permitted attempt consumes additional global capacity | Generic429 at either agreed limit |
| Exact expiry | Oldest reservation reaches3600 seconds | Only that expired reservation ceases counting | No premature refund |
| Upgrade | Valid version1 journal with prior rows | Explicit upgrade preserves every digest/timestamp and metadata secret/clock | Roll back transaction on failure |
| Unsafe state | Missing, malformed, locked, unwritable, sidecars or clock rollback | No dispatch/automatic repair | Safe unavailable response |
| Concurrency/restart | Separate service instances or cancelled/failed calls | Durable atomic limits still hold | No duplicate capacity |
| Old application | Upgraded journal opened by old version | Fail closed; never restore an older journal to regain capacity | Document forward recovery |

</frozen-after-approval>

## Code Map

- `app/services/email_admission.py`: recipient is currently a version1 primary
  key. Reuse atomic `reserve`, `_validate` and read-only `inspect_ready`.
- `scripts/email_admission.py`: existing exclusive `init` command; add explicit
  existing-state upgrade rather than initialization/reset.
- `tests/test_email_admission.py`: real SQLite/fake provider matrix, including
  preservation/rollback and shared recipient limits across purposes/processes.
- `scripts/hosted_server.py`, `tests/test_hosted_startup.py`: preflight uses
  `inspect_ready`. Retain validation/environment precedence; sanitize only the
  new child process's inherited app variables for hosted activation.
- `app/api/auth.py`, `tests/test_auth.py`: reuse existing admission/error cleanup;
  no endpoint or authentication redesign.
- `README.md`, `.docs/implementation-artifacts/assessor-access.md`: replace current
  one-recipient wording and document explicit upgrade/operational limits.

## Tasks & Acceptance

- [x] `app/services/email_admission.py` — bounded version2 repeated-recipient
  reservations retaining each timestamp and existing transaction/privacy fences.
- [x] `scripts/email_admission.py` — explicit exclusive version1→2 upgrade,
  exact preservation of existing rows/metadata, safe idempotent already-current
  handling and atomic rollback. HTTP requests never upgrade state.
- [x] `tests/test_email_admission.py` — exercise the matrix through real SQLite,
  separate instances/process reopen and both HTTP purposes without network.
- [x] `tests/test_hosted_startup.py` — preserve startup rejection/inspection rules.
- [x] `README.md`, `.docs/implementation-artifacts/assessor-access.md` — accurate
  new limits and no-reset/forward-recovery instructions; keep dated old results.
- [x] `.docs/implementation-artifacts/hosting-acceptance.md` — verify offline,
  stop the checked worker, explicitly upgrade the journal, restart through the
  hidden launcher and verify preserved state/HTTPS. User performs any email retry.

Given the approved limits and an existing reservation, when the upgraded app
receives another eligible request, then it reserves the additional attempt
without losing old usage. Given rejected/uncertain requests, when the process
restarts, then prior reservations still constrain capacity. Given valid upgraded
state, when hosted startup runs, then login/demo remain available and the same
budget/capability/configuration remain intact.

## Implementation Notes

Dispatch route: persistent migration and activation require a policy decision.
Prior documentation is committed separately at the baseline; the working tree
was clean before this proposal. No application/state changes had been made at
the proposal stage.

Parent performs the final real-journal upgrade/restart and records activation;
the implementation handoff supplies verified code and offline tests first,
leaving that operational checklist item for the parent.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence / disposition |
| --- | --- | --- |
| Blind1: current issue still says approval/activation pending | low | Direct finalization correction: close the tracking entry with actual activation and preserved-state evidence. No runtime defect. |
| Blind2: planning notes still describe no implementation | low | Rejected as a spec-only edit request; earlier notes describe the planning/handoff stage and the appended parent record explicitly states activation. Final completion notes will identify the finished state. |
| Blind3: no admission test after upgrading active prior usage | low | Patch the focused migration test to cover one preserved active normalized-recipient reservation, one permitted retry and exact expiry. |
| Blind4: actual v1 rejection needs a permanent duplicate regression | false | Parent executed immutable actual v1 code from baseline a22c11d72f9478508fdf8f92763d3fa55f5a5a4b against v2 synthetic state; rejection and unchanged bytes passed. That old code cannot drift. Existing matrix evidence is real, rather than an inferred assertion. |
| Blind5: historical fixture imports production schema | medium | Verified by verification reviewer: replacing legacy PRIMARY KEY with UNIQUE left127 tests passing while actual historical state was rejected. Patch independent frozen SQL shared by the two migration consumers. |
| Blind6: some unsafe legacy-state inputs lack direct upgrade tests | low | Add representative oversized/nonregular/bad-value cases to the existing rejection matrix; production already uses shared validators, no new guard needed. |
| Blind7: concurrency may only prove an upper bound | low | Complete remaining capacity sequentially, then reject the next attempt for both repeated/distinct recipients. |
| Verification1: migration fixtures track the implementation contract | medium | Pre-verified broken-verification gap, same root cause as Blind5. Same independent baseline-fixture patch; both findings retained here. |
| Root1: sensor guide includes host journal-upgrade instructions | low | Direct deletion from sensor-facing flow; operator upgrade instructions remain in README. |

Edge-case reviewer returned no findings. No production-code defect was found;
review patches improve independent verification and final documentation.

All review patches are complete: frozen independent v1 fixtures, active prior
usage/expiry, expanded unsafe migration inputs and exact concurrency capacity.
Final parent verification:319 tests passed, one inherited TestClient warning,
38.51 seconds. No deferred findings. Final read-only live inspection at11:34
confirmed schema2, one active reservation and one remaining global attempt.

## Verification

`python -m pytest -q tests/test_email_admission.py tests/test_auth.py tests/test_hosted_startup.py`
must pass with synthetic journals/providers. Run scoped `git diff --check`.
Before activation, compare preserved reservation/metadata values without printing
them, and fingerprint model budget/capability/configuration before/after.
Inspect the upgraded real journal read-only and verify normal TLS, workspace200,
anonymous auth available/no-store and exactly one loopback worker. Existing
same-address provider cooldowns remain separate; see
[Supabase rate limits](https://supabase.com/docs/guides/auth/rate-limits).

Parent verification21 November:310 requested offline tests passed after all implementation edits. Matrix audit: shared HTTP retry, exact expiry, explicit upgrade/idempotence, rollback/unsafe state and separate-instance/process-reopen tests ran; actual baseline-v1 rejection of a synthetic v2 journal also passed. At11:27 the parent explicitly upgraded real state and restarted only the checked worker. Secret/clock/reservation invariants and configuration/model budget/capability matched; HTTPS startup passed. One active reservation and one free global slot remained. See hosting-acceptance.md; no real email/model operation was triggered.
