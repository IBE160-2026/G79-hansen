# AI Study Buddy — development plan

Updated 2026-11-11 after the user delegated architecture finalization, backlog, sprint planning and the first runnable demo. [Epics and stories](../../epics.md) now own task order and acceptance criteria; [sprint status](../../../implementation-artifacts/sprint-status.yaml) owns actual progress. The historical numbered task sequence is superseded by this integrated plan after the login/storage scope expansion.

## Delivery sequence

1. **Try the complete study flow locally:** Story 1.1 builds one FastAPI app serving the approved plain HTML/CSS/JavaScript workspace and a validated named-fixture demo API. No external credentials, real AI, auth or durable persistence. Story 1.2 tests PDF extraction before later own-source feature work.
2. **Study your own material privately:** email/password signup/login/recovery/logout, active-source extraction and all four real generated outputs with references and explicit failure handling. A provider/model/API/budget/data-handling decision is required before live model integration.
3. **Keep and resume your study material:** owner-only explicit Save, My documents, reopen and delete. Source/settings/results only persist on Save. Independent practice positions automatically synchronize for saved generations; reopening hides answers; stale views must fetch latest progress before writing again.
4. **Use and assess the finished app reliably:** authorized hosting/configuration, real two-account/two-device checks, reproducible setup, complete content evaluation and browser/accessibility checks. Hosting/region/cost and operations decisions precede deployment.

Each story introduces only the entities it needs. No upfront complete database, vector search, separate frontend build or agent framework. Every epic delivers usable behavior using only earlier epics. Demo functionality never counts as complete live functionality.

## Early PDF experiment

After Story 1.1, use a synthetic PDF with readable pages 1 and 3, blank page 2 and image-only page 4. Preserve physical page positions, list unreadable pages and compare extracted text against the document. Exercise malformed/encrypted/oversized files, byte/time/memory limits and 40/41-page plus 30,000/30,001-character boundaries. Record the tested library/version and limitations before adoption. Do not add OCR/table/figure interpretation. A failed experiment requires investigation before PDF feature work proceeds.

## Quality and scope

Before real generation, select five central concepts and supporting locations per document for three test documents. Include text and PDF. All sampled content must be source-supported, references correct, and at least four of five concepts covered per document; separately record unsupported content, wrong references and missing concepts. Source insufficiency must explain missing parts without invented material.

Generation failure retains every input/setting with explicit retry. One Generate action supplies all four parts. Tab changes, answer reveal, navigation and saved reopen never call AI. New session clears the active workspace, not saved documents. Limits remain 40 physical PDF pages and 30,000 Unicode code points, with rejection rather than truncation.

Live identity/storage uses Supabase Auth/Postgres/private Storage through owner-scoped FastAPI access and RLS. One-process in-memory login state means server restart requires re-login, without deleting saved records. Operation/revision safeguards and cleanup tests are defined in the architecture and stories; private material/secrets never enter Git/logs/static assets.

## Scheduling and evidence

Approximate deadline remains 15 December 2026 and the desired core-completion target around 1 December; neither is a confirmed delivery guarantee. Use backlog progress to reassess scope/pace and reserve time for correction. The first increment is runnable demo only; the full live scope is not promised complete in the same session.

Keep README setup/demo/live instructions, lockfile, implementation specs, sprint status and observed validation evidence. Record significant decisions and actual errors/checks in the session/reflection notes; do not invent test outcomes or learning experiences. Browser keyboard/narrow-window/200% zoom and screen-reader checks remain part of final application acceptance.

EXT-1 multiple-choice scoring remains optional after all core checks, and is not included in these epics. Export, spaced repetition, sharing, multi-document analysis and native mobile apps remain outside v1. No paid service or public deployment is authorized by the local implementation request.
