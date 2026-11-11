# Final architecture rubric and source reconciliation — 2026-11-11

Verdict at initial review: **CONCERNS**, two medium findings to close before final handoff. No critical or high finding in the reviewed invariant/source boundary. This review evaluates planning documents, not implemented security or browser behavior.

Follow-up: the rewritten `addendum.md` now summarizes the adopted architecture, links AD-3/AD-7 and reserves only bounded PDF/provider/hosting/configuration milestone gates. The linked-handoff finding is **closed**. Initial Save remains pending the author's announced AD-6/PRD/UX clarification; the review will close that finding after the text is present.

Final narrow recheck: **PASS — both findings closed at document level.** AD-6 now fixes first Save capturing the current validated independent item IDs, no position for absent/insufficient sections, and replacement Save resetting to the new generation's initial available items. The PRD explicit-save acceptance check exercises practice before first Save and reopening both positions; EXPERIENCE states the same first-Save rule. The updated addendum remains aligned. No remaining rubric/source-reconciliation finding from this review. Runtime acceptance remains pending implementation.

## Scope

Read the current architecture spine and append-only memlog, PRD, DESIGN and EXPERIENCE. Compared their required inputs, combined generation, source grounding, limits, explicit save, private ownership, authentication/recovery, saved progress, cross-device conflict behavior, demo independence and acceptance obligations. Read the PRD-linked architecture handoff to verify source links do not reintroduce open decisions.

## Findings

### Medium — first Save does not fix which practice positions are stored

AD-6 fixes replacement Save resetting progress; AD-7 fixes automatic writes only after a generation is already saved. Neither fixes initial Save after the student has already moved through an unsaved generation. One builder can initialize saved progress at the first card/question while another captures the current positions. Both can obey the existing words, yet reopening after initial Save differs and can discard practice progress.

Close by explicitly specifying initial Save captures the current independent positions for that generation (validated against its item IDs), while replacement-generation Save resets to initial positions. Add a corresponding PRD/UX acceptance example: advance in unsaved work, Save, reopen, verify the chosen positions with hidden answers. Define empty-part positions as absent rather than a fake first item.

### Medium — linked architecture handoff still reopens settled choices

The PRD says implementation details are collected in `addendum.md`. That handoff still introduces its table as choices that "remain open", asks to decide account/library UX, progress-write timing and revealed-answer handling, and lists token/cookie/session details as unresolved. These conflict with the adopted AD-3/AD-6/AD-7 decisions and revised UX, so a story writer following the PRD's link can derive a different build contract.

Close by updating that linked handoff to summarize the adopted contract and reserve only the bounded PDF/provider/hosting milestone gates. Keep historical reports explicitly historical.

## Rubric result

- **Paradigm and boundaries:** pass. Same-origin layered FastAPI application; browser owns presentation, services own mutation, adapters isolate external systems; one canonical source/bundle boundary.
- **Stable decision identity:** pass. AD-1 through AD-9 retain identity and each states Binds/Prevents/Rule.
- **Private ownership and session boundaries:** pass at contract level. Server-derived owner, user-scoped credentials, database/Storage RLS, backend memory sessions, restricted recovery and no-store responses are enforceable rules. Runtime evidence remains required.
- **State mutation consistency:** pass apart from initial Save ambiguity above. Atomic revisioned operations, idempotent progress retries and explicit conflict/refetch behavior prevent silent stale writes. Save/delete operation states distinguish partial completion.
- **Capability coverage:** FR-1–FR-12 and NFR-1–NFR-5 land in the architecture map and remain acceptance obligations. PDF physical-page references, incomplete sources, no hidden tab/reopen AI calls, no arbitrary-input demo generation, and three-document live quality evaluation are retained.
- **Deferred decisions:** bounded appropriately for a local demo. PDF experiment gates adapter adoption; model/provider/budget gates live generation; hosting/region/email/backup decisions gate provisioning and real data. They must remain explicit future story criteria, not be counted as delivered.
- **Source alignment:** PRD and current EXPERIENCE agree with the adopted cross-device/restart/save/reveal decisions. DESIGN keeps the approved visual baseline and clearly states browser/accessibility validation remains pending. Linked addendum needs the correction above.
- **Implementation honesty:** pass. No planning artifact claims deployed authentication, permanent storage, extracted PDFs or live AI based on the fixture prototype. Existing report statuses/old memlog entries are historical and should not supersede the finalization record.

## Minor observations

The final frontmatter/status changes and a new memlog finalization event are expected after this gate, not evidence of a missing feature. Keep mobile/narrow-screen and 200% zoom checks explicit in implementation stories because cross-device access is part of the live requirement. No additional visual redesign is needed.
