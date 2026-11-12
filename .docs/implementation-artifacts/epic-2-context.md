# Epic 2 Context: Study your own material privately

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Let students create an account and produce source-grounded summaries, concepts, flashcards and quiz questions from their own material, with private authenticated access and checkable paragraph/page references. Build on the credential-free demo and proven PDF extraction boundaries. Live model selection is an explicit integration gate; fixed responses never substitute for live completion.

## Stories

- Story 2.1: Sign up and sign in securely
- Story 2.2: Recover a password through a restricted session
- Story 2.3: End access on logout expiry and restart
- Story 2.4: Validate and extract the active source
- Story 2.5: Generate all learning parts from the source
- Story 2.6: Evaluate generated content against known sources

## Requirements & Constraints

- Supabase email/password accounts support confirmation, login, recovery and logout. Derive identity from validated authentication, never submitted owner IDs. Keep credentials, tokens, sources and private output out of Git, logs, browser storage, static files and shared caches. Introduce document tables only when persistence stories need them.
- Accept exactly one active pasted-text, text-file or text-based PDF source. Optional subject is context, never factual authority. Norwegian/short are defaults; English and detailed summary are independent choices and output language applies to all four sections.
- Reject empty, invalid, unreadable or over-limit input before model calls. Limits are 30,000 Unicode code points and 40 physical PDF pages, including blank/image-only pages; reject rather than truncate. Initial upload ceiling is 10 MiB with bounded extraction worker/time resources. No OCR, table/figure interpretation or encrypted-PDF password workflow.
- All generated content must have source support. Adapt item counts to available evidence; explain insufficiency per section instead of inventing content. Technical failure preserves every input/setting and offers explicit retry; incomplete output cannot appear complete.
- Before live integration, record provider/model, API access, quality/cost comparison, budget ceiling, data handling and timeout/output limits. No silent live-to-demo fallback, paid commitment or public deployment is implied.
- Evaluate three documents including text and PDF. Preselect five central concepts and locations per document; checked content must be supported, references correct and at least four concepts covered. Record unsupported content, wrong references and omissions separately, then fix and recheck.

## Technical Decisions

- Keep one same-origin FastAPI application with plain HTML/CSS/JavaScript. Services own orchestration; request-scoped adapters handle Supabase Auth, extraction and the model. Never share a mutable authenticated Supabase client across users or expose privileged keys. Private access later uses user credentials and owner RLS.
- Use one backend process and a bounded in-memory session registry containing provider credentials. Browser holds an opaque random HttpOnly, SameSite=Lax cookie, Secure on HTTPS. Rotate its identifier after authentication/privilege transition; validate every private request and serialize token refresh per session. Require same-origin and CSRF protection for cookie-authenticated mutations. Private/auth/callback responses use Cache-Control: no-store.
- Confirmation/recovery use backend PKCE exchange with separate bounded, expiring pending attempts containing verifier, random state, initiating-browser cookie binding and purpose. Overlapping tabs must not replace each other's verifier. Reject wrong-browser/state, expired/replayed/missing attempts and implicit token fragments. Configure redirect allowlists. Recovery grants password-update-only access, consumes that authority on success and requires normal login afterward.
- Default expiry is configurable 30-minute idle / 12-hour absolute. Restart requires re-login. Logout denies locally and clears the cookie before bounded provider revocation with local scope; provider outage cannot retain access or sign out another device. Saved data survives session endings; private UI and late responses cannot restore ended access.
- Canonicalize CRLF/CR to LF and count code points before reference labels. Text uses nonempty blank-line-separated paragraphs; PDFs retain original one-based physical pages, including unreadable positions. Stable source-unit IDs connect model references to server-resolved locations; reject unknown IDs.
- Demo/live share schema-versioned Source and LearningBundle contracts with stable item IDs, settings/source identity, warnings and per-section insufficiency. One bounded structured-output request produces all four parts without hidden retries. Errors use safe code/message/requestId, JSON camelCase and UTC timestamps; never include provider bodies or private data.
- Upload/generation remains transient until explicit Save in Epic 3. Generation prepares a 30-minute signed receipt binding owner, session, workspace/revision, generation/receipt IDs and deterministic canonical hashes. A bounded in-memory authority registry stores metadata/hashes only, at most eight workspaces per session. Generation, invalidation and Save admission share a workspace mutex. Edits/reset/new generation revoke older authority; signature validity alone cannot authorize Save. Failed or uncertain invalidation blocks Save pending retry/reload. Discard stale replies after source/reset/account changes.

## UX & Interaction Patterns

- Preserve the compact material/settings area above four accessible tabs: Sammendrag, Begreper, Flashcards, Quiz. Expand initially/on error; collapse the entire region only after success. Vis/rediger preserves state. Summary is selected after generation; disable duplicate Generate while busy.
- Each practice section shows one item, its own position and per-item reveal state. Answers/references appear together only on request. Tab switches preserve state and never call AI; new generation/reset hides answers. Insufficient sections retain tabs without fabricated items or navigation.
- Use Norwegian account controls Opprett konto, Logg inn, Glemt passord and Logg ut, labelled fields, suitable password autocomplete, understandable error/expired-link states and generic recovery responses. Explain that email recovery must open in the initiating browser. Session failure offers sign-in again and clears private UI.
- Retain light background #f8fafc, white surfaces, dark #172033 text, blue #315f91 accent and system fonts. Preserve readable text, visible focus, keyboard operation, polite status, safe text rendering, narrow-window/200% reflow and primary-flow screen-reader verification.

## Cross-Story Dependencies

Epic 1 supplies the runnable demo and PDF feasibility evidence. Authentication precedes recovery, then complete session endings; source extraction depends on that lifecycle and the PDF experiment. Live generation follows extraction and the provider gate; content evaluation follows live generation. Epic 3 consumes authenticated ownership, canonical sources/bundles and receipt authority for explicit persistence; saving, library, deletion and cross-device progress remain its work.
