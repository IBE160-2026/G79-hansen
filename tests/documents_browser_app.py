"""Synthetic browser-only Save ports; never imported by production code."""
from sources_browser_app import app, model
from test_documents import MemoryRepository, MemoryStorage
from app.services.documents import Documents

repository, storage = MemoryRepository(), MemoryStorage()
app.state.documents_injected = True
app.state.documents = Documents(repository, storage, app.state.workspaces, app.state.save_admission)


@app.post('/__test/save-failure')
def save_failure():
    repository.fail_action = 'commit'
    return {'ok': True}


@app.post('/__test/save-conflict')
def save_conflict():
    for value in repository.documents.values():
        value['revision'] += 1
    return {'ok': True}


@app.post('/__test/save-lose-ready')
def lose_ready():
    repository.lose_ready_reply = True
    return {'ok': True}


@app.post('/__test/save-upload-failure')
def upload_failure():
    storage.fail_before_upload = True
    return {'ok': True}


@app.get('/__test/save-state')
def save_state():
    return {'documents': len(repository.documents), 'operations': len(repository.operations), 'modelCalls': model.calls,
            'positions': [value['positions'] for value in repository.documents.values()], 'files':len(storage.objects)}


@app.post('/__test/save-restart')
def restart():
    registry = app.state.auth_registry
    for session in tuple(registry.sessions.values()):
        registry.terminate(session.browser_id)
    return {'ok': True}


@app.post('/__test/save-terminal/{operation_id}/{status}')
def terminal(operation_id: str, status: str):
    assert status in ('expired','conflict')
    operation=next(value for value in repository.operations.values() if value['operationId']==operation_id)
    operation.update(status=status,snapshot=None,cleanupNeeded=bool(operation.get('objectKey')))
    return {'ok': True}
