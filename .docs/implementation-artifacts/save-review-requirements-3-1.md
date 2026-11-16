# Story 3.1 review re-derivation requirements

These clarify the approved protocol without changing frozen intent. Read the
spec's individual review verdicts. No hosted mutation, new model inference,
account/email/password operation, budget reset or deployment is authorized.

## Preserve positive implementation and evidence

The parent reverts the prior application implementation before this iteration.
An ignored, parent-owned source snapshot at
`test-results/story-3-1-pre-review/` preserves the previous implementation and
tests. Its manifest identifies the exact source files. Use it as a positive
basis for unchanged, verified parts; re-derive affected functions and tests from
these requirements rather than carrying the identified defects forward.

KEEP strict owner-free contracts, immutable canonical digest, receipts/file
authority, replay-before-old-proof checks, short global locks/per-workspace
ordering, responsive logout, bounded owned IO and retained permits, atomic
user-JWT SECURITY INVOKER RPCs/owner+backend gate, unexposed schema, immutable
Storage keys and internal byte verification. Preserve replacement CAS, initial
independent positions/reset-on-replacement, private safe rendering/reflow and
all earlier passing source/auth/demo behavior. Retain truthful unknown-write
records and cleanup_pending for uncertain physical files; no false physical
quiescence claim. Preserve the exact CLI-created migration filename and all
previous results as historical, not automatic proof of re-derived code.

Parent-only runtime files remain in place: `supabase/config.toml`, ignored CLI
binary/local Docker stack, existing `.env`, real allowance ledgers and ignored
`.save-backend-key`. Do not read secrets, create/overwrite keys or change these
runtime files. The existing SHA-256 verifier in the acceptance record is public
metadata. Parent alone runs actual SQL/Storage acceptance and prepares hosted
approval. The migration is not installed on hosted.

## Required derived behavior

1. After locking operation and target document, commit must recheck the actual
   wall clock against immutable admission expiry. An action waiting across the
   boundary erases staging/disables upload and returns save_expired without any
   publication. Check the other expiry-sensitive upload/verification paths too.
2. Recovery discovery must include recent ready outcomes for seven days, so a
   lost successful response remains discoverable after page/server restart.
   Return existing identifiers/status, not private bundle bytes. Render confirmed
   ready outcomes as completion, not pending work or an invitation to regenerate.
   Superseded-file ready operations remain cleanup-only while their registered
   cleanup is unresolved. Keep stable UUID pagination and ownership.
3. Pending recovery rows include a safely rendered title, admittedAt and
   expiresAt so the student can distinguish operations and resupply the correct
   original file. Do not retain a private staging title after cancellation,
   terminal conflict or expiry of an initial pending document. Ready document
   titles/content are unaffected. Terminal tombstones contain no staged content.
4. A cancelled/expired/conflicted operation with no registered file is provably
   object-free: cleanup may return cleanup_complete; hide completed cleanup
   rows while retaining the operation ID/digest tombstone. Never delete uncertain
   file records, declare file cleanup complete on DELETE alone, or delete the
   current ready object. Distinguish completion in UI/CLI.
5. Add automatic all-owner staging expiry via a narrowly scoped administrator
   database job, independent of owner login or user-token availability. Use
   pg_cron with an unexposed SECURITY INVOKER maintenance function whose execute
   permission is revoked from public/anon/authenticated. The job uses its database
   administration identity, never a service key in ordinary app requests. Bound
   each transaction/batch, lock before disabling finalization, erase only overdue
   non-ready private staging/title, retain digest/object cleanup metadata and
   make retries idempotent. Do not log content or keys. Schedule at least once
   per minute; recovery/commit expiry is exact, physical staging purge occurs
   on the next successful maintenance run. Document scheduler delay/health and
   backup limitations explicitly. A disabled/failed job remains an acceptance
   failure, not a silent retention guarantee. Actual hosted job installation and
   monitoring join the final approval package; no hosted change now.
6. Browser title validation must agree with server whitespace/control/Unicode
   constraints before freezing. Definite unadmitted invalid input permits title
   correction; uncertain admitted attempts keep their exact identity. A saved
   generation's title is disabled until a saveable new generation exists.
7. Discovery failures must be visible with explicit retry using existing
   controls; disabled Save configuration may stay quiet. Fence discovery and
   pagination by current session plus independent request epoch so stale replies
   cannot erase newer rows or re-enable stale actions.
8. Save intake accommodates two copies of the largest legitimate accepted source
   with bounded member/structure budgets; source/generation limits remain intact.
   Test many short paragraphs through source, generation and Save, never with a
   live model. Preserve 16 MiB/five-second envelope and owned work deadlines.
9. Strengthen browser evidence: first Save persists submitted noninitial item IDs;
   explicit reload restores independent noninitial flashcard/quiz positions and
   keeps answers hidden. Add loss-of-ready-response/restart discovery, title
   correction, discovery error/retry/out-of-order and object-free completion tests.
   Actual local SQL tests must cover waiting across expiry and unattended expiry,
   ordinary-role denial of admin maintenance, preserved ready/other-owner rows,
   scheduled execution and retained uncertain objects. Parent handles actual
   provider checks after the derived migration is ready.
10. Update contradictory README current-behavior text, acceptance evidence,
    architecture notes and exact hosted approval package, preserving historical
    counts. Final verification is fresh; previous 506 tests, later focused27 and
    15 browser scenarios, 16 pgTAP and parent38 provider checks are historical.

Official references checked 16 November 2026:
[Supabase Cron](https://supabase.com/docs/guides/cron),
[installation](https://supabase.com/docs/guides/cron/install),
[quickstart](https://supabase.com/docs/guides/cron/quickstart).
The actual local image exposes pg_cron as available but not yet installed.
