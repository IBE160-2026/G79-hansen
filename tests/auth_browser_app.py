"""Explicit browser-test-only app. Never import this module from application code."""

import os
import time
from secrets import token_urlsafe
from uuid import uuid5, NAMESPACE_DNS

from app.adapters.auth import AuthFailure, Identity
from app.config import Settings
from app.main import create_app
from app.services.sessions import Registry
from fastapi import Request


class BrowserAuth:
    def __init__(self):
        self.links = []
        self.passwords = {}
        self.updates = []
        self.revoked = set()

    def revoke(self, identity, *, budget):
        budget.remaining()
        self.revoked.add(identity.access_token)

    def identity(self, email):
        return Identity(str(uuid5(NAMESPACE_DNS, email)), email,
                        "BROWSER_PRIVATE_ACCESS_" + token_urlsafe(16),
                        "BROWSER_PRIVATE_REFRESH_" + token_urlsafe(16), time.time() + 3600)

    def signup(self, email, password, pending, redirect):
        pending.verifier = "v" * 43
        self.links.append({"email": email, "url": redirect + "&code=BROWSER_PRIVATE_CODE"})

    def login(self, email, password):
        if email == "outage@example.test":
            raise AuthFailure()
        if password != self.passwords.get(email, "BROWSER_PRIVATE_PASSWORD"):
            raise AuthFailure("invalid_credentials")
        return self.identity(email)

    def exchange(self, code, pending):
        if code != "BROWSER_PRIVATE_CODE":
            raise AuthFailure("invalid_credentials")
        return self.identity(pending.email)

    def validate(self, identity):
        if identity.access_token in self.revoked:
            raise AuthFailure("invalid_credentials")
        return identity

    def refresh(self, identity):
        return self.identity(identity.email)

    def request_recovery(self, email, pending, redirect):
        pending.verifier = "r" * 43
        self.links.append({"email": email, "purpose": "recovery", "url": redirect + "&code=BROWSER_PRIVATE_CODE"})

    def update_password(self, identity, password, *, expires_at):
        if time.time() >= expires_at:
            raise AuthFailure("invalid_recovery")
        self.updates.append({"email": identity.email})
        self.passwords[identity.email] = password
        if identity.email == "uncertain@example.test":
            raise AuthFailure()


class PermissiveEmailAdmission:
    """Only this synthetic browser-test app bypasses durable mail admission."""
    async def reserve_for_dispatch(self, recipient):
        pass


adapter = BrowserAuth()
app = create_app(Settings(True, os.environ["AUTH_TEST_ORIGIN"], "https://example.supabase.co",
                          "sb_publishable_test", True), auth_adapter=adapter,
                 email_admission=PermissiveEmailAdmission())


@app.get("/__test/links")
def links():
    return adapter.links


@app.post("/__test/end-sessions")
def end_sessions():
    app.state.auth_registry.sessions.clear()
    app.state.auth_registry.recoveries.clear()
    return {"ok": True}


@app.get("/__test/updates")
def updates():
    return adapter.updates


@app.post("/__test/restart")
def restart():
    app.state.auth_registry = Registry()
    from app.services.workspaces import Workspaces
    app.state.workspaces = Workspaces(app.state.auth_registry)
    return {"ok": True}


@app.post("/__test/deadline")
def short_deadline(request: Request):
    registry = app.state.auth_registry
    from app.api.auth import current_session
    session_id = current_session(request)
    with registry.lock:
        session = registry.sessions.get(session_id)
        grant = registry.recoveries.get(session_id)
        if session:
            session.touched = registry.clock() - registry.idle_seconds + 1
        if grant:
            grant.expires = registry.clock() + 1
    return {"ok": True}
