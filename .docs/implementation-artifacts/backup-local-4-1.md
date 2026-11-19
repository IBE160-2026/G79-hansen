# Local prepared-export backup bundles (Story 4.1 component)

This component packages **prepared export only**. A successful pack or byte-exact
file extraction does not establish an operational complete Supabase backup,
database consistency, or a successful PostgreSQL/Storage restore. No database
export password or privileged export access has been established. The tool never
loads application configuration, discovers current state, calls providers,
changes Supabase/Tailscale, starts the application, or schedules work.

## Prerequisites and private directories

Use Windows and the existing locked environment (`cryptography==50.0.2`). Prepare
the dedicated absolute `C:\StudyBuddy-Backup` directory with a private Windows
ACL restricted to the authorized operator and necessary system administrators
before using it. Restrict the prepared-source and quarantine parent directories
too: both contain plaintext. ACL preparation is an operator gate; the tool does
not create or audit ACLs. Do not permit concurrent untrusted writers or modify
sources during packing. Paths and all existing ancestors must be real directories,
without symlinks, junctions or other reparse points. Use absolute paths. The
source and encrypted roots must be separate and neither may contain the other.

No real export or real state should be placed in the repository. The ignored
`.backup-prepared/`, `.backup-quarantine/`, `*.sbb` and `*.sbb.partial` patterns
are a fallback against accidental commits, not access control. Synthetic tests
use their own temporary directories and never the actual backup root.

### Confirmed session-pooler parameters — 19 November

The student copied these non-secret parameters from the existing project's
Connect dialog: host `aws-0-eu-west-3.pooler.supabase.com`, port `5432`, database
`postgres`, user `postgres.fssrvicgmijksgozgfoj`. The user suffix matches the
app's configured project `fssrvicgmijksgozgfoj`; this is session pooling, not the
transaction endpoint on 6543. No password was supplied, stored or reset. Connect
displays how to use an existing database password; it does not create one.
Export authentication, verified TLS configuration and privileged Storage access
remain pending. Firefox URL-policy enforcement is unsupported by the available
UI tool, so dashboard details are being supplied manually by the student.
TCP port5432 was reachable in a read-only socket check on19 November; the
sandbox initially blocked it and the authorized non-sandbox check succeeded.
This was not a TLS, password, SQL or export validation.

The student subsequently reported changing the database password manually.
Do not request another reset. Capture and read-only checker helpers have passed48
synthetic checks and a focused review. The first interactive capture launch exited
without saving its credential file; the student's observed outcome is pending.
No password has been received in chat, stored locally or used for authentication
by the agent. Real connection/backup remain unverified.

### Manual masked credential capture and read-only check

The local helpers are prepared; actual capture and authenticated live verification
remain pending until the operator explicitly performs these steps. These helpers
do not change/reset the password, initialize application state, restart the app or
container, access Storage, perform exports or activate public access.

Use an interactive Windows PowerShell 5 window under the same Windows account
that will run the checker. Enter the existing password manually at the masked
prompt; never put it in chat, clipboard, shell arguments, environment setup or
logs:

```powershell
.\scripts\save-backup-password.ps1
uv run --locked --no-env-file python -m scripts.check_backup_connection
```

Capture writes only DPAPI CurrentUser-protected binary UTF-8 data, exclusively
creating `C:\StudyBuddy-Backup\.database-password.dpapi`. The private parent must
already exist, restricted to the operator, SYSTEM and Administrators, without
concurrent untrusted writers; the helper does not create directories or audit
ACLs. The destination and its ancestors may not be reparse points. Relative,
traversal, alternate-stream and UNC destinations are rejected. An existing file
is never overwritten; a failed/cancelled capture never reports success. Input
must be nonempty, at most 1,024 UTF-8 bytes and contain no CR, LF or NUL. The
script clears mutable plaintext buffers and its BSTR on a best-effort basis.
`-Destination 'C:\AnotherPrivateParent\new.dpapi'` supports a separate synthetic
destination under an existing private parent. Copying ciphertext alone does not
make it portable: decryption normally requires the same Windows account/profile
and PC as capture. Preserve that scope as with bundle keys.

The Python checker bounds and validates a regular, single-link credential read
before DPAPI decryption. `--credential 'C:\AnotherPrivateParent\new.dpapi'`
selects an explicit local file; importing the module does not connect. Production
uses the existing `SUREUbuntu` WSL distro and running
`supabase_db_studybuddy-save-local` container's PostgreSQL 17 client, without
setup, restart or reconfiguration. A fixed subprocess argument list sends the
password as one UTF-8 stdin line; the constant shell script reads it literally
and exports `PGPASSWORD` only inside that client process. The password is never
interpolated into shell code or placed in command arguments.

The exact host, port, database and routed username remain those above. The
checker uses `PGSSLMODE=verify-full`, `PGSSLROOTCERT=system`, an eight-second
connection timeout and a 20-second subprocess deadline, with no TLS downgrade
or automatic retry. Incidental service/passfile/options overrides are cleared.
`psql -X -w -qAt` executes only
`BEGIN READ ONLY; SELECT current_database(), current_user; ROLLBACK;`.
Expected database and actual PostgreSQL role are both `postgres`; the project
suffix is pooler routing in the connection username. Output must match exactly.
No SQL results, decrypted bytes or client diagnostics are printed; native stderr
is discarded. A successful checker prints `studybuddy-backup: connection-ok`.
Failures print only `credential-invalid`, `arguments-invalid`,
`connection-timeout`, `connection-result-invalid` or `connection-failed` after
that fixed prefix and exit nonzero. TLS, wrong-password and other client errors
share `connection-failed` so raw diagnostics never escape.

This limited probe establishes authenticated access to that endpoint only. It
does not establish privileged export completeness, roles/schema/data capture,
snapshot consistency, Storage coverage, an actual backup or successful restore.
All remaining live export, consistency, Storage, restore and scheduling gates
below remain in force.

## Exact prepared-source contract

An operator must first create a consistent, private source copy. The tool only
reads files explicitly represented by the contract; it never locates current
budget, signing capability or email journals implicitly. Example `prepared.json`:

```json
{
  "version": 1,
  "email": {"enabled": true},
  "database": ["database/roles.sql", "database/schema.sql", "database/data.sql"],
  "state": [
    {"role": "budget", "path": "state/budget.json"},
    {"role": "signing_key", "path": "state/signing.key"},
    {"role": "email_journal", "path": "state/email.sqlite3"},
    {"role": "blocked_marker", "path": "state/budget.blocked"}
  ]
}
```

At least one nonempty database export is required. Exactly one `budget` and one
`signing_key` copy are required. The `email` declaration is mandatory: use
`{"enabled": true}` with exactly one `email_journal` copy, or
`{"enabled": false}` with no journal or email sidecars. Explicitly disabled email
does not require creating a journal. The current runtime has email disabled;
declare that state honestly when preparing a future source. Optional `blocked_marker`
and `email_sidecar` entries preserve explicitly supplied markers and SQLite
sidecars; zero-byte blocked markers are supported. Missing roles fail closed;
there is no implicit disabled-state exemption. A snapshot producer must ensure
journal consistency and include every existing blocked marker and required
sidecar. A missing or ambiguous email declaration rejects the source. The local
engine validates bytes and declarations, not SQL semantics,
budget schema, SQLite consistency or the authority of the export producer.

The second fixed metadata file is `storage-inventory.json`:

```json
{
  "version": 1,
  "objects": [
    {
      "path": "storage/private-bucket/object.bin",
      "size": 3,
      "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    }
  ]
}
```

That example object contains the three UTF-8 bytes `abc`. Paths must be unique
relative forward-slash file paths under `database/`, `storage/` or `state/` as
appropriate. Storage `size` and lowercase SHA-256 must match every supplied
object byte. An empty `objects` array explicitly declares empty prepared Storage;
this is not proof that live Storage is empty. The file set must match the two
metadata files plus all declared database, state and Storage files exactly.
Undeclared files, missing objects, duplicate JSON keys/paths, case aliases,
file/directory path conflicts, absolute/traversal paths, Windows reserved names,
links, reparse points and hardlinked files reject the bundle.

Limits are 64 MiB **for the entire plaintext bundle**, including its manifest,
4,096 files and 4,096 directories, 240 characters per relative path, 256 KiB for each source metadata
file, 512 KiB for the encrypted content manifest and 16 KiB for the protected
key header. Oversized inputs reject without truncation. Each read is bounded;
Fernet and manifest verification require several bounded in-memory copies, so
peak memory is greater than 64 MiB. This is deliberately unsuitable for larger
projects. Empty directories are not archived.

## Commands

From the repository root, using existing installed dependencies without sync,
downloads or automatic dotenv loading:

```powershell
.\scripts\backup-studybuddy.ps1 -Action pack -Source 'C:\PrivatePreparedExport'
.\scripts\backup-studybuddy.ps1 -Action rotate
.\scripts\backup-studybuddy.ps1 -Action restore -Archive 'C:\StudyBuddy-Backup\studybuddy-YYYYMMDDTHHMMSSZ-UUID.sbb' -Destination 'C:\PrivateQuarantine\new-restore'
```

The sample archive name is a placeholder: select an actual generated file in the
private directory. `-Root 'C:\AnotherPrivateBackupRoot'` overrides the pack/rotate
root. Restore needs an existing private parent and an entirely new destination;
it cannot replace an existing file/directory. All wrapper arguments are literal
data. The wrapper suppresses raw stderr and admits fixed value-free summaries
only. Success prints `studybuddy-backup: pack-passed`, `rotate-passed` or
`restore-passed`; failure prints `studybuddy-backup: backup-failed` and exits 1.
Source paths, content, addresses and keys are never logged.

## Format and key scope

Version 1 `.sbb` files contain an eight-byte `SBB1` signature, a big-endian
four-byte protected-key length, a DPAPI-protected fresh random Fernet key, and
one authenticated Fernet token. The plaintext, held only in memory during pack,
is a four-byte manifest length, bounded JSON manifest, and concatenated file
bytes. The encrypted manifest carries version, `prepared export only` coverage,
creation time, relative names, exact sizes and SHA-256 hashes. There are no archive
symlink entries, executable extraction hooks or compression. Authentication and
every manifest/hash/contract check complete before any extraction begins.

[Fernet](https://cryptography.io/en/latest/fernet/) supplies authenticated
encryption. The small per-archive key uses
[Windows DPAPI CryptProtectData](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata)
with CurrentUser scope and `CRYPTPROTECT_UI_FORBIDDEN`; typed ctypes calls free
DPAPI output with `LocalFree`. No plaintext master key is stored. Recovery
normally depends on the same Windows account, profile and PC; a copied archive
alone is not portable disaster recovery. Losing the profile/key material can
make archives unrecoverable. Any eventual scheduled pack must run as the same
Windows user/profile that will perform restore; scheduling is still pending.
Fernet exposes its token timestamp; archive names,
sizes, filesystem timestamps and the DPAPI envelope remain visible outside the
encrypted manifest. No source filenames appear in the outer format.

Pack writes only an exclusively created, recognized `.sbb.partial`, flushes and
verifies it, then atomically publishes without replacing an existing archive.
Failure removes only the attempt's owned partial. Restore stages plaintext under
an owned temporary directory in the quarantine parent, verifies those bytes,
then renames to the new destination without replacement. A handled failure cleans
its own staging. Power loss/forced termination can leave a partial encrypted file
or a plaintext quarantine staging directory; inspect and privately remove those
owned remnants manually. Plaintext staging is never automatically published as
a completed restore. Production extraction intentionally requires Windows.

## Retention and later recovery gates

Rotation runs before source-content validation on every pack and also runs separately.
An unsafe root or lexical source/root overlap rejects before any deletion.
It deletes only recognized regular, single-link files directly beneath the
checked root, with names `studybuddy-<UTC timestamp>-<32 lowercase hex>.sbb` or
the same name ending `.sbb.partial`, and a valid UTC timestamp in the name at
least seven days old (including the exact boundary). Invalid calendar dates are
preserved. Touching/copying a file cannot extend that deadline; old modification
times do not expire a newer named archive early. Other files, hardlinks, links, junctions and
directories are preserved. No recursive deletion is used. This does not inspect
ciphertext validity or source coverage and does not guarantee a minimum number
of usable copies. Rotation is invocation-based: there is no daily scheduler,
and nothing expires while the PC/tool is off. Same-PC failure risk is accepted
through submission on 15 December 2026. File deletion is not secure erasure of
disk remnants, external copies or provider backups.

Restored state remains **quarantined**. Never copy an older budget, blocked
marker, signing key or email journal over the running authority. Later recovery
must reconcile budget reservations monotonically, retain blocked/exhausted
markers and account for email reservations made after the snapshot. Restoring
data must replay/reconcile deletions committed after the snapshot before any
user access; a backup must never resurrect deleted private content. File
extraction does not perform these operations.

Unimplemented or unverified gates remain: privileged administrative export
access and database password, live database roles/schema/data export, complete
live Storage export, consistent/quiescent cross-system snapshot capture,
daily scheduling and operational retention monitoring, actual isolated
PostgreSQL and Storage import, application compatibility/login verification,
post-snapshot deletion replay, monotonic state reconciliation and disaster
recovery beyond this PC. Follow the official
[Supabase backup scope](https://supabase.com/docs/guides/platform/backups) and
[CLI backup/restore guidance](https://supabase.com/docs/guides/platform/migrating-within-supabase/backup-restore):
database backups do not include the actual Storage object bytes. Ordinary
user credentials and RLS-scoped reads cannot establish all-user completeness.

## Focused proof

Run `uv run --locked pytest -q tests/test_backup_studybuddy.py`, parse the
PowerShell wrapper, and run a scoped `git diff --check`. Tests use synthetic
prepared directories, injected failure protectors where appropriate, and an
actual DPAPI CurrentUser/Fernet pack/restore on Windows. They cover roundtrip,
incomplete inventory/state, tamper/wrong key, bounds, unsafe entries/links,
exclusive publication and interrupted writes, and exact seven-day rotation
even when packing fails. These prove the local component only.

18 November verification: **62 focused tests passed**, including a valid authenticated
manifest implying more than 4,096 directories being rejected before staging.
The real empty `C:\StudyBuddy-Backup` folder has separately been restricted to
the operator, SYSTEM and Administrators. No real backup, credentials or runtime
state was placed there. Actual exports, scheduling and database restore remain pending.

Credential helper checks use only synthetic temporary data and shadow
`Read-Host` in the test process; they never read actual credentials or invoke
WSL/provider operations. Run
`uv run --locked pytest -q tests/test_backup_connection.py`, including the
PowerShell AST parse, and a scoped whitespace check. The focused suite verifies
actual Windows DPAPI capture/Python unwrap, exclusive writes, sanitized failures,
literal path parsing, exact command/stdin/TLS/read-only settings, bounded reads,
timeouts, client failure and unexpected query output. Live credential capture
and authenticated connection verification remain separate pending operator steps.


## Prepared retention task ? 19 November

`./scripts/install-backup-retention.ps1 -Plan` returns metadata without Scheduler
or private-root access. Later `./scripts/install-backup-retention.ps1` registers
only `\StudyBuddy-Backup-Rotation`, refusing collisions or query errors. It uses
the current operator's Interactive token and Limited privileges, installed
`.venv/Scripts/pythonw.exe`, fixed repository working directory and
`-m scripts.backup_studybuddy rotate --root "C:\StudyBuddy-Backup"`.
Daily03:00 local and same-user logon triggers catch up when available; the user
must be logged on. Battery operation is allowed, overlapping runs ignored and
runtime capped at five minutes. No wake or network condition is required.
The PC cannot expire files while off; expiry also runs after successful hosted
preflight, before app import. An expiry error blocks startup with a safe category;
`--check` never performs expiry.

**No task has been registered.** This prepares seven-day deletion, not daily
backup creation. Full export/consistency/isolated import remain pending. The
student explicitly deferred checking password capture/authentication; do not
reopen its prompt or request another reset.75 focused offline scheduler/startup
checks passed, with all Scheduler operations mocked and real roots untouched.
