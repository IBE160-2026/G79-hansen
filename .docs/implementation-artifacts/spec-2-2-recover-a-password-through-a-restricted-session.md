---
title: Recover a password through a restricted session
type: feature
created: 2026-11-14
status: done
route: dispatch
story_key: 2-2-recover-a-password-through-a-restricted-session
baseline_commit: 32b1586bf6c1ebc3297205eefe538c1a3b176af9
review_loop_iteration: 0
context: [.docs/implementation-artifacts/epic-2-context.md]
---

<frozen-after-approval reason="approved by the student on 2026-11-14: gjør det">

## Intent

**Problem:** Students cannot recover a forgotten password.

**Approach:** Add “Glemt passord”, browser-bound email recovery and a password-update-only view. Successful update ends recovery authority and requires ordinary login.

## Boundaries & Constraints

**Always:** Preserve auth protections/demo. Use request-scoped SDK operations, validated owner/email, shared deadlines, no hidden retries. Attempts bind state/browser/verifier/purpose, expire after ten minutes and share 1,000-total/four-per-browser limits. Bound recovery grants by browser/ten-minute expiry and 1,000 combined normal/restricted sessions. Retain opaque HttpOnly/Lax/Secure-on-HTTPS cookies, Origin/CSRF, body bounds, no-store/redaction. Atomically consume authority before mutation; failure requires a new link and timeout may mean password changed. Preserve other users.

**Never:** Grant normal access from recovery, trust submitted owners/editable metadata, expose secrets, accept implicit fragments, weaken confirmation, add document tables/general logout, deploy or incur costs. Retain Free/Paris and open Story 2.1 email gates. Real email/password mutation needs explicit tester authorization.

## I/O & Edge-Case Matrix

| Scenario | Given / When | Then / safe failure |
| --- | --- | --- |
| Request | Given valid email, when requested | Generic existing/missing-account acknowledgment; safe provider failure; no login |
| Callback | Given unused bound recovery code, when exchanged | Validate identity, rotate restricted authority, clean redirect; normal auth false |
| Invalid link | Given wrong browser/purpose, missing state/verifier, expiry, replay or restart, when used | Reject; explain new request; overlapping attempts keep separate verifiers |
| Update | Given valid grant/password, when submitted | One provider write; consume grant; require login; normal-session authority rejected |
| Race/outage | Given concurrent updates or failure after admission, when completed | At most one write attempt; no reuse, leaked error or late cookie overwrite |
| Protection | Given invalid/oversized/slow JSON, foreign Origin/CSRF or missing configuration, when requested | Reject safely before provider work; privacy headers retained |

</frozen-after-approval>

## Code Map

- `app/adapters/auth.py`: reuse `client()`, budget, storage, `_validated()`. SDK stores `verifier/PASSWORD_RECOVERY`; submit actual verifier. `set_session()` may refresh; validate owner before mutation within one budget.
- `app/services/sessions.py`: reuse `Pending`, pruning, bindings and atomic consumption; exclude recovery from normal validation.
- `app/api/auth.py`, `app/main.py`: reuse protection/body bounds, exact callbacks and redaction. Preserve the delayed-status cookie fix documented in `auth-code-review-2026-11-13.md`.
- `app/static/account.*`, `styles.css`: reuse cleanup, alerts, one-use outcomes and stale-response guards. Tests already supply SDK/browser fixtures.

## Tasks & Acceptance

**Execution:**
- [x] `app/adapters/auth.py` — request/exchange/update, verifier handling, owner checks before mutation/after response.
- [x] `app/services/sessions.py` — purpose-aware attempts, bounded disjoint grants, atomic update claim and rotation.
- [x] `app/api/auth.py` — POST `/recovery/request`, GET `/recovery/callback`, POST `/recovery/password` under auth prefix; strict email-only/password-only schemas, shared limits. Status adds `recoveryAvailable` boolean.
- [x] `app/static/account.html`, `account.js`, `styles.css` — request/new-password/confirmation forms, matching validation, restricted view, safe guidance/login outcome; preserve keyboard/reflow.
- [x] `tests/test_auth.py` — matrix, concurrency/capacity, owner mismatch, authority denial; exact SDK challenge/verifier/redirect/update, deadline/uncertainty tests.
- [x] `tests/auth_browser_app.py`, `tests/browser-auth.cjs` — journeys, isolation, replay, duplicates/stale replies, cleanup/storage/URL/console safety, login afterward.
- [x] `README.md`, `.docs/implementation-artifacts/auth-setup.md`, `.docs/implementation-artifacts/sprint-status.yaml` — setup/evidence; keep unexecuted gates/Story 2.1 open.

**Acceptance Criteria:**
- Given no auth configuration, when demo runs, then its fixed flow works without external requests.
- Given recovery authority, when normal authentication is checked, then access is denied; no unimplemented document-isolation claims.
- Given offline tests, when hosted evidence is recorded, then only executed authorized email/mutation checks count.

## Implementation Notes

2026-11-14: Student approved this concrete plan with “gjør det”. A fresh-context
implementation agent completed the tasks sequentially. Parent read the staged
baseline diff including untracked files, checked the unchanged frozen block and
visually inspected recovery at 200%. The parent found an SDK-internal refresh
boundary before mutation; the implementation now validates that final session
before PUT, with exact real-SDK transport regressions.

Parent verification: 207 passed, one expected PDF platform skip, one existing
Starlette/httpx warning, 26.21 seconds; ignored JUnit file
`test-results/recovery-parent-verification.xml`. XML audit confirms all 145 auth
cases passed and all six matrix rows have executed passing coverage: request 1,
callback 5, invalid-link 13, update 2, race/outage 15, protection 31 (overlapping
families include existing regressions). Agent browser evidence: 20 account and
11 demo scenarios passed. Hosted recovery email/password mutation and callback
configuration/template checks remain unexecuted and documented separately in
[auth setup](auth-setup.md); no such actions are implied by implementation approval.

## Spec Change Log

## Review Triage Log

2026-11-14: Three independent layers completed before triage. Edge-case review
returned no findings. Each blind/verification finding is adjudicated below before
grouping; reviewer severities and proposed fixes are not taken as decisions.

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 delayed callback replaces newer login | medium | Reproduced with a blocked recovery exchange and intervening login: callback sets a new cookie and the newer login becomes a recovery-only view. Patch the callback's atomic rotation to reject an intervening authentication transition; add regression. |
| B2 already-expired grant performs provider reads | low | Claim/pruning rejects already-expired grants at HTTP admission; only expiry while queued could reach the adapter this way. Final checked session denies PUT after expiry. Extra early guard would optimize an unusual queued-read case, not repair unauthorized mutation; rejected low-complexity tradeoff. |
| B3 Unicode length mismatch | medium | New HTML minlength/maxlength count UTF-16 units; strict Python schema counts code points. Four emoji can reach a rejected request and long supplementary passwords are prematurely limited. Patch recovery client validation to match server code-point limits; test boundaries. |
| B4 pre-admission errors treated as uncertain writes | medium | All update errors currently hide recovery and use uncertainty text, including explicit invalid_request/request_rejected/auth_unavailable that leave the grant unclaimed. Patch typed error handling to retain the correctable view and specific safe guidance; add browser cases. |
| B5 no recovery exit to login | medium | Restricted mode hides every normal-login/new-link control; the only ordinary exit requires expiry or submission. Patch a clear route back to the existing normal-login UI; validated normal login retires the old grant without a password write. No new cancellation API is needed. |
| B6 focused view does not proactively expire | low | Visible controls remain until the next action/focus check, but every write is checked against the grant deadline and failure supplies new-link guidance. No access survives expiry. A new expiry response/timer surface adds complexity for a harmless stale view; rejected. |
| B7 no recipient cooldown | medium | Baseline signup already permits fresh browser bindings to exhaust the same hosted email quota; the provider limits actual sends. This is a pre-existing shared email-admission hardening issue, not a recovery authorization regression. Defer local recipient/request throttling before public operation; do not claim current capacity limits prevent quota abuse. |
| B8 signed-in recovery action hidden | low | Normal signed-in mode hides the new recovery request with all normal forms. A student who remembers no password cannot request recovery from that view. Patch an explicit entry to the existing recovery form; keep normal server authority until a valid transition. |
| B9 only first recovery verifier exchanged in SDK test | medium | The exact SDK test creates two attempts but only exchanges the first. Add completion of each with its own code/verifier; this prevents a future second-attempt overwrite regression. Patch verification. |
| B10 expiry during final validation untested | medium | Existing expiry case starts expired; operation-budget clocks are distinct from grant expiry. Add a controlled grant-clock crossing during final SDK validation and assert zero PUT. Patch verification. |
| V1 failed request pending cleanup untested | medium | Pre-verified mutation demonstration removed discard_attempt and all 145 tests still passed. Assert released slots after repeated failures and successful retry after service recovery. Patch verification. |
| V2 grant expires during SDK validation | medium | Pre-verified mutation demonstration moved expiry checking before final validation and all 145 tests still passed. Add the same controlled-clock zero-PUT regression as B10; adjudicated separately before grouping. Patch verification. |

Surviving patch groups: callback ordering (B1), Unicode validation (B3), known
pre-admission errors (B4), navigation from non-form views (B5/B8), overlapping SDK
attempts (B9), expiry regression (B10/V2), failure cleanup regression (V1). Each
small fix keeps the existing public API and frozen intent. B7 is deferred; B2/B6
are rejected as described. No intent-gap or bad-spec loopback is required.

All seven patch groups were completed by the same implementation agent. Parent
read the patch diff and reran the full verification: 213 passed, one expected PDF
platform skip and one existing warning (26.89s); all 151 auth cases passed in
`test-results/recovery-parent-verification-final.xml`. Account browser: 23
scenarios passed; demo browser: 11 passed, 21 generation requests. The original
blocked-exchange probe now reports no callback session-cookie write, no replaced
newer login, authenticated true and recovery false. Updated recovery at 200% was
visually inspected. B1/B3/B4/B5/B8/B9/B10/V1/V2 are resolved; B2/B6 remain rejected;
B7 is recorded in [deferred work](deferred-work.md).

This spec's implementation/review workflow is complete. Sprint Story 2.2 remains
at review, with hosted callback/template/email/password acceptance unexecuted.
The normal configured local server was restarted with one worker, PID 35884,
tool session 37132. No genuine recovery email or password change occurred.

## Design Notes

Reuse opaque `sb_session` for disjoint normal/restricted registries. Valid recovery retires replaced local authority. Status reports `authenticated:false,recoveryAvailable:true`. Admitted update leaves the spent cookie untouched to avoid erasing newer login; fresh login rotates it. Do not promise unchanged provider behavior for other same-account sessions after password change.

## Verification

- `uv run --group pdf-experiment pytest` — all regressions pass.
- `node tests/browser-auth.cjs`; `node tests/browser-demo.cjs` — both pass.
- `git diff --check` — clean.
- Record hosted email/mutation separately; implementation tests send no real email.
