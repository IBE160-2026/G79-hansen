---
title: Capture local export password and verify read-only database access
type: chore
created: 2026-11-19
status: in-progress
route: dispatch
review_loop_iteration: 0
baseline_commit: 53c46688245e66f496f8e921e6881a93d6599066
context: []
---

<frozen-after-approval reason="User reported changing the database password and authorized backup access preparation">

## Intent

The student changed the database password in Supabase manually. Capture the existing password locally without chat/clipboard/argv/log exposure and verify read-only authenticated access to the confirmed project. Prepare the helper, run only focused synthetic checks, then parent will launch it interactively for the student. No backup or full export acceptance is claimed here.

## Boundaries & Constraints

Exact target: session pooler `aws-0-eu-west-3.pooler.supabase.com:5432`, database `postgres`, user `postgres.fssrvicgmijksgozgfoj`. The project is active in Paris and matches .env. Credential file defaults to `C:\StudyBuddy-Backup\.database-password.dpapi`, in the existing private operator/SYSTEM/admin directory. No password change/reset, live-state initialization, app restart, provider mutation, role/policy/account changes, Storage access or public activation. Never print raw secrets, SQL/client stderr or decrypted data. Do not read real credentials or start interactive prompts in tests. Existing .docs backup-local-4-1.md has parent-owned uncommitted connection notes; preserve them.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior |
| --- | --- | --- |
| Capture | Student enters password locally | Masked prompt; DPAPI CurrentUser-protected binary UTF-8 credential, exclusive new file, no plaintext disk/output |
| Cancel/failure | Empty/cancelled input, bad path or existing file | No replacement, no misleading success; generic safe error |
| Check | Valid credential and live exact endpoint | Verified TLS, bounded read-only query of current_database/current_user, safe success only |
| Failure | Corrupt/wrong password, timeout, TLS failure | Safe category, no credential/argv/stdout/stderr disclosure; no TLS downgrade |
| Secret transport | Password to existing local PostgreSQL client | stdin only, never shell interpolation or command arguments |

</frozen-after-approval>

## Code Map

- `scripts/backup_studybuddy.py`: `WindowsProtector.unprotect()` already provides typed DPAPI CurrentUser unwrap of arbitrary small binary data; reuse without changing bundle semantics.
- Local installed client is PostgreSQL17.11 in existing WSL distro `SUREUbuntu`, Docker container `supabase_db_studybuddy-save-local`. Never restart/reconfigure it. Use fixed subprocess argument list (`wsl.exe --exec docker exec -i ... sh -c <constant script>`). Password is a UTF-8 stdin line read with `IFS= read -r PGPASSWORD; export PGPASSWORD`; fixed script never evaluates input. Reject CR/LF/NUL. Exact PGHOST/PORT/DATABASE/USER, PGSSLMODE=verify-full, PGSSLROOTCERT=system, connect timeout8. Clear PGSERVICE/PGSERVICEFILE/PGPASSFILE/PGOPTIONS to avoid incidental overrides. psql -X -w -qAt, fixed BEGIN READ ONLY / SELECT current_database(), current_user / ROLLBACK, bounded process timeout. Check expected output and suppress all raw diagnostics.

## Tasks & Acceptance

- [x] `scripts/save-backup-password.ps1`: compact PS5-compatible user-run masked Read-Host -AsSecureString helper; use .NET ProtectedData.Protect CurrentUser on UTF-8 secret bytes, matching Python unprotect. No plaintext persistent temp/argv/env. Existing private parent, no reparse/relative destination, exclusive CreateNew, bounded input, no overwrite, best-effort memory clearing. Fixed safe saved/failed output. Destination parameter permits synthetic tests; default is fixed private path. Parent launches a visible interactive PowerShell only after review; script itself never changes DB password or connects to cloud.
- [x] `scripts/check_backup_connection.py`: read bounded regular single-link DPAPI credential, decode/validate secret, run fixed local client script and exact endpoint via subprocess stdin with timeout. No raw diagnostics. Do not connect automatically on import. CLI prints only connection-ok or safe failure categories. Never fall back to require/insecure TLS. Explicit unit injection/mocks only in tests.
- [x] `tests/test_backup_connection.py`: synthetic real Windows DPAPI capture/unwrap test with test-only Read-Host shadowing, exclusive-file and sanitized failure checks, parameter/path parsing and fixed command/secret stdin transport assertions, timeout/TLS/password failures and wrong query output. Mock all WSL/provider execution; no real files or real prompts. Parse PowerShell syntax. Focused test command only.
- [x] `README.md`, `.docs/implementation-artifacts/backup-local-4-1.md`: explain manual masked capture, same-user key scope/private path, exclusive write, read-only connection check, no password change and no full backup claim. Keep pooler metadata notes and all pending live export/consistency/Storage/restore/scheduling gates.

**Acceptance Criteria:**
- Given synthetic user input, when captured locally, then only DPAPI ciphertext persists and existing files remain untouched.
- Given captured real credentials later, when parent explicitly runs the checker, then only fixed endpoint/read-only SQL is attempted with verified TLS and no secret output.

## Implementation Notes

Use one compact implementation and focused checks. Parent handles interactive launch and actual read-only check, review, logs and commits. Do not recursively orchestrate skills.

Capture/check helpers implemented. Final parent focused suite:48 passed in63.26s outside the sandbox, including actual synthetic .NET DPAPI capture and Python unwrap. One focused independent review reported no findings. Real capture and authenticated connection remain pending. Parent launched capture process26796; it exited without the credential file. Cause (cancel, launch restriction or runtime failure) is not confirmed; student status has been requested. Do not claim a stored password or successful login.

## Spec Change Log

19 November: student explicitly deferred checking the local capture outcome. Keep real capture/authentication pending; continue independent local preparation without reopening the prompt or requesting another reset.

## Review Triage Log

| Finding | Verdict | Resolution |
| --- | --- | --- |
| P1: initial current_user expectation included Supavisor project suffix | medium | Route username remains postgres.<ref>; expected actual PostgreSQL role corrected to postgres. No live attempt was made with the wrong expectation. |
| P2: synthetic Read-Host shadow used script-scoped input across child script invocation | low | Mock lost its synthetic input, producing a safe RuntimeException. Isolated test process now uses a unique global fixture variable; Unicode/punctuation DPAPI roundtrip and full48 passed. Production secret handling unchanged. |

Independent focused review: no findings. Runtime capture/check are unverified and keep this access task in-progress; the overall backup gate remains open.

## Verification

`uv run --locked pytest -q tests/test_backup_connection.py` and PowerShell AST parse/scoped whitespace. No broader auth/bundle/provider suites or real credential input during implementation. Report live verification as pending until parent runs it after the user saves the secret.

Final synthetic verification: **48 passed**,63.26s. Windows crypto requires normal user-profile access outside the sandbox. No WSL/provider execution, real prompt or real credential was used by tests. Actual launch result: process closed, credential file absent; no live checker run yet.
