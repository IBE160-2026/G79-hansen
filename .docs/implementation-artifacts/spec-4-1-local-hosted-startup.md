---
title: Prepare safe foreground Windows startup for hosted StudyBuddy
type: chore
created: 2026-11-18
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 6a77afe3869f8cdd0aeddf1eacd72b5eb3ff718b
context: []
---

<frozen-after-approval reason="Student authorized the next local preparation step; activation remains separate">

## Intent

Prepare a safe Windows foreground launcher for the existing one-process app behind the proposed HTTPS proxy. The operator needs reproducible validation, fixed loopback binding and sanitized diagnostics before later activation. This subtask prepares files and offline tests; it does not start/restart the real server or publish anything.

## Boundaries & Constraints

Preserve running port8000, private Tailscale mappings443/8765 and8443/3000, current .env, keys, budgets and Supabase project. No model/email/provider calls, real credential reads, actual state initialization, scheduled tasks, paid resources, downloads or Funnel/Supabase changes during implementation/testing. Use installed libraries and standard facilities. Never initialize/reset budget, signing key or email journal during launch/check. One backend worker, no reload, loopback127.0.0.1:8000 only, proxy headers trusted only from127.0.0.1 and no access logging. Current .env supports local HTTP; a separate ignored hosted environment is required. Errors must contain safe categories rather than environment values, secrets, dotenv input lines or raw exception details.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure |
| --- | --- | --- | --- |
| Valid configuration | Explicit valid HTTPS auth and existing enabled-feature state | Check exits successfully without starting or mutating; actual launch fixes server settings | Safe summary only |
| Unsafe config | HTTP, loopback exemption, malformed/secret provider key, missing feature state | Reject before application/server starts | Generic nonzero error |
| Collision | Existing port8000 listener | Reject; never stop or replace it | Safe port-busy category |
| Journal | Configured journal malformed/missing/clock-invalid | Reject without reservation/reset | Safe category |
| Email disabled | Empty email journal setting | Password login remains usable; email fails closed as before | Explicit safe disabled notice |
| Hostile input | Bad/missing env file or shell-sensitive path/value | Treat path as data; no execution and no secret output | Generic nonzero error |

</frozen-after-approval>

## Code Map

- `app/config.py`: reuse `Settings.from_env`, `available`, `secure_cookies`, `model_available`, `save_backend_key`; do not weaken configuration checks or change demo defaults.
- `app/services/model_budget.py`: `ModelBudget.read()` checks existing journal without resetting state. Respect blocked state; never initialize/unblock it. Validate enabled generation has a real non-placeholder key and existing valid budget.
- `app/services/email_admission.py`: reuse existing schema/clock validation; add a small read-only inspection method if needed. No reservation, pruning, clock update or file creation during preflight. Missing configured state rejects startup; unconfigured email remains disabled.
- `app/main.py`: create the app only after preflight passes; preserve auth/CSRF/ownership behavior. No app features or routes change.
- Existing S3 settings: when Save is enabled require existing valid backend key, Paris region and project ID matching configured Supabase URL, and legacy anon S3 key (never secret/service key).
- README/.env.example: current local/demo commands remain unchanged; add hosted launcher instructions separately.

## Tasks & Acceptance

- [x] `scripts/start-hosted.ps1`: PowerShell5-compatible wrapper anchored to repo root; explicit ignored `.env.hosted` default and optional literal path, plus `-Check`. Invoke installed uv with offline/no-sync/locked behavior, fixed Python module and no evaluated shell strings. Keep foreground Ctrl+C stop; no background windows, kill commands or network configuration. Suppress untrusted native dotenv/exception stderr and return a generic failure category/exit code, so malformed secret lines cannot leak.
- [x] `scripts/hosted_server.py`: validate effective settings before create_app/Uvicorn; reject unsafe auth/feature state without printing values. Validate state paths are existing regular files, distinct and not confused across budget/key/journal. Check loopback8000 availability without replacing listeners; check mode must not retain a listener. Actual launch explicitly sets workers1/reloadFalse/loopback8000, proxy headers with loopback allowlist, no access log and bounded keepalive. Do not run actual launch during this task.
- [x] `app/services/email_admission.py`: minimal read-only journal readiness inspection reusing schema/clock checks; no change to reservation semantics. Keep it bounded and fail closed, including SQLite errors. Test that inspection leaves bytes/state/sidecars unchanged.
- [x] `.env.hosted.example`, `README.md`: placeholders only; exact HTTPS origin with separate candidate port10000, no loopback exemption, feature/state paths and mail-disabled option explained. Real settings remain outside Git. Explain check/start/Ctrl+C, persistent state, restart invalidating sessions and that launcher never activates Funnel. Document ambient process env precedence and safe diagnostics.
- [x] `tests/test_hosted_startup.py`: focused offline tests for every matrix row, exact Uvicorn arguments with mocked run, no app import/run for failed or check mode, configured feature validation, unchanged state and sanitized failure output. Parse/check PowerShell and exercise wrapper with synthetic env/missing/malformed files where useful; never read real .env/state or touch real port8000 during tests (mock collision probe).

**Acceptance Criteria:**

- Given synthetic valid hosted settings, when check executes, then no app/server/provider starts and state stays unchanged; when run is mocked, then only the fixed one-worker loopback configuration is selected.
- Given unsafe config/state or occupied port, when launch is requested, then it rejects before app creation without exposing input values or affecting another process.
- Given the real machine, when this preparation task finishes, then current server/routes/runtime secrets remain untouched and activation still requires separate later approval.

## Implementation Notes

Continuation authorizes this bounded local subtask. Backup/restore, actual runtime configuration, assessor address and public acceptance remain in the parent Story4.1. Keep code compact; no new dependencies or generalized deployment framework.

Implemented foreground wrapper and preflight module, separate placeholder environment example and read-only email readiness inspection. The wrapper prevents uv auto-dotenv loading; a bounded literal app-variable loader rejects malformed/duplicate/unknown input before setting process values. No expansion or evaluated shell strings. Native stderr is suppressed and stdout restricted to fixed categories. Inspection rejects sidecars/concurrent changes and does not reserve/prune/update state. Configured blocked/exhausted valid model budgets remain unchanged and do not prevent login/library startup; the generation gate remains authoritative.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Resolution |
| --- | --- | --- |
| Pre-review P1: valid blocked/exhausted budget initially rejected entire startup | medium | Removed capacity-based startup rejection; retain structural validation and unchanged runtime generation denial. Three synthetic budget-state cases passed. |
| Pre-review P2: native dotenv parser can warn and continue on malformed input | medium | Strict bounded literal parser now rejects entire input before loading values or app creation; wrapper passes path as data with uv auto-env disabled. Parser and actual PowerShell rejection cases passed. |
| Pre-review P3: original quoted subset accepted embedded quote garbage | medium | Restrict quoted values to the matching quote form; malformed quote/control/size cases passed. |
| Test P4: pre-existing zero-timeout concurrency test required at least one competing winner | low | One observed all-denied run was safe behavior, not a quota violation. Test now permits zero competing winners and requires uncontended progress afterward; production locking/limits unchanged. Final parent run passed. |

One focused independent review covered correctness, edge cases and test coverage and found no remaining actionable defects. Extra standalone review layers were skipped to keep this bounded local preparation short. No findings deferred in this subtask.

## Verification

Run only `uv run --locked pytest -q tests/test_hosted_startup.py tests/test_email_admission.py` if email-readiness code changes, plus scoped whitespace check and PowerShell syntax parse. Use synthetic state, injected offline adapters and mocked server/probes. Do not rerun browser/provider/broad auth suites without a new failure.

Final parent run: **99 passed**, one inherited Starlette/httpx deprecation warning, **12.96s**. Every matrix row was covered; PowerShell parse and four actual wrapper rejection invocations used synthetic files only. No real listener, credentials/configuration, runtime state, provider or model API was used. Actual server launch remains unexecuted; wrapper/preflight behavior is verified locally, not live hosting acceptance.
