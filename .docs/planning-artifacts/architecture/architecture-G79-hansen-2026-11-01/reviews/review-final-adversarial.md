# Final adversarial architecture review — 2026-11-11

**Verdict: CONCERNS — tighten three live-session/lifecycle seams before binding the affected stories.** The local fixed-data demo is unaffected. This review examines the current architecture contract only; it does not claim the application already exhibits these faults.

## A1 — High: local logout depends on unspecified upstream failure handling

**Seam:** AD-3 says to revoke the provider session, delete the application entry and clear the cookie. It does not state which steps must happen when provider revocation times out.

**Two plausible implementations:** the Auth adapter raises on a failed upstream sign-out; the route deletes the local entry only after awaiting that adapter. The UI clears its private workspace as UX requires, yet the existing application cookie still opens protected API routes. Another route implementation deletes the application entry first and is safe. Both follow the named sequence on success, but disagree on the failure path.

**Fix:** invalidate the local application session and clear the cookie regardless of upstream sign-out outcome. Attempt local-scope provider revocation after local invalidation; do not restore an invalidated application session on failure. Keep provider access/refresh tokens inaccessible to browser code and record only a content-free revocation failure. Add an outage-on-logout acceptance case proving the old cookie is denied.

## A2 — Medium: Save/Delete idempotency is less defined than progress idempotency

**Seam:** AD-6/AD-8 require owner-scoped operation keys and resumable retries, but do not bind each key to an immutable payload or define replay after a successful commit whose response was lost. AD-7 defines those details for progress only.

**Reproduction:** Save commits revision 2, then the response is lost. Retry arrives with the same operation key after its generation receipt expired. A receipt-first API rejects it and asks for regeneration; an operation-first API replays the completed result. A third component can accept a changed snapshot under the same key and resume the wrong provisional file.

**Fix:** bind each save/delete operation key to owner, document/generation identity and immutable request digest. Reject changed-payload reuse. Authenticate first, then replay a recorded completed result for an identical request before checking receipt expiry or the original expected revision; never execute the mutation again. Check current ownership/lifecycle for any returned content. Pending operation validation still needs the receipt rules. State the tombstone/result retention window so a retry cannot recreate a deleted document after its key was forgotten.

## A3 — Medium: deleting a document must account for outstanding operation objects

**Seam:** AD-8 tracks provisional and previous-generation cleanup objects durably, but delete mentions removing the document's file and associated rows without explicitly including every outstanding operation object.

**Reproduction:** replacement A commits, leaving old-file cleanup pending; replacement B has uploaded a provisional object but not committed. Delete removes the current ready object and document/associated operation rows. The old and provisional objects remain without durable operation records, or an FK prevents deletion indefinitely. A storage adapter deleting only `document.currentObjectKey` and a repository cascading associated rows appear compatible with the ordinary delete description but violate recoverability together.

**Fix:** under the document lock, mark deleting, invalidate pending saves, and durably enumerate current, superseded-cleanup and provisional object keys. Keep operation/tombstone records until every referenced object is removed. Concurrent uploads/commits must recheck deleting state and cannot add untracked keys. Only then report complete deletion/remove content rows; retain minimal idempotency tombstone metadata as required by A2. Add delete-during-pending-replacement and cleanup-failure cases.

## Checks without findings

- Owner/document/generation checks and row locking protect progress from replacement/deletion races.
- A stale device must explicitly fetch current progress instead of rebasing an old position, avoiding silent rollback.
- Browser late-response guards, no-store private responses and hidden answers on reopen have clear owners.
- PDF experiment, provider/model/budget, hosting plans and real-data readiness have explicit milestone conditions and do not block the credential-free demo.

No request is made to choose a model, provision cloud resources, add microservices or expand the product scope.

## Narrow resolution check — 2026-11-11

**Current verdict: PASS at document level for planning; the affected live implementation remains gated by tests.** Re-read AD-3, AD-6 and AD-8 after the architecture author's fixes. This check is limited to A1–A3 and is not a fresh whole-system review.

- **A1 closed in the contract.** AD-3 now unconditionally invalidates the local session and clears the cookie before the bounded provider revocation attempt. Provider failure cannot restore access. The explicit old-cookie-during-outage test is required.
- **A2 closed in the contract.** Save/Delete operation keys now bind owner, document/generation and immutable request digest; changed-payload reuse is rejected. Identical completed outcomes replay before the original receipt/revision checks without a second mutation, and no content is replayed without current ownership/lifecycle checks. The 30-minute new/pending receipt window and 7-day content-free result/tombstone retention are explicit. Operation cleanup cannot remove still-needed file recovery records.
- **A3 closed as a safety invariant with an explicit live-file readiness gate.** Deletion now shares application/file-IO and database locks, invalidates pending saves, enumerates current/provisional/superseded object keys and retains durable records while uploads have unknown outcomes. It cannot report completion until cleanup and write quiescence/reconciliation are proven. Delayed upload completion, pending replacement and failed prior cleanup are named tests. The selected Storage adapter's ability to establish that quiescence is not demonstrated by this document; implementing and passing those tests is required before real files are accepted.

No cloud execution, SDK integration, migration policy, network-failure simulation or runtime correctness was established by this recheck. Those remain implementation evidence, not finalization claims.
