"""Source browser fixtures. This module is never imported by application code."""

from fastapi import Request
from fastapi.responses import Response

from auth_browser_app import app, adapter
from app.api.auth import current_session
from pdf_fixtures import make_pdf


@app.get("/__test/source-pdf")
def source_pdf():
    return Response(make_pdf(["Physical page one", None, "Physical page three", None], image_pages=(4,)),
                    media_type="application/pdf", headers={"Cache-Control": "no-store"})


@app.post("/__test/provider-denial")
def provider_denial(request: Request):
    registry = app.state.auth_registry
    with registry.lock:
        session = registry.sessions.get(current_session(request))
        if session:
            adapter.revoked.add(session.identity.access_token)
    return {"ok": True}

# Synthetic model injection is confined to this browser fixture module.
import tempfile
from pathlib import Path
from app.adapters.model import Completion, MODEL, ModelFailure
from app.services.model_budget import ModelBudget


class BrowserModel:
    def __init__(self):
        self.calls = 0
        self.mode = 'complete'
        self.last_settings = None

    async def complete(self, body):
        import json
        data = json.loads(json.loads(body)['input'][0]['content'])
        self.calls += 1
        self.last_settings = {key: data[key] for key in ('language', 'detail')}
        if self.mode == 'failure':
            self.mode = 'complete'
            raise ModelFailure()
        names = ('summary', 'concepts', 'flashcards', 'quiz')
        if self.mode == 'insufficient':
            self.mode = 'complete'
            return Completion({**dict.fromkeys(names, []), 'warnings': [],
                'insufficiency': dict.fromkeys(names, 'The source does not contain enough evidence.')}, 100, 100, MODEL)
        practice = [{'question': f'Practice question {n}', 'answer': f'Synthetic answer {n}', 'references': ['u1']}
                    for n in (1, 2)]
        return Completion({'summary': [{'text': 'Synthetic summary <img src=x onerror=window.compromised=true>', 'references': ['u1']}],
            'concepts': [{'term': 'Synthetic concept', 'explanation': 'Synthetic explanation', 'references': ['u1']}],
            'flashcards': practice, 'quiz': practice, 'warnings': [], 'insufficiency': dict.fromkeys(names)}, 100, 200, MODEL)


_model_directory = tempfile.TemporaryDirectory(prefix='studybuddy-browser-budget-')
_model_path = Path(_model_directory.name) / 'budget.json'
ModelBudget.initialize(_model_path)
model = BrowserModel()
app.state.model_adapter = model
app.state.model_injected = True
app.state.model_budget = ModelBudget(_model_path)


@app.post('/__test/model-failure')
def model_failure():
    model.mode = 'failure'
    return {'ok': True}


@app.post('/__test/model-insufficient')
def model_insufficient():
    model.mode = 'insufficient'
    return {'ok': True}


@app.get('/__test/model-state')
def model_state():
    return {'calls': model.calls, 'settings': model.last_settings,
            'reservedMicrousd': app.state.model_budget.read()['reservedMicrousd']}
