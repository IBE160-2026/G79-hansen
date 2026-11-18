---
title: Encrypt, rotate and restore prepared local backup bundles
type: chore
created: 2026-11-18
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 06fa99c9599a6bfd5276f885881d9d5ed7b35b18
context: []
---

<frozen-after-approval reason="Student authorized local backup preparation; export credentials are not established">

## Intent

Implement the local encrypted-bundle, seven-day rotation and isolated extraction portion of Story4.1 backup. The student has not established a database export password; no privileged export credentials were found locally. Build and prove the local component using synthetic prepared database/Storage/state exports first. This is not an operational complete Supabase backup, a live database restore or a scheduled job.

## Boundaries & Constraints

Reuse `C:\StudyBuddy-Backup` for eventual real encrypted copies; tests use temporary synthetic directories only. Same-PC risk is accepted through submission15.12.2026. No provider/model/email calls, credentials/password reset/creation, real exports, current app state reads/mutation, runtime restart, Supabase/Tailscale changes, scheduled tasks or public activation. Never weaken RLS or use application credentials to claim a complete all-user backup. Fail closed on unsafe/missing components; never silently call a partial export a complete project backup. Restore only into a new isolated directory; never restore over current budget, signing key, auth journal or application data. Later database import and replay of post-snapshot deletions remain separate gates.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure |
| --- | --- | --- | --- |
| Roundtrip | Synthetic prepared DB, Storage objects/inventory and local state | Authenticated encrypted archive, byte-exact isolated restore | No plaintext archive/key on disk |
| Missing/mismatch | Missing DB/Storage inventory/state, changed objects or hash mismatch | No published completed archive | Content-free error |
| Tamper/wrong key | Truncated/modified ciphertext or wrong Windows identity/key | No extraction published | Content-free failure |
| Rotation | Own backups/partials at least7days old | Remove only recognized regular files under verified root, even if next pack fails | Preserve unrelated files/links |
| Unsafe paths | Traversal, symlinks/reparse points, existing restore target, duplicate entries | Reject without escaping/overwriting | No state rollback |
| Limits/failure | Oversized bundle or interrupted write | Bounded memory/files; atomic publish only after verification | No misleading completed copy |

</frozen-after-approval>

## Code Map

- New `scripts/backup_studybuddy.py`: CLI and narrow reusable local bundle engine. No application imports needed. Use a documented prepared-source contract with database export(s), a complete local Storage inventory and object bytes, and explicit local state files. Validate inventory hashes and required components; generate an encrypted content manifest. Label archive coverage **prepared export only**, not verified live-project completeness.
- Existing model budget/signing-key/email journals are persistent authority: archive source copies supplied explicitly in the prepared bundle; never locate/read current real files implicitly. Restored copies stay quarantined. Preserve blocked markers in the bundle when supplied; never copy over a live journal.
- `cryptography`50.0.2 already exists installed and in `uv.lock`; add the exact same version as direct dependency using `uv add --offline cryptography==50.0.2`. No new download/version upgrade.
- Use maintained high-level **Fernet** authenticated encryption with a fresh random key per archive. Protect that small key with Windows **DPAPI CurrentUser**, UI forbidden, via typed ctypes calls and LocalFree. Do not implement cryptographic primitives or store a plaintext master key. Describe dependence on same Windows user/profile/PC honestly.

## Tasks & Acceptance

- [x] `scripts/backup_studybuddy.py`: implement bounded explicit prepared-source pack, authenticated verify/decrypt, isolated manual safe extraction, recognized-file rotation. Keep a conservative documented maximum64MiB plaintext bundle and bounded file/count/header limits; exceeding limits rejects, never truncates. Build plaintext archive in memory only. Include source metadata/manifest inside encryption; no source names, addresses or keys in logs. Reject archive symlinks/unsafe entries and root/path aliasing. Validate all authentication/manifest information before publishing restored files. Atomic encrypted publication through own `.partial` file, exclusive new output and cleanup on failure. Rotation executes before source validation/packing, independently of export success; only remove own exact-pattern regular files older than or equal to7days, under checked absolute root. Never follow a symlink/junction for deletes. No recursive deletion of existing user directories.
- [x] `scripts/backup-studybuddy.ps1`: small literal-argument wrapper with offline/no-sync/locked/no-auto-env uv. Expose pack, rotate and isolated restore without dynamic shell evaluation. Suppress raw stderr and filter fixed safe summaries. Default encrypted root `C:\StudyBuddy-Backup`; no live-credential loading or scheduling.
- [x] `tests/test_backup_studybuddy.py`: focused synthetic tests for every matrix row, actual Windows CurrentUser DPAPI/Fernet roundtrip, tamper/wrong-key, incomplete inventory, boundary limits, path escapes, atomic failures, seven-day boundary and rotation even when pack source fails. Use deterministic clocks where useful; never use real root/state or provider calls. Explicit test-only protector injection is acceptable for failures/portable unit cases; Windows crypto roundtrip must really run on Windows, not be silently skipped there.
- [x] `README.md`, `.gitignore`, `.docs/implementation-artifacts/backup-local-4-1.md`: document precise source contract/commands, plaintext64MiB limit, archive format/key scope, private ACL prerequisite, restore quarantine, monotonic-budget/deletion reconciliation, and retention limitations while PC is off. Clearly list unimplemented/unverified live export, administrative access, consistency/quiescence, daily scheduling and actual isolated PostgreSQL/Storage import. Do not imply these gates are satisfied by successful file extraction. Include official Fernet/DPAPI/Supabase references.

**Acceptance Criteria:**

- Given a complete synthetic prepared source, when packed and restored into a fresh isolated destination, then all declared bytes match and no plaintext archive/key exists on disk.
- Given tampered/incomplete/unsafe input, when packing or restoring, then no complete output is published and existing files/state remain unchanged.
- Given expired recognized files under the dedicated root, when rotation or a failed pack runs, then expiry occurs without deleting unrelated files or following links.

## Implementation Notes

This bounded component is useful before export credentials exist. Parent retains the full live backup/restore/scheduling gate. Implement compactly; avoid generalized snapshot/provider frameworks. Parent handles real root ACL preparation and any later actual demonstration separately.

Implemented the prepared-export-only engine/wrapper and exact source contract, using the already installed cryptography 50.0.2 as a direct pinned dependency. Fernet keys are fresh per archive and protected by Windows CurrentUser DPAPI. Disabled email is explicitly declared without inventing a journal; enabled email requires its journal. Expiry uses valid UTC creation time in owned filenames rather than modifiable filesystem timestamps. Restored state stays in a fresh quarantine directory; no live import or state replacement is performed.

Parent separately restricted the empty `C:\StudyBuddy-Backup` ACL to the operator, SYSTEM and Administrators, with previous SDDL saved in a system temporary file. No actual backup was created there. Student clarified: "Jeg har ikke laget noe passord"; export access remains unestablished. No password was created/reset and no actual credentials/state were copied.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and resolution |
| --- | --- | --- |
| Parent P1: initial expiry used modifiable mtime | medium | Touching a file could extend retention. Use validated UTC creation timestamp in exact owned filename; old-name/new-mtime, new-name/old-mtime, invalid dates and seven-day boundary tests passed. |
| Parent P2: initial source contract always required email journal | medium | Current runtime has no enabled mail journal. Require explicit boolean email state; disabled disallows journal/sidecars and enabled requires exactly one journal. Both paths and missing/ambiguous cases passed. |
| Independent R1: directory limit checked only after restore extraction | medium | An authenticated valid manifest with 1,000 empty objects could imply over 6 000 directories. Count distinct parent paths during manifest validation before staging; regression proves no staging creation. Fixed and parent verified. |

One focused combined independent review completed; its single actionable finding was patched. No findings deferred for this component. Parent Story4.1's live export/restore/scheduling gates are explicitly outside this completed local component and remain open.

## Verification

Run only `uv run --locked pytest -q tests/test_backup_studybuddy.py`, PowerShell syntax parse and scoped whitespace check. No broad suites. Report component proof separately from unimplemented live backup and database restore.

Final parent run 18 November: **62 passed in 17.84s**, including actual Windows CurrentUser DPAPI/Fernet roundtrip and pre-extraction directory bound. PowerShell AST parse and scoped whitespace checks passed. All matrix rows were covered by executed synthetic tests. No provider/model/email calls or real backup-root/state reads occurred in tests. This proves encrypted file packaging/extraction/rotation, not PostgreSQL or Storage import.
