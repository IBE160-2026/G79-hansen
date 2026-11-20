# Story 2.1 authentication setup and acceptance

The user reported on 2026-11-12 that the project has been created manually after the
organization. Project access, the Free plan and local configuration are verified;
email-template inspection and the remaining hosted confirmation cases are pending.
The application implementation is locally testable. **Provider reachability and
required email confirmation are verified. The student reports successful first
signup/email confirmation and separate private-window password login. The interim
independent review and its corrections are verified. Hosted HTTP authentication
and session isolation with two administrative test accounts passed 20 checks on
2026-11-14. A further 18 lifecycle checks and 24 real-browser checks passed;
remaining hosted email acceptance and final build acceptance are pending.** The organization's
Free plan is independently verified. The student explicitly approved retaining
Paris (`eu-west-3`) for this test project on 2026-11-14, superseding the original
Frankfurt requirement for this project only. Offline adapters live only in
`tests/`; the application has no mock-auth mode.

## Approved manual setup

**Assessor-access choice20 November2026:** the student chose both self-registration
and a pre-created ordinary app account as fallback. This does not authorize a
Supabase organization/project membership for the assessor. Read-only Auth settings
confirmed email provider enabled, signup not disabled and email autoconfirm false.
Application mail dispatch remains disabled; these public settings do not reveal
custom SMTP configuration. A sender, current HTTPS callbacks, durable admission
state and an explicitly authorized email/confirmation check still need preparation.
No account, email, auth setting or runtime state changed during this inspection.
See the latest [hosting plan](hosting-plan-4-1.md); the original local URLs below
are historical setup, not the intended HTTPS activation settings.

1. In Supabase, choose **Create an organization** first. Name it **Study Buddy**
   and select **Free**. Do not add a paid subscription or add-ons.
2. Use the existing **studybuddy-test** in **Paris (`eu-west-3`)**, explicitly
   approved by the student on 2026-11-14. The original plan specified Frankfurt;
   do not recreate or move the existing project. Keep its database password in a password manager; the
   application does not need that password.
3. Enable the email/password provider and **email confirmation**. The SDK adapter
   refuses signup responses containing an immediate session, so confirmation
   cannot silently become optional.
4. Under Authentication → URL Configuration set Site URL to
   `http://127.0.0.1:8000/account`. For this local test, add the redirect allowlist
   pattern `http://127.0.0.1:8000/api/v1/auth/callback[?]state=*`.
   The `[?]` character class is literal; the wildcard covers only the random
   state. Use the exact same scheme, host and port in the browser and APP_ORIGIN.
   The adapter supplies `email_redirect_to` with that callback and a new random
   state for each attempt. Do not allow arbitrary hosts or external return URLs.
   Supabase documents these pattern rules in its
   [redirect URL guide](https://supabase.com/docs/guides/auth/redirect-urls).
   For password recovery, also add the separate pattern
   `http://127.0.0.1:8000/api/v1/auth/recovery/callback[?]state=*`.
   On 20 November the dashboard rejected the earlier backslash escape. Use
   `[?]` for new dashboard entries; the old dated evidence below is historical.
   Keep the reset-password email's standard `{{ .ConfirmationURL }}` link so
   Supabase verifies it and returns an authorization code to the backend.
   This additional allowlist entry and template inspection have **not** been
   performed by the implementation tests; verify them before authorized live recovery.
5. Keep the standard confirmation email link through `{{ .ConfirmationURL }}`.
   Do not replace it with an implicit-fragment flow or a token-hash route: this
   app expects Supabase to confirm the email and redirect with `state` and `code`
   to the backend PKCE callback. Confirm that the state survives in the real flow.
6. Find the project's HTTPS URL and **publishable key** (or legacy **anon** key).
   Never use `sb_secret_...`, `service_role`, database credentials or privileged
   keys. Only send initial confirmation emails to authorized team testers. The
   Free provider's current email restrictions/rate limits must be checked in the
   dashboard before sending; do not add paid SMTP or other paid services here.

## Local server configuration

The default demo starts without any configuration and makes no Supabase requests.
`.env.example` lists the server variables; the app does not load `.env` itself.
Set them in the PowerShell process that starts the server. Obtain the URL/key
locally without committing them, exposing them in screenshots or pasting secrets
into terminal commands that are retained in shared logs.

Alternatively, the ignored local `.env` now contains the user-supplied project URL,
publishable key and explicit loopback settings. Load it only for the intended live
server (plain demo/test commands do not load it):

```powershell
uv run --env-file .env uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

```powershell
$env:AUTH_ENABLED = "true"
$env:APP_ORIGIN = "http://127.0.0.1:8000"
$env:AUTH_ALLOW_LOOPBACK_HTTP = "true"
# Set SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in this process from local settings.
uv sync --locked --group pdf-experiment
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Open `http://127.0.0.1:8000/account`. APP_ORIGIN and SUPABASE_URL must have no
trailing slash, path, credentials, fragment or query. The provider URL must use
HTTPS. HTTP app access is enabled only by the explicit loopback setting and only
for localhost/loopback IP origins. Other origins require HTTPS and Secure cookies.
Invalid/missing/disabled settings leave the demo working and make authentication
unavailable; there is no fallback identity. Optional AUTH_IDLE_SECONDS and
AUTH_ABSOLUTE_SECONDS may shorten, but never extend, the 1,800/43,200 second limits.

Use **one backend process**. Do not use multiple workers, a load balancer or reload
for live acceptance. Tokens, CSRF/browser state and PKCE attempts are bounded
single-process memory and intentionally disappear at restart. Browser cookies
are random host-only HttpOnly values with SameSite=Lax; they are Secure on HTTPS.
Closing the browser can also discard the browser binding. Each callback attempt
expires after 10 minutes. There are at most 1,000 sessions, 1,000 attempts and
1,000 browser bindings, with four simultaneous attempts per browser. Overflow is
rejected. Successful authentication extends its browser binding to cover the new
session's absolute lifetime; a pending attempt retains binding authority through
its own deadline, without extending any session deadline. Provider operations use
request-scoped SDK/HTTP clients, a shared 10-second elapsed budget, at most
3-second connect and 5-second transport phase timeouts, no redirects, retries or
background refresh. The remaining budget is checked between SDK requests,
response chunks and underlying network reads/writes/TLS operations; network phase
timeouts are capped by the remaining time. HTTP framing cannot reset the budget
by trickling incomplete headers. This is a cooperative deadline, not cancellation
of a running native operation: an in-progress blocking call (including the system
DNS resolver) must return before its elapsed deadline is observed. There is no
abandoned network thread presented as canceled work. The narrow HTTPX/httpcore
backend integration is pinned by the lockfile and covered by transport tests.
Auth UI requests time out after 15 seconds.

Each new authenticated status validation uses provider `get_user`; overlapping
requests for the same session share only that in-flight validation. Followers wait
without retaining worker threads, and cancellation of one HTTP waiter cannot
orphan the shared owner. Within 30 seconds of token expiry it explicitly refreshes,
then validates the returned user. Owner changes, invalid/incomplete responses and
provider failure deny locally and retire the registry session. Status responses
never set or delete the session cookie: a delayed old denial must not erase a
newer successful login cookie. An obsolete opaque cookie grants no authority and
is replaced by the next successful authentication. Sessions expire after
30 minutes idle or 12 hours absolute; provider refresh never resets those limits.
Recovery and complete logout controls belong to Stories 2.2/2.3. No private
document data, document tables, AI processing, persistence or deployment is added.

Uvicorn's access logger removes query strings, including encoded callback paths.
The SDK boundary suppresses provider exception text and HTTP client URL logging.
Do not add upstream request-body/query logging: reverse proxies, browser network
captures and Supabase dashboard logs are outside this application's redaction.

## HTTP contract

All `/account` and `/api/v1/auth...` responses, errors, redirects and method/path
errors have `Cache-Control: no-store` and `Referrer-Policy: no-referrer`.

| Route | Request | Safe response |
| --- | --- | --- |
| GET `/api/v1/auth/status` | Same configured origin/host; cookies optional | Disabled: `{available:false,authenticated:false}`. Enabled: `{available:true,authenticated:false,csrfToken}` plus browser binding cookie. Valid session adds `authenticated:true,email`. No owner ID or provider token. |
| POST `/api/v1/auth/signup` | JSON `{email,password}`, exact Origin, X-CSRF-Token from status, initiating browser cookie | Generic `{status:"check_email",message}`. No unconfirmed session; a separate PKCE verifier/state is retained for each attempt. |
| POST `/api/v1/auth/login` | Same JSON and protections | Provider-validated `{authenticated:true,email}` and newly rotated opaque session cookie. |
| GET `/api/v1/auth/callback?state=...&code=...` | Exact keys, browser binding and unexpired signup verifier; one atomic consumption | 303 to `/account?confirmation=success` or `/account?confirmation=invalid`. No credentials in destination. Account JS immediately removes even the safe outcome query and rejects/clears fragments. |

POST bodies are bounded to 8 KiB and a five-second elapsed reading deadline;
cumulative length is checked before copying each received chunk. Email is bounded
to 254 characters and password to 8–1,024
characters; unknown fields are rejected. Error JSON is `{code,message,requestId}`
with safe messages. Origin/CSRF failures precede parsing/provider calls (403),
invalid body is 422, invalid credentials 401, bounded-registry overflow 429 and
provider/configuration availability failures 503. A disabled status remains 200
with `available:false`. The browser clears submitted passwords immediately,
retains email on errors, focuses the alert, suppresses duplicate submissions and
ignores responses made stale by navigation. Background focus revalidation keeps
unsubmitted drafts and field focus when the forms remain usable; unavailable or
malformed bootstrap responses show an explicit retry. Navigation/retry retains
password cleanup. Confirmation outcomes are consumed once. No browser storage is used.

## Reproducible offline verification

```powershell
uv sync --locked --group pdf-experiment
uv run --group pdf-experiment pytest
node tests/browser-demo.cjs
node tests/browser-auth.cjs
git diff --check
```

`tests/test_auth.py` runs the security matrix, concurrency/capacity/expiry checks
and the real locked Supabase SDK through a synthetic HTTP transport. The browser
suite starts a real local application from `tests/auth_browser_app.py`, whose
adapter and inspection routes exist only in tests. It uses independent browser
contexts and covers confirmation binding/replay/rotation, independent login,
protection headers, safe display/logging/storage, malformed responses, stale
responses, duplicate guards, the 15-second timeout, keyboard focus and 320/390/480
pixel / 200% reflow. Screenshots go to ignored `test-results/`. These are offline
checks, including an accessibility-tree smoke check; they do not establish real
email delivery, hosted PKCE behavior or a complete manual screen-reader audit.

## Checkpoint 2026-11-12 — live acceptance pending

The user reported creating the project manually and supplied its URL and publishable
key. The agent saved them only in ignored `.env`. A read-only provider settings request
returned HTTP 200: email enabled, confirmation required, signup not disabled. No account
was created and no email was sent by this check. Name/plan/region, redirect allowlist,
email template/delivery and real user sessions have not been independently verified.

Parent full offline suite: **130 passed, 1 skipped** (the existing PDF unsupported-OS
case), one existing TestClient/httpx warning. Agent browser runs: **12 auth scenarios**
and **11 demo scenarios** passed. Parent inspected desktop and 200% screenshots.
The independent code-review phase is still pending. The student asked to finish the
day due to the usage allowance, so the story remains in-progress at this checkpoint.

Record only evidence actually observed; omit email addresses, keys, codes, states,
tokens, passwords and raw callback URLs. Use tester aliases A/B.

### Resumed 2026-11-13

The read-only provider settings check again returned HTTP 200: email enabled,
confirmation required and signup allowed. The existing implementation was started
locally with the explicit ignored `.env`, one worker and no reload. `/account`
returned 200; `/api/v1/auth/status` reported authentication available and no active
session, with `Cache-Control: no-store` and `Referrer-Policy: no-referrer`.
This bootstrap did not send an email or create an account.

Windows Computer Use could not connect its native pipe (`os error 2`), and no
Supabase management tool is connected. The student was asked to save the Site URL
and callback pattern in URL Configuration. The student subsequently confirmed
that these were saved ("lagret") and reported that the guided first signup and
email confirmation worked ("funka"). The server recorded one signup 200 and one
callback 303; inspected access entries contained no auth query strings. This is
partial live evidence, not proof of every acceptance/security case. A private-window
password-login check subsequently passed by student report: login form first,
then signed in. A login 200 was observed in server access entries. The subsequent
wrong-password check returned the expected safe rejection message by student
report; server login 401 observed. Availability of a second authorized tester is
now resolved: only tester A's account is available. Do not create/invite another
user or weaken confirmation/email restrictions implicitly. Cross-account live
isolation remains untested. For manual replay of the consumed confirmation link
in the unauthenticated private window, the student reported only the login page.
No new authentication was reported. The precise rejection mechanism and an
explicit expired/invalid message were not verified from that observation.

Ten additional HTTP boundary checks against the running configured server passed
on 2026-11-13: independent browser cookies/CSRF bootstrap, HttpOnly/host-only/Lax
cookie flags, privacy headers, no provider tokens in unauthenticated bootstrap,
missing Origin rejection, other-browser CSRF rejection, other-Origin rejection,
invalid body rejection, clean denial of an unknown callback, and denial/clearing
of an unknown session. The ignored local helper is
`test-results/auth-live-boundary-check.py`; it prints only boolean checks and
counts. It uses synthetic invalid input, calls no signup/provider operation and
sends no email. These checks do not establish authenticated user-to-user isolation,
refresh/restart behavior or the real provider's unused-link binding behavior.
The redirect-pattern and default SMTP documentation were rechecked: only team
addresses are supported by default, currently at two messages per hour. Actual
remaining account checks and independent review are pending. The 130 passing
offline tests are evidence from 2026-11-12, not a new run today.

| Check | Observed evidence |
| --- | --- |
| Free Study Buddy organization / studybuddy-test / specific eu-central-1 | User reports project created; provider settings reachable. Name/plan/region not independently verified |
| Confirmation enabled; local allowlist and template preserve state | Provider confirms required confirmation; user reports saved URL Configuration and successful guided confirmation. Template not separately inspected |
| A signs up, receives authorized test email and confirms in initiating browser | User reports success ("funka") on 2026-11-13 after guided test; server signup 200 and callback 303 observed |
| get_user validates provider identity; only opaque cookies and safe email reach browser | Pending live (offline checks pass separately) |
| B in independent browser cannot consume A's link; replay fails | Used link in unauthenticated private window returned login page by student report. Explicit error/rejection mechanism and unused-link binding remain unverified |
| A and B log in with independent accounts; invalid/unconfirmed credentials fail | A password login succeeds; wrong-password login rejected (user report and server 401, 2026-11-13). Second account and unconfirmed credentials pending |
| Fresh and overlapping attempts; expired link/restart require new registration | Pending live |
| Browser storage/output/server logs do not expose credentials | Pending live |
| Unconfigured demo still completes fixed study flow | Verified by offline regressions; rerun in intended runtime |

The provider can invalidate a superseded email confirmation even when the app
keeps both PKCE attempts separate; record actual hosted behavior. Do not report
Story 2.1 fully accepted until the real positive/negative two-browser checks above
have been executed with authorized testers.

### End-of-day checkpoint 2026-11-13

The student requested to end the session. The local test server was stopped;
the health endpoint no longer responded after the stop signal. Start one worker
with the command above next session; existing memory sessions/pending attempts
cannot be reused. The test account remains in Supabase and can log in normally.
No application code changed today. Ten local-server boundary checks passed;
the full offline suite was not rerun. Story 2.1 remains in-progress. Remaining
provider/security acceptance and independent review must be recorded honestly;
do not create a second tester or claim the missing evidence implicitly.

### Interim corrections after the checkpoint

The authorized interim review patches P1–P12 are implemented. The focused Python
auth suite passed **93 tests** and the isolated real-browser auth suite passed
**16 scenarios**; locked dependency sync and diff checks passed. Their new cases
cover malformed protection values, shared SDK deadlines, overlapping validation
and cancellation before worker admission, binding lifetimes, background drafts,
one-time outcomes, safe error-code lookup, delayed/oversized bodies, stale status
cookie races, exact SDK callback transport and negative existing-session identity.
See [the review evidence](auth-code-review-2026-11-13.md) for details and the
cooperative transport deadline limitation. The earlier boundary result described
unknown-cookie clearing for the pre-patch implementation; current status behavior
denies authority without changing `sb_session` to preserve newer login cookies.
No new hosted account/email check was performed by this patch verification.
Story 2.1 and its remaining live acceptance gates stay in-progress.

Final parent verification after the corrections: **155 passed, 1 expected PDF
platform skip**, one existing TestClient warning, 25.38 seconds; **16 browser-auth
scenarios** passed. The final configured server passed ten unauthenticated boundary
checks with the revised no-status-cookie-mutation expectation. The malformed-CSRF
probe now returns 403 and no-store instead of 500. A fresh one-worker test server
is running after the patch restart; the student has been asked to verify one
ordinary password login with the existing account. The student confirmed
"Ja, jeg er logget inn" after these corrections, and the new server recorded
login 200 without auth query strings in inspected entries. This is a fresh hosted
password-login check through the corrected adapter, not a second-account test or
a repeated signup/confirmation check.

### Low-effort hosted testing preflight — 2026-11-14

The student authorized continuing the two-account test with as little manual work
as possible. No Supabase management tools are connected. Plugin discovery reports
the Supabase integration is available but not installed; its earlier suggestion
was not a confirmed connection. The student was asked to connect it before any
automated account-management action is attempted. Its exact account-management
capabilities must be checked after connection, not inferred from its description.
The app's publishable key remains the only configured app credential; privileged
credentials are not requested in chat or added to app configuration.

The installed Docker client cannot reach its local engine, so a separate local
Supabase stack was not started or installed. Such a stack would not itself prove
two-account isolation on the approved hosted test project. No account, invitation,
email, auth-setting change or new test result was produced by this preflight.

The official [Auth Admin reference](https://supabase.com/docs/reference/python/admin-api),
[admin user creation reference](https://supabase.com/docs/reference/python/auth-admin-createuser)
and [SMTP restrictions](https://supabase.com/docs/guides/auth/auth-smtp) were checked.
Administrative creation does not send a confirmation email; if used later, record
it as administrative provisioning, never evidence that signup/email confirmation
was tested for that user. Do not substitute an admin-confirmed user for the
remaining unused-confirmation-link binding test.

### Connected project verification — 2026-11-14, 14:00 CET

Supabase tools are available in the new conversation. Read-only organization and
project requests verified **Study Buddy**, **Free**, **studybuddy-test** and
**ACTIVE_HEALTHY**. The actual region is **`eu-west-3`**, rather than approved
**`eu-central-1`**. Do not silently amend the approved specification or recreate,
move or delete the project; record the discrepancy for the student's decision.
An aggregate-only `auth.users` query found **one user, email confirmed**. No emails,
user IDs, password hashes or tokens were selected.

The available integration exposes database/project tools, but no Auth Admin
create-user operation. Do not provision users by inserting into `auth.users`,
extract privileged credentials or deploy an administrative helper. Windows
Computer Use still fails with native-pipe error 2; browser inventory also reports
that the browser access host is unavailable. A short manual dashboard step for
test-user provisioning was requested; no answer or new user is assumed.

The configured one-worker loopback server was restarted (PID 47644). Provider
settings returned HTTP 200: email enabled, confirmation required, signup allowed.
All **ten unauthenticated HTTP boundary checks passed again** against this server,
including independent browser/CSRF bootstrap, privacy/cookie controls, Origin/CSRF
rejection, invalid bodies/callbacks and unknown-session denial without session
cookie mutation. This is fresh boundary evidence, not authenticated isolation.
The full offline/browser suites were not rerun; the previously recorded 155/one
skip and 16 browser scenarios remain historical evidence. Story 2.1 stays
in-progress. No account/email, schema change, paid service or deployment occurred.

The security advisor reported only disabled leaked-password protection. The
[password-security documentation](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection)
states this feature requires Pro or higher. The approved Free plan is retained;
no paid upgrade or security-setting change was made. Remaining acceptance includes
two authenticated identities, unused-link binding and the documented hosted
negative cases; administrative provisioning would not establish email delivery.

The student answered **"Ja, jeg kan åpne Users"**. A local ignored helper
`test-results/hosted-auth-isolation.py` now prepares two random administrative
test-account credentials and the local copy page
`test-results/hosted-auth-test-accounts.html`. Passwords are kept only in ignored
local test files, never printed or committed. The student was guided to create
both users through **Create new user**, with per-user **Auto Confirm User** enabled
and no invitation/email; the global confirmation setting remains enabled.
Account creation is not yet confirmed. Local configuration and Python syntax
checks passed; **the hosted isolation run has not been executed**.

After the student confirms both users were created, verify the aggregate user
count and run `uv run python test-results/hosted-auth-isolation.py run` against the
current server. The helper checks two real hosted logins through the application,
independent browser/CSRF/session values, each identity after alternating requests,
fresh-browser and foreign-cookie denial, foreign CSRF/wrong-password rejection,
session rotation and old-cookie denial. It prints boolean checks only and writes
a credential-free result. This is HTTP-client acceptance, not browser storage/UI,
private document isolation, signup/email delivery, expiry or restart acceptance.
Do not delete test users without the appropriate user authorization and session
cleanup; no account cleanup has been performed at this checkpoint.

### Two-account hosted HTTP acceptance — 2026-11-14

The student confirmed that the two prepared test users were created. A read-only
aggregate query now reports **three users, all email confirmed**, including the
original account. No identities, password hashes or tokens were selected.

The first helper run could not reach the stopped local server and completed no
checks. The configured application was started again with ignored `.env`, one
worker and no reload (PID 48256, tool session 19066). The subsequent command
`uv run python test-results/hosted-auth-isolation.py run` completed successfully
at **2026-11-14 13:16:14 UTC**: **20/20 checks passed**. The credential-free result
is in ignored `test-results/hosted-auth-isolation-result.json`.

Verified through the application against hosted Supabase:

- Both administrative test accounts log in and receive distinct opaque,
  HttpOnly, host-only, SameSite=Lax session cookies.
- Independent browser bindings/CSRF values and alternating status requests keep
  each account's identity separate, including after negative checks.
- A fresh client remains unauthenticated; copying only another client's session
  cookie does not authenticate it.
- Foreign CSRF and wrong-password requests are rejected.
- A new successful login rotates the session cookie and the replaced cookie is
  rejected with its original browser binding.

This closes the prepared two-account **HTTP authentication/session isolation**
test. It does not establish private-document isolation, browser UI/storage,
signup/email delivery, unused confirmation-link binding, expiry or refresh.
The server restart enabled this run; no pre-restart authenticated cookie was
retained, so this is not a dedicated restart-invalidation check. Global email
confirmation settings were not changed. Test users remain available, and no
account was created/deleted by the helper. No application code changed and the
full offline/browser suites were not rerun. Story 2.1 remains in-progress;
remaining hosted acceptance and the recorded region discrepancy stay open.

### Lifecycle, browser acceptance and approved region — 2026-11-14

The student approved **“Ja, behold Paris for testprosjektet”**. Paris (`eu-west-3`)
is now accepted for the existing test project. This resolves the region issue;
it is not a production-region decision. The original frozen specification is
preserved with a separate dated amendment.

**18/18 lifecycle checks passed**, with the final run at 13:32:22 UTC:

- A separate real HTTP server with the genuine Supabase adapter rejected a
  session after a shortened three-second idle timeout.
- A real server restart rejected the preserved, previously authenticated cookie;
  a fresh password login succeeded afterward.
- To exercise refresh promptly, the test shortened only one session's local
  `expires_at` metadata to 15 seconds from now. Genuine provider tokens were
  retained. Status invoked the real Supabase refresh operation and get_user
  validation; owner identity and valid future expiry were preserved. The other
  account remained authenticated.
- An intentionally invalid in-memory refresh token caused safe rejection and
  local session retirement, while the other account stayed authenticated.
- An absolute six-second lifetime expired despite intervening status activity;
  its separate idle limit was ten seconds.
- Captured HTTP server logs contained login/status access entries and omitted
  both test accounts' credentials and every provider token observed by the test.

These are accelerated local lifetime checks using real hosted identities, not
wall-clock observation of the normal 30-minute/12-hour limits or natural JWT
expiry. Only the test harness observes provider responses and adjusts local
expiry metadata; application code and normal server settings are unchanged.
Test servers were stopped; the regular server on port 8000 was left running.

**24/24 real-browser checks passed**, at 13:31:00 UTC, against the normal configured
server and hosted Supabase. Two independent contexts submitted the real login
forms and retained their correct identities after reload; a third remained
unauthenticated. A wrong password produced the safe message, cleared the password,
retained email and focused the alert. Cookies were distinct, opaque, host-only,
HttpOnly and SameSite=Lax. Local/session storage, IndexedDB, Cache Storage and
JavaScript-visible cookies were empty in all three contexts. Passwords and
session-cookie values were absent from HTML, URL and captured console output;
API responses omitted provider-token/owner fields. Browser requests stayed on the
application origin, URLs were clean and no script errors were observed. This
does not claim a complete screen-reader audit or secure-cookie verification on
HTTPS; these runs used explicit loopback HTTP.

Reproduce the ignored, local-only helpers with:

```powershell
uv run --env-file .env python test-results/hosted-auth-lifecycle.py
node test-results/hosted-auth-browser.cjs
```

Results are saved without credentials in ignored lifecycle/browser result JSON
files beside the helpers. The final lifecycle rerun strengthened log assertions
to check every actually issued token; it is not an additional 18 unique cases.
The full offline suite was not rerun because application code did not change.

Remaining hosted acceptance concerns the email-confirmation path: an unused
authorized address/link, wrong-browser binding, precise replay/expiry rejection,
overlapping signup attempts, unconfirmed-login rejection and template inspection.
The agent initially suggested registering the already confirmed original address
again, then withdrew that instruction before assuming any action/result. Existing
confirmed accounts cannot establish a new-account confirmation test. Availability
of an unused authorized team address has been requested; no answer or email
delivery is assumed. No account/email or hosted Auth setting was changed by the
automated checks. Story 2.1 remains in-progress.

## Story 2.2 recovery implementation — 2026-11-14

Recovery is implemented for local verification. **No real recovery email or
password mutation was authorized or executed during implementation.** Story 2.1's
email-confirmation gates above remain open. Keep Study Buddy on Free and retain
the approved Paris (`eu-west-3`) test project. No hosted settings, accounts,
database tables, deployment or paid services were changed.

The browser requests `POST /api/v1/auth/recovery/request` with email only. The
generic check-email acknowledgement is identical for existing/missing accounts;
provider outages receive a fixed safe failure. Each attempt has its own verifier,
state, browser binding and purpose, expires after ten minutes, and shares the
1,000-total/four-per-browser pending-attempt limits with signup. The SDK stores
`verifier/PASSWORD_RECOVERY`; the adapter retains the actual verifier separately
and submits that actual value to the token exchange. Wrong-purpose callbacks
cannot consume signup attempts or create a normal login.

The exact recovery callback is `GET /api/v1/auth/recovery/callback?state=…&code=…`.
It consumes its attempt before exchange, validates confirmed provider owner/email,
rotates the opaque `sb_session`, retires any replaced local authority and redirects
to a clean account URL after the one-use outcome is read. Its server record is a
restricted, browser-bound ten-minute grant in a registry disjoint from normal
sessions. Normal validation denies it. Status reports
`authenticated:false,recoveryAvailable:true` and omits identity. Normal and
restricted sessions share a 1,000-entry bound.

`POST /api/v1/auth/recovery/password` accepts password only. It requires the same
Origin/CSRF/browser protection as login, atomically removes the restricted grant,
then performs at most one provider password write. The request-scoped SDK uses
one shared operation budget across set_session, validation, any SDK-internal
get_session refresh and update. Both refresh paths are checked against the
grant's validated owner/email before PUT; the returned user is also checked.
Success requires ordinary login afterward. Every admitted failure requires a
new link; a timeout can mean the password changed. Password/status replies never
change `sb_session`, so a late reply cannot erase a newer login cookie.
Unrelated users' local sessions are retained. Supabase may affect other sessions
for the same account when a password changes; no unchanged-provider-behavior
promise is made.

Bodies retain the 8 KiB and five-second streaming limits. Cookie, no-store,
referrer, redaction, restart, unknown-field and error privacy controls are reused.
The UI adds labelled email/new-password/confirmation forms, matching validation,
one-use link outcomes, duplicate/stale-reply guards and login/new-link guidance.
The fixed demo continues without configuration or external requests.

Relevant official references checked against the installed, locked SDK:
[password reset](https://supabase.com/docs/reference/python/auth-resetpasswordforemail),
[password update](https://supabase.com/docs/reference/python/auth-updateuser) and
[redirect patterns](https://supabase.com/docs/guides/auth/redirect-urls).
The Supabase changelog was inspected; no applicable Python reset/update breaking
change required a dependency update.

### Remaining hosted recovery acceptance

- Obtain explicit authorization naming the tester account/address before sending
  real recovery email or changing its password. Existing signup/login authorization
  is not treated as authorization to mutate a password.
- Verify the extra callback allowlist and reset-email template. Exercise genuine
  email delivery, same-browser completion, an unused link in the wrong browser,
  replay, expiry and overlapping requests. Preserve the existing confirmation gates.
- With explicit mutation authorization, verify one successful password change,
  normal login afterward, safe denial of reuse and unchanged access for a separate
  user. Record provider behavior for other sessions of the changed account without
  promising they survive. Record every executed hosted case separately.

Offline/browser checks below use only synthetic provider fixtures. They do not
establish hosted email delivery or private-document isolation. Full logout remains
Story 2.3; a full manual screen-reader audit and HTTPS-browser cookie check are
still pending.

### Initial recovery verification before review corrections

- `.venv/Scripts/python.exe -m pytest tests/test_auth.py -q -p no:cacheprovider`:
  **145 passed**, one existing Starlette/httpx deprecation warning.
- `uv run --group pdf-experiment pytest -q -p no:cacheprovider`:
  **207 passed, 1 skipped**, the same existing deprecation warning.
- `node tests/browser-auth.cjs`: **20 scenarios passed**, including the recovery
  form's labelled controls, matching validation, background-focus draft retention,
  keyboard operation, 320/390/480-pixel and 200% reflow. The ignored screenshot
  `test-results/account-recovery-200-percent.png` was visually inspected: no clipping
  or horizontal overflow was observed.
- `node tests/browser-demo.cjs`: **11 scenarios passed**, 21 fixture generation
  requests; the credential-free demo and its delayed-request protections remain valid.
- `git diff --check`: passed; only standard LF/CRLF conversion notices were emitted.

| Spec matrix row | Executed synthetic evidence |
| --- | --- |
| Request | Existing/missing-account generic acknowledgement; safe outage; email-only body and no login. |
| Callback | Exact SDK redirect/state, PKCE challenge and actual verifier; validated identity; rotated restricted authority; clean browser URL. |
| Invalid link | Wrong browser/purpose, missing state/code/verifier, expiry including during exchange, replay/restart, exact query and independent overlapping attempts. |
| Update | Matching UI validation, password-only provider write, consumed grant, normal-session rejection, normal authentication denial and ordinary login afterward. |
| Race/outage | Concurrent duplicate updates invoke one adapter write; SDK owner/email mismatches before mutation including both refresh paths; response mismatch/timeout/deadline failures; no grant reuse or late cookie overwrite. |
| Protection | Origin/CSRF rejection, malformed/oversized/slow bodies before provider work, unavailable configuration, shared capacity, no-store, opaque cookies, safe errors and browser storage/URL/console cleanup. |

All new provider responses and emails in these checks are synthetic. The full
suite's unchanged skip is not counted as executed coverage. Hosted recovery,
email delivery and real password mutation remain unexecuted.

### Final verification after independent review corrections

All three review layers completed before triage; every finding and disposition is
recorded in the [recovery specification](spec-2-2-recover-a-password-through-a-restricted-session.md).
Seven small patch groups addressed callback ordering, Unicode bounds, precise
pre-admission errors, navigation, overlapping SDK attempts, expiry during final
validation and failed-request capacity cleanup. Local email admission/throttling
for public operation is pre-existing hardening recorded in
[deferred work](deferred-work.md); current per-browser limits do not prevent quota
exhaustion. No provider settings or paid services were changed.

Final parent results supersede initial test counts above:

- Full Python suite: **213 passed, one expected PDF platform skip**, one existing
  Starlette/httpx warning, 26.89 seconds. Ignored result file:
  `test-results/recovery-parent-verification-final.xml`.
- XML audit: **151 auth cases**, all executed/passed, including three blocked
  recovery-versus-login races, two expiry-during-final-validation cases and repeated
  failed-request cleanup/retry.
- Real browser with test-only provider: **23 account scenarios** and **11 demo
  scenarios**, 21 fixture generation requests. Parent inspected the updated
  recovery screenshot at 200% with the login navigation action.
- The original synthetic callback-race probe changed from replacing a newer
  login with restricted authority to rejecting the stale callback without setting
  `sb_session`; the newer normal identity remained authenticated.
- Diff checks passed. No application code changed after these final checks.

Recovery password fields now accept 8–1,024 Unicode code points consistently with
the server. Known pre-admission errors retain the recovery form with specific
guidance; unknown/admitted failures remain conservative. Users can return from
restricted mode to normal login without a password write, and signed-in users
can reveal the existing account/recovery forms. A browser authority revision
rejects recovery rotation when another authentication transition happened during
provider exchange; sequential independent attempts still work.

The configured local server was restarted with one worker (PID 35884, tool session
37132). Bootstrap/account read-only checks confirm the new recovery surface and
privacy headers; they send no email and do not mutate an account. The spec's code
workflow is done and Story 2.2 is at review, while the hosted checks above remain
open. Story 2.1's remaining email-confirmation acceptance is unchanged.

### Recovery redirect reported saved — 2026-11-15

After being guided to add
`http://127.0.0.1:8000/api/v1/auth/recovery/callback\?state=*`
as a new Redirect URL in the existing project, the student answered **“lagret”**.
Record this as student-reported configuration, not independent inspection of the
dashboard, redirect matching or reset-email template. The agent's read-only local
status check returned 200 with authentication available and recovery support.
No email or password mutation was performed by that check.

Next manual observation: the student may request recovery for their own existing,
authorized team test account, open the email link in the initiating browser within
ten minutes, and report whether the restricted new-password view appears.
Administrative example.com test users are not email-delivery testers. Do not ask
for a password or raw confirmation/recovery link in chat. Genuine email delivery,
callback completion and password mutation remain pending until observed/reported;
the saved-setting report alone does not complete hosted acceptance.

### Recovery email received — student report, 2026-11-15

The student reported **“fikk epost om resatt passord”** and then clarified
**“Den har en lenke for å velge nytt passord”**. This is student-reported receipt
of a recovery link, not evidence that the password has changed. The next step is
opening that link promptly in the initiating browser/profile and observing the
restricted new-password form. Callback success, actual redirect/template matching
and password mutation remain unverified. No password or raw link was requested
in chat, and no further email was triggered by the agent.

### Hosted recovery positive path — 2026-11-15

The student reported **“resette passord fungerte”** and clarified **“jeg prøvde å
bytte passord, det fungerte”**. Record a successful password change by student
report following the received recovery email. The agent did not perform the write
or inspect the password.

The running configured server's access output corroborates one recovery request
200, one recovery callback 303 and one password-update POST 200. A normal login
POST 200 occurs after that password-update entry. This establishes observed
successful normal authentication afterward, without asserting which password
value was entered or selecting an account identity. Observed auth entries contain
no callback query values; raw logs/credentials were not printed to the conversation.

The previously reported saved recovery redirect is now supported by successful
functional callback/update behavior. Reset-template contents were not separately
inspected. Unused-link wrong-browser behavior, replay/expiry/overlap, other-user
isolation during a real change and other negative hosted cases remain unexecuted.
Keep Story 2.2 at review and Story 2.1's remaining gates open; do not repeat the
positive password-change test merely because these negative cases remain open.
No new automated suite was run for this observation.

### Story 2.3 session termination implementation — 2026-11-15

The local contract now includes protected `POST /api/v1/auth/logout` with an
empty JSON object. Before any provider work, one registry transition ends every
session, recovery grant and pending confirmation/recovery attempt belonging to
the initiating browser. The response deletes request-supplied session cookie generations, retains the browser
binding for fresh login, and then attempts provider revocation using the user's
JWT and explicit `local` scope. It does not install an SDK session, refresh a
token or use a privileged key. Other browsers remain independent even when they
use the same account. Unknown or spent session cookies are idempotent.

After-response revocation has 16 active slots, no queue or retries, and one
shared ten-second cooperative operation deadline per admitted batch, including
worker-admission time. A separate 16-permit limiter avoids the shared request pool. Saturation or provider failure never restores authority.
In-flight validation is still coalesced and survives waiter cancellation;
browser revisions fence installations across logout, expiry and provider denial.
An admitted password update may still finish remotely; its late response cannot
restore local authority. Access JWTs may remain valid at the provider until JWT
expiry, so this application's local registry remains the denial boundary.

Status validation is non-touching: it cannot keep idle authority alive. Normal
and recovery status provide bounded remaining lifetime in `expiresInSeconds`.
The account page uses a clearing timer, visible 30-second passive observations,
focus/pageshow checks, and secret-free BroadcastChannel termination signals.
Logout, expiry, restart and failed observation clear identity/recovery display;
sequence guards discard stale replies. No browser credential storage is added.

Offline evidence and hosted gates are recorded separately. The tests use only
synthetic identities, transport responses and test-only browser fixtures; they
perform no genuine account, email or password operations. No configuration,
hosting, billing, Free plan or Paris-region change is part of this work.

Unexecuted hosted Story 2.3 gates: ordinary and restricted logout, the same
account in two independent browsers, actual idle/absolute expiry, restart with
preserved cookies/open page, and provider-outage behavior. Existing Story 2.1
and Story 2.2 open hosted gates remain open. Private document endpoints and
saved-data durability are not claimed; persistence is Story 3.2.

Executed offline verification for Story 2.3: `uv run --group pdf-experiment
pytest` completed with **239 passed, 1 skipped** (the optional PDF integration
skip remains unchanged); `node tests/browser-auth.cjs` completed **28 scenarios**;
`node tests/browser-demo.cjs` completed **11 scenarios**. Server coverage includes
strict logout protection/body rejection, normal/restricted authority and pending
attempt removal, stale body/provider/validation fences, passive idle and absolute
expiry, same-account browser isolation, response-body/cookie deletion before
provider revocation, exact SDK user-JWT/local/no-refresh wire behavior, 16-slot
admission, waiter cancellation, and a shared deadline across admission/batch work.
Browser coverage includes focused normal/restricted deadline clearing, visible
passive restart detection, fresh login, sibling-tab logout and an unabortable
late login reply, restricted keyboard logout, reflow and credential-free storage.
These checks do not establish genuine hosted behavior.

Session-ending handoff, 2026-11-15: the parent independently repeated all three
verification commands with the same passing counts (all 177 auth cases passed)
and checked the matrix and frozen-plan hash. Independent review is incomplete:
blind review and a verification-gap report require triage/fixes, and edge-case
review was interrupted when the student requested commit and session end.
The implementation is saved for continuation, not accepted as a finished build.
See the Story 2.3 spec's Review Triage Log for the concrete remaining reports.


## Story 2.3 review completion — 2026-11-15

The interrupted build resumed at step 4 without a new planning/approval round.
B1–B8 and V1 were corrected; B9 was already resolved by the session-ending
handoff. The completed independent edge layer reproduced B1–B8 and reported no
additional root cause. Its final read-only inspection of the corrections found
no remaining defect. No review finding was deferred. The frozen approved block
is unchanged; implementation spec is done and the sprint story remains review.

Session cookies now use `sb_session_<16 hex generation digest>`. Their values
remain opaque HttpOnly credentials with the original flags/binding; only a live
browser-bound registry entry is accepted, irrespective of header order. Rotation
and logout retire only eligible names in the incoming request (maximum 32),
including legacy `sb_session`. A delayed logout cannot delete a later generation.
Status never writes session cookies. Old browser state still fails after restart.
Failed logout keeps its intent, hides private display and repeats POST on retry,
obtaining a fresh CSRF binding without restoring identity if necessary. Signals
trigger server observation after active work; local timers do not broadcast.
Passive latency leaves controls/drafts/focus usable, and observed lifetime is
reduced by request/JSON elapsed time. Late rejected login/callback identities
receive the same bounded local provider cleanup. Native/DNS blocking still has
only a cooperative budget; a hard OS-level deadline is not claimed.

Final parent offline verification: **243 passed, one unchanged optional PDF
platform skip**, all **181 auth cases** passed; **33 auth-browser scenarios** and
**11 demo scenarios / 21 generation requests** passed. New regressions cover
provider denial while signup/recovery callbacks remain unfinished, rejected
identity cleanup, delayed cookie deletion/header ordering/browser binding, shared
worker saturation, failed logout retry, old tab signals/timers, delayed normal
and restricted lifetime snapshots, passive recovery controls and acknowledgement
of restricted logout. The 200% account screenshot was inspected without clipping.

### Executed against hosted Supabase

`uv run --env-file .env node test-results/hosted-logout-browser.cjs` completed at
**2026-11-15 09:00:27 UTC** with **25/25 unique checks passed**. The harness uses
the existing authorized administrative test account in two independent browser
contexts, real Supabase identity validation/revocation and real refresh. It starts
and stops its own loopback test server; it is never imported by the normal app.
Credential-free evidence is in ignored `test-results/hosted-logout-result.json`.

- Ordinary UI logout acknowledges, deletes its cookie and denies local access;
  actual `scope=local` provider revocation completes successfully.
- Another browser on the same account remains authenticated and completes an
  actual Supabase refresh after the first browser logs out. Fresh login works.
- A restricted grant made locally from a genuine hosted identity is displayed,
  logged out and revoked; normal/restricted authority is denied afterward. This
  instruments grant admission and does **not** establish real recovery PKCE/email
  behavior. No recovery email or password write was performed.
- Idle and absolute metadata were shortened locally to a one-second remainder;
  the focused page cleared at its observed deadline and the server denied access.
  Default 30-minute/12-hour limits were separately verified offline; no claim of
  waiting those durations against hosted Supabase is made.
- A revoke failure injected at the adapter seam still acknowledges/denies locally
  and preserves the other browser. A genuine Supabase outage was not induced.
- An actual test-server process was stopped/restarted with the browser cookie and
  open page preserved. Focus clears identity; the old authority is denied and a
  fresh login succeeds. Storage/cookie visibility and script-error checks pass.

### Normal configured server

The old worker **35884** was identified by its project virtualenv/uvicorn command
before replacement. It had been running the previous Python code. It was stopped
and the existing ignored `.env` started one worker, **PID 11748**, bound to
`127.0.0.1:8000` (launcher 34908). Ten checks passed against this worker: health,
new UI/JS, private headers, available configuration, existing test-account login,
generation-specific cookie issuance, protected logout, local denial and cookie
removal. Evidence: ignored `test-results/logout-main-server-result.json`.
The isolated acceptance server was stopped; the normal configured server remains
running. Restart ends prior local sessions, so the student's page needs login.

### Remaining acceptance

Story 2.3 implementation/review is complete, with the precise hosted limitations
above. Genuine unused recovery/confirmation-link negative cases, email-template
inspection and the previously recorded Story 2.1/2.2 gates remain open. They need
appropriate unused authorized links; **do not automatically send emails, create
accounts, repeat the successful password change or change hosted Auth settings**.
No private document/storage, HTTPS production deployment, full screen-reader
acceptance, billing or persistence claim is added. Free/Paris is unchanged.
