from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

from app.api.demo import router

PUBLIC = Path(__file__).parent / "static"
app = FastAPI(title="Study Buddy fixed demo", version="0.1.0")
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def invalid_demo_request(request: Request, exc: RequestValidationError):
    # Do not echo submitted source or Pydantic's input values into responses/logs.
    return JSONResponse(status_code=422, content={
        "code": "unsupported_demo_input",
        "message": "Demoen støtter bare memory-basics-v1 med schemaVersion 1.0. Egen tekst, filer, innstillinger og ukjente felt støttes ikke.",
        "requestId": str(uuid4()),
    })


@app.get("/health")
def health():
    return {"status": "ok", "mode": "demo"}


# Explicit public files only: no repository or private-directory static mount.
@app.get("/", include_in_schema=False)
def index():
    return FileResponse(PUBLIC / "index.html", media_type="text/html")


@app.get("/assets/styles.css", include_in_schema=False)
def stylesheet():
    return FileResponse(PUBLIC / "styles.css", media_type="text/css")


@app.get("/assets/app.js", include_in_schema=False)
def javascript():
    return FileResponse(PUBLIC / "app.js", media_type="text/javascript")
