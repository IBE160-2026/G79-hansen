# Story 2.5 generation protocol

This is the implemented, reviewed and verified technical contract.
API readiness and the approved five model gates were resolved on 15 November
2026; generation, workspace authority, source proofs, receipts, budget controls
and private practice UI now exist. The four authorized synthetic live smoke
calls have been executed; that allowance is exhausted. See
[generation acceptance](generation-acceptance.md) for the original measurements
and separate Story 2.6/platform gates. Review fixes were verified using synthetic transports only.

Historical planning context: this protocol began as an implementation proposal
before API readiness. Statements in the original planning record that nothing
was implemented described that earlier state and are superseded by this status.


## Source acceptance and command ordering

Retain existing source JSON/base64 intake and limits. Add workspace ID, source revision and monotonic command sequence to its strict envelope; update its lexical member bound deliberately. A browser page owns a random workspace ID; at most eight workspaces are admitted per ordinary session. A record contains identifiers, timestamps, hashes and ordering metadata only. Capacity refusal must not evict authority still needed to reject delayed requests. Lifetime is bounded by its owning session; prune ended-session entries/locks/tasks without retaining source content.

Every state-changing workspace operation has a strictly increasing command sequence within that workspace and an immutable command digest. Under the shared workspace mutex, exact retries acknowledge the same known command without repeating inference; older commands or changed same-sequence payloads fail. Preserve a high-water mark even when clearing a source/result. Never recreate a tombstoned workspace from a late command. A lost generation response is not implicitly replayed or regenerated; explicit retry is a newer generation command. Content-free high-water metadata may remain until session end.

For extraction, register command/version before parser awaits and revoke prior generation authority. After extraction, publish only if command, revision and session still match. Issue a signed source acceptance proof over canonical source, settings, source kind, coverage/warnings, original file SHA-256 where applicable, owner/session/workspace identity, revision and expiry (30 minutes or earlier session end). The browser keeps source/proof/file only in page memory. Generation verifies the resubmitted canonical source/settings/coverage against proof and current authority; altered text, location, title, identity, coverage or settings fails before inference. Expired proof requires fresh extraction while retaining the draft.

Source/settings edits and reset synchronously remove browser result/receipt, advance command/revision and send invalidation. Register invalidation without awaiting an in-flight model/parser. Server acknowledges only after advancing/revoking authority. Coalesce unsent edits using the highest sequence, serialize acknowledgements and block subsequent generation/future Save on failed or uncertain invalidation until retry succeeds. A high-water comparison also protects against reordered server arrival. An accepted source proof may be reused across generation attempts at the same source revision; a settings change requires a fresh proof.

## Generation and receipt authority

Authenticate ordinary access; verify exact Origin, CSRF and X-Session-View before bounded body work. Source proof is supplementary, never authentication. Generation command admission revokes earlier generation/receipt authority before dispatch. Capture a version token, release locks before external awaits, and publish only after complete validation plus an atomic current-session/current-command check. Lock ordering between auth registry and workspace registry must be fixed; do not hold either lock during network calls. Generation, invalidation and future Save admission share this publication/admission mutex.

Provider input contains untrusted source units with compact keys such as `u1`, chosen language/detail and optional subject context. These keys map one-to-one to canonical SourceUnit IDs server-side; provider supplies keys, never physical locations or display labels. Delimit source/subject as data, forbid following embedded instructions, prohibit external facts and tools, and request fewer items or per-part insufficiency when evidence is absent. A source with injection text is a test case, not an instruction to the app.

Provider output contains only bounded section content, reference keys and insufficiency. Server generates unique item/generation IDs, maps keys to canonical unit IDs, resolves Norwegian UI reference labels consistently with the existing contract and validates LearningBundle. Selected output language applies to all generated prose, including warnings/insufficiency; source-reference UI metadata remains Norwegian. Server-owned extraction warnings remain explicit. Unknown keys, wrong types, blank required prose, output truncation/refusal or schema violation rejects the entire result. Structural validation cannot prove factual support; Story 2.6 measures that separately.

Issue a 30-minute signed generation receipt with schema version, owner/session/workspace/revision, command/generation/receipt IDs, issue/expiry times and canonical source/settings/bundle/file hashes. Use a separate purpose tag for source proofs versus generation receipts, SHA-256 and HMAC-SHA-256 with a process-only cryptographic random secret. Canonical JSON is schema-versioned UTF-8, sorted keys, compact separators, no NaN, `ensure_ascii:false`; preserve exact validated strings and array order. Define hash projections that exclude receipt/proof transport fields and prevent circular hashes. Check signatures in constant time.

Expose internal validation for future Save: signature, unexpired receipt, same owner/session, live authoritative workspace/revision/command/receipt, exact hashes. Do not implement Save or a durable unsaved snapshot. A properly signed superseded receipt is invalid immediately after ordered invalidation/new generation, before signature expiry. Logout/rotation/expiry/denial remove authority; restart loses session and signing secret. Test this validator directly now so Story 3.1 has a concrete enforceable boundary.

## Resource and output bounds

- Keep 30,000 canonical code points, 40 physical PDF pages and 10 MiB original file limits. Preserve the existing five-second upload and contained-PDF budgets. Generation does not upload a file to the model.
- Strict generation HTTP body: 2 MiB, five-second streamed read; constrain depth, field/array counts and string sizes before expensive object construction. Current sources can contain up to 10,000 short paragraphs; compact transport must cover that edge without silently truncating accepted source text or dropping units.
- Provider request: at most 256 KiB serialized UTF-8 JSON, including prompt/schema; no tools, cache breakpoints or history. Compact key/text arrays leave room for worst-case Unicode/unit counts. Conservative 4,096-token framing allowance; prove the envelope remains below the model's lower-price input threshold. Reject wholly if a resource bound is exceeded.
- One model request per session, two globally, no queue or automatic retries. A request ID prevents double dispatch. Invalidation uses a separate cheap admission path so model saturation cannot block revocation. Reserve budget atomically and durably before any network write; hold permits until actual transport cleanup, including cancellation.
- Budget reservation/check/usage filesystem work runs on two bounded dedicated workers without a queue. Cancellation retains ownership until the actual worker ends; event-loop revocation/deadline responses remain independent. Recheck current session/source/workspace command and deadline after reservation before dispatch.
- Generation API deadline: 60 seconds total after authentication/admission, including body/preflight/provider/validation. The HTTP waiter expires independently of cancellation-resistant cleanup; admission remains held until the owned work actually ends, and expired/cancelled work cannot publish. Check the deadline/cancellation before reservation and again immediately before dispatch; connect at most five seconds within that deadline. Browser waits at most 70 seconds for generation after extraction. Extraction is a separately bounded phase, not part of a misleading 60-second whole-click promise. Cancelling HTTP does not guarantee upstream billing stops.
- Provider output: 8,000 tokens including any reasoning, 256 KiB streamed response envelope; final private API response including source/bundle at most 2 MiB. Byte ceilings apply to actual/decompressed bytes and malicious/chunked responses. No partial UI publication.
- Content maxima: 3 short or 6 detailed summary items, 8 concepts, 8 flashcards and 8 quiz questions. Adapt counts downward; no required minimum beyond per-part insufficiency. At most 3 unique references per item; summary item 1,000 characters, concept term 160/explanation 800, practice question 500/answer 800, each insufficiency 500, at most 8 warnings of 500 characters in total. The provider schema receives the remaining warning allowance after server-owned extraction notices. Model completion hitting token limit fails instead of being presented as a complete bundle.
- Local ignored budget ledger stores only amounts/counters/config version. A monotonic content-free `.blocked` sidecar records excessive reported usage independently of ledger-lock contention and denies subsequent instances/restarts without changing reservation counters. Explicit initialization after approval; exclusive single-process update, durable reservation before dispatch and no automatic reset/refund. Missing/corrupt ledger refuses live generation. No keys, source hashes, identities, receipts or generated content in that durable ledger.

## UI and verification sequence

Keep optional “Kontroller materiale” and add primary “Lag læringsmateriale”. The primary action extracts if the accepted preview is not current, then performs one generation request. Retain all draft controls/file objects during technical failure. Reuse current workspace auth observation and sequence fencing; never load demo bootstrap on the private page. After success publish all parts atomically, select summary, reset independent positions/reveals and collapse the whole material region. “Vis/rediger” preserves current results until an actual edit invalidates them. Insufficient sections keep their tabs and show explanations without invented practice items.

On edit/reset/new generation immediately clear prior results/receipt; new generation revokes server authority before inference. Ignore cancellation-resistant late success after edits/reset/logout/expiry/relogin/pagehide, using both browser sequence and server command/session fences. Preserve auth's existing logout retry and non-touching passive status behavior. No browser local/session storage or private console diagnostics.

The implementation was verified with injected synthetic model/identity adapters before live checks; review corrections were verified with those adapters. Coverage includes schema/refusals, unknown refs, file preservation, selected language/detail, source proof and receipt tampering, cross-session access, out-of-order extraction/invalidation/generation, future Save admission races, late revoked success, response/body limits, disconnect/permit cleanup and budget restart/corruption/concurrent reservations. The inherited 306-test/one-skip and 19/33/11 browser evidence remains historical. Final independent parent verification passed 422 tests/one inherited skip and 28/33/11 browser scenarios after BMAD review; see the acceptance record for exact results and remaining gates.

All four explicitly approved live smoke calls have been executed on self-authored
sources (nb/short, en/detailed, insufficient evidence and PDF physical-page gaps).
The content-free usage/latency/reference observations in the acceptance record
remain historical evidence; they are not rerun during review corrections. No
further automated inference is authorized under that four-call allowance.
Full known-source evaluation across three documents belongs to Story 2.6; no
general fidelity or production-platform acceptance follows from smoke checks.
