"""Cheap ordered revocation path, independent of parser/model permits."""
from fastapi import APIRouter, Request
from app.adapters.auth import AuthFailure
from app.adapters.model import ModelFailure
from app.api.private import authenticate, collect, error
from app.contracts.generation import WorkspaceCommand
from app.services.workspaces import WorkspaceFailure

router = APIRouter(prefix='/api/v1/workspaces')


@router.post('/invalidate')
async def invalidate(request: Request):
    try:
        session_id, session = await authenticate(request)
        submitted = await collect(request, WorkspaceCommand, limit=1024, member_limit=4)
        await request.app.state.workspaces.ordered_command(session_id, session, submitted.workspace_id,
            submitted.client_revision, submitted.command_sequence, 'invalidate', submitted)
        return {'schemaVersion': '1.0', 'clientRevision': submitted.client_revision,
                'commandSequence': submitted.command_sequence}
    except AuthFailure:
        return error('session_ended')
    except (ModelFailure, WorkspaceFailure) as failure:
        return error(failure.code)
