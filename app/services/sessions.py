"""Bounded, single-process auth authority; restart deliberately ends every session."""

from dataclasses import dataclass, field
from secrets import compare_digest, token_urlsafe
from threading import Lock, RLock
import time

from app.adapters.auth import AuthFailure, Identity


@dataclass(repr=False)
class Browser:
    csrf: str
    expires: float


@dataclass(repr=False)
class Pending:
    browser_id: str
    email: str
    expires: float
    purpose: str = "signup"
    verifier: str | None = None


@dataclass(repr=False)
class Session:
    identity: Identity
    browser_id: str
    created: float
    touched: float
    lock: Lock = field(default_factory=Lock)


class Registry:
    def __init__(self, *, clock=time.time, capacity=1000, pending_ttl=600,
                 idle_seconds=1800, absolute_seconds=43200):
        self.clock, self.capacity, self.pending_ttl = clock, capacity, pending_ttl
        self.idle_seconds, self.absolute_seconds = idle_seconds, absolute_seconds
        self.browsers, self.pending, self.sessions = {}, {}, {}
        self.lock = RLock()

    def _expired(self, session, now):
        return (now - session.touched >= self.idle_seconds or
                now - session.created >= self.absolute_seconds)

    def _prune(self):
        now = self.clock()
        for key, value in list(self.sessions.items()):
            if self._expired(value, now):
                del self.sessions[key]
        for table in (self.browsers, self.pending):
            for key, value in list(table.items()):
                if now >= value.expires:
                    del table[key]

    def browser(self, browser_id):
        with self.lock:
            self._prune()
            if browser_id not in self.browsers:
                if len(self.browsers) >= self.capacity:
                    raise AuthFailure("auth_capacity")
                browser_id = token_urlsafe(32)
                self.browsers[browser_id] = Browser(token_urlsafe(32), self.clock() + self.absolute_seconds)
            return browser_id, self.browsers[browser_id]

    def csrf_valid(self, browser_id, csrf):
        with self.lock:
            self._prune()
            browser = self.browsers.get(browser_id)
            return bool(browser and csrf and compare_digest(browser.csrf, csrf))

    def start_attempt(self, browser_id, email):
        with self.lock:
            self._prune()
            if (browser_id not in self.browsers or len(self.pending) >= self.capacity or
                    sum(p.browser_id == browser_id for p in self.pending.values()) >= 4):
                raise AuthFailure("auth_capacity")
            state = token_urlsafe(32)
            pending = Pending(browser_id, email, self.clock() + self.pending_ttl)
            self.pending[state] = pending
            return state, pending

    def discard_attempt(self, state):
        with self.lock:
            self.pending.pop(state, None)

    def consume(self, state, browser_id, purpose="signup"):
        with self.lock:
            self._prune()
            pending = self.pending.get(state)
            if (not pending or not browser_id or not compare_digest(pending.browser_id, browser_id) or
                    pending.purpose != purpose or not pending.verifier or browser_id not in self.browsers):
                raise AuthFailure("invalid_confirmation")
            # Consume before any provider exchange. A concurrent callback cannot exchange twice.
            del self.pending[state]
            return pending

    def rotate(self, old_id, browser_id, identity):
        with self.lock:
            self._prune()
            if browser_id not in self.browsers:
                raise AuthFailure("invalid_credentials")
            old = self.sessions.get(old_id)
            replacing = old is not None and old.browser_id == browser_id
            if len(self.sessions) >= self.capacity and not replacing:
                raise AuthFailure("auth_capacity")
            if replacing:
                del self.sessions[old_id]
            session_id = token_urlsafe(32)
            now = self.clock()
            self.sessions[session_id] = Session(identity, browser_id, now, now)
            return session_id

    def authenticated(self, session_id, browser_id, adapter):
        with self.lock:
            self._prune()
            session = self.sessions.get(session_id)
            if not session or session.browser_id != browser_id:
                return None
        with session.lock:
            with self.lock:
                if self.sessions.get(session_id) is not session or self._expired(session, self.clock()):
                    self.sessions.pop(session_id, None)
                    return None
            try:
                if session.identity.expires_at <= self.clock() + 30:
                    identity = adapter.refresh(session.identity)
                else:
                    identity = adapter.validate(session.identity)
                # Preserve server-derived owner even with an injected adapter.
                if identity.owner_id != session.identity.owner_id:
                    raise AuthFailure("invalid_credentials")
            except AuthFailure:
                with self.lock:
                    self.sessions.pop(session_id, None)
                raise
            with self.lock:
                # Expiry/rotation during a bounded network request must still win.
                if self.sessions.get(session_id) is not session or self._expired(session, self.clock()):
                    self.sessions.pop(session_id, None)
                    return None
                session.identity, session.touched = identity, self.clock()
                return identity
