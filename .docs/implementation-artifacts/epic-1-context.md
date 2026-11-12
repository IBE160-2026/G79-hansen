# Epic 1 Context: Try the complete study flow locally

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Let an assessor run and inspect the complete study interaction locally without credentials or cloud services, while gathering early evidence that PDF extraction can preserve trustworthy physical page references within practical resource limits. The fixed-data demonstration and PDF feasibility experiment are incremental evidence; neither completes arbitrary-source generation, authentication, persistence, or final application acceptance.

## Stories

- Story 1.1: Run the four-part study demo
- Story 1.2: Verify physical PDF pages before integration

## Requirements & Constraints

- The local demo must start from README without service keys or a paid account. Display a discreet Norwegian example-data label and make the fixed source visible. Accept only documented fixture semantics, rather than presenting arbitrary text or uploads as genuinely processed. Never silently substitute fixture output for failed live generation.
- A single Generate action obtains summary, explained concepts, flashcards and quiz together. Each item has source references. Flashcard and quiz answers remain hidden until explicitly revealed, with their references revealed at the same time. Tab, reveal, navigation and material-panel actions must not call a model.
- Preserve separate flashcard and quiz positions and per-item reveal state while switching tabs. New session clears active material, settings context, results and practice state; stale pending responses must not restore them. Generation errors retain material/settings with explicit retry and must not show fabricated or partial success.
- PDF references identify original one-based physical page positions, including blank or image-only pages. Process readable text only, retain gaps in numbering, report original page numbers without usable text, and explain partial coverage. If no page contains readable text, reject rather than generate. OCR, image/table interpretation and encrypted-file password workflows are outside scope.
- Reject sources exceeding 40 physical PDF pages or 30,000 Unicode code points without truncation. Normalize CRLF and CR to LF before counting canonical extracted text; reference labels do not contribute to the count. Source units retain stable IDs, kind, original location and text. Never renumber readable PDF pages consecutively after skipping unreadable pages.
- Bound bytes, extraction time and memory. The initial upload ceiling is 10 MiB; the experiment must establish usable extraction limits and document observations and limitations before application integration. Synthetic fixtures must expose boundary and failure behavior without private uploaded material entering Git or logs.
- Keep secrets and private source content out of repositories, static assets, caches and logs. No cloud provisioning, paid service or public deployment is authorized by this epic. Final manual accessibility and live content-quality checks remain separate acceptance work.

## Technical Decisions

- Use one Python/FastAPI application serving plain HTML/CSS/JavaScript and API routes from the same origin. Do not add a separate frontend framework, build chain, full-stack template or database for the local demo. Private documents must never be served through public static assets.
- Keep API contracts typed and versioned, with a shared source/learning-bundle shape and a deliberate demo/live adapter boundary. A bundle carries source/settings identity, all four learning sections, warnings and per-section insufficiency explanations. Resolve source-unit IDs into display references on the server and reject unknown references.
- Preserve accepted source representations alongside eventual saved results so later extraction-library upgrades cannot change existing references. The experiment should establish an extraction representation suitable for later integration without claiming to implement owner storage now.
- pypdf 7.0.1 is a researched candidate, not an adopted PDF dependency. Validate it through the extraction experiment before adoption, then lock the tested version. The tested dependency lockfile is the exact version authority; the architecture stack table is only a seed.
- Use content-free health checks and safe error codes/messages. Demo failure must remain failure, with explicit recovery; no live private route or authentication bypass should be introduced as a shortcut. The PDF experiment is local feasibility tooling, not a public upload endpoint.

## UX & Interaction Patterns

- Keep a compact material/settings area above four clearly labelled tabs: Sammendrag, Begreper, Flashcards and Quiz. Summary becomes active after generation. Keep the whole material region open initially and on errors; collapse it only on success. Vis/rediger reopens it while preserving source, results and practice state.
- Show one card/question at a time, with count and bounded Previous/Next controls. Use labelled fields, visible focus, keyboard-operable tabs/reveal/navigation, polite status and understandable errors. Avoid fake counts for insufficient-source sections.
- Preserve the approved light background, white surfaces, dark text, discreet blue accent and system fonts. Keep readable text sizes, wrapping and narrow-window/200% zoom reflow. Do not add a sidebar, marketing layout or decorative animation. Automated or source checks do not establish screen-reader or full WCAG conformance.
- Keep confirmed Norwegian primary-action and reset wording, including the helper explaining that New session clears active material/results. Any PDF coverage notice must identify unreadable pages and the restriction to extracted text rather than imply complete document understanding.

## Cross-Story Dependencies

Story 1.2 follows the implemented Story 1.1 foundation; its extraction findings gate later authenticated source integration. Story 2.4 integrates real text/file/PDF input only after the PDF experiment and account/session work. Live model selection, API access, budget and data-handling decisions gate Story 2.5, not this epic. Owner persistence, cross-device progress, deployment and full application acceptance belong to later epics. Story 1.1 remains subject to the student's review even when its implementation and automated verification are complete.
