# Story 2.1 authentication setup and acceptance

The user reported on 2026-11-12 that the project has been created manually after the
organization. Local configuration and actual project settings still need verification.
The application implementation is locally testable. **Provider reachability and
required email confirmation are verified. The student reports successful first
signup/email confirmation and separate private-window password login. The interim
independent review and its corrections are verified; remaining hosted
negative/isolation checks and final build acceptance are pending.** The project's plan and region were not
independently checked. Offline adapters live only in
`tests/`; the application has no mock-auth mode.

## Approved manual setup

1. In Supabase, choose **Create an organization** first. Name it **Study Buddy**
   and select **Free**. Do not add a paid subscription or add-ons.
2. Inside that organization create **studybuddy-test**. Choose the **specific**
   region **Frankfurt (`eu-central-1`)**. Do not substitute an automatically chosen
   general Europe region. Keep its database password in a password manager; the
   application does not need that password.
3. Enable the email/password provider and **email confirmation**. The SDK adapter
   refuses signup responses containing an immediate session, so confirmation
   cannot silently become optional.
4. Under Authentication → URL Configuration set Site URL to
   `http://127.0.0.1:8000/account`. For this local test, add the redirect allowlist
   pattern `http://127.0.0.1:8000/api/v1/auth/callback\?state=*`.
   The escaped question mark is literal; the wildcard covers only the random
   state. Use the exact same scheme, host and port in the browser and APP_ORIGIN.
   The adapter supplies `email_redirect_to` with that callback and a new random
   state for each attempt. Do not allow arbitrary hosts or external return URLs.
   Supabase documents these pattern rules in its
   [redirect URL guide](https://supabase.com/docs/guides/auth/redirect-urls).
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
