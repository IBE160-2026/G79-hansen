---
title: Keep demo status consistent with the active learning tab
type: bugfix
created: 2026-11-19
status: done
route: oneshot
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="User explicitly requested fixing the observed stale demo status">

## Intent

When switching from flashcard2 to quiz1, the demo status still describes the
flashcard. Update the live status when any learning tab is selected by mouse
or keyboard. Practice tabs describe their current item; summary/concepts name
the selected section; empty sections describe insufficient material. Preserve
independent positions, revealed answers, focus behavior and request count.
Do not change live-mode services, credentials, backend, running app or hosting.

</frozen-after-approval>

## Implementation Notes

Small local fix with no intent gaps, irreversible actions or new production
surface. Reuse the existing status-announcement function in app/static/app.js
from navigation and tab selection. Add focused regression assertions to the
existing tests/browser-demo.cjs for mouse/keyboard switching, retained state,
unchanged generation count and empty sections. Run that demo suite once with
app variables removed from its child environment; no model/provider calls or
other suites. Record actual verification, close B1 and update delivery notes.

Implemented announceSection() for practice, summary/concepts and empty sections;
both navigation and tab selection call it. Initial generation success messaging
is unchanged. No position/reveal mutation or new network dispatch was added.
One bounded independent review was used; no additional review layers or agents.

## Review Triage Log

| Finding | Verdict | Resolution |
| --- | --- | --- |
| R1: practice assertions only checked status prefixes, allowing stale/missing question text | low verification gap | Compare complete status with the selected fixture question for each switch and return. |
| R2: new selection assertions omitted focus checks, especially empty sections | low verification gap | Assert selected-tab focus after pointer/keyboard switches, including empty tabs. |

Both were small test corrections; no production defect or deferred finding
remained from the review. Re-running the same demo suite after these assertions.


## Review Triage Log

One bounded independent review; no additional review layers or implementation agents.

| Finding | Verdict and resolution |
| --- | --- |
| R1: status assertions matched only number/total, allowing stale or missing question text | low verification gap; direct assertions now compare full status against the selected fixture item, including return switches. |
| R2: new selection cases did not explicitly preserve focused tab | low verification gap; direct focused-element assertions now cover mouse/keyboard switches and all empty sections. |

Both are direct test corrections. No production defect was reported by the reviewer; no findings deferred.
Final verification:13 demo browser scenarios passed,21 fixed-demo generation requests observed. App/provider/model/email credentials and external DEMO_BASE_URL removed from the child environment. No other suites or real model/provider/email calls. Node syntax and scoped whitespace passed. Initial demo suite also passed; repeat was justified by the strengthened assertions after review.
