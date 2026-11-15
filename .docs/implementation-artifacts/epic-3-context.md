# Epic 3 Context: Keep and resume your study material

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Let students explicitly save source/results, reopen them privately across visits/devices, resume acknowledged practice progress and delete saved material. Preserve consistency and ownership through concurrency, failures and restarts.

## Stories

- Story 3.1: Save a consistent private snapshot
- Story 3.2: Open your private document library
- Story 3.3: Synchronize practice progress across devices
- Story 3.4: Delete saved material completely

## Requirements & Constraints

- Only explicit Save persists source/settings/results; changes require Save again. New session clears only the workspace.
- First Save captures independent current valid card/quiz positions; absent exercise sections have no position. Replacement Save atomically replaces the generation and resets positions. Open restores stored content and acknowledged positions with answers hidden, without AI calls.
- Library lists only owner-ready items; pending/deleting recovery is separately discoverable. Restart requires login again but retains saved data/progress.
- Enforce ownership for every API, database and file operation, including direct identifier substitution. Keep private content, credentials and tokens out of Git/logs/static serving/shared caches; private responses use no-store.
- Verify two-account isolation, restart, conflicts, lost replies and lifecycle recovery. Prove upload reconciliation/stale-operation cleanup and document backup/deletion retention before real files. Keep credential-free demo separate.

## Technical Decisions

- Use same-origin FastAPI/plain HTML/CSS/JavaScript with Supabase Auth/Postgres/private Storage. Derive owners from validated sessions; use request-scoped user-token clients and owner RLS, never ordinary-operation service keys. Cookie mutations require CSRF/same-origin checks.
- Preserve schema-versioned canonical source/settings/LearningBundle, stable source/item IDs and physical PDF references. Constrain owner/document/generation consistency across document/content/bundle/progress. Documents carry lifecycle/revision; progress carries independent item IDs/revision. Use UUIDs, UTC, camelCase API fields and snake_case database mapping.
- New admission requires the current 30-minute receipt binding owner/session/workspace revision, generation/receipt IDs and deterministic UTF-8 snapshot/file hashes. Validate schema, hashes and bounded registry authority, not signature alone. Generation/invalidation/admission share a workspace mutex. Edits/reset invalidate authority; uncertainty blocks Save until retry/reload. Receipt registries contain no content.
- Explicit Save admits an immutable owner operation: accepted snapshot/digest, expected revision, file digest/size and pre-registered unique object key. Matching retries resume; changed payload fails. Upload privately, then transactionally commit source/bundle/progress and ready state. Replacement paths include operation/generation IDs; retain old file until commit and track cleanup durably.
- Same-owner reauthentication permits explicit exact admitted-Save recovery within seven days despite receipt/session expiry. Recheck ownership/lifecycle/revision and resupplied file bytes. Unknown/foreign/never-admitted operations cannot recover. Expiry cancels commit and erases staging; retained metadata permits cleanup only.
- Use versioned authenticated SECURITY INVOKER RPCs with RLS, explicit ownership, fixed search path, no anonymous execution, row locks and compare-and-swap revisions for multi-row mutations. Separate REST inserts cannot provide the required transaction. Completed identical operation replay returns recorded status/IDs before old receipt/revision checks, never mutates again; content reads still check current ownership/lifecycle. Retain content-free outcomes/tombstones seven days and object recovery records until cleanup completes; retries never recreate deleted IDs.
- Coordinate database/file work through pending/ready/deleting states. Deletion takes the document/application file-IO lock and database row lock, blocks reads/progress/uploads/commits, cancels pending saves and enumerates current/provisional/superseded objects. Keep durable records for uncertain uploads until writes quiesce and every object/row is removed; report success only then. Failed cleanup/deletion remains visible and retryable.
- Proxy downloads through FastAPI with owner/ready checks and user-scoped credentials; no reusable signed URLs. Storage also rejects pending/deleting/superseded reads.
- Autosync only saved generations. Serialize/coalesce browser progress writes containing both item IDs, expected generation/revision and mutation ID. Atomic RPC locks the document and validates owner, ready lifecycle, membership and revision; replacement/deletion uses the same lock. Same-ID/same-payload replay returns its original outcome; changed payload fails. Retry uncertain transport once with the same ID, then require explicit retry/refetch. Conflict blocks writes until fresh progress is fetched; never silently rebase stale positions. Ignore late/out-of-order responses after owner/document/generation/reset changes.

## UX & Interaction Patterns

- Secondary “Lagre” shows pending state, prevents duplicates, preserves workspace on failure and succeeds only at ready. Stale replacement offers Reload or Save as new.
- “Mine dokumenter” has loading/empty/error/ready states, title/date/positions, Open/Delete and Back. Empty state explains Save. Pending saves offer exact retry, same-file resupply or cleanup after expiry.
- Inline deletion confirmation names the document and associated learning material/progress. Cancel changes nothing; confirmed deletion clears its active view. Deleting failures remain visible with retry.
- Show pending/saved/failed sync. Conflict says “Fremdriften er endret på en annen enhet” and requires “Hent siste fremdrift”; fetching restores positions with hidden answers. Fetch failure retains the conflict. Tab changes preserve current reveal state.
- Preserve Norwegian UI, light surfaces, blue accent, system fonts and existing readable sizes. Use persistent labels, visible keyboard focus, polite status, safe text rendering and narrow-window/200% reflow. Logout/session failure clears private UI and offers login again.

## Cross-Story Dependencies

Epic 2 supplies authentication, source/bundle contracts and receipts. Stories run 3.1 → 3.2 → 3.3 → 3.4; introduce entities with their feature. Save/progress/deletion share lifecycle/concurrency rules. Epic 4 verifies hosted multi-device behavior and acceptance; deployment requires its separate milestone authorization.
