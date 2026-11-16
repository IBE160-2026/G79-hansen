"""Strict, owner-free Save wire contracts and versioned immutable projection."""
from typing import Annotated, Literal
from uuid import UUID
from pydantic import Field, StringConstraints, model_validator
from app.contracts.learning import Contract, LearningBundle
from app.contracts.sources import ExtractResponse
from app.services.receipts import acceptance_projection, digest

Uuid = Annotated[str, StringConstraints(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')]
Hash = Annotated[str, StringConstraints(pattern=r'^[0-9a-f]{64}$')]


class Positions(Contract):
    flashcard_id: str | None = Field(default=None, max_length=100)
    quiz_id: str | None = Field(default=None, max_length=100)


class SaveRequest(Contract):
    schema_version: Literal['1.0']
    operation_id: Uuid
    document_id: Uuid
    expected_revision: int | None = Field(default=None, ge=1, le=9_007_199_254_740_991)
    title: str | None = Field(default=None, max_length=160)
    acceptance: ExtractResponse
    bundle: LearningBundle
    receipt: str = Field(min_length=1, max_length=8192)
    positions: Positions
    content_base64: str | None = Field(default=None, max_length=13_981_016)

    @model_validator(mode='after')
    def consistent(self):
        if self.bundle.source != self.acceptance.source or self.bundle.settings != self.acceptance.settings:
            raise ValueError('source mismatch')
        if self.acceptance.kind == 'paste' and self.content_base64 is not None:
            raise ValueError('unexpected file')
        title = self.title if self.title is not None else self.bundle.source.title
        if not title.strip() or len(title) > 160 or any(ord(c) < 32 or 0xd800 <= ord(c) <= 0xdfff for c in title):
            raise ValueError('invalid title')
        UUID(self.document_id)
        return self


class RetryRequest(Contract):
    schema_version: Literal['1.0']
    operation_id: Uuid
    digest: Hash
    content_base64: str | None = Field(default=None, max_length=13_981_016)


class OperationRequest(Contract):
    schema_version: Literal['1.0']
    operation_id: Uuid


class ReloadRequest(Contract):
    schema_version: Literal['1.0']
    document_id: Uuid


class DiscoverRequest(Contract):
    schema_version: Literal['1.0']
    cursor: Uuid | None = None


def snapshot(submitted, owner_id, file_hash, file_size):
    """No bearer proof/receipt, original bytes, credentials, or transport timestamp."""
    positions = submitted.positions.model_dump(mode='json', by_alias=True)
    for section, key in (('flashcards', 'flashcardId'), ('quiz', 'quizId')):
        items = getattr(submitted.bundle, section)
        if submitted.expected_revision is not None:
            positions[key] = items[0].id if items else None
        elif positions[key] not in ({item.id for item in items} if items else {None}):
            raise ValueError('invalid position')
    return {'schemaVersion': '1.0', 'ownerId': owner_id, 'documentId': submitted.document_id,
            'generationId': submitted.bundle.generation_id, 'expectedRevision': submitted.expected_revision,
            'title': submitted.title if submitted.title is not None else submitted.bundle.source.title,
            'acceptance': acceptance_projection(submitted.acceptance),
            'bundle': submitted.bundle.model_dump(mode='json', by_alias=True), 'positions': positions,
            'fileHash': file_hash, 'fileSize': file_size}


def snapshot_digest(value):
    return digest(value)
