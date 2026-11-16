"""Bounded authenticated extraction, fenced to the same live session throughout."""

import asyncio
import json
import hashlib
from threading import RLock
from uuid import uuid4

from anyio import CapacityLimiter, to_thread
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.requests import ClientDisconnect

from app.adapters.auth import AuthFailure
from app.adapters.pdf import extract_pdf
from app.api.auth import BROWSER_COOKIE, context, current_session, protected
from app.contracts.sources import ExtractRequest
from app.services.extraction import ExtractionFailure, extract_pdf_result, extract_text, prepare
from app.services.workspaces import WorkspaceFailure
from app.services.extraction import decode_file, canonical_text

router = APIRouter(prefix="/api/v1/sources")
MAX_WIRE_BYTES = 14 * 1024 * 1024
BODY_SECONDS = 5.0
MESSAGES = {
    "invalid_input": "Velg én kilde og kontroller materialet før du prøver igjen.",
    "invalid_text": "Teksten må være gyldig UTF-8 uten binære kontrolltegn.",
    "character_limit": "Materialet kan ha høyst 30 000 tegn. Ingen del er godtatt.",
    "byte_limit": "Filen kan være høyst 10 MiB. Ingen del er godtatt.",
    "wire_limit": "Opplastingen er for stor. Ingen del er godtatt.",
    "page_limit": "PDF-en kan ha høyst 40 fysiske sider, også blanke sider og bildesider.",
    "no_readable_text": "Materialet har ingen lesbar tekst. OCR er ikke tilgjengelig.",
    "encrypted_pdf": "Krypterte PDF-er støttes ikke. Passord kan ikke oppgis.",
    "invalid_pdf": "PDF-en kunne ikke leses. Ingen del er godtatt.",
    "isolation_unavailable": "Sikker PDF-behandling er ikke tilgjengelig på denne serveren.",
    "source_capacity": "For mye materiale behandles nå. Vent litt og prøv igjen.",
    "body_timeout": "Opplastingen tok for lang tid. Prøv igjen.",
    "session_ended": "Tilgangen er avsluttet. Logg inn på nytt.",
    "request_rejected": "Forespørselen ble avvist. Last siden på nytt og prøv igjen.",
    "extraction_failed": "Materialet kunne ikke behandles. Prøv igjen.",
}


def error(code, status=None):
    if code not in MESSAGES:
        code = "extraction_failed"
    if status is None:
        status = {"session_ended": 401, "request_rejected": 403, "source_capacity": 429,
                  "body_timeout": 408, "wire_limit": 413, "byte_limit": 413,
                  "extraction_failed": 503, "isolation_unavailable": 503}.get(code, 422)
    return JSONResponse({"code": code, "message": MESSAGES[code], "requestId": str(uuid4())}, status_code=status)


class Admission:
    """No queue; permits belong to actual work, including post-cancellation cleanup."""
    def __init__(self):
        self.sessions = set()
        self.pdf_active = False
        self.lock = RLock()
        self.tasks = set()
        self.pdf_limiter = CapacityLimiter(1)
        self.parse_limiter = CapacityLimiter(2)

    def acquire(self, session_id):
        with self.lock:
            if len(self.sessions) >= 2 or session_id in self.sessions:
                raise ExtractionFailure("source_capacity")
            self.sessions.add(session_id)

    def release(self, session_id):
        with self.lock:
            self.sessions.discard(session_id)

    async def pdf(self, content):
        with self.lock:
            if self.pdf_active:
                raise ExtractionFailure("source_capacity")
            self.pdf_active = True
        try:
            return await to_thread.run_sync(extract_pdf, content, limiter=self.pdf_limiter)
        finally:
            with self.lock:
                self.pdf_active = False


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate field")
        result[key] = value
    return result


def decode_envelope(raw):
    # This protocol has only an envelope/settings object and scalar fields.
    # Refuse arbitrary object graphs before json.loads allocates them. Structural
    # characters inside strings (including escaped quotes) remain source text.
    quoted = escaped = False
    depth = members = 0
    for char in raw:
        if quoted:
            if escaped:
                escaped = False
            elif char == 92:
                escaped = True
            elif char == 34:
                quoted = False
        elif char == 34:
            quoted = True
        elif char in (91, 93):
            raise ExtractionFailure("invalid_input")
        elif char == 123:
            depth += 1
            if depth > 2:
                raise ExtractionFailure("invalid_input")
        elif char == 125:
            depth -= 1
        elif char == 58:
            members += 1
            if members > 16:
                raise ExtractionFailure("invalid_input")
    try:
        return ExtractRequest.model_validate(json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object))
    except (ValueError, UnicodeError, ValidationError, RecursionError):
        raise ExtractionFailure("invalid_input") from None


async def collect(request):
    if request.headers.get("content-type", "").split(";")[0].strip() != "application/json":
        raise ExtractionFailure("invalid_input")
    lengths = request.headers.getlist("content-length")
    if lengths and (len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit()):
        raise ExtractionFailure("invalid_input")
    if lengths and int(lengths[0]) > MAX_WIRE_BYTES:
        raise ExtractionFailure("wire_limit")
    raw = bytearray()
    try:
        async with asyncio.timeout(BODY_SECONDS):
            async for chunk in request.stream():
                if len(chunk) > MAX_WIRE_BYTES - len(raw):
                    raise ExtractionFailure("wire_limit")
                raw.extend(chunk)
    except TimeoutError:
        raise ExtractionFailure("body_timeout") from None
    except ClientDisconnect:
        raise ExtractionFailure("invalid_input") from None
    return await to_thread.run_sync(decode_envelope, raw,
                                   limiter=request.app.state.source_admission.parse_limiter)


async def process(request, session_id, session, admission):
    registry = request.app.state.auth_registry
    try:
        submitted = await collect(request)
        registry.live_session(session_id, session)
        canonical_text(submitted.settings.subject)
        if submitted.kind == 'paste':
            canonical_text(submitted.text)
        workspaces = request.app.state.workspaces
        await workspaces.ordered_command(session_id, session, submitted.workspaceId, submitted.clientRevision,
                           submitted.commandSequence, 'extract', submitted)
        content = await to_thread.run_sync(prepare, submitted, limiter=admission.parse_limiter)
        registry.live_session(session_id, session)
        if submitted.kind == "pdf":
            result = extract_pdf_result(submitted, await admission.pdf(content))
        else:
            result = extract_text(submitted, content)
        # Construct/serialize first, then atomically check and touch with no await
        # before returning. Logout, replacement and expiry always defeat old work.
        file_hash = (hashlib.sha256(decode_file(submitted.contentBase64)).hexdigest()
                     if submitted.kind != 'paste' else None)
        result = workspaces.accept(session_id, session, submitted, result, file_hash)
        response = JSONResponse(result.model_dump(mode="json", by_alias=True))
        registry.live_session(session_id, session, touch=True)
        return response
    except AuthFailure:
        return error("session_ended")
    except ExtractionFailure as exc:
        return error(exc.code)
    except WorkspaceFailure as exc:
        from app.api.private import error as workspace_error
        return workspace_error(exc.code)
    except Exception:
        # Parser/transport details and private strings never become diagnostics.
        return error("extraction_failed")
    finally:
        admission.release(session_id)


@router.post("/extract")
async def extract(request: Request):
    settings, registry, adapter = context(request)
    if not protected(request, settings, registry):
        return error("request_rejected")
    if not settings.available:
        return error("session_ended")
    session_id = current_session(request)
    browser_id = request.cookies.get(BROWSER_COOKIE)
    try:
        identity = await registry.authenticated_async(session_id, browser_id, adapter, touch=False)
        views = request.headers.getlist("x-session-view")
        session = registry.live_session(session_id)
        if identity is None or len(views) != 1 or not registry.session_view_matches(session, views[0]):
            return error("session_ended")
        admission = request.app.state.source_admission
        admission.acquire(session_id)
    except AuthFailure:
        return error("session_ended")
    except ExtractionFailure as exc:
        return error(exc.code)
    task = asyncio.create_task(process(request, session_id, session, admission))
    admission.tasks.add(task)
    task.add_done_callback(admission.tasks.discard)
    return await asyncio.shield(task)
