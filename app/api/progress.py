"""Authenticated bounded progress endpoints; mutations survive lost replies."""
import asyncio
import time
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.adapters.auth import AuthFailure
from app.adapters.documents import DocumentFailure
from app.adapters.model import ModelFailure
from app.api.private import authenticate, collect, error
from app.contracts.progress import ProgressRead, ProgressWrite
from app.services.progress import Progress

router = APIRouter(prefix='/api/v1/progress')
PROGRESS_SECONDS = 15


async def process(request, session_id, session, write, deadline):
    try:
        submitted = await collect(request, ProgressWrite if write else ProgressRead, limit=4096,
                                  member_limit=16, structure_limit=3)
        result = await Progress(request.app.state.documents).execute(session.identity, submitted, write=write, deadline=deadline)
        request.app.state.auth_registry.live_session(session_id, session)
        return JSONResponse(result)
    except AuthFailure:
        return error('session_ended')
    except (DocumentFailure, ModelFailure) as failure:
        return error(failure.code)
    except Exception:
        return error('progress_pending')
    finally:
        request.app.state.save_admission.release(session_id)


async def run(request, write):
    try:
        session_id, session = await authenticate(request)
        if not request.app.state.documents_injected:
            request.app.state.settings.save_backend_key()
        request.app.state.save_admission.acquire(session_id)
    except AuthFailure:
        return error('session_ended')
    except (DocumentFailure, ModelFailure) as failure:
        return error(failure.code)
    admission = request.app.state.save_admission
    task = asyncio.create_task(process(request, session_id, session, write, time.monotonic() + PROGRESS_SECONDS))
    admission.tasks.add(task)
    task.add_done_callback(admission.tasks.discard)
    done, _ = await asyncio.wait({task}, timeout=PROGRESS_SECONDS)
    return task.result() if done else error('progress_pending')


@router.post('/read')
async def read(request: Request):
    return await run(request, False)


@router.post('/write')
async def write(request: Request):
    return await run(request, True)
