---
title: End access on logout expiry and restart
type: feature
created: 2026-11-15
status: in-review
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

- `app/services/sessions.py`: reuse pruning, coalesced validation and authority_revision; only recovery rotation is fenced. Separate validation from caller activity.
- `app/api/auth.py`: reuse protection, cookie helpers and complete_callback; clear_session is unused. Fence login/signup across body/provider awaits. Status never mutates session cookies.
- `app/adapters/auth.py`: installed SDK admin.sign_out(jwt, scope="local") directly uses user JWT, no privileged key/session installation. Ordinary sign_out defaults global and may refresh.
- `app/static/account.*`: reuse sequence/abort/focus guards; add termination observation. Existing auth/browser fixtures supply tests, never production debug routes.

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

## Spec Change Log

## Review Triage Log

Review was interrupted at the student's explicit request to end the session and commit on 2026-11-15 at 09:42. Final triage and fixes are pending; this build is not complete. Do not restart planning or ask for approval again. The three layers were launched together after parent verification. Blind and verification reviewers returned; edge-case review was interrupted before its final report. No review fixes have been applied.

Outstanding reports to verify individually before grouping/routing:

| ID | Reported issue | Current evidence/status |
| --- | --- | --- |
| B1 | Failed logout hides its buttons; retry only checks status and can restore the old signed-in view when POST never reached the server. | Inspect logout catch/retry in `../../app/static/account.js`; final verdict pending. |
| B2 | A prior tab's timer/termination broadcast can clear or abort a newer login in another tab. | Broadcast has only `ended`, no generation; reproduce ordering before choosing the smallest fix. |
| B3 | Delayed status delivery starts the client lifetime later than the server snapshot. | Timer uses received `expiresInSeconds`; add delayed-response evidence. |
| B4 | Revocation slots may wait indefinitely for shared thread-pool admission despite a ten-second cooperative budget. | Budget is checked in worker; existing test releases admission after advancing clock. Assess actual bound and disposition. |
| B5 | Identity returned by a late login/callback and rejected by revision fencing is never included in local provider revocation. | Local denial works; determine required provider cleanup and scope from approved intent. |
| B6 | Delayed logout cookie deletion may overwrite a sibling tab's newer login cookie. | Reproduce actual response ordering; immediate after-response provider ordering alone does not prove network ordering. |
| B7 | Passive observations hide current panels/disable controls during every provider request. | Trace background bootstrap and recovery focus under latency. |
| B8 | Restricted browser logout test may finish at synchronous display clearing before server acknowledgement. | Add response/cookie/server authority assertions if confirmed. |
| B9 | Active log/issue still described implementation in progress. | Corrected in the user-requested session-ending handoff; no app change required. |
| V1 | Provider-denial revision fencing is not directly tested against an unfinished callback. | Pre-verified regression gap: old session removal would pass outage tests while allowing a late callback. Add a synthetic blocked callback + failed current-session validation test; reviewer recommended patch. |

Resume Build step 4 with these reports and the existing implementation agent if available. Read the snapshot's step-04-review instructions, verify B1–B8 individually, trust V1's filed gap evidence, and complete edge-case review. If code changes, run all spec verification commands again. Do not mark done until triage/fixes/review are complete. No genuine hosted account operations are authorized by these synthetic checks.

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

Initial task/matrix verification passed against the inspected implementation and executed offline checks. Independent review subsequently raised the reports above; review and final acceptance are incomplete. Hosted acceptance remains unexecuted and is separately documented.
