"""Model admission, grounded reference resolution, and atomic complete publication."""
import asyncio
import time
from threading import RLock
from uuid import uuid4
from app.adapters.model import MODEL, ModelFailure, request_bytes
from app.contracts.generation import GenerationResponse, ModelOutput
from app.contracts.learning import LearningBundle
from app.services.receipts import canonical


class GenerationAdmission:
    def __init__(self):
        self.sessions = set()
        self.lock = RLock()
        self.tasks = set()

    def acquire(self, session_id):
        with self.lock:
            if session_id in self.sessions or len(self.sessions) >= 2:
                raise ModelFailure('generation_capacity')
            self.sessions.add(session_id)

    def release(self, session_id):
        with self.lock:
            self.sessions.discard(session_id)


def resolve(accepted, output):
    validated = ModelOutput.model_validate(output)
    if accepted.settings.detail == 'short' and len(validated.summary) > 3:
        raise ModelFailure()
    if len(accepted.warnings) + len(validated.warnings) > 8:
        raise ModelFailure()
    units = {f'u{i}': unit for i, unit in enumerate(accepted.source.units, 1)}
    parts = {}
    for name in ('summary', 'concepts', 'flashcards', 'quiz'):
        parts[name] = []
        for item in getattr(validated, name):
            value = item.model_dump()
            references = []
            for key in value.pop('references'):
                if key not in units:
                    raise ModelFailure('unknown_reference')
                unit = units[key]
                references.append({'sourceUnitId': unit.id,
                                   'label': f"{'Side' if unit.kind == 'page' else 'Avsnitt'} {unit.location}"})
            parts[name].append({'id': str(uuid4()), **value, 'references': references})
    # Extraction notices remain explicit, in Norwegian UI metadata; generated prose
    # follows the selected language and is separately bounded by the model contract.
    return LearningBundle(generation_id=str(uuid4()), source=accepted.source, settings=accepted.settings,
                          **parts, warnings=[*accepted.warnings, *validated.warnings],
                          insufficiency=validated.insufficiency.model_dump())


async def generate(application, session_id, session, submitted, *, deadline=None, cancelled=lambda: False):
    def current_wait():
        if cancelled() or (deadline is not None and time.monotonic() >= deadline):
            raise ModelFailure('generation_timeout')

    current_wait()
    registry, workspaces = application.state.auth_registry, application.state.workspaces
    with registry.lock, workspaces.lock:
        workspaces.verify_source(session_id, session, submitted)
        workspaces.command(session_id, session, submitted.workspace_id, submitted.client_revision,
                           submitted.command_sequence, 'generate', submitted)
    if not application.state.settings.model_available and not application.state.model_injected:
        raise ModelFailure('model_unavailable')
    body = request_bytes(submitted.acceptance)
    registry.live_session(session_id, session)
    current_wait()
    # This await retains ownership through actual filesystem cleanup. It never
    # blocks the event loop or holds authentication/workspace locks during I/O.
    await application.state.model_budget.reserve_for_dispatch()
    current_wait()
    with workspaces.locked(session_id, session, submitted.workspace_id) as record:
        workspaces.current(record, submitted.client_revision, submitted.command_sequence, 'generate')
        workspaces.verify_source(session_id, session, submitted)
    current_wait()
    try:
        completion = await application.state.model_adapter.complete(body)
    except ModelFailure as failure:
        if failure.usage is not None:
            await application.state.model_budget.observe_async(*failure.usage)
        raise
    await application.state.model_budget.observe_async(completion.input_tokens, completion.output_tokens)
    current_wait()
    if completion.model != MODEL:
        raise ModelFailure()
    bundle = resolve(submitted.acceptance, completion.output)
    # Build bounded response before assigning any receipt authority.
    provisional = GenerationResponse(bundle=bundle, receipt='', client_revision=submitted.client_revision,
                                     command_sequence=submitted.command_sequence)
    if len(canonical(provisional)) + 8192 > 2 * 1024 * 1024:
        raise ModelFailure('provider_output_limit')
    current_wait()
    provisional.receipt = workspaces.publish(session_id, session, submitted, bundle)
    registry.live_session(session_id, session, touch=True)
    return provisional
