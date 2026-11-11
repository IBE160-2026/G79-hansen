# Architecture input reconciliation

2026-11-11. Finalized reconciliation against the revised PRD/addendum, DESIGN/EXPERIENCE, architecture decision log and student explanation. The user delegated the remaining technical decisions. Independent rubric/source recheck closed its findings; see reviews/review-final-rubric.md. Final status means planning readiness, not completed runtime acceptance.

## Captured decisions

| Input decision | Architecture coverage |
| --- | --- |
| Python/FastAPI with plain HTML/CSS/JavaScript | AD-1 and structural seed. |
| Supabase Auth/Postgres/private Storage | AD-2, AD-8, AD-9 and data seed. |
| Email/password signup/login/recovery/logout | AD-2/3; isolated PKCE attempts, restricted recovery session, secure backend cookie and expiry rules. |
| One pasted/text-file/PDF source, optional subject, Norwegian/short defaults | AD-4, capability map and inherited UX; settings captured in source/bundle identity. |
| One action makes summary/concepts/flashcards/quiz; hidden answers; navigation has no new generation | AD-5/7 and approved UX reference. |
| Original physical PDF pages, partial/unreadable PDF notices, no OCR/table/figure interpretation | AD-4 and conventions. |
| 40 PDF pages and 30,000 characters, no silent truncation | AD-4, with adopted normalization/counting convention. |
| Source-adaptive counts and insufficient-material explanations | AD-5 contract and PRD quality requirement inheritance. |
| Input/settings preserved on generation failure; Try again | AD-5 and conventions. |
| Explicit Save, never auto-save source/results; New session preserves saved documents | AD-6/7: signed generation receipts, consistent revisioned snapshots and idempotent operation outcomes. |
| My documents, title/date/progress, Open and confirmed Delete | AD-6/8 and library convention. |
| Resume independent positions on another visit/device | AD-7: automatic independent progress, hidden reopen, revisioned conflict/refetch and bounded idempotent retry. First Save captures valid current positions; replacement Save resets. |
| Saved document/content deletion, no other-owner access | AD-2/8, with failed-operation recovery. |
| Fixed-data local demo without credentials plus hosted live access | AD-5/9. No cloud resource has been created by architecture planning. |
| Three documents, five concepts selected before generation, source/reference checks and at least four concepts | AD-5 explicitly retains the PRD evaluation; the architecture does not claim these checks have run. |
| Compact material panel, whole-panel Vis/rediger collapse, tabs, discreet demo label, primary/secondary action copy | Kept by source UX ownership and companion; not duplicated as technical pixel rules. |
| Reflection evidence and understandable student/sensor explanation | architecture-explained.md and research-notes.md complement the technical spine. |

## No silent expansion

CV processing, collaboration/sharing, advanced library search/folders, OCR, marking/scoring, mobile native apps, vectors and extra AI agents are not introduced. A single same-origin service and provider adapters do not require a separate frontend project.

## Bounded milestone gates

pypdf adoption and bounded extraction wait for the agreed PDF experiment. Model/provider/API/budget/data handling wait for live integration. Hosting/region/plan/email/backup configuration wait for provisioning/deployment or real private data. These have explicit owners and revisit points in the spine and do not block the key-free demo.

Session security/expiry/recovery, signed generation-to-save handoff, progress conflict/retry, replacement-save semantics and file/database lifecycle are adopted shared contracts. PRD/UX are reconciled as final planning inputs. Security/RLS, Storage write-quiescence, multi-device concurrency, browser/accessibility and live generation quality still require real implementation acceptance tests.

Final checks: mechanical lint 0 findings, 22 relative Markdown links resolve across seven current planning documents, and git diff --check passes. Independent rubric, technology and adversarial reviews plus editorial structure/prose all have documented resolution follow-ups. No remaining document-level blocker from these checks; no runtime proof is implied.
