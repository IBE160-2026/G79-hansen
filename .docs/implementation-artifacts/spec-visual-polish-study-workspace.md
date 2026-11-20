---
title: 'Polish the existing study interface'
type: 'feature'
created: '2026-11-20'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

The student finds the current website too basic and wants its presentation improved.
Give the existing demo, account and own-material workspace a coherent, polished
appearance: shared navigation, stronger hierarchy, readable cards and consistent
forms, with a usable mobile layout. Follow the approved light surfaces, blue
accent, system fonts and content-first composition. Keep the learning workflow
recognizable; no sidebar, marketing hero, external assets, new framework or new
features. Preserve existing control IDs, labels, hidden states, tab semantics,
keyboard focus, source references and visible privacy guidance. Correct clearly
outdated account copy about generation/saving already implemented. Authentication,
requests, quotas, saved data and public hosting configuration remain unchanged.

</frozen-after-approval>

## Implementation Notes

- Scope: `app/static/styles.css`, `index.html`, `account.html`, `workspace.html`.
  Shared CSS and static markup only; preserve the JavaScript integration contract.
- Existing UX reference: DESIGN.md in the2026-11-01 UX folder; spacing/radius/width
  were implementation defaults, while readable contrast and no external fonts
  remain constraints. The source/model/auth code is outside this change.
- Verification: reuse the fixed-data demo browser checks; inspect rendered demo,
  account forms and workspace at desktop/mobile widths. Exercise selected results
  and keyboard focus with offline fixtures where needed. No model/email requests
  or real account mutations. No mirrored CSS unit tests or broad backend suite.
- No irreversible operation or unresolved product decision is needed for this
  bounded presentation change. Static assets update only the existing private
  preview; no public Funnel activation or push.
- Implemented shared book-mark/navigation/skip link, light card layout, consistent
  controls, responsive account grid and readable visible source/privacy guidance.
  The account's obsolete "generation/saving comes later" text is corrected.
- First demo regression:13 scenarios passed with21 fixed-data requests. Temporary
  offline browser verification captured9 views and checked synthetic login/source/
  results/reveal, skip-link focus, no overflow/JS errors/external requests.
- Independent review identified small presentation issues; all are patched
  below. Kept tabs in one horizontally navigable row with compact mobile labels
  and contained scrolling at the narrowest sizes. Empty live regions remain
  rendered so their first announcement is not lost to display:none.
- Final verification after the review patches: all13 existing demo scenarios
  passed again (21 fixed-data requests), including320/390/480px and200% zoom.
  Nine refreshed desktop/mobile screenshots passed the offline smoke flow with
  no page overflow, JavaScript errors or external browser requests. Visually
  inspected demo, account forms, source form and mobile generated results.
  Synthetic provider adapters were confined to the existing tests/ fixture app;
  no live model/email calls, real account mutations or server restart occurred.
  This does not claim a new full WCAG or backend-auth acceptance round.

## Review Triage Log

- low/patch — Settings input bottom margin displaced it relative to selects;
  normalize settings controls to50px and remove their bottom margin.
- medium/patch — Two-row mobile tab grid conflicts with the existing horizontal
  arrow interaction; retain a single row and focus-safe scroll container.
- low/patch — Answer paragraphs/nested question headings missed the reading-width
  selector; include them without truncating source content.
- low/patch — Disabled input/textarea appearance stayed editable-looking; include
  all form controls in the existing disabled treatment.
- medium/patch — Non-error source/PDF warnings lost their background treatment;
  restore the blue notice surface/left border with distinct error coloring.
- medium/patch (self-check) — New empty-live-region hiding could suppress first
  screen-reader announcement; remove that rule. Full screen-reader testing is not
  claimed by these layout checks.
