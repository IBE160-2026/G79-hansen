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
