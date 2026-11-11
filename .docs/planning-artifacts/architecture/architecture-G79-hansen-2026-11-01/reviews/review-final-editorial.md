# Editorial review — architecture explanation, 2026-11-11

This document exists to help the student and assessor understand how Study Buddy's chosen behavior maps to its planned technical parts, what remains to choose, and how the work will be checked.

Reader: humans, especially the student. Model: **Explanation (Conceptual)**, with an initial status statement followed by responsibilities, concrete usage, technical consequences and checks. Baseline: Microsoft Writing Style Guide, calibrated to Norwegian explanatory prose and the document's direct, conversational voice. The technical content and adopted choices are preserved. Structure ran first; prose ran afterward against its recommendations.

Exact `word_metrics.py` count before edits: **872 words**. Sections: opening 25; choices 223; responsibility table 107; usage example 79; technical choices/milestones 195; accounts/setup 70; checks 84; next steps 46. No length target was supplied.

| Pass | Original Text | Revised Text | Changes |
| --- | --- | --- | --- |
| structure | §Tekniske valg og avgrensede milepæler, first two bullets: pypdf and Render precede fixed progress/session decisions. | MOVE the two candidate bullets into a short final subsection headed "Avklares før integrasjon og publisering" and label both "kandidat". Keep the adopted protocol/session/recovery explanation together before them. | The current mixed list makes the candidate hosting/PDF choices look as settled as the adopted technical rules. Moving preserves all facts and the distinction already stated in the spine; word impact approximately 0, excluding the short new heading. |
| structure | §Det du har valgt: three "Vedtatt 11.11.2026:" prefixes and the repeated "(vedtatt 11.11.2026)" inside the first dated paragraph. | CONDENSE by removing these four date markers; keep the top document update date and the section's adopted-choice meaning. | These eight words repeat the same date already present in the status and interrupt the explanation. Saves 8 words from a 223-word section without removing a decision. |
| prose | "Innloggingstilstanden styres av backend og oppbevares i minnet på én serverprosess i førsteversjonen." | "FastAPI-serveren håndterer innloggingstilstanden og oppbevarer den i minnet på én serverprosess i førsteversjonen." | Defines the actor using the component name already introduced, avoiding the unexplained English term "backend" for a beginner reader. Leaves the technical choice intact. |

Preserve the responsibility table, six-step usage example and separate checks. They reinforce different mental models rather than repeat the same prose. Preserve the explicit warning that the prototype is not runtime proof; it is important to the student/assessor audience.

Summary: three recommendations. The date condensation has a measurable reduction of **8 words (0.9% of 872)**; the move is length-neutral apart from its optional heading, and the prose change is length-neutral. No cut sacrifices an example, visual aid or other comprehension scaffolding. These are editorial improvements, not behavioral findings or blockers to implementation planning.

## Narrow follow-up

All three recommendations are applied: the PDF/Render candidates are labelled and separated under "Avklares før integrasjon og publisering"; repeated adopted-date markers are removed while the top update date remains; and the first unexplained "backend" is now "FastAPI-serveren". The responsibility table, usage example and testing/implementation limits are preserved. **Editorial findings closed; no remaining issue from this pass.**

Exact post-edit `word_metrics.py` total: **871 words**. The choice section is 215 words, down from 223. Added candidate labelling and subsection scaffolding offset most of that saving, yielding a net reduction of one word (0.1%); the useful outcome is clearer separation of adopted choices and milestone candidates, not a shorter document at the expense of comprehension.
