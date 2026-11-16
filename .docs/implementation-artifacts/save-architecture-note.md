# Story 3.1 implementation note

The approved protocol remains authoritative. Save adds request-scoped user-JWT
RPC and Storage adapters; the existing authentication SDK client still yields
only auth. The private `studybuddy` schema is not exposed through PostgREST.
Versioned public business RPCs use SECURITY INVOKER, fixed empty search paths,
explicit `auth.uid()` owner predicates, RLS and short row-locked transactions.

An additional server-only random 256-bit capability establishes backend origin
after FastAPI validates receipt authority. The database retains only active
SHA-256 verifiers. Its visibility does not reveal the random preimage. The gate
is required by each RPC and every mutation policy; old/new owner checks remain
mandatory. There is no function for installing trusted request context and no
ordinary service-role access. The setup utility uses exclusive file creation,
restricts ACLs before writing bytes and prints only nonsecret ID/hash metadata.
Missing key/configuration fails closed, and browser headers are never forwarded
into either adapter.

New Save takes an owned per-workspace asynchronous gate shared with extraction,
generation commands and invalidation. Synchronous authentication/workspace locks
protect brief authority checks only. The gate orders durable admission against
edits; logout immediately detaches authority independently of network completion.
Only an already-dispatched explicit action may finish after access ends. HTTP
wait expiry does not release the worker permit or invent an outcome. Browser
view/revision/generation/epoch fences discard obsolete responses.

The immutable digest includes schema version, validated owner, selected target,
generation, canonical acceptance/source/settings/bundle, title, expected revision,
file digest/size and captured independent positions. Proofs/receipts/original
bytes/credentials/transport timestamps are excluded. First Save validates both
positions; replacement derives first available positions. Existing owner
operations are loaded before process-local proof checks. Recovery reads the
admitted snapshot and verifies resupplied bytes, so restart never recreates an
unadmitted draft.

Admission registers the exact owner/document/generation/operation object key.
Storage accepts immutable INSERT only, never UPDATE/upsert. Bounded internal
readback requires user JWT, backend gate and a backend-selected verification
marker. End-user pending/list/signed access remains denied. The Storage policy
locks the operation during metadata finalization; cancellation/expiry conflicts
with that lock and disables subsequent finalization before external deletion.
Commit installs document/content/bundle/progress atomically, records cleanup for
the previous object and erases staging. Expiry erases staging and disables
upload/commit. Registered uncertain attempts/cleanup metadata are retained.

Physical blob deletion and metadata fencing are separate facts. The application
does not turn a timeout, absent lookup or successful DELETE into proof that an
earlier provider write cannot finish. Cleanup currently remains `cleanup_pending`
after attempted deletion for registered files, retaining records. An operation
with no registered object has no possible provider write, so cancellation can
return `cleanup_complete` and discovery hides that terminal row while its
content-free ID/digest tombstone remains. Actual provider delayed-completion
and retention/backup acceptance must establish any later cleanup-complete path.
No record compaction removes outcome/tombstone IDs, so the seven-day minimum is
preserved conservatively; bounded discovery uses stable UUID pagination. Ready
operations with registered superseded cleanup objects remain discoverable as
cleanup-only entries across restart; neither discovery nor the CLI offers their
original Save for retry. Both cleanup enumeration and Storage deletion exclude
the exact current ready object. Commit conflicts erase staging immediately;
expiry scrubs pending title/source/settings/bundle while retaining immutable
digests and registered cleanup identity. Cancellation and commit conflict scrub
an initial pending document's title immediately without changing ready content.

Every expiry-sensitive commit/upload-attempt/verification transaction checks the
wall clock after acquiring its operation/target locks. A commit queued across the
deadline fences uploads, erases staging and returns `save_expired` without
publication. The Storage finalization helper also checks the actual wall clock
after locking its registered operation; verification reads use that deadline too.

All-owner expiry is independent of application sessions. The unexposed
`studybuddy.expire_staging_admin(integer)` function is SECURITY INVOKER, revoked
from public/anon/authenticated, and scheduled by the database administrator as
`studybuddy-expire-staging-v1` each minute using pg_cron. Transactions process at
most 100 operations, skip locked operations/targets and impose a ten-second job
statement timeout. Busy targets retry on the next run; exact deadline rejection
still applies immediately. Health records contain completion time/count only.
Missing/disabled/failed jobs or an overdue backlog fail retention acceptance;
the next successful maintenance batch, rather than the exact seven-day instant,
is the physical staging-purge boundary. Backup retention and physical Storage
deletion are separate gates. Hosted job installation/health monitoring require
the same separate final approval as the migration and bucket policies.

Owner discovery uses stable UUID pagination and a seven-day window from immutable
`completed_at` for confirmed outcomes. It returns no private bundle/source bytes;
pending rows alone expose their owner-only title and admission/expiry times.
Cleanup-only terminal rows use scrubbed labels. Browser discovery has its own
request epoch, independent of workspace resets, so obsolete list/page replies
cannot erase newer rows or revive actions. Discovery failures show explicit retry;
disabled configuration stays quiet. Title validation agrees with the server
before freezing; a definitively unadmitted invalid request unlocks correction,
while an uncertain operation retains its exact identity and a saved generation
keeps its title locked until another generation can be saved.

Storage operation helpers and operation names were checked against the
[official helper documentation](https://supabase.com/docs/guides/storage/schema/helper-functions)
and [provider operation definitions](https://github.com/supabase/storage/blob/master/src/http/routes/operations.ts).
Actual local instance acceptance, including header propagation, is recorded
separately; source inspection alone is not isolation evidence.
