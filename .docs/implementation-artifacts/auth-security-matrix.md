# Story 2.1 security matrix evidence

This maps the approved matrix to actual assertions, not just test names. It is
separate from the hosted acceptance record in [auth-setup.md](auth-setup.md).
An offline test cannot establish hosted email delivery or cross-account isolation.

## Foundation evidence inspected 2026-11-13

Source: `tests/test_auth.py` at
`7ad7ade208f95c3ef2032cba5e2128d6dc8ee6c4`, unchanged when this audit began.
The parent inspected the test bodies and parsed the existing JUnit evidence,
`test-results/auth-parent-verification.xml`: **68 auth cases, zero failures,
zero skips**. This evidence is from the 2026-11-12 run; parsing it today is not
a new test run. The total historical suite was 130 passed and one PDF platform skip.

| Approved scenario | Covering tests in `tests/test_auth.py` | Assertions inspected |
| --- | --- | --- |
| Signup | `test_signup_is_generic_and_confirmation_validates_rotates_and_cleans_url`; `test_sdk_signup_requires_confirmation_and_does_not_enumerate_existing_accounts` | Generic check-email, no initial session cookie, bounded pending entry; SDK immediate session rejected; existing-user response remains generic |
| Confirmation | `test_signup_is_generic_and_confirmation_validates_rotates_and_cleans_url`; `test_real_sdk_transport_pkce_exchange_login_validation_and_refresh_contracts` | 303 fixed clean destination, no-store/no-referrer, opaque session ID, validated user display and session rotation; S256 challenge and exchange verifier reach actual SDK transport |
| Bad callback | All ten `test_bad_callback_rejects_before_exchange` cases; overlapping callback replay test | Missing/wrong browser/state/code, duplicate code, wrong purpose, absent verifier, expiry, restart and implicit inputs produce invalid-confirmation destination, no exchange call and no new session |
| Overlap/race | `test_overlapping_attempts_and_simultaneous_callbacks_consume_exactly_once` | Separate verifiers/redirects, two concurrent callbacks consume one attempt once, other attempt still works, no pending entries remain and final rotation leaves one session |
| Login | Signup/rotation test; real SDK transport test; nine `test_sdk_rejects_incomplete_mismatched_and_failed_provider_responses_without_secrets` cases | Login rotates cookie; SDK invokes get_user; unconfirmed/mismatched/incomplete/expired/failing responses deny session creation without echoing provider data |
| Request protection | Sixteen `test_origin_csrf_fail_before_provider_call` cases; strict credentials and chunked body tests | Origin/CSRF/host failures reject with safe 403 before provider calls; strict fields/types/lengths and oversized/malformed input reject safely |
| Missing config/outage | Fifteen `test_missing_invalid_or_disabled_configuration_fails_closed_without_provider_calls` cases; browser-isolation outage test; SDK failure matrix | Disabled/missing/privileged/invalid config yields unavailable and no provider calls, fixed demo still works; provider failure denies/clears affected identity |
| Browser isolation | `test_browser_isolation_unknown_sessions_outage_and_restart`; expiry and serialized refresh tests | Distinct test identities/cookies remain independent; one failure does not end the other session; cleared registry denies old session; idle/absolute expiry and failed refresh deny, concurrent refresh serializes |

## Known verification limits found by independent review

The historical SDK transport test did not assert the exact callback/state value,
and its negative identity matrix exercised login rather than existing-session
status validation. The interim review also found previously uncovered malformed
CSRF input, late-status/login rotation, UI focus behavior and elapsed-time bounds.
See [the individual review findings](auth-code-review-2026-11-13.md).

## Post-correction evidence

The parent executed the full suite after the corrections:
`uv run --group pdf-experiment pytest -q --junitxml=test-results/auth-review-parent-verification.xml`.
Result: **155 passed, 1 expected PDF platform skip, 1 existing TestClient warning**,
25.38 seconds. Parsing that new XML confirms **93 auth cases, no auth failures or
skips**. Every original matrix test above ran again and passed.

The additional coverage includes malformed raw headers/bindings, shared SDK
operation budgets, partial HTTP-header trickles and TLS stream closure, overlapping
and canceled queued validation, independent sessions, near-expiry bindings, a
complete valid delayed credential body, pre-append/exact 8 KiB bounds, delayed
validation and already-created denial cookie races, exact route-to-SDK callbacks,
and invalid real-SDK status identities. See the review report for the cooperative
native/DNS deadline limit rather than a hard wall-time claim.

The parent also ran all **16 browser-auth scenarios** after the final Python
changes. The updated configured local server passed ten unauthenticated boundary
checks. The original non-ASCII CSRF probe changed from **500 without no-store** to
**403 with no-store**. No account/email was created by these automated checks.
Manual hosted acceptance remains a separate open gate.
