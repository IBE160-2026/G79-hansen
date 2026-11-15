"""Transient source input. Wire names are deliberately strict and owner-free."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.contracts.learning import Contract, Settings, Source


class ExtractRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schemaVersion: Literal["1.0"]
    kind: Literal["paste", "text-file", "pdf"]
    settings: Settings
    clientRevision: int = Field(ge=0, le=9_007_199_254_740_991)
    workspaceId: str = Field(pattern=r"^[A-Za-z0-9_-]{16,80}$")
    commandSequence: int = Field(ge=1, le=9_007_199_254_740_991)
    text: str | None = None
    contentBase64: str | None = None

    @model_validator(mode="after")
    def one_input(self) -> Self:
        expected = "text" if self.kind == "paste" else "contentBase64"
        other = "contentBase64" if self.kind == "paste" else "text"
        if expected not in self.model_fields_set or other in self.model_fields_set or getattr(self, expected) is None:
            raise ValueError("Exactly one input is required")
        return self


class ExtractResponse(Contract):
    schema_version: Literal["1.0"] = "1.0"
    source: Source
    settings: Settings
    kind: Literal["paste", "text-file", "pdf"]
    character_count: int = Field(ge=1, le=30_000)
    total_pages: int | None = Field(default=None, ge=1, le=40)
    unreadable_pages: list[int] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    client_revision: int
    workspace_id: str = ""
    command_sequence: int = 0
    source_proof: str = Field(default="", max_length=8192)
