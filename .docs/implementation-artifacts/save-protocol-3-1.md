# Story 3.1: private Save protocol and implementation plan

**Status: proposed, 15 November 2026. No Save implementation, schema change,
bucket, new credential or storage acceptance has been created.**

## Observed baseline

Clean starting revision: `15987b9dc74859b8272883af85e2a404ea0af89c`.
Story 2.6 implementation: `bd65d4b38a1a688f15a0b002ffe2680c72c45912`;
historical tests: 481 passed/one inherited skip. Existing browser evidence is
28 source/generation, 33 auth and 11 demo scenarios, not rerun in this planning phase.

Read-only connected inspection confirmed `studybuddy-test`
(`fssrvicgmijksgozgfoj`), ACTIVE_HEALTHY, Postgres 17.11, region eu-west-3,
organization Study Buddy on Free. No public tables, Storage buckets or public /
storage.objects policies exist. `pgcrypto` is already installed. The Storage
operation helpers `allow_only_operation(text)` and `allow_any_operation(text[])`
exist. No existing data/schema needs replacing. Docker CLI is installed but the
Linux engine pipe is unavailable; Supabase CLI and psql are not installed.

Two focused read-only agents examined persistence/receipt boundaries and Save
UI/test reuse; another compiled Epic 3 context. None accessed credentials,
changed application code, ran tests or made provider calls. No lower-numbered
Story 3 spec exists; Epic 2's authentication, source/generation receipts and
quality acceptance provide continuity.

## User-visible result and story boundary

After generation, secondary **Lagre** persists the exact validated source,
settings, four learning sections and current independent flashcard/quiz positions.
An optional labelled title defaults to the canonical source title and accepts
at most 160 Unicode code points. Original text/PDF bytes are retained only when
the active source was a file. Do not send a filename/title to the model or make
any model call during Save/recovery.

Explain in the page that generation is transient until Save, and Save retains
the source, optional file and study results under the account. Do not expose RPC,
operation/key-management details in ordinary product copy. Show pending/saved /
retry states separately; disable duplicate clicks and say saved only for ready.
Preserve source/file/settings/results/positions on technical failure. A same
generation already saved is not a new Save merely because practice navigation
changed; autosync belongs to 3.3. Ordinary edits/new generation retain the active
saved-document target for explicit replacement; New session clears that target
without deleting saved data.

Offer a small owner pending-operation panel after login, with exact retry,
matching-file resupply and expired-operation cleanup. This is needed for 3.1
restart recovery, not a full library. Revision conflicts retain the unsaved
workspace and offer explicit current-target reload or Save as new. Only the
minimal current-target read needed to resolve that conflict is included; general
library list/open UI is 3.2, ongoing progress synchronization 3.3, deletion UI 3.4.

## Durable records and transactional boundary

Introduce owner documents (identity/title/lifecycle/revision), content/settings,
validated bundles and independent progress, plus immutable Save operations and
registered object/upload/cleanup records. Composite keys/checks bind owner,
document and generation consistently. Index owner/operation uniqueness, pending
expiry and document/ready lookup. Restrict app tables in an unexposed application
schema; expose only narrowly granted, versioned public RPC wrappers. Enable RLS,
revoke anonymous/default mutation/execute privileges and explicitly grant the
minimum authenticated access needed by SECURITY INVOKER functions. Restrict
configuration verifier updates to administration.

The immutable Save digest includes schema version, authenticated owner, target
document/generation, canonical acceptance/source/settings/bundle, title, expected
revision, file SHA-256/size and captured initial practice item IDs. Exclude
cookies, raw credentials, transport retries and timestamps. First Save validates
both selected item IDs independently; absent sections have null positions.
Replacement derives initial available positions for the new generation.

1. Authenticate ordinary access before bounded body work. Look up known owner
   operation first. Matching completed replay returns IDs/status before old
   receipt/revision checks; a changed digest fails. Do not return private content
   from replay without a current owner/ready check.
2. A never-admitted operation needs current receipt and live authoritative
   source/bundle/file checks. Hash original bytes server-side. Under the ordered
   admission gate, persist the immutable private staging snapshot and object
   identity via one transactional admission RPC before uploading anything.
3. Upload under an owner/document/generation/operation-derived unique key with
   overwrite disabled. Record each upload attempt/uncertain result durably.
   Verify stored bytes with bounded internal readback and SHA-256; mutable object
   metadata or a client-submitted digest alone is insufficient.
4. A commit RPC locks operation/document, rechecks current owner, admission
   lifetime, immutable digest, uploaded-file verification, target lifecycle and
   expected revision. Atomically install source/settings/bundle/progress, advance
   revision and mark ready; register previous-file cleanup in the same transaction.
   No sequence of independent REST inserts substitutes for this transaction.
5. Clean registered superseded/provisional keys only after the new revision
   commits. Retain cleanup-needed/unknown-write records until reconciliation
   confirms completion. Expose ready success separately from cleanup status;
   never claim cleanup finished while a write can still complete.

## Ordered admission without blocking logout

`Workspaces.validate_save()` currently holds `Registry.lock` and the global
`Workspaces.lock` across its yield. Putting an RPC in that context would block
logout/all workspaces and violate the module's no-await rule.

Add a bounded owned per-workspace asynchronous admission gate, coordinated with
generation and invalidation. Keep auth/global lock sections brief and synchronous.
New Save checks/freeze are ordered against invalidation; remote admission runs
outside global locks. If Save wins the gate, its explicit immutable snapshot may
be admitted even if an edit follows. If invalidation wins, reject the old receipt
before admission. An uncertain already-dispatched admission is resolved using
the same operation identity, never by silently admitting another snapshot.

Logout immediately revokes/detaches local authority without waiting for the
network. Capture authorization only for the already-dispatched explicit action;
no post-logout worker may initiate new admission. Owned network cleanup may
outlast the HTTP wait, but permits remain held and late responses cannot revive
the display. Observe admission identity/session/workspace/revision/generation
in browser completion fences. A restart must discover only actual durable
operations; it cannot recreate a lost in-memory draft.

Use the existing source/file limits. Save's envelope may reach 16 MiB because it
contains a 10 MiB base64 file plus accepted source/bundle; apply strict depth,
field, byte and five-second body limits before expensive decoding. Bound Save
to two global/one per-session active requests with no queue, 60 seconds work
deadline and 70-second browser wait. Provider suboperations consume the same
deadline. Retain cleanup ownership and explicit pending status for uncertain work.

## Backend-origin gate, without ordinary service-role access

Owner RLS/user JWT alone does not prove FastAPI validated a receipt: the owner
could otherwise call the admission RPC or allowed table writes directly. Close
that route with an additional **server-only 256-bit random capability**:

- Generate it after plan approval into an exclusively created, ignored server
  file with restrictive Windows access. Output only its key ID and SHA-256
  verifier. Keep the raw value out of command arguments, .env output, Git, logs,
  errors and browser responses. Setup never overwrites an existing key.
- Administration installs only the verifier hash in a protected configuration
  table; no raw shared secret is needed in the database. A read-only invoker
  helper checks `request.headers` against an active verifier. Hash visibility
  does not reveal a random 256-bit preimage. Missing/wrong/inactive keys fail closed.
- Fresh request-scoped repository/Storage clients use the validated user's JWT
  and publishable API key, plus this backend-owned header. Never forward a
  browser-supplied copy of the header. It is additional origin authorization,
  not an owner credential and not a service key that bypasses RLS.
- Require the gate in every mutating RPC and corresponding INSERT/UPDATE/DELETE
  policy, including Storage. Audit permissive-policy OR semantics so no owner-only
  alternate path bypasses it; UPDATE must protect old and new owner/lifecycle.
  Never expose a function that lets a client install trusted request context.
- Keep versioned business mutations SECURITY INVOKER, explicit `auth.uid()`
  ownership, fixed search paths, row locks and database constraints. A correct
  backend key with a foreign owner must still fail.
- Recovery uses current backend configuration plus fresh same-owner authentication;
  replacing/retiring a gate key does not revoke already-admitted operation identity.

This is an implementation detail consistent with adopted user-token/RLS rules;
record it in an architecture implementation note after approval. No privileged
ordinary-operation key or pgsodium extension is proposed. The latter is available
but officially pending deprecation and not recommended for new use.

## Private files, verification and cleanup

Create one private `studybuddy-sources` bucket after explicit hosted approval
(or in the isolated local stack first). Limit original uploads to 10 MiB and
the accepted text/PDF media types. Paths and policies require registered operation
and matching owner/document/generation; arbitrary owner-folder uploads are insufficient.

User-facing download/list policies require the exact current ready object,
not merely an owner folder or Storage owner_id. No pending/deleting/superseded
bytes or reusable signed URLs are delivered. Any future served file goes through
the FastAPI owner/ready proxy.

The backend-origin gate permits a narrowly scoped **internal verification read**
of a registered pending object, using current user credentials and an additional
backend-selected verification operation marker. Its bytes are streamed only into
the bounded hash check and never returned to the user. This refines the pending
read prohibition for internal reconciliation while retaining end-user denial;
document and test this distinction explicitly. Operation-aware Storage helpers
separate authenticated info/download/list/delete policy requirements. Do not add
broad owner SELECT just to make verification/DELETE work.

Unknown upload outcomes remain durably marked. Prove write quiescence or reconcile
provider-confirmed immutable object state before accepting completion/cleanup;
a timeout or a single absent lookup is not such proof. If the provider cannot
establish the required state, remain pending/cleanup-only and report the gate
open. Test delayed upload completion, cancellation, superseded-file cleanup and
expired admission before accepting real files. This milestone uses synthetic
fixtures first; it does not override the existing backup/retention/hosting gates.

Implement the upload fence at database finalization: the operation-aware Storage
write-policy helper checks and locks the registered operation row for the short
Storage transaction. Cancellation/expiry takes the conflicting operation lock,
disables upload finalization and commits before external deletion. Finalization
that wins first must finish before that fence; a later finalization is denied.
Never hold an application SQL transaction open around a Storage network call.
Use immutable keys/no UPDATE to keep a verified matching object from being
replaced by a delayed attempt. Validate the actual Storage provider's order of
byte upload, metadata commit and failure cleanup with delayed-completion tests;
the database fence alone is not proof of physical-blob deletion. Keep unknown
attempt/object records until that provider verification succeeds.

## Seven-day recovery and expiry

Pending discovery/retry requires a freshly validated same owner. Load the stored
immutable snapshot instead of accepting replacement source/results from the
client. Resupplied original file bytes must match the admitted size/hash. Retry
uses the same operation ID/digest and rechecks revision/lifecycle at commit.
Unknown/foreign operations never create staging. Completed replay returns
recorded IDs/status without requiring the old receipt or reusing an old session.

At seven days, atomically cancel upload/commit and erase staged private source /
bundle/settings; preserve only identifiers/digests/object-recovery metadata
needed for cleanup. Explicit retry and a maintenance CLI perform stale-operation
expiry/cleanup. No paid cron/Edge Function is required. Never remove recovery
records while an upload may still complete. Tombstones/outcomes retain the
architecture's seven-day minimum; deletion IDs are not reusable.

## Verification and permission sequence

Plan approval starts **local implementation and local tests**. Install/pin the
CLI using its current help, create migration names with `supabase migration new`,
and prepare an isolated Docker Supabase stack. Docker startup/tool setup is a
local reversible action; failure is reported, not hidden by passing mocks.

Run real local SQL/RLS/Storage tests with two fixture owners, plus injected
repository/network failures and browser scenarios. Explicitly test direct RPC /
REST/table/Storage mutations with owner JWT but no gate, wrong/retired gate,
foreign owner with correct gate, safe configured success, operation-specific
pending reads/deletion, immutable snapshots and lost responses. Storage must
actually propagate the selected header into SQL policy evaluation; upstream
code/docs are evidence for the design, not acceptance of this project's instance.

Only after implementation, review and passing local checks, show the exact
migration, grants/policies, bucket restrictions and nonsecret verifier to the
student for **final hosted approval**. Do not change the existing Free/Paris
project before that. Hosted synthetic tests may then reuse already-existing
authorized test accounts if needed; no signup/email/password mutation or new
model inference. Validate advisors and two-owner isolation, rollback/retry and
registered test-data cleanup. State precisely any hosted gates still unexecuted.

## Official sources checked, 15 November 2026

- [Supabase changelog](https://supabase.com/changelog.md): CLI v3 changes defaults/confirmation; inspect installed help and pin tooling. [CLI v3 change](https://supabase.com/changelog/supabase-cli-v3).
- [API grants/RLS/request checks](https://supabase.com/docs/guides/api/securing-your-api): additional request-key checks complement owner RLS; pre-request hooks alone do not cover Storage, so enforce checks in applicable policies.
- [Database functions](https://supabase.com/docs/guides/database/functions): invoker versus definer, fixed search paths and explicit execute revocation/grants.
- [Storage private buckets](https://supabase.com/docs/guides/storage/buckets/fundamentals), [access policies](https://supabase.com/docs/guides/storage/security/access-control) and [operation helpers](https://supabase.com/docs/guides/storage/schema/helper-functions): distinguish metadata/list/download/delete policies.
- [Storage database request context](https://github.com/supabase/storage/blob/master/src/http/plugins/db.ts): upstream forwards request headers and operation into its database context; verify against the actual local/hosted target before relying on it.
- [pgsodium deprecation](https://supabase.com/docs/guides/database/extensions/pgsodium): do not add this extension for the new gate. Existing pgcrypto provides the needed verifier hashing.

These sources support the design; none proves that unimplemented policies,
provider reconciliation or local/hosted integration already works.
