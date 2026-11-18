import logging
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

from app.api.auth import router as auth_router
from app.api.demo import router
from app.api.sources import Admission, router as sources_router
from app.adapters.auth import SupabaseAuth
from app.config import Settings
from app.services.sessions import Registry, Revocations
from app.services.email_admission import EmailAdmission
from app.services.workspaces import Workspaces
from app.services.model_budget import ModelBudget
from app.services.generation import GenerationAdmission
from app.adapters.model import OpenAIModel
from app.api.generation import router as generation_router
from app.api.workspaces import router as workspaces_router
from app.api.documents import router as documents_router
from app.api.progress import router as progress_router
from app.adapters.documents import SupabaseDocuments
from app.adapters.storage import SupabaseStorage
from app.services.documents import Documents, SaveAdmission

PUBLIC = Path(__file__).parent / 'static'


class RedactAuthQuery(logging.Filter):
    def filter(self, record):
        if isinstance(record.args, tuple) and len(record.args) == 5:
            args = list(record.args)
            # Redact all query strings, including percent-encoded callback paths.
            if isinstance(args[2], str):
                args[2] = args[2].split('?', 1)[0]
                record.args = tuple(args)
        return True


logging.getLogger('uvicorn.access').addFilter(RedactAuthQuery())


def create_app(settings=None, *, auth_adapter=None, registry=None, model_adapter=None,
               workspaces=None, model_budget=None, documents_repository=None, storage_adapter=None,
               email_admission=None):
    settings = settings if settings is not None else Settings.from_env()
    application = FastAPI(title='Study Buddy', version='0.1.0', redirect_slashes=False)
    application.state.settings = settings
    application.state.auth_registry = registry if registry is not None else Registry(
        idle_seconds=settings.idle_seconds, absolute_seconds=settings.absolute_seconds)
    application.state.auth_revocations = Revocations()
    application.state.auth_adapter = auth_adapter if auth_adapter is not None else SupabaseAuth(settings)
    application.state.email_admission = (email_admission if email_admission is not None
                                        else EmailAdmission(settings.auth_email_admission_path))
    application.state.source_admission = Admission()
    application.state.workspaces = workspaces if workspaces is not None else Workspaces(application.state.auth_registry)
    application.state.generation_admission = GenerationAdmission()
    application.state.model_adapter = model_adapter if model_adapter is not None else OpenAIModel(settings)
    application.state.model_injected = model_adapter is not None
    application.state.model_budget = model_budget if model_budget is not None else ModelBudget(settings.model_budget_path)
    application.state.save_admission = SaveAdmission()
    application.state.documents_injected = documents_repository is not None
    application.state.documents = Documents(documents_repository if documents_repository is not None else SupabaseDocuments(settings),
        storage_adapter if storage_adapter is not None else SupabaseStorage(settings),
        application.state.workspaces, application.state.save_admission)
    application.include_router(router)
    application.include_router(auth_router)
    application.include_router(sources_router)
    application.include_router(workspaces_router)
    application.include_router(generation_router)
    application.include_router(documents_router)
    application.include_router(progress_router)

    @application.middleware('http')
    async def private_headers(request: Request, call_next):
        response = await call_next(request)
        if request.url.path in ('/account', '/workspace') or request.url.path.startswith(('/api/v1/auth', '/api/v1/sources', '/api/v1/generation', '/api/v1/workspaces', '/api/v1/documents', '/api/v1/progress')):
            response.headers['Cache-Control'] = 'no-store'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Referrer-Policy'] = 'no-referrer'
            response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    @application.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError):
        if request.url.path.startswith(('/api/v1/auth', '/api/v1/sources', '/api/v1/generation', '/api/v1/workspaces', '/api/v1/documents', '/api/v1/progress')):
            return JSONResponse(status_code=422, content={'code': 'invalid_request',
                'message': 'Forespørselen ble avvist.', 'requestId': str(uuid4())})
        return JSONResponse(status_code=422, content={'code': 'unsupported_demo_input',
            'message': 'Demoen støtter bare memory-basics-v1 med schemaVersion 1.0. Egen tekst, filer, innstillinger og ukjente felt støttes ikke.',
            'requestId': str(uuid4())})

    @application.get('/health')
    def health():
        return {'status': 'ok', 'mode': 'demo'}

    # Explicit public files only: no repository or private-directory static mount.
    @application.get('/', include_in_schema=False)
    def index():
        return FileResponse(PUBLIC / 'index.html', media_type='text/html')

    @application.get('/account', include_in_schema=False)
    def account():
        return FileResponse(PUBLIC / 'account.html', media_type='text/html')

    @application.get('/workspace', include_in_schema=False)
    def workspace():
        return FileResponse(PUBLIC / 'workspace.html', media_type='text/html')

    @application.get('/assets/workspace.js', include_in_schema=False)
    def workspace_javascript():
        return FileResponse(PUBLIC / 'workspace.js', media_type='text/javascript')

    @application.get('/assets/styles.css', include_in_schema=False)
    def stylesheet():
        return FileResponse(PUBLIC / 'styles.css', media_type='text/css')

    @application.get('/assets/app.js', include_in_schema=False)
    def javascript():
        return FileResponse(PUBLIC / 'app.js', media_type='text/javascript')

    @application.get('/assets/account.js', include_in_schema=False)
    def account_javascript():
        return FileResponse(PUBLIC / 'account.js', media_type='text/javascript')

    return application


app = create_app()
