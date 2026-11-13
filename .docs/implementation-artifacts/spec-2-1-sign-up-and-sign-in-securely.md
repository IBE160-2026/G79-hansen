---
title: Sign up and sign in securely
type: feature
created: 2026-11-12
status: in-progress
route: dispatch
story_key: 2-1-sign-up-and-sign-in-securely
baseline_commit: 74fa5f971e187bbb3de924a8f438aff2cba5e782
review_loop_iteration: 0
context:
  - .docs/implementation-artifacts/epic-2-context.md
---

<frozen-after-approval reason="approved by the student on 2026-11-12">

## Intent

**Problem:** The demo cannot authenticate a student for later private features.

**Approach:** Add Supabase email/password signup, browser-bound PKCE confirmation, validated login and an account page. Retain the credential-free demo.

**Approved setup:** New `studybuddy-test` in a Free organization, specific Frankfurt `eu-central-1`, no paid add-ons, confirmation enabled and initial emails only to authorized team testers. User approved this plan/setup with “godkjenner”. Provisioning requires actual connected access; approval alone does not prove the project exists.

## Boundaries & Constraints

**Always:** Validate provider identity. Keep tokens in bounded single-process memory; browser cookies are opaque, host-only, HttpOnly, SameSite=Lax and Secure on HTTPS, with explicit loopback-only HTTP development. Protect signup/login and mutations with exact Origin/CSRF checks. Auth responses/errors/redirects are no-store. Each PKCE attempt has its own expiring verifier, state, browser binding and purpose; consume callbacks atomically. Follow AD-3 expiry/refresh rules. Clear submitted passwords; redact sensitive logs, including callback query strings.

**Never:** Persist passwords/browser tokens, expose privileged keys, trust signup's user object alone, share authenticated clients, accept implicit fragments or use mock authentication outside tests. No document tables, AI, recovery UI, deployment, paid provisioning or unapproved emails. Default demo makes no Supabase calls.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
| --- | --- | --- | --- |
| Signup | Valid email/password | Generic check-email state; isolated PKCE attempt | No session from an unconfirmed signup |
| Confirmation | Bound valid state/browser/code | Validate exchanged user; rotate opaque session ID; clean redirect | No credentials in URL after redirect |
| Bad callback | Wrong/missing binding, purpose, verifier, expiry, replay or restart | Reject before exchange | Safe restart-signup message |
| Overlap/race | Two attempts or simultaneous callbacks | Independent verifiers; at most one session per consumed attempt | No overwritten verifier or replay |
| Login | Confirmed credentials | Validate returned token with get_user; server-derived owner | Invalid/mismatched/incomplete response creates no session |
| Request protection | Missing/wrong Origin or CSRF | Reject before provider call | Content-free error, no-store |
| Missing config/outage | Disabled/missing settings, provider failure/timeout | Explicit unavailable/error state; demo still works | No mock success or secrets echoed |
| Browser isolation | Two clients with independent cookies | Independent session/CSRF state and refresh | Unknown/expired session denied |

</frozen-after-approval>

## Code Map

- `app/main.py`: static routes/demo-only validation handler; add injected configuration and safe auth errors without weakening demo rejection.
- `app/static/`: preserve `/` as demo; add `/account` with shared styles.
- `tests/test_demo.py`, `tests/browser-demo.cjs`: existing regressions.
- `.env.example`, `pyproject.toml`, `uv.lock`: no auth settings/SDK.

## Tasks & Acceptance

**Execution:**
- [x] `pyproject.toml`, `uv.lock`, `app/config.py`, `.env.example` — verify/lock `supabase==2.34.1`; explicit auth enablement, origin, HTTPS provider URL and publishable/anon key; missing settings fail closed.
- [x] `app/adapters/auth.py` — request-scoped SDK with bounded transport, no background refresh, safe errors and per-attempt memory storage; signup, exchange, login, get_user and explicit refresh.
- [x] `app/services/sessions.py` — bounded registries, atomic consumption, rotation, injectable clock, 30-minute idle/12-hour absolute expiry, refresh locks. Pending TTL: 10 minutes; capacity: 1,000 sessions/attempts, four attempts/browser; reject overflow.
- [x] `app/api/auth.py`, `app/main.py` — bootstrap/status, signup/login/callback routes, shared validation, CSRF/Origin, safe errors, no-store/referrer headers and redacted callback access logs; fixed clean redirects.
- [x] `app/static/account.html`, `account.js`, `styles.css` — labelled Norwegian forms, autocomplete, error focus/email retention, password clearing, duplicate/stale-response guards; explain confirmation in the initiating browser and fixed demo data. Recovery/full logout UX follow in 2.2/2.3.
- [x] `tests/test_auth.py`, `tests/browser-auth.cjs` — every matrix row, SDK transport contracts and real browser contexts with test-only adapters; safe logs/storage/headers, independent users/attempts, capacity/expiry and default demo isolation.
- [ ] `README.md`, `.docs/implementation-artifacts/auth-setup.md` — configured project/redirect setup, one-process runtime, live acceptance evidence separate from mocks. Never claim completion from offline tests alone.

**Acceptance Criteria:**
- Given approved setup, when testers complete real signup/confirmation/login, then identity is provider-validated and only an opaque session/safe display state reaches the browser.
- Given two browsers, when positive/negative cases run, then sessions remain independent and credentials never appear in storage/output/logs.
- Given no auth settings, when demo startup/tests run, then the fixed study flow works without external calls.

## Implementation Notes

2026-11-12: The student approved the concrete specification and Free/Frankfurt setup with “godkjenner”. The existing context/setup/reflection changes belong to this workflow and are preserved. Implement all locally verifiable work now; report actual provisioning/live acceptance accurately. No Supabase tools are currently available and browser/native access previously failed. The unchanged demo must remain safe without configuration. Never mark live acceptance complete from mocks or invent a provisioned project.

Session checkpoint 2026-11-12: Account configuration, adapter, registries, routes, account UI and offline tests are implemented. Parent corrections addressed malformed legacy-key JSON, encoded-path query redaction and null/raw-error UI responses; browser tests also found and fixed same-document fragment cleanup. Preserve these fixes. The user manually created the project and supplied its URL/publishable key; they are stored only in ignored `.env`. A read-only live `/auth/v1/settings` check returned HTTP 200, email enabled, confirmation required and signup allowed. This does not prove callback allowlisting, delivery or real account sessions.

The student asked to wrap up today because their five-hour usage allowance was nearly exhausted. Save the verified implementation checkpoint with status in-progress. Remaining work: actual project URL/template/allowlist setup and authorized two-browser live signup/confirmation/login checks, followed by the independent step-04 code review and any fixes. No new feature work or further email attempts started. The setup/spec approval persists; do not ask for it again. The README/setup task remains unchecked because live acceptance evidence is incomplete.

## Spec Change Log

2026-11-13 continuation: approved scope and baseline preserved. Provider settings
again confirmed required email confirmation. The one-worker live-configured local
server starts; account/status bootstrap and privacy headers were checked. Desktop
automation is unavailable (native pipe, os error 2), so the student was asked to
save URL Configuration. No actual account flow or independent review has run;
keep the story in-progress and do not advance to step-04 before live acceptance.

2026-11-13 follow-up: the student confirmed URL Configuration saved and reported
the guided first signup/email-confirmation flow worked. Server access evidence:
one signup 200 and callback 303, without auth query strings in inspected entries.
Separate private-window password login was requested; its result and remaining
live security cases are pending. This does not complete the live acceptance tasks.

The private-window check subsequently passed by student report (login form first,
then signed in); server login 200 observed. Wrong-password rejection and a second
authorized tester are being checked next. No full acceptance/review claim.

End-of-day 2026-11-13: wrong-password rejection passed (safe message and server
401). Only one authorized test account is available. Reusing the confirmation
link in the unauthenticated private window returned the login page by student
report; no new login was reported, but the exact rejection/error display was not
verified. Ten HTTP boundary checks against the configured local server passed.
The student asked to end for today; the test server was stopped. Preserve existing
scope, approval and baseline. Next session restart one worker, complete remaining
live acceptance and then independent review. No code changes or fresh full-suite
results today; status remains in-progress.

## Review Triage Log

## Verification

- `uv sync --locked --group pdf-experiment` and `uv run --group pdf-experiment pytest` — auth, demo and PDF tests pass.
- `node tests/browser-demo.cjs` and `node tests/browser-auth.cjs` — real browser regressions and account journeys pass.
- `git diff --check` — clean.
- Record actual provider checks; account acceptance remains pending until executed.

Implementation checkpoint: parent full pytest run **130 passed, 1 skipped**, one existing TestClient/httpx warning, 47.18 seconds; `test-results/auth-parent-verification.xml`. Implementation agent executed **12 real-browser auth scenarios** and all **11 existing demo scenarios**, locked sync and diff checks. Parent inspected desktop and 200% screenshots. These are offline app/SDK tests, not hosted account acceptance. Independent step-04 reviewers have not yet run. No completed-build or fully accepted-story status is claimed.
