"""Named synthetic fixture; no model calls, file writes or cloud configuration."""

from uuid import uuid4

from app.contracts.learning import (
    Concept, DemoFixture, LearningBundle, PracticeItem, Reference,
    Settings, Source, SourceUnit, SummaryItem,
)

FIXTURE_ID = "memory-basics-v1"


def get_fixture() -> DemoFixture:
    return DemoFixture(
        fixture_id=FIXTURE_ID,
        source=Source(
            id=FIXTURE_ID,
            title="Hukommelse og aktiv gjenhenting",
            units=[
                SourceUnit(id="memory-p1", kind="paragraph", location=1,
                           text="Arbeidsminnet holder og bearbeider informasjon i en kort periode."),
                SourceUnit(id="memory-p2", kind="paragraph", location=2,
                           text="Langtidsminnet lagrer informasjon over tid."),
                SourceUnit(id="memory-p3", kind="paragraph", location=3,
                           text="Aktiv gjenhenting betyr å forsøke å huske informasjon uten å se på kilden."),
            ],
        ),
        settings=Settings(),
    )


def reference(location: int) -> Reference:
    return Reference(source_unit_id=f"memory-p{location}", label=f"Avsnitt {location}")


def generate_demo() -> LearningBundle:
    fixture = get_fixture()
    return LearningBundle(
        generation_id=str(uuid4()), source=fixture.source, settings=fixture.settings,
        summary=[SummaryItem(
            id="summary-memory", text="Arbeidsminnet bearbeider informasjon kortvarig, mens langtidsminnet lagrer den over tid. Aktiv gjenhenting innebærer å prøve å huske uten å se på kilden.",
            references=[reference(1), reference(2), reference(3)],
        )],
        concepts=[
            Concept(id="concept-working", term="Arbeidsminne", explanation=fixture.source.units[0].text, references=[reference(1)]),
            Concept(id="concept-long", term="Langtidsminne", explanation=fixture.source.units[1].text, references=[reference(2)]),
            Concept(id="concept-retrieval", term="Aktiv gjenhenting", explanation=fixture.source.units[2].text, references=[reference(3)]),
        ],
        flashcards=[
            PracticeItem(id="card-working", question="Hva gjør arbeidsminnet?", answer="Det holder og bearbeider informasjon i en kort periode.", references=[reference(1)]),
            PracticeItem(id="card-long", question="Hva gjør langtidsminnet?", answer="Det lagrer informasjon over tid.", references=[reference(2)]),
            PracticeItem(id="card-retrieval", question="Hva betyr aktiv gjenhenting?", answer="Å forsøke å huske informasjon uten å se på kilden.", references=[reference(3)]),
        ],
        quiz=[
            PracticeItem(id="quiz-memory", question="Hva skiller arbeidsminnet fra langtidsminnet?", answer="Arbeidsminnet bearbeider informasjon kortvarig. Langtidsminnet lagrer informasjon over tid.", references=[reference(1), reference(2)]),
            PracticeItem(id="quiz-retrieval", question="Hvordan foregår aktiv gjenhenting?", answer="Man prøver å huske uten å se på kilden.", references=[reference(3)]),
        ],
    )
