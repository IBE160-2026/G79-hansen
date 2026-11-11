# Full-diff follow-up — receipt authority and admitted Save recovery

2026-11-11. Targeted author resolution of two findings forwarded by the build review. This is an inline document correction, not a new independent review or runtime test. Final planning status is retained.

## Pending Save recovery after receipt expiry or fresh login

**Resolved in AD-6 and AD-8.** AD-6 limits current-session/receipt validity to admission of a new Save. AD-8 now states: “This durable admission record—not an expired receipt or old session—authorizes recovery of this exact Save after relogin/restart.”

Only the explicit, validated Save action can create an owner-scoped durable admitted operation and its immutable accepted snapshot/digest/file identity. A fresh same-owner login may explicitly resume that operation for 7 days; changed data/file/target needs a new admission, and current revision/ownership/deleting state are rechecked. Expiry cancels commit and erases staged private snapshot; minimal object metadata remains for cleanup. Completed status replay and registered-object cleanup need current owner authentication, never an old receipt/session, and cannot create content. An unknown/never-admitted operation has no recovery authority. Generation alone remains ephemeral.

## Revocation of an old but correctly signed generation receipt

**Resolved in AD-6, “Receipt authority” and “Source/settings edits” paragraphs.** “Save admission compares the signed identity and revision with the current registry entry, not merely the signature.”

The bounded in-memory session/workspace registry holds only current revision, generation/receipt identity, expiry and hashes. It stores no private unsaved snapshots. Source/settings/reset actions invalidate server authority with an authenticated acknowledgment; the browser disables Save immediately. Starting another generation revokes independently, and only a current successful generation installs fresh identity. Per-workspace mutex ordering covers Save admission/invalidation races and rejects old response sequences. Expiry/logout/restart/eviction require regeneration for new admission. Unreported local edits cannot be inferred, but hashes reject changed payloads and observed invalidation rejects even unchanged old snapshots.

## Source reconciliation and verification

PRD adds Save admission/recovery acceptance cases for restart/relogin, receipt expiry, unknown/foreign/expired admission, changed retry data, delayed responses, lost commit replies and invalidation races. The handoff and EXPERIENCE clarify admitted recovery versus never-admitted work and server acknowledgment of invalidation. The decisions are appended to architecture/UX/PRD memlogs. Mechanical spine lint remains 0 findings and `git diff --check` passes. The affected live stories must implement and test the protocol; the fixed demo does not prove it.
