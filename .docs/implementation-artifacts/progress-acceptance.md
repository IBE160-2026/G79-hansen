# Story 3.3: practice progress acceptance

Implementation and test-project integration completed on 18 November 2026.
The parent applied the reviewed migration to the existing `studybuddy-test`
project as version `20261118142904`, verified existing test-account sessions,
and restarted the local app on port8000 (worker10088).

## Behavior and protocol

Only navigation in an already-saved generation autosyncs both stable practice IDs.
The owner-free `/api/v1/progress/read` and `/write` endpoints reuse session-view,
CSRF/origin checks, bounded admission, backend gate and user-JWT transport. Write
adds `mutationId`, `expectedProgressRevision` and both `positions`; success returns
`progressRevision`. Content Save and progress revisions remain independent.

Migration `20261117184855_synchronize_practice_progress.sql` was CLI-created.
Invoker RPCs lock the shared document row, enforce ready owner/current generation
and both memberships, compare the progress revision, and retain exact canonical
requests/outcomes in owner-RLS `progress_mutations`. Identical admitted retries
replay before old revision checks; changed requests fail. Ready/current generation
and both item memberships are checked before replay. Replacement retains original replay generation identity.
Reload reads positions and revision atomically; Save records its initial revision1.

The browser serializes/coalesces navigation, preserves the frozen mutation through
one automatic uncertain retry, and then offers explicit retry/refetch. A conflict
blocks persistence until successful explicit fetch. Fetch hides answers; failures
retain the block. New generations require reopening the saved document. Responses,
timers and queued intent are fenced by active workspace/session/document/generation.
Library pagination/back does not invalidate same-document acknowledgements.

## Executed verification

- `uv run --locked pytest tests/test_progress.py -q --tb=short`: **23 passed**,
  one existing Starlette/httpx deprecation warning.
- Final progress browser run: **16 scenarios passed**, including coalescing,
  stale-view fetch blocking, exact retries and reset/edit/open/logout/owner fences.
- Local migration applied successfully after correcting a CASE-expression parser
  error; final `progress_protocol.test.sql`: **36 assertions passed**, including
  membership-before-replay validation.
- Affected existing browser suites: **Save25, library21 passed**. Final Save run
  includes the replacement-retry/navigation regression from review finding E1.
- Existing document/library Python baseline on 17 November: **66 passed**.
- Guarded real local RPC runner: **20 checks passed**, including an actual
  same-revision race and dropping an already-committed successful reply before
  exact replay. Synthetic accounts were confined to the isolated local stack.
- Hosted progress acceptance: **23 checks passed**, with two sessions of one
  existing owner and another existing owner. Concurrent writes produced one win
  and one conflict; exact replay, request binding, owner/generation/membership
  rejection, explicit fetch and fresh-login resume passed. Original synthetic
  document positions were restored through an ordinary new progress mutation.
- Restarted normal server: **16 checks passed**, including authenticated atomic
  reload/read, session-view rejection, private headers and owner isolation.
- Model budget files remained byte-identical under the hosted/normal checks;
  no real inference, new hosted accounts, source writes or public deployment.

One focused independent edge-case review found E1: a retried content replacement
could mistake intervening practice navigation for unchanged state. The original
attempt now retains private navigation metadata outside its wire payload; the
Save browser regression passed. Further broad review contexts were omitted in
line with the student's five-hour allowance preference.

An extra old Save SQL rerun did not complete: Docker/systemd reported a cgroup
unit timeout, followed by a stalled SUREUbuntu even for `/bin/true`. With explicit
student approval, only that distribution was terminated/restarted. A bounded
probe subsequently exited0; Docker showed all six local Supabase containers and
SURE web/worker/database/Redis/HTTPS running again. This interrupted Save SQL run
is not a pass. Production transport deadlines were unchanged.

Hosted security advisors reported only the existing leaked-password-protection
warning; Auth settings were not changed.

Logs are under ignored `test-results/progress-*`. Run the real local runner with
`SAVE_TEST_WSL_DISTRO=SUREUbuntu` and
`uv run --locked python tests/progress_provider_acceptance.py`. Browser command:
`node tests/browser-progress.cjs`. SQL assertions use the existing guarded local
stack harness and roll back their synthetic fixtures.

## Remaining acceptance limits

Only acknowledged progress is guaranteed after leaving or restart. No background
or unload delivery guarantee, inference or implicit content Save was introduced.
Hosted semantics were verified through separate authenticated sessions. A public
deployment and two physical devices remain Epic4 release acceptance.
Prior real-file retention/physical deletion gates and the historical broad Save
provider failures remain separate and unproven; this story does not relabel them.
