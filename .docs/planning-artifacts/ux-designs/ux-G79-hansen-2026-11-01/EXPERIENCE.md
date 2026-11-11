---
name: AI Study Buddy Experience
status: final
created: 2026-11-01
updated: 2026-11-11
sources:
  - ../../prds/prd-G79-hansen-2026-09-26/prd.md
  - ../../briefs/brief-G79-hansen-2026-09-26/brief.md
---

> Scope revision 2026-11-10: login, owner-only saved documents/results, My documents, open/delete are required in v1. This supersedes all temporary-only/no-account statements in the prior UX baseline below. New session clears active workspace only; saved deletion is separate. The approved study layout and the account/library/save flows below form the reconciled implementation baseline. Browser/accessibility and live backend validation remain acceptance work. Earlier finalization and accessibility reports cover the earlier scope only.

# AI Study Buddy - Experience

## Foundation

Hosted live application with one active source, authenticated accounts and owner-only saved documents/progress. A separate fixed-data local demo starts through README without keys. Sharing is outside v1. Demo-first development does not replace final live generation. [DESIGN.md](DESIGN.md) owns visual identity. Python/FastAPI with plain HTML/CSS/JavaScript and Supabase is selected.

[ASSUMPTION: exact helper/error wording, source-selector presentation, narrow-window behavior and focus handling below are proposed details. Mock UI is Norwegian; the confirmed output-language choice covers all generated content, not an agreed full UI translation.]

## Information Architecture

One workspace: compact material-panel, settings and Generate above the four result-tabs. Keep the whole material-panel open before generation and on errors. After success, collapse the entire panel to its heading and a "Vis/rediger" button. Reopening restores all material/settings without changing results or practice progress. Do not collapse on start or failure. [Earlier before-generation reference](.working/key-input.html) (historical; superseded by the clickable prototype) and [after-generation mock](.working/key-study.html) illustrate input and practice; key-study.html is the active clickable prototype.

| Surface | Purpose |
| --- | --- |
| Workspace | One active pasted text/text-file/PDF source, optional subject, language/detail, Generate and New session. |
| Sammendrag | Default selected tab after generation; summary and supporting references. |
| Begreper | Concepts with explanations and references. |
| Flashcards | One card, counter, navigation and answer reveal. |
| Quiz | One question, counter, navigation and solution reveal. |

All parts belong to the same generation. Switching tabs neither regenerates nor resets content/progress. Card and quiz positions are independent.

## Voice and Tone

Plain, specific and supportive. Explain the next action without promising correctness or improved grades.

| Context | UI text |
| --- | --- |
| Generate/loading | "Lag læringsmateriale"; "Lager læringsmateriale …". |
| Recovery/reset | "Prøv igjen"; "Ny økt". |
| Cards | "Forrige", "Vis svar", "Neste"; "Kort 2 av 8" (dynamic example). |
| Quiz | "Forrige", "Vis fasit", "Neste"; "Spørsmål 2 av 8" (dynamic example). |
| Reference | "Kilde: avsnitt 3" / "Kilde: side 3". |
| Proposed empty/error | "Legg inn tekst eller velg en fil." / "Kunne ikke lage læringsmaterialet. Materialet og innstillingene er beholdt." |
| Proposed unreadable PDF | "Ingen sider har lesbar tekst. Bruk en tekstbasert PDF eller lim inn tekst." |
| Proposed coverage | "Disse sidene har ikke lesbar tekst: 2, 4. Resultatene dekker bare teksten som kunne leses." |
| Proposed insufficient part | "Materialet gir ikke nok grunnlag for denne delen." |
| Proposed demo | "Demo – eksempeldata" beside the title; no large demo notice box. Explain arbitrary documents are not processed. |

## Component Patterns

| Component | Behavioral rules |
| --- | --- |
| material-panel | The whole panel starts expanded; collapse it after success to a heading and "Vis/rediger" button. Expansion preserves material, settings, results and progress; expose expanded state and controlled panel. Return focus to a visible control when collapsing. Source text stays open inside the panel. New session restores expanded empty input. Exactly one source method active. Subject is optional context only; factual content comes from the source. Default Norwegian/short; English and detailed independently selectable before generation. |
| field | Persistent labels and input limits. Ignore inactive material. Source changes must not present previous output as current. No silent truncation. |
| primary-action | One Generate action creates all four parts. During generation disable Generate and show loading text; re-enable on success/failure. Prevent concurrent submissions. |
| secondary-action | New session clears pasted text, uploaded file, subject, results, indices and reveal state; restores Norwegian/short. Try again retains source/settings. Previous/Next moves one item. [ASSUMPTION: disable at first/last item, no wraparound.] |
| result-tabs | Sammendrag selected after generation. Preserve contents, card/quiz indices and per-item revealed state across tab changes. |
| learning-panel | Item counts depend on source support. One card/question at a time; answers initially hidden. Reveal only the selected answer. Preserve revealed state on tab switches during the same visit; reopening a saved document restores positions with both answers hidden (confirmed 2026-11-11); successful new generation/reset starts again hidden. Insufficient parts show an explanation instead of invented items. |
| source-reference | Adjacent to summary/concept content. Card/quiz reference appears together with the answer, in identical styling with original paragraph/page numbers. No embedded source viewer or clickable jump is required. |
| feedback | Separate validation, technical failure, insufficiency, PDF coverage and demo notices. Errors preserve input. Use {colors.error} with explanatory text and {colors.text-secondary} for helper text. |

## State Patterns

| State | Behavior |
| --- | --- |
| Empty/start | Norwegian/short defaults. Blank subject permitted. Reject empty active source even if inactive input exists. |
| Source/settings changed | Do not label old results as generated from new material. [ASSUMPTION: a changed-settings notice requests regeneration when settings differ from displayed output.] |
| Busy | "Lager læringsmateriale …", disabled Generate; no duplicate request. [ASSUMPTION: a late response cannot populate a different/reset source; architecture decides cancellation/version handling.] |
| Success | Whole material-panel collapsed to compact heading and "Vis/rediger" button; material/settings retained. All four parts available, Sammendrag selected, first card/question and hidden answers/references. |
| Revealed practice item | Answer/reference together, preserved per item and across tabs; independent card/quiz positions. |
| Technical error/offline live request | Readable error and Try again; retain source/settings; re-enable Generate. Never present incomplete output as a complete generation. No offline live-generation promise. |
| Oversized | Reject above 30,000 characters for pasted/file/PDF-extracted text, or above 40 physical PDF pages. Ask for shorter excerpt, report actual limit, no truncation or live request. |
| Partial PDF | Process readable text; list original pages without readable text and disclose limited coverage. Preserve physical page offsets. No OCR/table/figure interpretation. |
| No readable text/unusable file | No generation; request text-based PDF or pasted text and allow replacement. |
| Insufficient source | Explain unsupported/empty parts; do not invent items or show "1 av 0". Keep all four tab destinations available. |
| Reset | Clear all source/subject/results/progress and restore defaults. Session expiry/cleanup is an architecture choice. |
| Demo | Clearly labelled fixed example/responses, usable without credentials. Never imply custom-source processing. Final demo fixtures must be distinct from live-source entry. The local UX prototype allows editing controls for walkthrough only; its results always use fixed example material, not those edits. |
| Missing live configuration | [ASSUMPTION: explain missing API setup, refer to README and keep demo available; no API-key field in study workflow.] |

## Interaction Primitives

Native keyboard-operable inputs/buttons. Tab/Shift+Tab follows visible order; result tabs support arrow-key navigation and expose selected state. Reveal controls expose expanded state. No hover-only action, auto-advance, time pressure or animation. Use {spacing.5} between input/results and {spacing.2} between related controls.

Learning state belongs to the generation, not tab mounting. New successful generation or New session resets it; tab changes do not.

## Accessibility Floor

Persistent labels, meaningful roles, visible focus with {colors.accent}, selected-tab underline and no color-only state. Hidden answers/references stay outside screen-reader reading order until revealed. Announce loading/completion/errors/coverage without repeated interruption. After successful collapse, focus Vis/rediger and announce result availability. Expanding focuses source-method selection. Reset focuses source-method selection. Practice navigation retains the same directional button when enabled, otherwise the opposite enabled button; announce only the new position and question, not hidden answers.

Text wraps and remains selectable at zoom; no truncated answers or controls. DESIGN.md owns contrast and typography tokens; implementation must check actual focus, disabled and error states. No unnecessary motion.

## Responsive & Platform

Primary surface is local desktop/laptop browser. Input remains above tabs. [ASSUMPTION: stack settings on narrow windows, keep tab labels reachable, avoid page-wide horizontal overflow and support 200% zoom. Exact breakpoints remain implementation details.] No native mobile or sidebar layout.

## Inspiration & Anti-patterns

No reference product named. User rejects unnecessary animation/decoration and chooses input above results. Avoid gamification, ornamental branding and accidental score/marking features in core quiz.

## Key Flows

[ASSUMPTION: Fredrik below is an illustrative reconstruction of confirmed choices, not a user-narrated or research-validated journey.]

### Flow 1 - Source to overview (Fredrik preparing for a test)

1. Fredrik opens the local workspace and supplies one pasted/text-file/PDF source.
2. He optionally enters subject and keeps Norwegian/short or changes settings.
3. He presses "Lag læringsmateriale" once; loading text appears and Generate disables.
4. For partial PDFs, he sees unreadable page numbers and limited-coverage notice.
5. **Climax:** the whole material-panel folds into a compact row with "Vis/rediger" and all four parts are available with Sammendrag active and supporting references.

Failure: empty/oversized/unreadable input requests correction before live calls. Technical failure preserves inputs for retry; insufficient source is explained per part.

### Flow 2 - Practice and verify (Fredrik moving between tabs)

1. Fredrik selects Flashcards; one question appears with "Kort 1 av N" and hidden answer.
2. "Vis svar" reveals answer and paragraph/page reference together.
3. He advances, selects Quiz and reveals its solution/reference in the same style.
4. **Climax:** returning to Flashcards restores his card position and revealed state without regenerating; Quiz retains its independent position.

Empty part: show the source-insufficiency explanation, without fake card/navigation. Navigation and reveal never start an AI call.

### Flow 3 - Retry and reset (Fredrik completing a session)

1. A generation fails; Fredrik sees explanatory error and "Prøv igjen".
2. He retries without entering source/settings again.
3. **Climax:** successful retry produces all parts with initial hidden-answer state.
4. "Ny økt" clears material, settings context, outputs and progress; Norwegian/short return.

Failure: another failed retry retains inputs again. Generate after reset must reject empty input rather than reuse old source.

### Flow 4 - Key-free demonstration (Fredrik acting as assessor)

1. Fredrik starts the app from README without credentials.
2. A labelled demo shows fixed example material and responses.
3. **Climax:** all four parts and reveal/reference navigation can be inspected without a paid account.

Limitation: arbitrary-source generation is not simulated as real AI; live generation and the three-document quality evaluation remain final requirements.

## Walkthrough acceptance check

Before generation the whole material-panel is expanded and text size is unchanged. Success collapses the whole panel to its heading and "Vis/rediger". Expand it by keyboard and verify no input, generated content, card/question position or revealed-answer state is lost. A generation failure retains source/settings and keeps the whole panel expanded. New session restores the expanded empty source.

Confirmed microcopy: primary action "Lag læringsmateriale" with helper "Lager sammendrag, begreper, flashcards og quiz." immediately above; secondary "Ny økt" with adjacent helper "Ny økt tømmer materialet og resultatene." Demo label "Demo – eksempeldata" appears discreetly beside the title.

## Prototype coverage and implementation checks

The active clickable prototype uses local fixed examples only. It demonstrates input controls, empty/oversized pasted-text validation, loading/success, whole-panel collapse/expansion, tabs, item navigation/reveal and reset. PDF extraction, language/detail-sensitive generation, technical failure/retry, partial/unreadable PDF notices and source-insufficiency outcomes now have explicit fixed-fixture previews in the separate prototype controls. Implement and test them against PRD acceptance checks; absence from this example prototype is not evidence of completed application functionality.

Before application acceptance, perform keyboard-only and screen-reader walkthroughs, verify focus after collapse, validate narrow-window/200% zoom reflow and visible error/focus states. Source inspection and Node state checks do not establish browser or WCAG conformance.

Remaining adjustable defaults (owner: student with implementation assistant): numerical dimensions, responsive breakpoints, noncritical error copy, demo fixture presentation and lifecycle concurrency mechanisms. Resolve during architecture or affected stories; preserve confirmed text sizes, composition and behavior. Illustrative journey names are documentation examples, not research evidence. No backend/framework choice is introduced by UX.

## Prototype example-state controls

The user-approved prototype controls are outside the product workspace, in a separately labelled dashed region. A selector and Show example state button preview fixed normal, generation-failure, partial-PDF, entirely unreadable PDF and insufficient-material fixtures. These are walkthrough tools, not product features or backend integration. Selecting a fixture never changes the student's source/settings.

Failure keeps the material-panel open and shows Try again; retry demonstrates success using fixed data while preserving inputs/settings. Partial PDF lists unreadable pages 2 and 4 and uses original page 3 in references, including revealed practice answers. Entirely unreadable PDF keeps input open, explains replacement options and hides results. Insufficient-material results keep all four tabs, explaining the missing source support without fake cards/questions or navigation. New session clears notices and results. No file is actually parsed or sent anywhere.

Finalized 2026-11-01 after user approval of the visual walkthrough and added example states. Remaining numerical implementation defaults and real browser/accessibility checks are owned by the student and implementation assistant before application acceptance; they do not block architecture.

Confirmed save interaction (2026-11-10): use an explicit secondary "Lagre" action for source/settings/generated learning material; no automatic save on upload or generation. New session clears the active workspace without deleting saved items. The current prototype demonstrates the button using fixed fixture state only; durable owner-scoped persistence and login remain implementation work.

Confirmed resume behavior (2026-11-10): reopening a saved document continues from the last flashcard and quiz question, with independent positions per owner/document across visits. New session clears only the active workspace. Progress persistence must not implicitly save previously unsaved material. Update 2026-11-11: position changes are saved automatically only for an already-saved document/generation. Source/settings/new results still require explicit Save; unsaved progress stays in browser memory. Reopening restores the independent positions with flashcard and quiz answers hidden (confirmed 2026-11-11); answers are revealed only on request. Tab switches during the current visit retain revealed state. Confirmed 2026-11-11: an outdated device/tab must not overwrite newer saved progress. Show "Fremdriften er endret på en annen enhet" with "Hent siste fremdrift" and require fetching current progress before further progress writes from that view. Never silently retry the stale position over newer progress. Show pending/failed sync during network problems; only acknowledged updates can resume on another device. The technical revision/locking/idempotent retry protocol is governed by AD-7. This requirement is not yet implemented in the fixed-fixture prototype.

Delivery/service update (2026-11-10): live mode supports same-account content/progress across devices using Supabase Auth/Postgres/private Storage. Local demo remains available. Email/password login and the library flows below are the implementation baseline; offline cross-device editing/synchronization is not promised. Current prototype remains fixed local examples with no Supabase connection.

Confirmed authentication (2026-11-10): Supabase email/password with Opprett konto, Logg inn, Glemt passord and Logg ut. Use labelled inputs, appropriate password autocomplete in the actual app, understandable failed/expired-link states and generic password-recovery responses. Password changes require a valid recovery session. The local prototype uses read-only fictional credentials and simulated messages; no email is sent and no real authentication is performed. Logout clears active private UI state; saved server-side documents are retained for their owner. The demo fixture is cleared on simulated logout to avoid showing previous local example state as another user's content.

Confirmed login lifecycle (2026-11-11): backend-managed login state lives in memory on one server process for v1. Server restart/redeploy requires login again. Show an understandable sign-in-again message when the application session is no longer valid and block private actions until authenticated. Saved documents, learning material and acknowledged progress remain in Supabase; after login the owner can reopen them at the saved positions with answers hidden. Unsaved work has no durability guarantee. Multiple devices may be signed in simultaneously. This behavior is planned, not implemented in the local fixed-fixture prototype. AD-3 governs secure backend sessions and recovery: initial 30-minute idle / 12-hour absolute expiry, renewed login after restart, recovery restricted to password change and normal login afterward.

## Live account and persistence states — implementation baseline 2026-11-11

Signup uses labelled email/password fields and a check-your-email state when confirmation is required. Login failure retains the email and shows a safe error; passwords are never logged. Recovery requests give the same generic acknowledgment regardless of account existence. Recovery links must be opened in the initiating browser. Expired, reused, wrong-browser or restart-invalidated links explain how to request a new link. A valid recovery view contains only new-password fields; it cannot show documents. After password update require normal login. Logout ends only this device's login and clears its active private UI; other devices retain their sessions.

The first Save captures the current independent practice positions; absent exercise sections have no position. Saving shows pending state, prevents duplicate submissions, and reports success only after the accepted document/source/settings/bundle is ready. On failure preserve active inputs/results and offer retry. After re-login/restart, show the owner any already-admitted pending Save separately from ready documents and allow explicit retry of that same accepted snapshot. If its registered original file is missing, request that same file again; changed content requires new generation/Save. After the 7-day resume window, offer cleanup rather than completion. A Save never admitted by the server has no recovery guarantee and requires fresh generation after loss of its session/receipt. Source/settings edits and New session immediately disable Save and notify the server to invalidate the prior generation receipt; failed invalidation requires retry/reload. A successful new generation enables Save only for its current acknowledged workspace revision. Source/settings/new output changes still require explicit Save. Replacing an existing saved generation resets its saved practice positions only after successful Save. Stale replacement shows a conflict with Reload and Save as new; it does not silently replace another device's content. New session clears the workspace without deleting saved items.

The library distinguishes loading, empty, ready and failed-list states. Pending save/delete operations appear with status/retry for their owner, separate from openable ready items. Delete confirmation names the document; cancel changes nothing. A deleting item cannot reopen; failure remains visible with retry and is never reported as deleted. A confirmed delete clears the active view if it showed that document. Access denial never exposes another owner's title/content. Following reset, logout, source change or account change, late private responses are discarded.

Practice shows pending, saved or failed sync status. A conflict blocks further writes until Hent siste fremdrift; fetching current saved progress restores positions with answers hidden, equivalent to reopening. Fetch failure retains the conflict and offers retry. These states require real browser and backend checks before application acceptance; the fixed fixture remains a demonstration only.

## My documents - prototype refinement (2026-11-10)

A secondary Mine dokumenter action beside the account controls opens an owner-library surface with title, saved date and practice positions, plus Open and Delete per item. Empty state explains how to generate/save the first item. Back returns to the active workspace. Open restores that document's source/settings/results and independent positions without regeneration. Delete first shows an inline confirmation naming the document and including its learning material/progress, with Cancel and Delete document. Confirmed deletion clears the active view if that item is open; cancellation changes nothing. Show no fake exercise counts for insufficient-source items. The prototype supports several in-memory examples only, with no backend or real owner isolation. Actual app requires server/database/storage ownership checks and delete-failure recovery from the PRD.
