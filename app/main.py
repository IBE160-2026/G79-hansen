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


def create_app(settings=None, *, auth_adapter=None, registry=None):
    settings = settings if settings is not None else Settings.from_env()
    application = FastAPI(title='Study Buddy', version='0.1.0', redirect_slashes=False)
    application.state.settings = settings
    application.state.auth_registry = registry if registry is not None else Registry(
        idle_seconds=settings.idle_seconds, absolute_seconds=settings.absolute_seconds)
    application.state.auth_revocations = Revocations()
    application.state.auth_adapter = auth_adapter if auth_adapter is not None else SupabaseAuth(settings)
    application.state.source_admission = Admission()
    application.include_router(router)
    application.include_router(auth_router)
    application.include_router(sources_router)

    @application.middleware('http')
    async def private_headers(request: Request, call_next):
        response = await call_next(request)
        if request.url.path in ('/account', '/workspace') or request.url.path.startswith(('/api/v1/auth', '/api/v1/sources')):
            response.headers['Cache-Control'] = 'no-store'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Referrer-Policy'] = 'no-referrer'
            response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    @application.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError):
        if request.url.path.startswith('/api/v1/auth'):
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
