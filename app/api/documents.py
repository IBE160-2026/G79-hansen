"""Bounded private Save endpoints with owned work surviving lost HTTP replies."""
import asyncio
import time
from urllib.parse import quote
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
from app.adapters.auth import AuthFailure
from app.adapters.model import ModelFailure
from app.adapters.documents import DocumentFailure
from app.api.private import authenticate, collect, error
from app.contracts.documents import SaveRequest, RetryRequest, OperationRequest, ReloadRequest, DiscoverRequest
from app.services.workspaces import WorkspaceFailure

router = APIRouter(prefix='/api/v1/documents')
SAVE_SECONDS = 60


async def process(request, session_id, session, action, contract, deadline):
    try:
        # A 30,000-code-point source can have 15,000 one-character paragraphs.
        # Two copies use 30,000 structures/150,000 members, plus bounded
        # learning/envelope overhead. Other routes retain their smaller limits.
        submitted = await collect(request, contract, limit=4096 if action in {'library', 'file', 'reload'} else 16 * 1024 * 1024,
                                  member_limit=160_100, structure_limit=32_100)
        documents = request.app.state.documents
        identity = session.identity
        if action == 'save':
            result = await documents.save(session_id, session, submitted, deadline)
        elif action == 'retry':
            result = await documents.retry(identity, submitted, deadline)
        elif action == 'cleanup':
            result = await documents.cleanup(identity, submitted.operation_id, deadline)
        elif action == 'file':
            content, descriptor = await documents.download(identity, submitted, deadline)
            request.app.state.auth_registry.live_session(session_id, session)
            extension = '.pdf' if descriptor['mediaType'] == 'application/pdf' else '.txt'
            # The original upload name is not retained. Use a safe title-based
            # attachment name; never disclose an object key in a header.
            name = ''.join(c for c in descriptor['title'] if ord(c) >= 32 and c not in '/\\\x7f')[:160] or 'dokument'
            return Response(content, media_type=descriptor['mediaType'], headers={
                'Content-Disposition': "attachment; filename=original" + extension + "; filename*=UTF-8''" + quote(name + extension, safe=''),
                'X-Content-Type-Options': 'nosniff', 'Cache-Control': 'no-store'})
        else:
            result = await documents.rpc(identity, action, submitted.model_dump(mode='json', by_alias=True), deadline)
        request.app.state.auth_registry.live_session(session_id, session)
        return JSONResponse(result)
    except AuthFailure:
        return error('session_ended')
    except (DocumentFailure, WorkspaceFailure, ModelFailure) as failure:
        code = failure.code
        if action in {'library', 'reload', 'file'} and code in {'save_pending', 'save_unavailable'}:
            code = 'file_unavailable' if action == 'file' else 'library_unavailable'
        return error(code)
    except Exception:
        return error('file_unavailable' if action == 'file' else 'library_unavailable' if action in {'library', 'reload'} else 'save_pending')
    finally:
        request.app.state.save_admission.release(session_id)


async def run(request, action, contract):
    try:
        session_id, session = await authenticate(request)
        if not request.app.state.documents_injected:
            request.app.state.settings.save_backend_key()
        admission = request.app.state.save_admission
        admission.acquire(session_id)
    except AuthFailure:
        return error('session_ended')
    except (ModelFailure, DocumentFailure) as failure:
        return error(failure.code, save_disabled=not request.app.state.settings.save_enabled)
    deadline = time.monotonic() + SAVE_SECONDS
    task = asyncio.create_task(process(request, session_id, session, action, contract, deadline))
    admission.tasks.add(task)
    task.add_done_callback(admission.tasks.discard)
    # Never cancel the owner: its permit lasts through provider completion.
    done, _ = await asyncio.wait({task}, timeout=SAVE_SECONDS)
    return task.result() if done else error('save_pending')


@router.post('/save')
async def save(request: Request):
    return await run(request, 'save', SaveRequest)


@router.post('/retry')
async def retry(request: Request):
    return await run(request, 'retry', RetryRequest)


@router.post('/pending')
async def pending(request: Request):
    return await run(request, 'pending', DiscoverRequest)


@router.post('/cleanup')
async def cleanup(request: Request):
    return await run(request, 'cleanup', OperationRequest)


@router.post('/reload')
async def reload(request: Request):
    return await run(request, 'reload', ReloadRequest)


@router.post('/library')
async def library(request: Request):
    return await run(request, 'library', DiscoverRequest)


@router.post('/file')
async def file(request: Request):
    return await run(request, 'file', ReloadRequest)
