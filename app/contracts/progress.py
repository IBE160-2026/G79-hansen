"""Small, strict owner-free progress protocol, independent of content Save."""
from typing import Literal
from pydantic import Field
from app.contracts.learning import Contract
from app.contracts.documents import Uuid


class ProgressPositions(Contract):
    flashcard_id: str | None = Field(max_length=100)
    quiz_id: str | None = Field(max_length=100)


class ProgressRead(Contract):
    schema_version: Literal['1.0']
    document_id: Uuid
    generation_id: Uuid


class ProgressWrite(ProgressRead):
    mutation_id: Uuid
    expected_progress_revision: int = Field(ge=1, le=9_007_199_254_740_990)
    positions: ProgressPositions


class ProgressResult(ProgressRead):
    progress_revision: int = Field(ge=1, le=9_007_199_254_740_991)
    positions: ProgressPositions
