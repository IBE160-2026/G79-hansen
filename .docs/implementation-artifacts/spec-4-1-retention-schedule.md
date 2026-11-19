---
title: Prepare unattended backup expiry and require it before hosted startup
type: chore
created: 2026-11-19
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 462f2b9b89b8030ec0b213b2eb2b0ca11dcfb5bd
context: []
---

<frozen-after-approval reason="Student deferred password interaction and requested continued independent local work">

## Intent

Prepare the password-independent seven-day retention operation: a reviewable Windows scheduled-task installer and expiry before actual hosted app start. User cannot check the password dialog now; do not reopen it, ask for secrets, retry authentication or change/reset passwords. Existing tested bundle rotation already deletes only its own expired regular files. Reuse it, without creating another retention algorithm. No task registration during this preparation subtask; parent will inspect a pure plan and leave installation pending while user is unavailable.

## Boundaries & Constraints

No Supabase/provider/model/email calls, real credentials/config/state reads, actual backup exports, current app restart or Tailscale/public changes. No existing tasks, files or server processes modified during implementation/tests. The real root is `C:\StudyBuddy-Backup` and remains private operator/SYSTEM/admin. Expiry affects only existing recognized archives/partials as defined by bundle code; credentials and unrelated files remain untouched. One explicit new task name; no force overwrite or broad task enumeration/removal. Keep all preparation noninteractive.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior |
| --- | --- | --- |
| Plan | Installed Pythonw and repo | Safe deterministic plan only; no Task Scheduler call or filesystem mutation |
| Install later | No task with exact name | Only named task registered for current Windows user, no saved password/elevation |
| Collision | Task with same name exists | Refuse without replacing or changing any task |
| Hosted check | --check, valid synthetic state | No retention mutation or app import |
| Actual start | Successful preflight | Rotate before app import/server run; exact fixed root |
| Expiry failure | Any cleanup error | Safe category, no application start or raw exception |

</frozen-after-approval>

## Code Map

- `scripts/backup_studybuddy.py`: reuse `rotate(Path(...))` unchanged; filename-time seven-day policy, link/root checks and no recursion are already covered by62 tests. No credential unwrap required for rotation.
- `scripts/hosted_server.py`: after successful preflight and after returning from check mode, invoke narrow expiry helper before `load_application` and `uvicorn.run`. Convert failures to `StartupFailure('backup-retention-failed')`. Do not initialize any live state.
- `scripts/start-hosted.ps1`: include the new fixed safe failure category in stdout filter.
- `.venv/Scripts/pythonw.exe` exists and is the installed console-free executable. Scheduled action should use it directly with `-m scripts.backup_studybuddy rotate --root "C:\StudyBuddy-Backup"`, fixed repo working directory. No PowerShell execution-policy changes or visible windows needed.

## Tasks & Acceptance

- [x] `scripts/install-backup-retention.ps1`: compact PS5 installer with `-Plan` that returns task metadata before any Scheduler access. Exact root-path task `StudyBuddy-Backup-Rotation`; current operator Interactive logon, Limited run level, daily03:00 local plus same-user AtLogOn, StartWhenAvailable, AllowStartIfOnBatteries/DontStopIfGoingOnBatteries, IgnoreNew instances, five-minute runtime cap, no WakeToRun/network requirement. Validate known executable/module/root paths structurally. Plan does not read actual root/state, require credentials or register anything. Actual registration later must refuse an existing same-name task (including access/query errors), use no -Force and preserve all unrelated tasks. No installation/run-now/delete in tests or this task.
- [x] `scripts/hosted_server.py`, `scripts/start-hosted.ps1`: require existing rotation before actual app start, never during --check. Fail closed, safe message and unchanged port/proxy/cookie settings.
- [x] `tests/test_backup_schedule.py`, `tests/test_hosted_startup.py`: offline/mock tests for every matrix row; PS AST and pure -Plan invocation; shadow Scheduler cmdlets in isolated PS tests so registration/collision/error branches cannot call actual scheduler. Check exact task action/principal/triggers/settings and no forced replacement. Existing startup fixture must mock expiry so no real root is touched; add ordering/failure/read-only-check assertions. No actual scheduled task, GUI, private folder, WSL/provider or real file deletion in tests.
- [x] `README.md`, `.docs/implementation-artifacts/backup-local-4-1.md`: explain prepared plan/installation commands, same-user logged-on requirement, daily/logon catchup, no wake guarantees while PC off, scheduled rotation versus unimplemented daily full backup, and expiry-before-app-start behavior. Label task not registered and password work explicitly deferred. Preserve existing user-reported password change; never suggest reset.

**Acceptance Criteria:**
- Given plan invocation, when the operator inspects it, then the exact task is reviewable and no scheduled/system/data changes occur.
- Given actual launch later, when preflight succeeds, then expiry completes before app construction or launch; failure prevents start and check remains read-only.
- Given student unavailability, when this task ends, then no password interaction or actual task registration/real deletion was attempted.

## Implementation Notes

Parent owns bmad-build orchestration, review/logging/commits and later installation. Existing reflection notes from prior session are parent-owned; do not edit them. Keep implementation compact. If a tool needs escalation, report to parent instead of waiting for a hidden approval in the child.

## Spec Change Log

## Review Triage Log

One compact independent review covering correctness, edge cases and verification gaps found no actionable defects. Additional separate review layers skipped under the project's explicit time/token constraint. No findings deferred.

## Verification

Only `uv run --locked pytest -q tests/test_backup_schedule.py tests/test_hosted_startup.py`, PS syntax/pure plan and scoped whitespace. No wider suites. Tests must never inspect/delete actual backup-root files or register actual tasks.

Final parent verification:75 passed in32.71s with the exact focused command, including PS syntax and pure/mock task branches. The sandbox blocked uv cache access; approved normal-profile execution succeeded. No real task registration, backup-root inspection/deletion, provider connection, credential prompt, app restart or publication. Actual task installation and full backup remain pending outside this local preparation subtask.
