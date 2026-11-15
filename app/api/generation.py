"""One bounded generation with owned cleanup and no partial result publication."""
import asyncio
import time
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.adapters.auth import AuthFailure
from app.adapters.model import ModelFailure
from app.api.private import authenticate, collect, error
from app.contracts.generation import GenerationRequest
from app.services.generation import generate
from app.services.model_budget import BudgetFailure
from app.services.workspaces import WorkspaceFailure

router = APIRouter(prefix='/api/v1/generation')
GENERATION_SECONDS = 60


async def process(request, session_id, session, cancelled, deadline):
    admission = request.app.state.generation_admission
    try:
        submitted = await collect(request, GenerationRequest)
        result = await generate(request.app, session_id, session, submitted,
                                deadline=deadline, cancelled=cancelled.is_set)
        response = JSONResponse(result.model_dump(mode='json', by_alias=True))
        request.app.state.auth_registry.live_session(session_id, session)
        return response
    except AuthFailure:
        return error('session_ended')
    except (WorkspaceFailure, ModelFailure) as failure:
        return error(failure.code)
    except BudgetFailure:
        return error('budget_unavailable')
    except TimeoutError:
        return error('generation_timeout')
    except Exception:
        return error('generation_failed')
    finally:
        admission.release(session_id)


@router.post('')
async def generation(request: Request):
    try:
        session_id, session = await authenticate(request)
        request.app.state.generation_admission.acquire(session_id)
    except AuthFailure:
        return error('session_ended')
    except ModelFailure as failure:
        return error(failure.code)
    cancelled = asyncio.Event()
    deadline = time.monotonic() + GENERATION_SECONDS
    task = asyncio.create_task(process(request, session_id, session, cancelled, deadline))
    expired = False
    def expire():
        nonlocal expired
        if not expired:
            expired = True
            cancelled.set()
            task.cancel()
    # Owned by the work, so client disconnection cannot discard its deadline.
    timer = asyncio.get_running_loop().call_later(max(0, deadline - time.monotonic()), expire)
    task.add_done_callback(lambda _: timer.cancel())
    admission = request.app.state.generation_admission
    admission.tasks.add(task)
    task.add_done_callback(admission.tasks.discard)
    # The task owns the permit through real network cleanup, even on disconnect.
    try:
        done, _ = await asyncio.wait({task}, timeout=max(0, deadline - time.monotonic()))
        if done:
            if expired:
                return error('generation_timeout')
            return task.result()
        expire()
        return error('generation_timeout')
    except asyncio.CancelledError:
        cancelled.set()
        raise
