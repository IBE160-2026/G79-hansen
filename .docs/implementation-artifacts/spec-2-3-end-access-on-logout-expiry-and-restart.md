---
title: End access on logout expiry and restart
type: feature
created: 2026-11-15
status: done
route: dispatch
story_key: 2-3-end-access-on-logout-expiry-and-restart
baseline_commit: e46308987f89998ae9623ea050a801a50a7ec19c
review_loop_iteration: 0
context: [.docs/implementation-artifacts/epic-2-context.md]
---

<frozen-after-approval reason="approved by the student on 2026-11-15: Godkjenn og fortsett med implementering">

## Intent

**Problem:** Students cannot explicitly log out, and an ended session can leave an apparently signed-in view.

**Approach:** Add device-local logout and consistent sign-in-again states after idle/absolute expiry, provider failure or restart. Old authority and late replies must not restore ended access.

## Boundaries & Constraints

**Always:** Atomically end this browser's local sessions/grants/pending attempts before provider work; emit cookie deletion before bounded best-effort revocation with explicit `local` scope. Outage never restores access or ends another browser's sessions. Fence in-flight authority creation; retain browser binding for fresh login. Keep 30-minute idle/12-hour absolute maxima, one process, Origin/CSRF, body bounds, no-store and opaque HttpOnly cookies. Bound revocation work; no retries/unbounded queue. Passive status never renews idle. Clear private display and discard stale replies on termination.

**Never:** Global/others logout, privileged keys, refresh merely to revoke, browser credential storage, external redirects, new persistence/document features, costs or deployment. Preserve Free/Paris, recovery/demo and prior open acceptance. Automated fixtures perform no genuine account/email/password operations. Saved-data durability is Story 3.2.

## I/O & Edge-Case Matrix

| Scenario | Given / When | Then / safe failure |
| --- | --- | --- |
| Logout | Given normal/restricted authority, when protected logout runs | End local authority/attempts, clear cookie, acknowledge; unknown/spent IDs are idempotent |
| Outage | Given two browsers, when revocation blocks/fails | Local response/denial first; other browser remains valid, including same account; bounded work |
| Expiry | Given idle/absolute deadline, when crossed | Server denies; visible private/recovery state clears and offers login; passive checks cannot keep alive |
| Restart | Given preserved cookies/open page, when restarted | Deny old authority; passive check/focus/pageshow clears display; fresh login works |
| Races | Given delayed auth/validation/update replies, when access ends | Reject old installations; stale cookies/replies confer no ended access |
| Protection | Given foreign Origin/CSRF, invalid body or unavailable configuration, when requested | Safe rejection/availability before provider work; no leaks or demo regression |

</frozen-after-approval>

## Code Map

- `app/services/sessions.py`: atomic browser termination, revision/expiry fences, live browser-bound cookie selection, non-touching snapshots, coalesced validation and separately limited revocation workers.
- `app/api/auth.py`: protected logout, revision-fenced login/callback, generation-specific cookie installation/retirement, safe lifetime status and bounded after-response cleanup of rejected identities.
- `app/adapters/auth.py`: pinned SDK admin.sign_out(jwt, scope="local") directly uses the user JWT, without privileged keys, session installation or refresh for revocation.
- `app/static/account.*`: logout retry intent, sequence/abort guards, latency-aware deadline/passive observations and authoritative reconciliation of secret-free fan signals; focused browser fixtures supply regressions without production debug routes.

## Tasks & Acceptance

**Execution:**
- [x] `app/services/sessions.py` — atomic termination, revision/expiry fencing, non-touching observation and lifetime snapshots; preserve coalescing/cancellation.
- [x] `app/adapters/auth.py` — budgeted user-JWT local revocation without refresh or raw errors.
- [x] `app/api/auth.py`, `app/main.py` — protected POST `/api/v1/auth/logout`, strict empty JSON, local denial/cookie deletion then capped after-response revocation; safe remaining-lifetime status.
- [x] `app/static/account.html`, `account.js`, `styles.css` — normal/restricted logout, centralized clearing/login action, deadline/passive observation; preserve keyboard/reflow/recovery.
- [x] `tests/test_auth.py` — matrix, response-before-revoke, admission/cancellation/outage bounds, exact SDK JWT/local/no-refresh wire, expiry defaults, stale auth races and same-account browser isolation.
- [x] `tests/auth_browser_app.py`, `tests/browser-auth.cjs` — focused-page expiry/restart/logout, stale replies/tab signals, recovery, keyboard/reflow and credential-free storage/demo.
- [x] `README.md`, `.docs/implementation-artifacts/auth-setup.md`, `.docs/implementation-artifacts/sprint-status.yaml` — contract/evidence and separate unexecuted hosted gates.

**Acceptance Criteria:**
- Given no auth configuration, when demo runs, then it completes without external calls.
- Given ended authority, when normal auth is checked, then access stays denied; no claims about unimplemented document endpoints.
- Given synthetic tests, when hosted evidence is recorded, then only actually executed checks count.

## Implementation Notes

Completed review corrections preserve the approved intent. Session cookies now use `sb_session_<16 hex generation digest>` with opaque values and the same HttpOnly/SameSite/Secure rules; legacy names are accepted only against live browser-bound registry authority. Resolution considers at most 32 eligible cookie names and ignores retired/foreign authority, independent of header order. Rotation/logout retire only the request's names, so delayed deletion cannot erase a later generation. Status still never changes session cookies.

Logout intent remains pending after transport failure: private display stays cleared, retry obtains a fresh CSRF binding without rendering its identity and repeats the protected POST. Fan signals request authoritative passive observation, deferred during active work; a local display deadline does not broadcast server termination. Lifetime snapshots subtract elapsed request/JSON time. Background checks preserve panels, drafts, focus and controls; explicit user work aborts/supersedes the observation. Revocation uses a separate 16-permit AnyIO limiter and retains running-worker ownership; its ten-second network budget remains cooperative, not a hard bound on OS/native work. Late login/callback identities rejected by fencing/expiry receive bounded after-response local cleanup.

## Spec Change Log

2026-11-15 resumed review: no approved/frozen requirement changed and no new planning round. Non-frozen implementation notes document generation-specific cookie retirement, retry intent, signal reconciliation, elapsed lifetime and dedicated revocation admission. KEEP: atomic local denial, response-before-provider ordering, explicit local scope/no-refresh, browser independence, revision fences, existing recovery/demo behavior, no new persistence/cost/settings/email/password operations.

## Review Triage Log

Resumed at step 4 on 2026-11-15 under the student's explicit instruction to finish fixes without replanning or another approval. The saved blind/verification reports were retained; the interrupted independent edge layer completed against the baseline diff before triage. Its eight reports reproduce B1?B8, with no additional root cause. The old implementation agent is unavailable in this resumed session; the parent applies corrections. All verified cases are resolved within the approved intent and frozen block; the explicit continuation instruction takes precedence over a workflow loopback/re-approval.

| ID | Verdict | Route | Verified evidence / required correction |
| --- | --- | --- | --- |
| B1 | medium | patch | Logout catch exposes retry but its handler only calls bootstrap; an aborted POST leaves authority valid and restores identity. Retain pending logout intent and retry POST before allowing login. |
| B2 | medium | patch | Bare `ended` broadcasts unconditionally call endAccess and abort active requests. Old timers/signals can clear a later login. Treat signals as non-touching server observations; reconcile after active work, and never broadcast a local timer as server termination. |
| B3 | medium | patch | armLifetime starts the entire server snapshot duration upon delivery. Subtract measured request/JSON elapsed time and reject already-expired snapshots. |
| B4 | medium | patch | _own awaits the shared thread limiter before _batch checks budget. Sixteen slots can remain occupied indefinitely behind unrelated work. Use a separate limiter with the same capacity as admitted revocations; keep running-worker cancellation ownership. |
| B5 | medium | patch | submit/complete_callback discard a returned Identity when rotate rejects its obsolete revision or callback expires. Attach bounded after-response local revocation to these rejected responses; never revoke another browser's identity. |
| B6 | medium | patch | A probe replayed the actual logout deletion headers after a fresh login: the new cookie disappeared while its registry authority remained live. Use generation-specific session cookie names; delete only names supplied by the old request and select live authority by registry/browser binding. |
| B7 | medium | patch | Background bootstrap unconditionally clearDisplay/setBusy, hiding recovery and disabling inputs during provider latency. Preserve current display/drafts and controls while observing; an explicit action supersedes the observation. |
| B8 | medium | patch | ready() can resolve at synchronous endAccess before POST acknowledgement. Wait for logout response/completion and assert cookie deletion and server normal/recovery denial. |
| B9 | false | reject | The session-ending log and issue already distinguish saved implementation from incomplete review. No remaining application defect at the cited location. |
| V1 | medium | patch | Trusted pre-verified coverage gap: outage/old-session-removal tests cannot detect loss of revision fencing for an unfinished callback. Add blocked callback plus failed current-session validation and assert late authority denial. |
| E1 | medium | patch (B1) | Independently traced same logout retry failure; same verified outcome/correction as B1. |
| E2 | medium | patch (B2) | Independently traced unconditional old fanesignal; same verified outcome/correction as B2. |
| E3 | medium | patch (B3) | Independently traced delayed lifetime delivery; same verified outcome/correction as B3. |
| E4 | medium | patch (B4) | Independently traced shared-worker admission; same verified outcome/correction as B4. |
| E5 | medium | patch (B5) | Independently traced late rejected provider login; same verified outcome/correction as B5. |
| E6 | medium | patch (B6) | Independently traced delayed cookie deletion; same verified outcome/correction as B6. |
| E7 | medium | patch (B7) | Independently traced passive panel/control interruption; same verified outcome/correction as B7. |
| E8 | medium | patch (B8) | Independently traced premature browser assertion; same verified outcome/correction as B8. |

Grouping: E1?E8 join their matching B rows only. V1 remains a separate verification correction. No findings deferred. Fix/verification completion is recorded below after actual execution.

## Design Notes

No product gaps; existing auth/UI/tests plus logout/lifetime status. Runtime revocation has provider side effects; fixtures do not.

After-response revocation: 16 active slots, no queue/retry, one shared ten-second cooperative budget per admitted batch; saturation/failure never retains local authority. Status is non-touching; successful authenticated work still touches idle. Return bounded `expiresInSeconds` for normal/restricted state, arm a clearing timer and passive checks every 30 seconds while visible plus focus/pageshow. Probe after login without changing its existing response contract. BroadcastChannel signals contain no secrets/storage. Deny obsolete cookies even after late delivery. An admitted password PUT may finish remotely; its late response cannot restore local access.

## Verification

- `uv run --group pdf-experiment pytest` — all pass; deterministic short deadlines.
- `node tests/browser-auth.cjs`; `node tests/browser-demo.cjs` — both pass, including passive expiry.
- `git diff --check` — clean.
- Record hosted checks separately; fixtures are synthetic.

Parent verification on 2026-11-15: the full baseline diff (including newly tracked files) was read. `uv run --group pdf-experiment pytest --junitxml=test-results/logout-parent-verification.xml` ran 240 cases: 239 passed, one unchanged optional PDF platform skip; all 177 auth cases passed. `node tests/browser-auth.cjs` passed 28 scenarios; `node tests/browser-demo.cjs` passed 11 scenarios/21 generation requests. `git diff --check` passed. The approved block SHA-256 remains `0669a8ae87bcd57293b81ccc0cee6567e7795f60388dde9e08aa8946d82fc64e`.

Matrix audit (all listed Python cases are present and passed in the parent JUnit output):

| Matrix row | Executed evidence |
| --- | --- |
| Logout | `test_logout_ends_all_browser_authority_and_attempts_but_retains_fresh_login[False/True]`; normal/restricted keyboard browser logout |
| Outage | `test_local_logout_provider_outage_preserves_other_browser_even_for_same_account`; `test_logout_response_is_sent_before_revocation_starts_and_old_cookie_is_denied`; `test_revocation_admission_cancellation_and_shared_batch_deadline`; independent-browser scenario |
| Expiry | `test_passive_status_cannot_renew_idle_but_authenticated_work_can`; `test_default_maximum_lifetimes_absolute_expiry_and_recovery_snapshot`; focused normal/recovery browser deadline clearing |
| Restart | `test_browser_isolation_unknown_sessions_outage_and_restart`; visible passive browser restart/fresh-login scenario and existing page restoration coverage |
| Races | `test_logout_fences_inflight_authority_after_provider_await` (six flows); `test_logout_during_body_stream_prevents_subsequent_provider_work` (three flows); validation-expiry fence; existing password stale-reply tests and sibling-tab late-login scenario |
| Protection | `test_logout_protection_empty_json_and_configuration_precede_provider` (eight cases); SDK exact local wire test; privacy/reflow browser scenarios and full no-config demo |

At the initial checkpoint, task/matrix verification passed and independent review remained incomplete. The dated completion below supersedes that handoff; earlier counts remain historical evidence.


### Review completion and final parent verification ? 2026-11-15

All B1?B8/E1?E8 corrections and V1 are complete; B9 was already resolved.
The independent edge reviewer inspected the final patch and found no further
concrete defect (read-only, no separate test rerun). No review finding was
deferred. The parent inspected the application patch, fixture/test changes,
full verification results and 200% screenshot. The approved frozen-block SHA-256
remains `0669a8ae87bcd57293b81ccc0cee6567e7795f60388dde9e08aa8946d82fc64e`.

Final executed commands/results:

- `uv run --group pdf-experiment pytest --junitxml=test-results/logout-parent-verification-final.xml`: **243 passed, 1 unchanged optional PDF platform skip**, all **181 auth cases** passed; one existing Starlette deprecation warning. Last full Python run: 56.38 seconds.
- `node tests/browser-auth.cjs`: **33 passed** after final regression-fixture sequencing correction, including actual old-timer firing while a newer login response is held. The synthetic 33-scenario run before that strengthening also passed; the intermediate strengthened run failed because its own test signal revalidated the old timer. No production change followed the passing full Python/demo runs.
- `node tests/browser-demo.cjs`: **11 passed / 21 generation requests**.
- `git diff --check`: passed.
- Genuine provider/browser acceptance: **25/25 checks** using existing authorized test accounts; **10/10 checks** on the restarted normal configured server. See [acceptance details and limitations](auth-setup.md#story-23-review-completion--2026-11-15).

The added Python regressions prove provider-denial fencing during unfinished
signup/recovery callbacks, local cleanup of rejected late identities, generation
cookie deletion/header ordering/binding, and revocation progress with the shared
worker limiter occupied. Browser regressions prove POST retry without identity
restoration, old timer/signal safety, elapsed normal/restricted snapshots, usable
recovery controls during passive latency, acknowledged restricted logout and real
late logout-header ordering across tabs.

Hosted evidence uses real Supabase validation, local revocation and refresh,
including same-account independence and actual local server-process restart.
Restricted grant admission and expiry metadata were locally instrumented;
revocation outage was injected at the adapter seam. No actual recovery-email/PKCE
acceptance, natural 30-minute/12-hour wait or genuine provider outage is claimed.
No emails, account provisioning, password writes, Auth settings, costs or
deployment were performed. Existing Story 2.1/2.2 link/template gates remain
open and are not retriggered. Normal server PID 11748 runs one worker with the
existing ignored `.env`; the isolated test server is stopped. Spec is done;
sprint Story 2.3 remains review for final product acceptance.
