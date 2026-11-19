# Story 4.1 — local preparation

18 November 2026. IBE160, Molde University College. Submission: 15 December 2026.
This is a preparation record, not an activation package. No public activation requested.

## Route ownership established

Read-only Windows and Tailscale inspection at approximately 20:19 Oslo time:

| HTTPS listener | Loopback target | Purpose and evidence | Observed access |
| --- | --- | --- | --- |
| 443 | 127.0.0.1:8765 | Football dashboard: listening PID 20488, parent executable under `C:\Users\fredr\football-agent`; command-line match for `dashboard_server`; running scheduled task `Fotballrapport-Statistikk`; `dashboard_server.py:308` defaults to 8765 | tailnet only |
| 8443 | 127.0.0.1:3000 | SURE: `C:\Users\fredr\sure\README.md:87` and `setup-tailscale.ps1` explicitly assign this mapping; no Windows TCP listener observed on 3000 during inspection | tailnet only |
| None | 127.0.0.1:8000 | StudyBuddy: listener PID 25940, matching the preceding hosting/deletion log | local only |

Both `tailscale funnel status` and `tailscale serve status` label the existing routes **tailnet only**. Their shared JSON configuration alone was insufficient to establish public Funnel access. This corrects the earlier hosting log's terminology. No routes, processes or scheduled tasks were changed. No external requests were made to these apps. The absence of a Windows listener on 3000 does not establish SURE's overall service health.

Reserve **HTTPS port 10000 as the StudyBuddy candidate**, subject to a fresh conflict check at activation. Do not replace ports 443/8443 or run a global Serve/Funnel reset. Tailscale documents 443, 8443 and 10000 as permitted Funnel ports, and warns that switching a port from Serve to Funnel makes that port public. See [Funnel limitations](https://tailscale.com/docs/features/tailscale-funnel).

## Local work sequence

1. Add one bounded, shared admission mechanism covering signup **and** recovery, with recipient and global limits. Browser-cookie rotation and restart must not bypass the shared email allowance. Preserve existing generic responses and callback/browser binding. Use offline adapter checks only when this code changes.
2. Prepare one-worker Windows startup on `127.0.0.1:8000`. Reuse existing ignored credentials, signing key and budget journal. Require the exact HTTPS origin, Secure cookies and trusted loopback proxy headers; disable access logging in the hosted launcher. Do not start a second worker or replace the current process during preparation. Verify these controls locally before activation.
3. Implement backup/export, encryption and retention below. Do not mark a manifest-only or database-only export as a complete backup.
4. Prepare the assessor's **own account**. Student selected this on 18 November; email will be supplied later. No account creation, password change or email sending is authorized by this selection. Keep public email registration/recovery availability explicitly gated until delivery and shared throttling are ready.
5. When local controls and account access are ready, create the exact activation package: intended origin/port and backend, exact callback allowlist changes, startup and port-specific rollback, existing-route preservation and remaining acceptance gates. Obtain separate approval **then**. Real PC/mobile/external access checks follow authorized activation.

## Backup implementation contract — not implemented

`C:\StudyBuddy-Backup` exists and was independently counted: **zero entries**. The student accepts same-PC loss risk through submission. No backup, encryption key, export credential or scheduled backup task was created.

- Daily encrypted database **and separate private Storage-object** exports, plus preserved local budget state and signing-key recovery material; never publish these files or commit them. Database exports omit Storage bytes: [Supabase backup documentation](https://supabase.com/docs/guides/platform/backups).
- Verify export privileges and installed CLI/version before choosing commands. Do not put privileged export credentials in the application or chat. CLI v3 changes targeting defaults; explicitly verify the intended existing project rather than assuming the linked target: [CLI v3 changes](https://supabase.com/changelog/supabase-cli-v3).
- Use a dedicated backup format and restrict directory access to the operator/system. Implement encryption with authenticated integrity and a protected local recovery key; prove decryptability before scheduling. Do not count directory ACLs alone as encryption.
- Publish a completed backup atomically only after all required components and integrity checks succeed. On partial failure, report an incomplete backup without raw data in logs. Bound staging files and clean them on failure.
- Expire only this job's own recognized backups and staging files after **7 days**, including failed runs. Validate resolved deletion targets remain under the dedicated folder. Retention must not depend on a successful new export. When the PC resumes after downtime, run expiry before exposing the app; powered-off storage cannot perform timed deletion.
- Prove restore using synthetic material in an isolated **local** database/storage target, with no model calls or new hosted project. Keep service closed during restore; reconcile later deletions before reopening and preserve maximum budget spend/blocked state. Never overwrite the current budget journal with an older copy.

## Evidence limits

Only documentation and read-only local inspection in this session. No application tests, model calls, Supabase mutation, auth redirect changes, exports, scheduled jobs, server restarts or public activation. Supabase Free/Paris status carries forward the already confirmed evidence; it was not queried again. Existing physical-retention and earlier release gates remain open. Story 4.1 remains draft/backlog.

## Subsequent local email implementation — 18 November

The student instructed continuation. Shared durable signup/recovery admission is now implemented and reviewed in [the local subtask](spec-4-1-local-email-admission.md): two reservations globally and one per normalized recipient per rolling hour. Final focused offline suite: 221 passed. A missing/unsafe journal disables email dispatch while password login and demo work. No production journal initialized, environment changed or server restarted. Configure the dedicated journal before enabling email on a restarted server; preserve it across restarts/uncertain outcomes. Backup, startup, assessor address, activation and real-device gates remain pending. Existing routes are untouched.

## Subsequent local startup implementation — 18 November

[Startup subtask](spec-4-1-local-hosted-startup.md) completed locally: foreground Windows launcher, separate placeholder environment, strict literal bounded configuration reader, read-only state validation and fixed loopback/proxy/logging settings. Final startup/email checks:99 passed; independent focused review found no remaining actionable defects. One existing overly strict concurrency-test assertion was corrected to allow safe all-denied contention followed by required uncontended progress; production quotas/locking unchanged. Real hosted configuration, actual journal initialization, backup/restore and startup remain unexecuted. No current process, state or private route was changed. Continue with encrypted backup/rotation/restore preparation before making the activation package.

## Subsequent local backup component — 18 November

[Prepared-bundle subtask](spec-4-1-local-backup-bundle.md) complete locally: authenticated encryption with CurrentUser-protected keys, seven-day invocation-based expiry and byte-exact new-directory quarantine extraction. Final proof 62 synthetic tests; one independent directory-bound finding was patched. The actual backup root has no real archives and has private operator/SYSTEM/Administrators ACLs. Live roles/schema/data and Storage export, consistency, scheduled operation, actual isolated DB/Storage import and state/deletion reconciliation remain open. File extraction is not a database restore. Do not request publication approval yet.

## Export-access update — 19 November

The student reports manually changing the database password. Masked local DPAPI capture and a fixed read-only TLS connection helper are prepared (48 synthetic checks). The first prompt process exited without a saved credential; its cause is unconfirmed. The student explicitly deferred checking this. Do not reopen the prompt, request another password reset or retry live authentication until they resume this step. No real authenticated export or backup has occurred.

## Retention preparation — 19 November

The installer now prepares a current-user, limited interactive task for daily03:00 and logon expiry, with catchup when available, no wake/network requirement and a hidden pythonw action. `-Plan` does not contact Scheduler or the private backup root; installation refuses existing exact-name tasks and query errors. No task has been registered. A real hosted start now reuses expiry before importing the app and refuses startup on failure; `--check` stays read-only. Focused offline checks:75 passed. This prepares deletion of expired archives, not creation of daily backups.

Subsequently installed after the student requested continuation: exact task
`\StudyBuddy-Backup-Rotation`, current operator Interactive/Limited, actual
action/settings/triggers confirmed. One real run at13:35 finished with result0;
next daily run20 November03:00 local. No daily backup/export, app restart,
credential check, provider call or route/public change occurred.
