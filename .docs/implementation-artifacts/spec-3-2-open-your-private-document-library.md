---
title: Open your private document library
type: feature
created: 2026-11-17
status: done
route: dispatch
review_loop_iteration: 0
story_key: 3-2-open-your-private-document-library
baseline_commit: 8e02357a7165ec3f43451b341a0079457772aa60
context: [.docs/implementation-artifacts/epic-3-context.md]
---

<frozen-after-approval reason="user requested the agreed next story with kjør neste steg; reversible local implementation authorized, new hosted migration requires the finished review package">

## Intent

Saved work currently lacks a library. Add Norwegian **Mine dokumenter** to the existing workspace so an authenticated student can list and reopen saved learning material, resume saved positions with answers hidden, and download the original file without regeneration.

## Boundaries & Constraints

**Always:** Reuse sessions, CSRF/session-view checks, owner RLS, backend gate, ready lifecycle and Save/recovery. Keep drafts on list/back/failed open; confirm before replacing unsaved work. Fence late replies and clear private state on access end. Safe text, keyboard focus/status, mobile/200% reflow and no-store. Reopening grants no generation receipt; edits use normal extraction. Preserve PDF references.

Proxy original files through authenticated FastAPI/uncached user-JWT S3. Recheck owner/ready, bound time/10MiB and verify size/hash. Return an attachment, never Storage keys/signed URLs. Already downloaded bytes cannot be recalled.

**Never:** Add deletion/autosync, inference, accounts/emails/password changes, privileged keys, browser persistence, frameworks, costs, deploy or hosted mutation. Test the RPC migration locally; hosted application needs separate approval. Preserve unrelated inaccessible evidence files.

## I/O & Edge-Case Matrix

| Scenario | State | Behavior | Failure |
|---|---|---|---|
| List | Owner ready records | Title/date, saved card/quiz positions, Open and original-file action; stable bounded pagination | Retry preserves draft |
| Empty | No ready records | Explain explicit Save; Back returns draft | No invented entries |
| Open | Ready saved generation | Exact source/settings/all sections/independent positions; answers hidden; zero model calls | Preserve active draft |
| Replace draft | Unsaved input/results | Confirm; Cancel preserves everything | No mutation on cancel |
| New session | Open saved document | Clear only active workspace | Saved rows remain |
| Restart/device | Fresh same-owner login | List/reopen same saved snapshot | No old receipt needed |
| Isolation | Missing session, wrong owner, pending/deleting/unknown ID | Deny list/open/file as applicable | No content or file bytes |
| Races | Late list/open/download after back/edit/reset/logout/new login | Ignore obsolete result | No private-state resurrection |
| File | Current verified ready original | Bounded exact attachment via S3 | Missing/corrupt/unavailable reports failure |
| Cached read | Earlier allowed read then supersede/delete/gate removal | Fresh S3 read denied | REST download stays denied |

</frozen-after-approval>

## Code Map

- `app/{api,contracts,services}/documents.py`: bounded pipeline, Save admission, UUID-cursor DiscoverRequest and document-ID ReloadRequest.
- `app/adapters/documents.py`: existing user-JWT `sb_save_{action}_v1` RPC mapping.
- `app/adapters/storage.py`, `config.py`: working S3 signing/configuration and bounded verification.
- `supabase/migrations/20261115214610_save_consistent_private_snapshot.sql`: tables/updated_at/progress and exact reload RPC; latest migration forbids REST file reads.
- `app/static/workspace.{html,js}`, `styles.css`: savedTarget, reload restoration, session/sequence guards and study rendering.
- `tests/test_documents.py`, `documents_browser_app.py`, `browser-documents.cjs`, `save_provider_acceptance.py`: reusable synthetic ports and real local provider. Use `SAVE_TEST_WSL_DISTRO=SUREUbuntu`.

## Tasks & Acceptance

- [x] Add bounded library/file routes and invoker RPCs: owner-ready metadata (50/page, UUID keyset cursor), title/date, position ordinals/totals, hasOriginalFile; internal-only file descriptor. No content/keys in list.
- [x] CLI-create migration; no new tables/policy relaxation. Reuse reload. Authenticated-only EXECUTE, backend gate, fixed search_path. Verify actual local RLS/Storage.
- [x] Add bounded, integrity-checked S3 attachment proxy; fresh session/owner/ready checks. Preserve Save.
- [x] Add library states, pagination/back/open/download, safe draft replacement/restoration, focus and session/epoch fences. Keep pending recovery separate.
- [x] Cover matrix/API/browser/SQL and zero model calls on open/practice.
- [x] Update README, sprint, concise acceptance and notes with executed results/hosted gate.

Given previously saved material, when the owner reauthenticates and opens it, then exact learning content and saved positions return without inference; another owner receives neither metadata nor bytes.

## Implementation Notes

User prefers low context use: read relevant excerpts and keep full test output in ignored logs. Decide routine implementation details autonomously within these boundaries; do not expand the story.

Initial local handoff completed without hosted mutation or inference; see
`library-acceptance.md` for behavior, results and provider observations.
The parent then completed the requested next feature in the existing approved
test project: read-only RPC migration20261117182650, hosted25 and normal-server34.
No new service, account, price or public deployment was introduced.

## Spec Change Log

## Review Triage Log

One focused edge-case and one verification-gap layer ran; the forced-finding
blind layer was omitted to respect the student's lean-work preference. Each
reported finding was judged separately; the parent added two direct corrections.

| ID | Verdict | Route | Evidence |
|---|---|---|---|
| E1 | medium | patch | submit increments sequence but not revision; openDocument checks only revision/epoch/view, so an older conflict reload can replace and abort a newer generation. Capture/check sequence too. |
| E2 | medium | patch | render rejects acceptance.schemaVersion after invalidate has cleared the draft; current becomes false and suppresses the error. Validate version before replacing state. |
| V1 | medium | patch | Existing confirmation test generates a bundle, so it cannot detect removal of draftDirty from requestOpen. Add an ungenerated source/settings confirm-and-cancel case. |
| V2 | medium | patch | Existing failed-open test is HTTP503; no successful response carries an invalid saved position. Add invalid-position HTTP200 preservation evidence. |
| P1 | medium | patch | openDocument disables Save, but Back clears libraryBusy without saveControls; Save stays disabled until the obsolete request resolves/times out. Refresh controls when leaving. |
| P2 | low | patch | Library helper text implies practice can be resaved explicitly, while same-generation Save is disabled until later autosync work. Describe positions captured with the saved material. |

All six direct corrections/gaps are resolved. Library browser21, parent Save25
and affected-source28 passed. No re-derivation or additional review round was
needed. Earlier broad local provider observations remain documented without
attributing an unproven cause.

## Verification

Run focused Python/library browsers and real local SQL/provider tests; repeat Save browsers for shared workspace changes. Broaden only for affected shared paths. Baseline: Python51/browser25/SQL15/provider50; hosted32/normal30. No inference/hosted writes.

Executed: Python74; library browser16; Save browser25; library pgTAP23 and Save
pgTAP23; focused actual provider17; clean public/studybuddy lint and diff check.
Two broad provider failures at different stages remain unexplained historical
observations; no new broad-provider success is claimed. The initial handoff was local.

Final: library browser21, Save25, source28, hosted25 and normal-server34 passed.
Hosted migration20261117182650; UTF-8/LF SHA-256
6217a7d409f163f68f816368080af7074f9b266e5394f152c09d041b601e16b8.
Worker14736 serves local port8000. No real inference/new accounts.
