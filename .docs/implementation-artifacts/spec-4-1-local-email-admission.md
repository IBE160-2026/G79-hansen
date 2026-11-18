---
title: Bound shared authentication email dispatch before public hosting
type: chore
created: 2026-11-18
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: fd72e94a6b5796f1910d6176a0b601af9a4b4ca2
context: []
---

<frozen-after-approval reason="Local preparation authorized by student's continue instruction; public activation remains separate">

## Intent

Implement the shared signup/recovery email admission subtask from Story 4.1. Fresh browsers currently bypass the pending-attempt limit and can exhaust the shared provider email allowance. Reserve durable recipient/global capacity before either email-producing provider call. This is local preparation only; the remainder of Story 4.1 (backup, startup, assessor account and activation) stays pending.

## Boundaries & Constraints

Use existing standard-library facilities, single-app-process architecture and server-only state. No email, live provider/model calls, Supabase changes, server restart, route changes, new packages, public deployment or budget/key reset. Preserve CSRF, callback binding, login/logout and existing generic response contracts. Bound storage and concurrency; store no raw addresses, passwords or tokens in the admission journal or logs. Missing/invalid/unwritable admission configuration must disable email dispatch while password login and the fixed demo remain available. Never silently create/reset state on an HTTP request. Preserve uncertain dispatch reservations across failure and restart.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure |
| --- | --- | --- | --- |
| Shared recipient | Signup then recovery from fresh browser, normalized same address | At most one dispatch per recipient in rolling hour | Generic 429 before provider |
| Shared global | Distinct recipients across both endpoints | At most two reservations in rolling hour | Generic 429 before provider |
| Restart/failure | Provider failure or new app/service instance | Existing reservation still consumed | No refund/reset |
| Unsafe state | Missing/corrupt/locked/unwritable journal or clock rollback | No dispatch | Generic safe error, no raw details |
| Invalid request | Bad CSRF/body or exhausted pending capacity | No provider call or email reservation | Existing error semantics |
| Concurrency | Simultaneous reservations through separate service instances | Limits hold atomically | Bounded rejection, no waiting queue |

</frozen-after-approval>

## Code Map

- `app/api/auth.py`: `submit` signup branch and `recovery_request` share a durable admission service via `app.state`. Reserve after validated credentials and pending-attempt admission, before SDK dispatch, using existing threadpool facility; existing exception paths must discard pending state on denial.
- `app/config.py`, `app/main.py`: add server-only `AUTH_EMAIL_ADMISSION_PATH` setting and injectable service for offline tests. Default unconfigured means no dispatch; do not make `Settings.available` depend on the journal, since login must work.
- `app/services/model_budget.py`: example of durable fail-closed server state; do not change it or reuse its actual files.
- `tests/test_auth.py`, `tests/auth_browser_app.py`: legacy auth tests intentionally need an explicit test-only permissive injected service; never automatically bypass admission because a fake adapter was supplied. No production switch disables the gate.
- `.env.example`, `.gitignore`, `README.md`: document email setup and ignored journal/SQLite sidecars.

## Tasks & Acceptance

- [x] `app/services/email_admission.py`: implement durable bounded reservations using SQLite transactions, zero/short lock timeout and durable commit. Normalize strip/casefold recipient and persist keyed digest with locally generated journal secret, timestamps and schema version only. Fixed maximum two dispatches globally and one per recipient per 3600 seconds, shared across purposes; prune expired rows. Validate schema/data/clock and refuse unsafe state, including missing journal. No refunds for uncertain outcomes.
- [x] `scripts/email_admission.py`: explicit offline exclusive initialization command for new state only; refuse overwrite. Avoid raw addresses/output. Initialization is not run against real configuration during this task.
- [x] `app/config.py`, `app/main.py`, `app/api/auth.py`: wire service and reserve on both endpoints; keep login available. Fail closed with existing generic 429/503 errors. No receipt/body logging.
- [x] `tests/test_email_admission.py`: offline real-journal checks for every matrix row, including process-reopen persistence, exact rolling-window boundary, normalization, provider failure, concurrent instances, clock rollback, corrupt/missing/locked state and no reservation on rejected requests. Explicitly test default app cannot dispatch without state while login works.
- [x] `tests/test_auth.py`, `tests/auth_browser_app.py`: preserve existing tests through explicit injection confined to test code; run focused offline Python auth and admission suites. Do not run browser/provider/broad regression unless a new failure requires it.
- [x] `.env.example`, `.gitignore`, `README.md`: explain initialization, fixed limits, dedicated path/sidecars, no reset on restart or uncertainty, and that app-local limits do not account for provider sends from other tools/projects. Keep foreleser email deferred.

**Acceptance Criteria:**

- Given configured synthetic journal and offline provider adapter, when independent browsers invoke either endpoint, then atomic durable combined limits apply and denied calls never reach the provider.
- Given no safe journal, when email dispatch is requested, then it fails closed without breaking password login/demo.
- Given prior reservations, when the service restarts or an outcome is uncertain, then unused capacity is not falsely replenished.

## Implementation Notes

Local subtask separated to keep unresolved assessor/backup/public acceptance outside this implementation handoff. Student authorized continuing local preparation; no further public approval is requested here.

Implemented fixed limits using durable SQLite transactions and a bounded shielded IO owner. Explicit offline initialization only; no runtime state initialized or existing server restarted. Test-only injections preserve old auth matrix independently of the real-gate tests. All local tasks complete; parent Story 4.1 remains incomplete.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and disposition |
| --- | --- | --- |
| Parent P1: cancellation before threadpool entry could leak a capacity slot | medium | Original reservation acquired a slot outside the worker's lifecycle. Retained shielded owner task now releases it in its own finally; targeted pre-worker cancellation regression passed. Patched before independent review. |
| Verification V1: no write/commit-failure HTTP coverage | medium | Existing unsafe-state tests exercise pre-write failures only. Add offline injected commit failures at both endpoints, including an uncertain committed outcome; patch test coverage. |
| Verification V2: cancellation test skips actual journal mutation | medium | Mocked pool does not call the journal operation. Add held real-worker HTTP cancellation coverage proving durable reservation, no provider call and slot recovery; patch test coverage. |

Independent correctness and edge tracing reported no actionable defects. Limits apply at reservation time; this is not a guarantee about exact provider-send timing or sends initiated by other tools.

V1 and V2 closed: tests inject write, pre-commit and uncertain post-commit failure for both endpoints, and hold real SQLite commits while cancelling both HTTP waiters. They prove rollback/no-refund, provider suppression, persistent capacity and reusable worker slots. No findings deferred.

## Verification

Run only `uv run --locked pytest -q tests/test_email_admission.py tests/test_auth.py` and scoped whitespace check. All provider adapters in these tests must be offline. No network, real mail, model requests or live state initialization.

Final parent verification 18 November: **221 passed**, one inherited Starlette/httpx deprecation warning, 5.82 seconds. Every matrix row is covered by the executed admission tests. No browser/provider/broad suite rerun.
