"""Canonical, transient sources. No source/settings are retained by this service."""

import base64
import binascii
import re
import unicodedata
from uuid import uuid4

from app.contracts.learning import Source, SourceUnit
from app.contracts.sources import ExtractRequest, ExtractResponse

MAX_BYTES = 10 * 1024 * 1024
MAX_CHARACTERS = 30_000
PDF_NOTICE = "Bare tekst som kan hentes ut av PDF-en vises. Bilder, tabeller og figurer tolkes ikke."


class ExtractionFailure(Exception):
    def __init__(self, code="invalid_input"):
        self.code = code
        super().__init__(code)


def canonical_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if any(unicodedata.category(char) in ("Cs", "Cc") and char not in "\n\t" for char in text):
        raise ExtractionFailure("invalid_text")
    return text


def decode_file(encoded):
    # Reject before decoding an oversized base64 value; no disk/multipart spool.
    if len(encoded) > 4 * ((MAX_BYTES + 2) // 3):
        raise ExtractionFailure("byte_limit")
    try:
        content = base64.b64decode(encoded, validate=True)
        # validate=True allows some noncanonical padding; the envelope requires strict base64.
        if base64.b64encode(content).decode("ascii") != encoded:
            raise ExtractionFailure("invalid_input")
    except (ValueError, binascii.Error):
        raise ExtractionFailure("invalid_input") from None
    if len(content) > MAX_BYTES:
        raise ExtractionFailure("byte_limit")
    return content


def prepare(submitted: ExtractRequest):
    canonical_text(submitted.settings.subject)
    if submitted.kind == "paste":
        return canonical_text(submitted.text)
    content = decode_file(submitted.contentBase64)
    if submitted.kind == "pdf":
        return content
    try:
        return canonical_text(content.decode("utf-8-sig", errors="strict"))
    except UnicodeError:
        raise ExtractionFailure("invalid_text") from None


def extract_text(submitted, text):
    if len(text) > MAX_CHARACTERS:
        raise ExtractionFailure("character_limit")
    paragraphs = [part for part in re.split(r"\n(?:[^\S\n]*\n)+", text) if part.strip()]
    if not paragraphs:
        raise ExtractionFailure("no_readable_text")
    units = [SourceUnit(id=f"paragraph-{n}", kind="paragraph", location=n, text=part)
             for n, part in enumerate(paragraphs, 1)]
    return response(submitted, units, len(text))


def extract_pdf_result(submitted, result):
    if result.status != "accepted":
        raise ExtractionFailure(result.code)
    units = [SourceUnit(id=unit.id, kind="page", location=unit.location,
                        text=canonical_text(unit.text)) for unit in result.units]
    warnings = [PDF_NOTICE]
    if result.unreadable_pages:
        warnings.append("Disse fysiske sidene har ingen lesbar tekst: " +
                        ", ".join(map(str, result.unreadable_pages)) + ". Dekningen er delvis.")
    return response(submitted, units, result.character_count,
                    total_pages=result.total_pages, unreadable_pages=list(result.unreadable_pages), warnings=warnings)


def response(submitted, units, count, **coverage):
    title = {"paste": "Innlimt tekst", "text-file": "Tekstfil", "pdf": "PDF"}[submitted.kind]
    return ExtractResponse(source=Source(id=str(uuid4()), title=title, units=units),
                           settings=submitted.settings, kind=submitted.kind,
                           character_count=count, client_revision=submitted.clientRevision, **coverage)
