---
name: AI Study Buddy
description: A clear study workspace with light surfaces, dark text and a discreet blue accent.
status: final
created: 2026-11-01
updated: 2026-11-20
sources:
  - ../../prds/prd-G79-hansen-2026-09-26/prd.md
  - ../../briefs/brief-G79-hansen-2026-09-26/brief.md
colors:
  background: '#F4F6FF'
  surface: '#FFFFFF'
  text: '#1B2240'
  text-secondary: '#475569'
  accent: '#5A4AD0'
  accent-text: '#4433B5'
  on-accent: '#FFFFFF'
  border: '#DEE3F0'
  control-border: '#64748B'
  note: '#EEECFC'
  sidebar: '#171E38'
  sidebar-text: '#C1CBE1'
  error: '#9B1C1C'
typography:
  title: {fontFamily: 'system-ui, sans-serif', fontSize: 40px, fontWeight: '750', lineHeight: '1.2'}
  heading: {fontFamily: 'system-ui, sans-serif', fontSize: 21px, fontWeight: '700', lineHeight: '1.35'}
  body: {fontFamily: 'system-ui, sans-serif', fontSize: 16px, fontWeight: '400', lineHeight: '1.6'}
  meta: {fontFamily: 'system-ui, sans-serif', fontSize: 14px, fontWeight: '400', lineHeight: '1.5'}
rounded: {sm: 9px, md: 18px, mobile: 12px}
spacing: {'1': 4px, '2': 8px, '3': 12px, '4': 16px, '5': 24px, '6': 32px}
components:
  material-panel: {background: '{colors.surface}', radius: '{rounded.md}', padding: '{spacing.5}'}
  field: {background: '{colors.surface}', foreground: '{colors.text}', border: '{colors.control-border}'}
  primary-action: {background: '{colors.accent}', foreground: '{colors.on-accent}', radius: '{rounded.sm}'}
  secondary-action: {foreground: '{colors.text}', background: '{colors.surface}'}
  result-tabs: {active: '{colors.accent-text}', foreground: '{colors.text}'}
  learning-panel: {background: '{colors.surface}', padding: 28px}
  source-reference: {foreground: '{colors.text-secondary}', background: '{colors.note}'}
  feedback: {foreground: '{colors.text}', error: '{colors.error}'}
---

> Scope revision 2026-11-10: login, owner-only saved documents/results, My documents, open/delete are required in v1. This supersedes all temporary-only/no-account statements in the prior UX baseline below. New session clears active workspace only; saved deletion is separate. The approved study layout and the account/library/save flows below form the reconciled implementation baseline. Browser/accessibility and live backend validation remain acceptance work. Earlier finalization and accessibility reports cover the earlier scope only.

## Brand & Style

**Student-selected revision20 November2026:** after finding the initial visual
polish too basic, the student explicitly selected a modern study-app layout with
a desktop sidebar, blue/purple accents and a clear light workspace. Use compact
top navigation on mobile. This supersedes the older no-sidebar direction below;
the structured palette/tokens above now describe the current design. Preserve readable contrast,
visible focus, system fonts, real study controls and clear source/privacy text.
No fabricated usage metrics, external assets or new application features.

Current direction: a clear light study workspace with dark desktop navigation and blue/purple accents. Material entry, Generate and learning navigation must be easy to find. Avoid unnecessary animation and fabricated dashboard content. Use the existing HTML/CSS without a UI framework.

Colors and readability were accepted in visual walkthrough. [ASSUMPTION: exact widths, spacing, radii and control dimensions remain implementation defaults, adjustable without changing the confirmed composition or reducing text size.]

## Colors

Use {colors.background} around {colors.surface} panels, {colors.text} for content and {colors.text-secondary} for helper text. Purple/blue accents identify primary action, focus and selected tabs. Use {colors.error} with explanatory words, never color alone. Decorative separators use {colors.border}; interactive fields use {colors.control-border}.

Target normal text contrast at least 4.5:1, large text and focus/control boundaries at least 3:1 against adjacent surfaces. Checked20 November: white/purple primary6.32:1, sidebar text/background10.08:1, light sidebar focus/background8.50:1, secondary text/canvas7.03:1. Selected navigation also has a light inset marker. These measured pairs do not claim completed browser/screen-reader accessibility acceptance.

## Typography

Use {typography.body.fontFamily}, without external font downloads. Title, heading, body and meta roles distinguish hierarchy. Text wraps and remains selectable; do not truncate questions, answers or references.

## Layout & Spacing

Current composition: desktop navigation sidebar and a light workspace. The demo places the picker/primary action beside the source preview, with compact fixed settings; mobile stacks these in reading order and uses visible top navigation. Keep the entire material-panel expanded before generation and on errors. After successful generation collapse the entire panel to a compact heading row with a secondary "Vis/rediger" button. Expanding preserves material, settings, results and progress. Keep source text open inside the expanded panel. The real source form retains visible privacy guidance and labelled controls. Use {spacing.5} between major regions and {spacing.4} within related groups.

[Implementation defaults:244px desktop sidebar, content maximum1240px, compact top navigation at960px and below, minimum mobile side padding16px and controls at least44px high.]

[Earlier before-generation reference](.working/key-input.html) (historical; superseded by the clickable prototype) shows the expanded source; [workspace mock after generation](.working/key-study.html) is the active clickable example-data prototype for input, loading, summary, concepts, flashcards, quiz, disclosure and reset. DESIGN.md and EXPERIENCE.md take precedence if a visual reference conflicts with them.

## Elevation & Depth

Use whitespace, subtle borders and modest card elevation on the light workspace. Keep the sidebar flat and dark. No animated elevation or decorative hero effects.

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

Confirmed save interaction (2026-11-10): use an explicit secondary "Lagre" action for source/settings/generated learning material; no automatic save on upload or generation. New session clears the active workspace without deleting saved items. The current prototype demonstrates the button using fixed fixture state only; durable owner-scoped persistence and login remain implementation work.

Confirmed authentication (2026-11-10): Supabase email/password with Opprett konto, Logg inn, Glemt passord and Logg ut. Use labelled inputs, appropriate password autocomplete in the actual app, understandable failed/expired-link states and generic password-recovery responses. Password changes require a valid recovery session. The local prototype uses read-only fictional credentials and simulated messages; no email is sent and no real authentication is performed. Logout clears active private UI state; saved server-side documents are retained for their owner. The demo fixture is cleared on simulated logout to avoid showing previous local example state as another user's content.

## My documents - prototype refinement (2026-11-10)

A secondary Mine dokumenter action beside the account controls opens an owner-library surface with title, saved date and practice positions, plus Open and Delete per item. Empty state explains how to generate/save the first item. Back returns to the active workspace. Open restores that document's source/settings/results and independent positions without regeneration. Delete first shows an inline confirmation naming the document and including its learning material/progress, with Cancel and Delete document. Confirmed deletion clears the active view if that item is open; cancellation changes nothing. Show no fake exercise counts for insufficient-source items. The prototype supports several in-memory examples only, with no backend or real owner isolation. Actual app requires server/database/storage ownership checks and delete-failure recovery from the PRD.
