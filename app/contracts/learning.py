"""Shared typed source and result contract, independent of the demo transport."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel


class Contract(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="forbid", strict=True
    )


class SourceUnit(Contract):
    id: str = Field(min_length=1)
    kind: Literal["paragraph", "page"]
    location: int = Field(ge=1)
    text: str = Field(min_length=1)


class Source(Contract):
    schema_version: Literal["1.0"] = "1.0"
    id: str
    title: str
    units: list[SourceUnit] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_ordered_units(self) -> Self:
        if len({unit.id for unit in self.units}) != len(self.units):
            raise ValueError("Source unit IDs must be unique")
        if [unit.location for unit in self.units] != sorted(
            {unit.location for unit in self.units}
        ):
            raise ValueError("Source locations must be unique and ordered")
        return self


class Settings(Contract):
    language: Literal["nb", "en"] = "nb"
    detail: Literal["short", "detailed"] = "short"
    subject: str = Field(default="", max_length=200)


class Reference(Contract):
    source_unit_id: str
    label: str


class ReferencedItem(Contract):
    id: str = Field(min_length=1)
    references: list[Reference] = Field(min_length=1)


class SummaryItem(ReferencedItem):
    text: str = Field(min_length=1)


class Concept(ReferencedItem):
    term: str = Field(min_length=1)
    explanation: str = Field(min_length=1)


class PracticeItem(ReferencedItem):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class Insufficiency(Contract):
    summary: str | None = None
    concepts: str | None = None
    flashcards: str | None = None
    quiz: str | None = None


class LearningBundle(Contract):
    schema_version: Literal["1.0"] = "1.0"
    generation_id: str
    source: Source
    settings: Settings
    summary: list[SummaryItem]
    concepts: list[Concept]
    flashcards: list[PracticeItem]
    quiz: list[PracticeItem]
    warnings: list[str] = Field(default_factory=list)
    insufficiency: Insufficiency = Field(default_factory=Insufficiency)

    @model_validator(mode="after")
    def validate_items_and_references(self) -> Self:
        units = {unit.id: unit for unit in self.source.units}
        item_ids: set[str] = set()
        for name in ("summary", "concepts", "flashcards", "quiz"):
            items = getattr(self, name)
            if not items and not getattr(self.insufficiency, name):
                raise ValueError(f"Empty {name} needs an insufficiency explanation")
            for item in items:
                if item.id in item_ids:
                    raise ValueError("Learning item IDs must be unique")
                item_ids.add(item.id)
                for reference in item.references:
                    unit = units.get(reference.source_unit_id)
                    if unit is None:
                        raise ValueError("Unknown source unit reference")
                    expected = f"{'Avsnitt' if unit.kind == 'paragraph' else 'Side'} {unit.location}"
                    if reference.label != expected:
                        raise ValueError("Reference label must match its source location")
        return self


class DemoRequest(BaseModel):
    # Only these wire names are accepted; arbitrary source/settings are unsupported.
    model_config = ConfigDict(extra="forbid", strict=True)
    schemaVersion: Literal["1.0"]
    fixtureId: Literal["memory-basics-v1"]


class DemoFixture(Contract):
    schema_version: Literal["1.0"] = "1.0"
    fixture_id: str
    source: Source
    settings: Settings
