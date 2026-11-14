"""Explicit browser-test-only app. Never import this module from application code."""

import os
import time
from uuid import uuid5, NAMESPACE_DNS

from app.adapters.auth import AuthFailure, Identity
from app.config import Settings
from app.main import create_app


class BrowserAuth:
    def __init__(self):
        self.links = []
        self.passwords = {}
        self.updates = []

    def identity(self, email):
        return Identity(str(uuid5(NAMESPACE_DNS, email)), email,
                        "BROWSER_PRIVATE_ACCESS", "BROWSER_PRIVATE_REFRESH", time.time() + 3600)

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


adapter = BrowserAuth()
app = create_app(Settings(True, os.environ["AUTH_TEST_ORIGIN"], "https://example.supabase.co",
                          "sb_publishable_test", True), auth_adapter=adapter)


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
