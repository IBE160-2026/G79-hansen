---
title: 'Modern study app layout'
type: 'feature'
created: '2026-11-20'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

The student found the first visual polish still too basic and explicitly chose
"modern study app: desktop sidebar, blue/purple accents and a clear workspace".
Make that direction visibly distinct: dark desktop navigation, a light workspace,
stronger blue/purple actions, organized panels and a more deliberate demo input
layout. On mobile retain a compact, visible top navigation. This choice supersedes
the older no-sidebar UX constraint. Keep the existing study functionality, IDs,
control labels, privacy disclosures, hidden-answer states, keyboard access and
working authentication. Use local SVG/CSS and system fonts; no new framework,
external assets, fabricated stats/features or marketing landing page. No backend,
quota, account, model/email integration, or public hosting changes.

</frozen-after-approval>

## Implementation Notes

- Scope: shared styles.css and index/account/workspace HTML in app/static;
  document the explicit visual-direction override in the existing DESIGN.md.
  Existing scripts address IDs, not the proposed additional layout wrappers.
- Reuse the fixed-data demo browser regression and the isolated synthetic
  account/source/result screenshot smoke check. Inspect desktop/mobile and200%
  layout, keyboard focus and hidden-state behavior. No live generation or mail.
- Small reversible presentation change with explicit visual choice, no remaining
  intent gap or irreversible action; oneshot route. Existing private preview only.
- Implemented244px sticky navy sidebar above960px, visible top navigation below
  that breakpoint, violet primary actions, SVG navigation/output icons and a
  grouped, explicitly labelled output overview. The demo action is adjacent to
  its picker before the read-only source on mobile; real-source workflow unchanged.
- Reproducible regression: `node tests/browser-demo.cjs` starts an isolated local
  app and verifies13 fixed-data scenarios, hidden answers, keyboard tabs/focus,
  collapse/reopen/reset and no overflow at320/390/480px and200% layout zoom.
- Visual verification: desktop1280px and mobile390px captures from the existing
  synthetic fixture app (local helper under test-results). At desktop, navigation
  remains alongside content; at mobile it stays above it and all destinations are
  visible. Focus/selected states remain visible, main actions remain reachable,
  and the entire material panel still collapses after generation. Ordinary input,
  generation/reveal and skip-link focus use synthetic data only, with zero external
  browser requests. No live model/email calls or account changes are permitted.
- Final result:13 existing demo scenarios passed after the layout/action changes,
  with21 fixed-data requests. Ten final desktop/mobile/narrow screenshots cover
  synthetic login, source/results/reveal and skip-link focus, without external
  requests, page overflow or JavaScript errors. Desktop/mobile/320px renders were
  visually inspected. Narrow output labels retain whole words after a compact
  icon/padding correction. No new full WCAG/auth-backend acceptance is claimed.

## Review Triage Log

- medium/patch — Demo action was too far below picker, especially on mobile;
  move action/help before read-only source, compact overview/fixed settings and
  shorten the redundant demo introduction without losing fixed-data disclosure.
- low/patch —320px top navigation wrapped Konto to a third header row; hide only
  decorative nav icons at360px and below, keeping all text links visible.
- low/patch — Static output tiles resembled navigation; group them under the
  explicit "Fire læringsformer fra samme kilde" label and remove individual
  button-like borders/backgrounds. Actual tab controls remain in results.
- low/patch — DESIGN frontmatter retained old tokens; update palette, radii,
  typography and current layout prose to match the student-selected direction.
- low/patch — Verification notes lacked reproducible criteria; add the tracked
  demo command, widths, breakpoint and expected hidden/focus/layout behavior.
- low/rejected — Three static pages duplicate navigation, as in the existing
  architecture; actual labels/URLs/aria-current were inspected and are consistent.
  A new rendering dependency is outside this bounded styling change; permanent
  tests mirroring the same markup would add little value. No current divergence
  or user failure was demonstrated, so no new architecture work is deferred.
- medium/patch (self-check) — Initial selected-nav border had only2.98:1 against
  the sidebar; lighten it and add a high-contrast inset marker. Primary/secondary
  text and sidebar focus contrast pairs were measured separately.
