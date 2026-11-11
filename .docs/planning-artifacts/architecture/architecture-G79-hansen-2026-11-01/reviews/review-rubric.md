# Architecture draft rubric review

Reviewed 2026-11-10. Scope: ARCHITECTURE-SPINE.md, plain-language companion, research notes, current PRD and latest UX additions. This is a draft with explicitly proposed decisions, not an implementation or deployment approval.

## Verdict

The draft covers the revised product scope and has a usable architecture shape. It is suitable for student review after tightening the generation-to-save and authentication-recovery seams below. These are concrete consistency fixes, not reasons to select the deferred model provider or hosting immediately. No critical finding; two high, two medium and one low finding.

## High — generation-to-save handoff is not an enforceable shared contract

Location: AD-5 through AD-6 (lines 71–85), Data seed.

The generation adapter returns a validated bundle, while explicit Save later persists a source snapshot/settings/bundle. Unsaved generation must not be persisted. The spine does not define how Save establishes that a submitted bundle, source/settings and generationId are the same server-validated generation. A generation builder could retain an ephemeral server snapshot and return a handle; a save builder could expect the complete payload in the browser and trust it. Both obey the current prose but do not interoperate, and a changed source could be saved with stale results.

Fix: choose one small boundary rule before stories: for example an owner/session-bound, expiring in-memory generation handle whose immutable snapshot the save service reads. Explicitly state expiry/restart behavior and that Save cannot replace its source/results from unverified browser fields. An authenticated signed-envelope approach is another option, but one contract must be fixed. This need not introduce durable saving before the Save action.

## High — recovery callback does not join the proposed backend session model

Location: AD-3; FR-8 and Authentication acceptance check in PRD.

The opaque application-session registry is concrete, but confirmation/recovery links are only described as configured redirects and expired-link handling. Auth and UI builders can independently choose incompatible callback routes and token/code exchange expectations. A normal login session and a valid password-recovery session are not distinguished, although PRD specifically requires recovery proof for the password-update step.

Fix: bind a callback/exchange contract and session purpose. For example the callback validates/exchanges the provider recovery code, creates a restricted recovery-purpose application session, and permits only password-update until completed. Define how invalid/expired callbacks recover and how completion clears/replaces that restricted session. Keep raw provider tokens out of frontend storage/logs as AD-3 already requires. This is a configuration/flow proposal, not a new user-facing feature.

## Medium — replacement save lacks a conflict rule matching progress writes

Location: AD-6 proposed revision behavior; AD-7; Data seed.

Progress has explicit revision conflict handling, but a replacement Save only mentions a document revision. It does not require compare-and-swap or define whether a new saved revision means replacing one document or creating another library item. Two devices can save different regenerated results while each assumes the same revision semantics; an old progress write can then target the replaced generation.

Fix: state that updating a saved document supplies expectedDocumentRevision, fails with conflict on mismatch, atomically replaces the current generation/source/results and resets progress, and rejects progress updates for superseded generation IDs. Alternatively choose save-as-new; do not leave both interpretations valid. No history browser is needed.

## Medium — save lifecycle order is ambiguous at the database/object seam

Location: AD-8 (line 99).

The first sentence says a database transaction creates records as a ready unit, but the remainder introduces pending/ready and provisional file cleanup without ordering the upload and ready transition. A repository can expose a ready document before its original file exists, while the storage builder expects pending ownership metadata before upload. Both are plausible from the current rule.

Fix: give a short ordered sequence: reserve owner/document plus operation as pending; upload private object; transactionally commit immutable content/bundle/progress and mark ready; use the same operation/idempotency key for retry/compensation. Define failure/retry state if cleanup itself fails, rather than requiring successful cleanup before any failure may be recorded.

## Low — adoption labels mix user choices with proposed mechanics

Location: AD-1, AD-2, AD-4, AD-6 and AD-7 labels.

Some blocks marked ADOPTED contain sensible but newly authored mechanics, such as request-scoped authenticated clients and server-generated source-unit identifiers. The opening says ADOPTED means user-approved, whereas only the product/stack/service choices were explicitly chosen.

Fix: use the same mixed label convention already used by AD-7, or split the factual adopted choice from proposed implementation rules. Do not ask the student to approve every low-level default; keep draft status and distinguish recommendations honestly.

## Coverage and shape checks

- FR-1–FR-7: all input forms, original references, source support and four learning outputs covered by AD-4/5 and the capability map.
- FR-8: signup/login/recovery/logout, active reset versus saved deletion and owner checks covered; recovery seam needs the high fix above.
- FR-9: one action, no model calls on navigation/open and shared demo/live contract covered.
- FR-10–FR-12: explicit Save, owner-only library, multi-device resume and deletion covered; revision/lifecycle seams need tightening.
- NFR-1–NFR-5: quality evaluation, input limits, failure/retry, secret/private-data boundaries, local key-free demo and UX checks covered.
- Operational envelope is explicit: hosted HTTPS, one worker/instance for proposed memory sessions, restart re-login, Supabase durability, configuration/migrations and deferred backups/quotas/email.
- Provider/model/API key, hosting plan/region/budget, exact SDK versions, pypdf experiment and actual browser/accessibility checks are intentionally deferred with owner and revisit condition. Those are not missing dimensions in this draft.
- Stack seed honestly distinguishes observed candidates and managed services from installed/tested dependency pins. An independent technology review should assess evidence currency; this rubric did not repeat web research.
- The plain-language companion agrees with the adopted scope and identifies the proposed progress/reveal/session/PDF/hosting choices.
- Deferred SDK details are acceptable for the draft; generation/save/recovery/revision contracts must be fixed before separate implementation stories.

## Validation limits

No application implementation, migrations, login, cloud policy or cross-device behavior was executed by this review. Existing prototype DOM checks are not backend/security acceptance. The current PRD/UX are draft after the storage/auth scope change and must be reconciled again before final planning status.

## Focused recheck after corrections — 2026-11-10

Rechecked only the prior two high and two medium findings against the revised spine. All four are cleared at the architecture-contract level:

- **Generation-to-save handoff:** AD-6 now fixes a server-signed, owner/session-bound receipt, canonical schema-versioned serialization and source/settings/bundle/file hashes. Save validates the resubmitted snapshot instead of trusting mutable client fields. Expiry and replacement-generation behavior are explicit, without durable pre-save content storage.
- **Recovery callback/session:** AD-3 now fixes backend PKCE exchange with verifier/state/browser/purpose/expiry binding. Recovery creates a restricted password-update session, consumes state and requires normal login afterward. Expired/replayed/wrong-browser callbacks cannot create a normal document-access session.
- **Replacement-save conflicts:** AD-6 requires expected document revision and atomic current-revision replacement with progress reset. AD-7 atomically gates progress by owner, ready state, current generation and progress revision under the same document lock used by replacement/deletion. Superseded writes fail without recreating rows.
- **Save lifecycle ordering:** AD-8 now orders durable pending-operation reservation, private unique-object upload and an authenticated transactional RPC committing the ready unit. Retries are idempotent; old-object cleanup happens after replacement commit, and failed cleanup remains durably discoverable/retryable rather than falsely complete.

No prior high/medium blocker remains. The low adoption-label observation is editorial and remains applicable to the mixed user-choice/mechanics blocks, but does not prevent presenting this explicitly marked draft. This focused recheck did not rerun broad review or validate implementation/provider behavior.
