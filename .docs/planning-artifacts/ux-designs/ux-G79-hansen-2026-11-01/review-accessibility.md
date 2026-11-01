# UX accessibility review - AI Study Buddy

Date: 2026-11-01. Scope: code inspection of DESIGN.md, EXPERIENCE.md and .working/key-study.html. No browser, screen-reader or automated accessibility engine was run; findings below are source-based, not a WCAG conformance claim. Prototype uses fixed example data without backend/AI by explicit user instruction.

## Overall verdict

The specification has an adequate accessibility floor and the prototype uses labelled native controls, visible button focus, keyboard-operated tabs, expanded-state answer controls and genuinely hidden answer content. Correct focus handling and the initial edit state before treating the prototype as a reliable keyboard walkthrough. No additional product clarification is needed for these fixes.

## Findings

### High - focus may be hidden when successful generation collapses the panel

Location: key-study.html, setMaterialOpen and the generation timeout callback.

After the keyboard user activates Lag laeringsmateriale, completion hides material-body (including the initiating button) without assigning focus to a visible control. Disabled-button behavior and resulting focus depend on browser; the code does not implement EXPERIENCE.md's visible-focus requirement.

Fix: at successful collapse, move focus predictably to Vis/rediger or the active Sammendrag tab and announce completion. When resetting, focus the expanded source entry or method control. Preserve source/settings/progress while expanding.

### Medium - first expansion does not open the source text

Location: key-study.html, initial source-disclosure markup and edit-material.onclick.

The initial rendered sample-result state has both the material body and its nested details closed. Vis/rediger opens only the outer body; the text remains under a second Vis materialet control. This conflicts with the agreed open text inside the expanded panel and makes editing require an unexpected extra disclosure. After successful generation this differs because that callback sets details.open=true.

Fix: remove the obsolete nested disclosure or always open it when the full panel expands, including initial editing.

### Medium - practice navigation moves focus to the opposite button without announcing the new item

Location: key-study.html, previous.onclick and next.onclick.

Next rerenders the content and focuses Previous; Previous focuses Next. The item counter/question has changed earlier in reading order, but there is no live item announcement or heading focus. A screen-reader user may hear only the opposite navigation control and miss which card/question is now active; repeated keyboard Next also requires repositioning.

Fix: retain focus on the same navigation action when still enabled, otherwise focus the new item heading/counter. Announce the updated card/question position and question in a concise status or focusable heading. Do not announce hidden answers/references.

### Medium - compact heading row needs narrow/zoom reflow verification

Location: key-study.html CSS, .material-heading.

The row uses display:flex without wrapping or shrinking rules for the heading and Vis/rediger button. The responsive rule stacks settings but does not alter this heading row. Combined minimum widths can overflow a narrow or zoomed viewport.

Fix: allow the heading row to wrap, retain a 44px action target and avoid clipping. Verify at narrow viewport and 200% zoom in the browser; code inspection alone cannot establish actual overflow dimensions.

### Low - invalid input is announced but not associated with its field

Location: key-study.html, empty/oversized validation branches.

The polite status message explains the problem, but the invalid text/file field has no aria-invalid or aria-describedby relationship to that message, and focus is not directed to it.

Fix: associate the validation message with the active source field, set aria-invalid only on actual invalid input, and focus that field on rejected submission. Clear invalid state after correction/reset. Do not mark the optional subject field invalid.

## Checked and adequate by inspection

- lang=no, visible persistent field labels and labelled file input.
- One active input method is visible; hidden inactive methods are excluded with hidden CSS.
- Tabs use tablist/tab/tabpanel, roving tabindex, selected state and Left/Right/Home/End navigation. Shared dynamic panel label follows the selected tab.
- Answers and references share hidden content and reveal controls expose aria-expanded/aria-controls.
- Independent card/question positions and per-item reveal state survive tab changes.
- Buttons have 44px minimum height; primary/secondary hierarchy is preserved.
- Status is a polite live region; no unnecessary animation or timed learning progression.
- Main text palette combinations already computed in DESIGN.md exceed 4.5:1. Actual focus/error/disabled rendering still requires browser inspection.
- Error simulation, PDF processing and arbitrary-source/language generation are intentionally absent from this local example-data prototype; implementation still owes the PRD's behavior and real-content evaluation.

## Follow-up checks in browser/implementation

Keyboard-only walkthrough through expansion, generation, tabs, reveal, Next/Previous and reset; screen-reader announcements; visible focus after collapse; narrow/zoom reflow; input errors and technical retry states. Keep these distinct from the completed source inspection.

## Resolution after review - 2026-11-01

All actionable source-level findings in this report were addressed before synthesis: source disclosure opens with the panel; collapse/reset focus is explicit; directional navigation retains usable focus and announces position/question; heading row wraps; validation errors are associated with the active field and cleared on correction/reset. Initial page starts with the panel open and results hidden. Compact padding token is 16px. Documentation identifies the active clickable prototype, fixed examples and specification-only states. Node state checks pass after changes. Browser, zoom and screen-reader checks remain implementation/manual validation work; no conformance claim is made.
