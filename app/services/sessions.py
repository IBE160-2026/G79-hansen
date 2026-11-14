"""Bounded, single-process auth authority; restart deliberately ends every session."""

from dataclasses import dataclass, field
import asyncio
from concurrent.futures import Future
from secrets import compare_digest, token_urlsafe
from threading import RLock
import time

from starlette.concurrency import run_in_threadpool

from app.adapters.auth import AuthFailure, Identity


@dataclass(repr=False)
class Browser:
    csrf: str
    expires: float
    authority_revision: int = 0


@dataclass(repr=False)
class Pending:
    browser_id: str
    email: str
    expires: float
    purpose: str = "signup"
    verifier: str | None = None
    authority_revision: int | None = None


@dataclass(repr=False)
class Session:
    identity: Identity
    browser_id: str
    created: float
    touched: float
    validation: Future | None = field(default=None, repr=False)


@dataclass(repr=False)
class RecoveryGrant:
    identity: Identity
    browser_id: str
    expires: float


def opaque_equal(expected, supplied):
    # compare_digest(str, str) only accepts ASCII; malformed browser input denies.
    return (isinstance(supplied, str) and supplied.isascii() and
            bool(supplied) and compare_digest(expected, supplied))


class Registry:
    def __init__(self, *, clock=time.time, capacity=1000, pending_ttl=600,
                 idle_seconds=1800, absolute_seconds=43200):
        self.clock, self.capacity, self.pending_ttl = clock, capacity, pending_ttl
        self.idle_seconds, self.absolute_seconds = idle_seconds, absolute_seconds
        self.browsers, self.pending, self.sessions, self.recoveries = {}, {}, {}, {}
        self.lock = RLock()
        self._validation_tasks = set()

    def _expired(self, session, now):
        return (now - session.touched >= self.idle_seconds or
                now - session.created >= self.absolute_seconds)

    def _prune(self):
        now = self.clock()
        for key, value in list(self.sessions.items()):
            if self._expired(value, now):
                del self.sessions[key]
        for table in (self.browsers, self.pending, self.recoveries):
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
            return bool(browser and opaque_equal(browser.csrf, csrf))

    def start_attempt(self, browser_id, email, purpose="signup"):
        with self.lock:
            self._prune()
            if purpose not in ("signup", "recovery"):
                raise AuthFailure("invalid_request")
            if (browser_id not in self.browsers or len(self.pending) >= self.capacity or
                    sum(p.browser_id == browser_id for p in self.pending.values()) >= 4):
                raise AuthFailure("auth_capacity")
            state = token_urlsafe(32)
            pending = Pending(browser_id, email, self.clock() + self.pending_ttl, purpose)
            self.pending[state] = pending
            self.browsers[browser_id].expires = max(self.browsers[browser_id].expires, pending.expires)
            return state, pending

    def discard_attempt(self, state):
        with self.lock:
            self.pending.pop(state, None)

    def retain_browser(self, browser_id):
        """Keep an already-protected login binding alive during bounded provider work."""
        with self.lock:
            self._prune()
            browser = self.browsers.get(browser_id)
            if browser is None:
                raise AuthFailure("request_rejected")
            browser.expires = max(browser.expires, self.clock() + self.pending_ttl)

    def consume(self, state, browser_id, purpose="signup"):
        with self.lock:
            self._prune()
            pending = self.pending.get(state)
            if (not pending or not opaque_equal(pending.browser_id, browser_id) or
                    pending.purpose != purpose or not pending.verifier or browser_id not in self.browsers):
                raise AuthFailure("invalid_confirmation")
            # Consume before any provider exchange. A concurrent callback cannot exchange twice.
            del self.pending[state]
            pending.authority_revision = self.browsers[browser_id].authority_revision
            return pending

    def rotate(self, old_id, browser_id, identity, *, recovery=False, expected_revision=None):
        with self.lock:
            self._prune()
            if browser_id not in self.browsers:
                raise AuthFailure("invalid_credentials")
            browser = self.browsers[browser_id]
            if expected_revision is not None and browser.authority_revision != expected_revision:
                raise AuthFailure("invalid_recovery")
            old = self.sessions.get(old_id) or self.recoveries.get(old_id)
            replacing = old is not None and old.browser_id == browser_id
            if len(self.sessions) + len(self.recoveries) >= self.capacity and not replacing:
                raise AuthFailure("auth_capacity")
            if replacing:
                self.sessions.pop(old_id, None)
                self.recoveries.pop(old_id, None)
            session_id = token_urlsafe(32)
            now = self.clock()
            if recovery:
                self.recoveries[session_id] = RecoveryGrant(identity, browser_id, now + self.pending_ttl)
            else:
                self.sessions[session_id] = Session(identity, browser_id, now, now)
            lifetime = self.pending_ttl if recovery else self.absolute_seconds
            self.browsers[browser_id].expires = max(self.browsers[browser_id].expires, now + lifetime)
            browser.authority_revision += 1
            return session_id

    def recovery_available(self, session_id, browser_id):
        with self.lock:
            self._prune()
            grant = self.recoveries.get(session_id)
            return bool(grant and opaque_equal(grant.browser_id, browser_id) and browser_id in self.browsers)

    def claim_recovery(self, session_id, browser_id):
        with self.lock:
            if not self.recovery_available(session_id, browser_id):
                raise AuthFailure("invalid_recovery")
            # Remove before provider work, including refresh/validation. Never restore it.
            self.browsers[browser_id].authority_revision += 1
            return self.recoveries.pop(session_id)

    def _begin_validation(self, session_id, browser_id):
        with self.lock:
            self._prune()
            session = self.sessions.get(session_id)
            if not session or session.browser_id != browser_id:
                return None, None, False
            if session.validation is not None:
                return session, session.validation, False
            session.validation = Future()
            return session, session.validation, True

    def _finish_validation(self, session_id, session, future, adapter):
        try:
            with self.lock:
                if self.sessions.get(session_id) is not session or self._expired(session, self.clock()):
                    self.sessions.pop(session_id, None)
                    future.set_result(None)
                    return
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
                    future.set_result(None)
                    return
                session.identity, session.touched = identity, self.clock()
                session.validation = None
                future.set_result(identity)
        except BaseException as exc:
            future.set_exception(exc)
        finally:
            with self.lock:
                if session.validation is future:
                    session.validation = None

    def _current_result(self, session_id, session, identity):
        with self.lock:
            self._prune()
            return identity if self.sessions.get(session_id) is session else None

    def authenticated(self, session_id, browser_id, adapter):
        session, future, leader = self._begin_validation(session_id, browser_id)
        if session is None:
            return None
        if leader:
            self._finish_validation(session_id, session, future, adapter)
        return self._current_result(session_id, session, future.result())

    async def authenticated_async(self, session_id, browser_id, adapter):
        session, future, leader = self._begin_validation(session_id, browser_id)
        if session is None:
            return None
        if leader:
            # The owner outlives any one HTTP waiter, including cancellation while
            # waiting for thread-pool admission. Keep a strong reference until done.
            task = asyncio.create_task(self._own_validation(session_id, session, future, adapter))
            self._validation_tasks.add(task)
            task.add_done_callback(self._validation_tasks.discard)
        # Followers wait on the event loop, without retaining thread-pool workers.
        identity = await asyncio.shield(asyncio.wrap_future(future))
        return self._current_result(session_id, session, identity)

    async def _own_validation(self, session_id, session, future, adapter):
        try:
            await run_in_threadpool(self._finish_validation, session_id, session, future, adapter)
        except BaseException:
            with self.lock:
                self.sessions.pop(session_id, None)
                if session.validation is future:
                    session.validation = None
                if not future.done():
                    future.set_exception(AuthFailure())
