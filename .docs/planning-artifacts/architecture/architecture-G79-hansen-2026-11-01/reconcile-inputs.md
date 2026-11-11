# Architecture input reconciliation

2026-11-10. Reconciled the current architecture draft against PRD, latest UX amendments, architecture decision log and plain-language companion. Earlier temporary-only UX prose is explicitly superseded by the 2026-11-10 scope revision; it is not the current requirement.

## Captured decisions

| Input decision | Architecture coverage |
| --- | --- |
| Python/FastAPI with plain HTML/CSS/JavaScript | AD-1 and structural seed. |
| Supabase Auth/Postgres/private Storage | AD-2, AD-8, AD-9 and data seed. |
| Email/password signup/login/recovery/logout | AD-2/3; callback/recovery session contract needs tightening before stories. |
| One pasted/text-file/PDF source, optional subject, Norwegian/short defaults | AD-4, capability map and inherited UX; settings captured in source/bundle identity. |
| One action makes summary/concepts/flashcards/quiz; hidden answers; navigation has no new generation | AD-5/7 and approved UX reference. |
| Original physical PDF pages, partial/unreadable PDF notices, no OCR/table/figure interpretation | AD-4 and conventions. |
| 40 PDF pages and 30,000 characters, no silent truncation | AD-4, with proposed exact normalization/counting convention. |
| Source-adaptive counts and insufficient-material explanations | AD-5 contract and PRD quality requirement inheritance. |
| Input/settings preserved on generation failure; Try again | AD-5 and conventions. |
| Explicit Save, never auto-save source/results; New session preserves saved documents | AD-6/7. Generation-to-save proof/handle seam needs a concrete contract. |
| My documents, title/date/progress, Open and confirmed Delete | AD-6/8 and library convention. |
| Resume independent positions on another visit/device | AD-7, owner/document/generation-keyed progress; write timing/conflict behavior is a marked proposal. |
| Saved document/content deletion, no other-owner access | AD-2/8, with failed-operation recovery. |
| Fixed-data local demo without credentials plus hosted live access | AD-5/9. No cloud resource has been created by this draft. |
| Three documents, five concepts selected before generation, source/reference checks and at least four concepts | AD-5 explicitly retains the PRD evaluation; the architecture does not claim these checks have run. |
| Compact material panel, whole-panel Vis/rediger collapse, tabs, discreet demo label, primary/secondary action copy | Kept by source UX ownership and companion; not duplicated as technical pixel rules. |
| Reflection evidence and understandable student/sensor explanation | architecture-explained.md and research-notes.md complement the technical spine. |

## No silent expansion

CV processing, collaboration/sharing, advanced library search/folders, OCR, marking/scoring, mobile native apps, vectors and extra AI agents are not introduced. A single same-origin service and provider adapters do not require a separate frontend project.

## Proposed choices versus blockers

The user authorized a concrete draft with marked suggestions. pypdf, Render, bounded session lifetimes, progress conflict handling and hidden answers after reopen remain proposals, not falsely adopted decisions. Model selection and hosting provisioning can wait until their specified checkpoints.

Before implementation stories independently build the seams, tighten generation-to-save handoff, recovery-session exchange, replacement-save conflict semantics and ordered save lifecycle. These fixes do not need additional product discovery. PRD/UX status should remain draft until the revised auth/storage/library scope and proposed UX consequences are reconciled.

Focused recheck 2026-11-10: the four identified seam fixes are now represented in AD-3, AD-6, AD-7 and AD-8. The architecture draft is ready for user review; no source-reconciliation blocker remains from this review. PRD/UX still require planned refinalization after draft proposals are reviewed.
