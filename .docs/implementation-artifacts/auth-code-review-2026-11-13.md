# Interim authentication code review — 2026-11-13

This is a read-only review of the existing authentication foundation, undertaken
while hosted acceptance is still incomplete. It does not advance the build past
its live acceptance gate or mark Story 2.1 complete. Existing approval covers
implementation corrections; the frozen specification remains unchanged.

Baseline: `74fa5f971e187bbb3de924a8f438aff2cba5e782`.
Reviewed head: `013dabff9bc5c30d5db3d3b6ad49e3ade7904aed`.
Diff: 24 files, 2,774 lines, 2,448 additions, 33 deletions.
All four review layers returned: blind hunter, edge cases, verification gaps,
and acceptance auditor. The fourth started when a three-reviewer slot became
free; no findings were triaged until every reviewer had returned.

## Individual verdicts before grouping

| ID | Source | Finding and verified evidence | Verdict | Route |
| --- | --- | --- | --- | --- |
| B1 | Blind hunter | Non-ASCII CSRF strings reach `compare_digest(str,str)`, which raises TypeError. Parent reproduced on the live local server: 500, without no-store. No credentials submitted. | medium | Patch P1 |
| B2 | Blind hunter | Repeated anonymous status requests fill the deliberately specified 1,000-browser registry. Admission then rejects as designed. On the current loopback-only test server, ordinary usage will not meet this abuse workload; adding IP/proxy policy is substantial new behavior. | low | Rejected for this local change; reconsider admission at hosting, not an accepted public-deployment posture |
| B3 | Blind hunter | HTTPX per-phase deadlines can be indefinitely reset by a trickling response; token acquisition and get_user are also sequential. There is no shared elapsed-time budget in the SDK adapter. | medium | Patch P2 |
| B4 | Blind hunter | `Registry.authenticated` acquires a synchronous session lock inside each thread-pool call, then independently validates again. Overlapping calls serialize provider operations and retain waiting workers. | medium | Patch P3 |
| B5 | Blind hunter | Browser binding expiry is fixed at initial bootstrap, but a session's 12-hour lifetime starts on successful login. `rotate` does not extend the binding, so an older bootstrap can invalidate a newly created session early. | medium | Patch P4 |
| B6 | Blind hunter | Every focus event calls bootstrap, which immediately clears unsubmitted passwords. A normal password-manager/window switch destroys the draft. | medium | Patch P5 |
| B7 | Blind hunter | The confirmation outcome is never consumed; focus bootstrap can display an old confirmation error after successful password login. | medium | Patch P6 |
| B8 | Blind hunter | Error lookup uses inherited object keys; `constructor`/`toString` resolve to functions instead of the fixed fallback. | low | Patch P7: direct lookup correction |
| B9 | Blind hunter | Credential request streaming has a byte limit but no elapsed-time budget; a valid browser can leave a small incomplete body open indefinitely. | medium | Patch P8 |
| B10 | Blind hunter | The code extends the accumulator before checking length, copying an oversized delivered chunk before rejecting it. | low | Patch P9: move existing bound before append |
| B11 | Blind hunter | Hosted tests, including unused-link browser binding and cross-account isolation, are explicitly pending in the setup record. This is an existing acceptance gate, accurately reported rather than a claim of completion. | medium | Existing open acceptance work, unchanged by this interim review |
| E1 | Edge cases | Independently confirms B1 at `Registry.csrf_valid`. | medium | Patch P1 |
| E2 | Edge cases | Reviewer reproduced delayed old-session status validation finishing after a successful login rotation. The old response unconditionally deletes sb_session, erasing the new login cookie. Parent traced the unconditional clear in both status success and error paths. | medium | Patch P10 |
| V1 | Verification gaps | SDK test records redirect_to but never asserts its exact supplied callback or distinct state. The route and browser tests bypass this adapter boundary. Filed test evidence accepted. | medium | Patch P11 |
| V2 | Verification gaps | Negative real-SDK tests exercise login/_validated, not existing-session validate. Missing/changed/unconfirmed provider identity on status is untested. Filed test evidence accepted. | medium | Patch P12 |
| A1 | Acceptance auditor | Independently confirms B11. No additional implementation-to-spec violations found. | medium | Existing open acceptance work |

## Patches authorized by the existing implementation request

- [x] P1: Reject malformed/non-ASCII CSRF and binding values safely before constant-time comparison. Exercise HTTP rejection with raw non-ASCII headers/cookies and preserve safe error headers.
- [x] P2: Give each complete SDK operation a finite elapsed-time budget covering all its HTTP requests and body reads. Respect the remaining budget between requests/chunks, cap blocking transport phases, close transport/streams on failure, and document any finite blocking-read overshoot honestly. Do not pretend that abandoning a still-running thread cancels network work. Keep SDK operations request-scoped, no retries, no credential logging; test trickled synthetic transport and a shared token/get_user budget with a controlled clock.
- [x] P3: Coalesce overlapping validation of the same session while retaining per-session refresh serialization, immediate denial after revocation/rotation/expiry and provider validation for new requests. Never introduce a long-lived authentication cache. Test overlap and failure as well as distinct sessions; no shared mutable SDK client.
- [x] P4: Successful authentication must not inherit a nearly expired anonymous binding. Keep browser-binding authority valid for the new session's permitted lifetime and each permitted pending attempt, without extending any session's own idle/absolute deadline. Test near-expiry login and confirmation.
- [x] P5: Background focus revalidation must preserve unsubmitted form drafts/focus while still clearing submitted passwords, ended private identity and stale responses. Explicit navigation/retry/bfcache handling retains security cleanup. Add a browser regression for an unsubmitted password across window focus.
- [x] P6: Consume confirmation outcomes once; successful password login must not resurrect an old invalid-link error after focus revalidation. Add a browser regression.
- [x] P7: Use an own-key-only safe error lookup, including constructor/toString/null and unknown response codes. Add malformed-response browser checks.
- [x] P8: Bound elapsed credential-body reading and reject a slow/incomplete request with the existing safe invalid-request contract, before provider work. Test an actually delayed async input stream using a short injected test deadline.
- [x] P9: Check cumulative chunk length before extending the credential accumulator; retain exact 8 KiB semantics and streamed overflow tests.
- [x] P10: An obsolete status request must not delete a cookie set by a newer successful login. Preserve registry denial/removal for invalid sessions; status responses must not mutate sb_session. Avoid resurrecting an ended identity. Test delayed success and failure racing rotation, including applying response cookies in arrival order.
- [x] P11: Use distinct callback states in the real-SDK transport test and assert the exact outgoing redirect_to for each. Prefer an HTTP-route-to-SDK boundary assertion so state cannot be dropped between the two layers.
- [x] P12: Establish a session through the real SDK transport, then parameterize invalid `/user` responses for status (missing/unconfirmed/changed owner/changed email). Assert authentication denied, old registry session removed and safe cookie handling. Do not put real users or credentials in tests.

## Existing acceptance gate

Only one authorized account is available. Signup/email confirmation, a separate
private-window password login, wrong-password denial and login after server
restart have been reported successful by the student; server status codes support
the successful/denied login reports. The exact old-cookie state before the latest
manual login was not separately reported. Reusing the consumed email link only
returned the login page by report; it does not prove unused-link browser binding.
Ten unauthenticated HTTP boundary checks passed earlier. These do not establish
cross-account isolation, all hosted error/race/expiry cases or a full browser
credential exposure audit. Keep the story in-progress and retain these open items.

## Rejected appendix

- B2 — low, not fixed in this local change: adversarial anonymous admission at a
  future public/proxied deployment requires policy, and the current bounded
  registry's overflow behavior is intentional. No public-hosting approval follows.

## Verification after patches

P1–P12 are implemented and locally verified. The frozen behavior remains unchanged;
the review's proposed cookie-clearing instruction for P10/P12 is corrected here:
status responses never mutate `sb_session`. Registry denial/removal is authoritative.
Even a response already created before login can arrive afterward, so inspecting
registry supersession before sending a deletion header would not solve the race.
Tests apply both delayed validation and already-completed denial/error responses
after the newer login and preserve that newer cookie. Retaining an invalid opaque
cookie grants no access. Full logout remains Story 2.3.

P2 uses one 10-second cooperative budget across complete SDK operations, body
chunks and low-level network reads/writes/TLS calls, with remaining-time transport
limits. Synthetic chunk and shared token/get_user tests pass, and a real HTTP
framing test with a synthetic raw network stream proves incomplete-header trickles
cannot reset the budget. Native blocking operations, including system DNS, cannot
be forcibly canceled by this mechanism; no strict 10-second wall-time or abandoned
thread cancellation claim is made. The HTTPX/httpcore backend hook is narrow,
lockfile-pinned and explicitly tested. The 3/5-second phase ceilings remain.

P3 keeps an independent owner task for shared in-flight validation. Followers
wait outside the worker pool. A deterministic occupied-limiter regression cancels
the first HTTP waiter before worker admission and proves the follower completes;
the shared Future cannot become orphaned. New non-overlapping calls still validate.
P8's delayed async body carries a complete otherwise-valid credential payload and
asserts cancellation before provider work. P9 tests the exact 8 KiB boundary and
checks that an oversized next chunk never reaches the accumulator.

Executed after these patches:

- `uv run pytest tests/test_auth.py -q`: **93 passed**, one existing
  TestClient/httpx deprecation warning.
- `node tests/browser-auth.cjs`: **16 scenarios passed**, including preserved
  password/focus on focus revalidation, unavailable-focus retry, one-time
  confirmation outcome and inherited/null/unknown error-code handling. Headless
  focus is explicitly dispatched because native activation is inconsistent there.
- `uv sync --locked --group pdf-experiment`: lock resolved and packages audited.
- `git diff --check`: passed (Git emitted only LF/CRLF conversion notices).

These checks use synthetic provider data and isolated local test servers. No new
email, account creation or live acceptance case was executed. Hosted acceptance
and formal step-04 remain open. The parent workflow records its broader regression
run and final checkpoint separately.

### Parent and independent follow-up

Follow-up review found an orphaned validation Future when its initiating HTTP
waiter was canceled before thread-pool admission, and a delayed-body test that
would also reject without the timeout because it omitted a password. Both were
corrected within P3/P8. The edge reviewer rechecked cancellation and executed the
occupied-worker regression: **1 passed**, no remaining defect in that fix.
The verification reviewer confirmed the exact SDK callback/status gaps are covered,
then confirmed the corrected complete-payload cancellation test and low-level
framing/deadline coverage. Parent inspection additionally found and corrected
closure of the newly returned TLS stream after an over-budget handshake. These
were fixes to implementation/test gaps, not changes to the frozen behavior.

Final parent full suite: **155 passed, 1 skipped, 1 existing warning**, 25.38 seconds;
`test-results/auth-review-parent-verification.xml`. Its 93 auth cases have no
failures or skips. Final parent browser suite: **16 scenarios passed**. The updated
configured server passed ten boundary checks; the exact non-ASCII probe that had
returned 500 now returns **403 with no-store**. The original frozen block was
compared with Git and is unchanged. These results do not close hosted acceptance.

After the corrected server restarted, the student explicitly confirmed a fresh
password login ("Ja, jeg er logget inn"); server login 200 observed. The corrected
real transport therefore has one positive hosted login check. Other hosted
acceptance gaps remain as listed; no real-account credentials were collected.
