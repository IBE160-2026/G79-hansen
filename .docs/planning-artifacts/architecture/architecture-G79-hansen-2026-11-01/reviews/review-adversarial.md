# Adversarial architecture review — AI Study Buddy

Reviewed: 2026-11-10. Scope: the proposed architecture contract, not implementation. Proposed decisions may remain proposals, but the interfaces they describe must prevent incompatible implementations before stories are built. No application code or external resources were changed.

## Verdict

The draft has a coherent service split and acknowledges the real persistence/authentication trade-offs. Five contract gaps were identified; the parent resolved the first during this review with a signed generation receipt. Tighten the remaining authentication seam before treating auth stories as implementation-ready; the three medium findings can be resolved as short shared operation rules rather than a larger architecture.

## High — Save has no authoritative connection to the validated generation

**Location:** AD-4, AD-5, AD-6; source/result contracts.

**Two conforming units:** The generation service validates source-unit references and returns a LearningBundle, then discards its inputs to avoid persisting unsaved work. The save service accepts the source/settings/bundle supplied by the browser and validates the schema before storing them under the authenticated owner. Both follow the written rules, yet the browser may change the bundle, citations or source after generation and save an apparently validated generation against unrelated material. A plain digest supplied by the client would not solve this.

**Tightening:** Define one authoritative unsaved-generation contract. For example, keep a bounded, session/owner-bound generation draft in server memory, return only its opaque draft ID with the display bundle, and make Save consume that draft rather than trusting browser-submitted source/results. Bind the upload/source snapshot, normalized source units, settings, validated LearningBundle and generation ID together. Define expiry/restart recovery: expired drafts require regeneration before saving; no silent reacceptance of client-authored results. This is temporary memory, not automatic durable saving. A server-authenticated envelope is another possible design if the complete original-file binding is specified.

**Resolved during review:** AD-6 now proposes a short-lived server-signed receipt binding the authenticated owner, generation ID, canonical source/settings/bundle hashes and original-file digest. Save resubmits and validates all bound values; expiry requires regeneration. This is a coherent alternative to a server-memory draft and closes the identified authenticity gap. Define canonical serialization in the shared contract during implementation so receipt verification uses the same hash input representation.

## High — Email confirmation/recovery flow is unspecified across the browser/backend boundary

**Location:** AD-2, AD-3; confirmation/recovery redirects.

**Two conforming units:** The Auth adapter selects a browser-oriented implicit confirmation/recovery flow that returns provider tokens in a URL fragment. The FastAPI callback implements server-side session establishment and expects an authorization code from the redirect. Both satisfy “Supabase Auth,” allowlisted redirects and browser-hidden provider credentials, but the backend cannot receive the URL fragment. Signup confirmation and password recovery cannot create the required application session.

**Tightening:** Choose a single callback contract compatible with AD-3, preferably a server-mediated code/PKCE flow if supported by the chosen client. Specify who creates/stores the verifier and state, the callback route that consumes the code, the purpose of confirmation versus recovery sessions, and how recovery authorizes only the password-update step before a normal session. Define expired/missing state/verifier behavior. Verify the concrete SDK flow in the implementation spike rather than relying on client defaults.

## Medium — Owner-only policies do not necessarily enforce lifecycle state

**Location:** AD-2, AD-8; database/object policy contract.

**Two conforming units:** The repository excludes pending/deleting documents from application queries. The RLS/Storage implementer uses only `auth.uid() = ownerId`, satisfying owner isolation. The object adapter issues a short-lived signed file URL before deletion. The document can remain readable through that URL or an owner-authorized storage request while its lifecycle says reads are blocked. The rule prohibiting cached public URLs does not specify signed URLs.

**Tightening:** Define the live file-delivery path. For example, proxy authorized private reads through FastAPI and issue no reusable download URLs in v1. Require all normal content/progress/file accesses to check parent ownership and `ready` lifecycle state, including applicable database/Storage policies. Operation-recovery paths may access non-ready records only through explicit owner-scoped recovery rules. The no-read-after-delete test must exercise the selected file path.

## Medium — Save operation ordering and restart recovery remain ambiguous

**Location:** AD-6, AD-8; idempotency and data seed.

**Two conforming units:** One service transaction writes ready records first and then stores the file. Another uploads the file first, then commits database content as ready. Each claims to coordinate through pending/ready/deleting and idempotent retries, but the first exposes a ready record without a file and the second can leave an orphan after process termination. “Clean provisional files before marking failed” cannot run if the process exits.

**Tightening:** State a minimal durable sequence: reserve a pending operation/document ID; store the private provisional file under that deterministic key; commit content/bundle/progress and transition to ready only after file success. Persist enough operation metadata to resume or clean up after restart. Define owner-scoped idempotency-key uniqueness and reject reuse with different payloads. Pending operations need an explicit resume/cleanup path, not only in-process exception handling. Specify the corresponding delete states and retry ownership.

## Medium — Content revision, progress revision and deletion concurrency need a common mutation gate

**Location:** AD-6, AD-7, AD-8; revision semantics.

**Two conforming units:** A progress service reads the saved generation and applies optimistic progress updates. A save service replaces the generation using document revision but does not atomically reset/check progress. A delete service marks deleting while a previously admitted save finishes. Each follows its own revision/state rule, yet progress may attach to an obsolete generation, a save may make a deleting document ready again, or two devices may replace each other’s content silently.

**Tightening:** Every mutation should atomically check owner, lifecycle, expected document revision and generation ID as applicable. Progress additionally checks expected progress revision. A generation replacement must change generation ID and reset progress in the same database transaction. Delete must win over any later mutation: no ready transition or progress write once deleting is committed. Specify a conflict response for stale saves as well as progress, with no implicit overwrite. File replacement must not delete the last ready version before the replacement is committed.

## Adequate invariants preserved

- One application origin and one worker/instance are explicit, so the in-memory application-session trade-off is visible.
- The browser does not receive privileged provider secrets and private files are excluded from static assets.
- Request-scoped user-token clients and owner-derived identity address the main cross-user contamination risk.
- Explicit Save remains distinct from automatic progress writes, and generation identity prevents blindly reusing indices.
- Local demo is distinct from live mode and does not silently become a fallback for failed real generation.
- Content quality evaluation is retained rather than inferred from structural validation.

## Review limits

This was an independent source-level consistency review. No backend, Supabase policy, account, PDF, model or browser behavior was executed. The findings identify architectural seams; they are not claims of vulnerabilities in implemented software, since that software does not exist yet.

## Targeted resolution verification — 2026-11-10

Rechecked only the five findings above against the amended spine. All five are resolved at draft-contract level; no prior adversarial finding remains open.

| Prior finding | Amended contract verified | Status |
| --- | --- | --- |
| Authoritative generation/save binding | AD-6 binds a server-signed, session/owner-scoped receipt to deterministic source/settings/bundle hashes and original-file digest, checks it on Save, rejects expired/mismatched values and distinguishes reopened saved revisions. | Resolved |
| Confirmation/recovery transport mismatch | AD-3 explicitly selects backend-managed PKCE code exchange, pre-auth verifier/state/browser/purpose/expiry binding and a restricted recovery session, with failure/restart behavior. | Resolved |
| Lifecycle state and file retrieval | AD-8 specifies a FastAPI private-file proxy that rechecks ready state, user-scoped Storage credentials, no reusable signed download URLs, lifecycle-aware Storage read rules and owner-only cleanup paths. | Resolved |
| Save ordering and crash recovery | AD-8 durably records a pending operation before upload, uses unique provisional object keys, then commits database state through one authenticated RPC. Old files survive until replacement commit; cleanup failures remain durable and owner-retryable. | Resolved |
| Revision/deletion concurrency | AD-6 rejects stale document revisions; AD-7 atomically checks owner, ready state, generation and progress revision and locks the same document row for progress, generation replacement and deletion. AD-8 RPCs implement row locks and compare-and-swap. | Resolved |

This verification does not claim implementation correctness or SDK/policy compatibility tests. The proposed contracts still require user review, concrete schemas and negative/concurrency tests when implemented. No broad re-review was performed.
