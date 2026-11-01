---
name: AI Study Buddy
description: A clear study workspace with light surfaces, dark text and a discreet blue accent.
status: final
created: 2026-11-01
updated: 2026-11-01
sources:
  - ../../prds/prd-G79-hansen-2026-09-26/prd.md
  - ../../briefs/brief-G79-hansen-2026-09-26/brief.md
colors:
  background: '#F8FAFC'
  surface: '#FFFFFF'
  text: '#172033'
  text-secondary: '#475569'
  accent: '#315F91'
  accent-text: '#234E7B'
  on-accent: '#FFFFFF'
  border: '#CBD5E1'
  control-border: '#64748B'
  note: '#EEF4FA'
  error: '#9B1C1C'
typography:
  title: {fontFamily: 'system-ui, sans-serif', fontSize: 28px, fontWeight: '700', lineHeight: '1.25'}
  heading: {fontFamily: 'system-ui, sans-serif', fontSize: 20px, fontWeight: '600', lineHeight: '1.35'}
  body: {fontFamily: 'system-ui, sans-serif', fontSize: 16px, fontWeight: '400', lineHeight: '1.6'}
  meta: {fontFamily: 'system-ui, sans-serif', fontSize: 14px, fontWeight: '400', lineHeight: '1.5'}
rounded: {sm: 6px, md: 8px}
spacing: {'1': 4px, '2': 8px, '3': 12px, '4': 16px, '5': 24px, '6': 32px}
components:
  material-panel: {background: '{colors.surface}', radius: '{rounded.md}', padding: '{spacing.4}'}
  field: {background: '{colors.surface}', foreground: '{colors.text}', border: '{colors.control-border}'}
  primary-action: {background: '{colors.accent}', foreground: '{colors.on-accent}', radius: '{rounded.sm}'}
  secondary-action: {foreground: '{colors.text}', background: '{colors.surface}'}
  result-tabs: {active: '{colors.accent-text}', foreground: '{colors.text}'}
  learning-panel: {background: '{colors.surface}', padding: '{spacing.5}'}
  source-reference: {foreground: '{colors.text-secondary}', background: '{colors.note}'}
  feedback: {foreground: '{colors.text}', error: '{colors.error}'}
---

## Brand & Style

Confirmed: simple and tidy, light background, dark text, discreet blue accent, clear headings and generous separation. Material entry, Generate and learning navigation must be easy to find. Avoid unnecessary animation and decoration. No UI framework is selected.

Colors and readability were accepted in visual walkthrough. [ASSUMPTION: exact widths, spacing, radii and control dimensions remain implementation defaults, adjustable without changing the confirmed composition or reducing text size.]

## Colors

Use {colors.background} around {colors.surface} panels, {colors.text} for content and {colors.text-secondary} for helper text. Blue accents identify primary action, focus and selected tabs. Use {colors.error} with explanatory words, never color alone. Decorative separators use {colors.border}; interactive fields use {colors.control-border}.

Target normal text contrast at least 4.5:1, large text and focus/control boundaries at least 3:1 against adjacent surfaces. Verify rendered states during implementation. Computed proposed-palette contrast: text/white 16.27:1, secondary/white 7.58:1, white/accent 6.61:1, accent/background 6.32:1. Error combinations still require verification; this is not a claim of completed browser accessibility testing.

## Typography

Use {typography.body.fontFamily}, without external font downloads. Title, heading, body and meta roles distinguish hierarchy. Text wraps and remains selectable; do not truncate questions, answers or references.

## Layout & Spacing

Confirmed composition: compact material/settings area above result-tabs, with visible labels and a prominent Generate button. Tighten panel padding and spacing without reducing text sizes. Keep the entire material-panel expanded before generation and on errors. After successful generation collapse the entire panel to a compact heading row with a secondary "Vis/rediger" button. Expanding preserves material, settings, results and progress. Keep source text open inside the expanded panel. The user approved the proposed colors and readability during visual walkthrough; numerical spacing remains proposed. No sidebar. Use {spacing.5} between major regions and {spacing.4} within related groups.

[ASSUMPTION: centered maximum width 960px, minimum side padding 16px and controls at least 44px high. Settings share a row where room permits and stack on narrow windows.]

[Earlier before-generation reference](.working/key-input.html) (historical; superseded by the clickable prototype) shows the expanded source; [workspace mock after generation](.working/key-study.html) is the active clickable example-data prototype for input, loading, summary, concepts, flashcards, quiz, disclosure and reset. DESIGN.md and EXPERIENCE.md take precedence if a visual reference conflicts with them.

## Elevation & Depth

Use whitespace, plain surfaces and subtle borders. No decorative gradients, animated elevation or ornamental shadows are needed.

## Shapes

Proposed {rounded.sm} controls and {rounded.md} panels. Keep shapes unobtrusive; no pill-heavy navigation or mascots.

## Components

| Component | Visual rules |
| --- | --- |
| material-panel | Compact white region above tabs; source input, labelled settings and primary action. |
| field | Persistent label, readable value, visible boundary and helper/limit text. |
| primary-action | Blue Generate with white text; clear focus and visibly disabled busy state. |
| secondary-action | Plain bordered New session, retry, reveal and previous/next buttons; consistent card/quiz layout. |
| result-tabs | Sammendrag, Begreper, Flashcards, Quiz; active label emphasized with blue underline, not color alone. |
| learning-panel | Readable text blocks or one card/question with counter, reveal area and navigation. |
| source-reference | Same paragraph/page treatment throughout; appears with revealed answers in flashcards/quiz. |
| feedback | Inline notices distinguish demo, busy, validation, error and coverage states using clear text. |

## Do's and Don'ts

| Do | Don't |
| --- | --- |
| Keep source entry and Generate easy to locate. | Hide main actions in a sidebar. |
| Separate content with headings and whitespace. | Add decorative animation, badges or a marketing hero. |
| Match answer/reference styling between cards and quiz. | Reveal references early if they give away hidden answers. |
| Preserve labels, readable contrast and visible focus. | Rely on placeholder-only labels or color-only feedback. |

Confirmed microcopy: primary action "Lag læringsmateriale" with helper "Lager sammendrag, begreper, flashcards og quiz." immediately above; secondary "Ny økt" with adjacent helper "Ny økt tømmer materialet og resultatene." Demo label "Demo – eksempeldata" appears discreetly beside the title.

## Prototype example-state controls

The user-approved prototype controls are outside the product workspace, in a separately labelled dashed region. A selector and Show example state button preview fixed normal, generation-failure, partial-PDF, entirely unreadable PDF and insufficient-material fixtures. These are walkthrough tools, not product features or backend integration. Selecting a fixture never changes the student's source/settings.

Failure keeps the material-panel open and shows Try again; retry demonstrates success using fixed data while preserving inputs/settings. Partial PDF lists unreadable pages 2 and 4 and uses original page 3 in references, including revealed practice answers. Entirely unreadable PDF keeps input open, explains replacement options and hides results. Insufficient-material results keep all four tabs, explaining the missing source support without fake cards/questions or navigation. New session clears notices and results. No file is actually parsed or sent anywhere.

Finalized 2026-11-01 after user approval of the visual walkthrough and added example states. Remaining numerical implementation defaults and real browser/accessibility checks are owned by the student and implementation assistant before application acceptance; they do not block architecture.
