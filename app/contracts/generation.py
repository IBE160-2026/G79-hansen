"""Strict private generation protocol; signatures never confer authentication."""

from typing import Literal, Annotated
from pydantic import Field, StringConstraints, model_validator
from app.contracts.learning import Contract, LearningBundle
from app.contracts.sources import ExtractResponse

Identifier = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9_-]{16,80}$")]
Sequence = Annotated[int, Field(ge=1, le=9_007_199_254_740_991)]
Prose = Annotated[str, StringConstraints(min_length=1, max_length=1000)]


class WorkspaceCommand(Contract):
    schema_version: Literal["1.0"]
    workspace_id: Identifier
    client_revision: int = Field(ge=0, le=9_007_199_254_740_991)
    command_sequence: Sequence


class GenerationRequest(WorkspaceCommand):
    acceptance: ExtractResponse


class GenerationResponse(Contract):
    schema_version: Literal["1.0"] = "1.0"
    bundle: LearningBundle
    receipt: str
    client_revision: int
    command_sequence: int


class ModelSummary(Contract):
    text: Annotated[str, StringConstraints(min_length=1, max_length=1000)]
    references: list[str] = Field(min_length=1, max_length=3)


class ModelConcept(Contract):
    term: Annotated[str, StringConstraints(min_length=1, max_length=160)]
    explanation: Annotated[str, StringConstraints(min_length=1, max_length=800)]
    references: list[str] = Field(min_length=1, max_length=3)


class ModelPractice(Contract):
    question: Annotated[str, StringConstraints(min_length=1, max_length=500)]
    answer: Annotated[str, StringConstraints(min_length=1, max_length=800)]
    references: list[str] = Field(min_length=1, max_length=3)


class ModelInsufficiency(Contract):
    summary: Annotated[str, StringConstraints(min_length=1, max_length=500)] | None
    concepts: Annotated[str, StringConstraints(min_length=1, max_length=500)] | None
    flashcards: Annotated[str, StringConstraints(min_length=1, max_length=500)] | None
    quiz: Annotated[str, StringConstraints(min_length=1, max_length=500)] | None


class ModelOutput(Contract):
    summary: list[ModelSummary] = Field(max_length=6)
    concepts: list[ModelConcept] = Field(max_length=8)
    flashcards: list[ModelPractice] = Field(max_length=8)
    quiz: list[ModelPractice] = Field(max_length=8)
    warnings: list[Annotated[str, StringConstraints(min_length=1, max_length=500)]] = Field(max_length=8)
    insufficiency: ModelInsufficiency

    @model_validator(mode="after")
    def complete_parts(self):
        for name in ("summary", "concepts", "flashcards", "quiz"):
            if not getattr(self, name) and not getattr(self.insufficiency, name):
                raise ValueError("missing section explanation")
            for item in getattr(self, name):
                if len(item.references) != len(set(item.references)):
                    raise ValueError("duplicate reference")
                for value in item.model_dump().values():
                    if isinstance(value, str) and not value.strip():
                        raise ValueError("blank prose")
        for value in self.insufficiency.model_dump().values():
            if value is not None and not value.strip():
                raise ValueError("blank explanation")
        if any(not warning.strip() for warning in self.warnings):
            raise ValueError("blank warning")
        return self
