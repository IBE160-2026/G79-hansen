"""Bounded, single-process auth authority; restart deliberately ends every session."""

from dataclasses import dataclass, field
import asyncio
from concurrent.futures import Future
from secrets import compare_digest, token_urlsafe
from threading import RLock
import time

from starlette.concurrency import run_in_threadpool
from anyio import CapacityLimiter, to_thread

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
    view_id: str = field(default_factory=lambda: token_urlsafe(24))
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
        ended = {value.browser_id for value in self.sessions.values() if self._expired(value, now)}
        ended.update(value.browser_id for value in self.recoveries.values() if now >= value.expires)
        for browser_id in ended:
            self.terminate(browser_id)
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

    def start_attempt(self, browser_id, email, purpose="signup", *, expected_revision=None):
        with self.lock:
            self._prune()
            self.check_revision(browser_id, expected_revision)
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
            return browser.authority_revision

    def check_revision(self, browser_id, revision):
        with self.lock:
            self._prune()
            browser = self.browsers.get(browser_id)
            if browser is None or (revision is not None and browser.authority_revision != revision):
                raise AuthFailure("invalid_credentials")

    def terminate(self, browser_id):
        """One atomic browser-local transition; retain its CSRF binding for fresh login."""
        with self.lock:
            identities = {}
            for table in (self.sessions, self.recoveries):
                for key, value in list(table.items()):
                    if value.browser_id == browser_id:
                        identities[value.identity.access_token] = value.identity
                        del table[key]
            for key, value in list(self.pending.items()):
                if value.browser_id == browser_id:
                    del self.pending[key]
            browser = self.browsers.get(browser_id)
            if browser:
                browser.authority_revision += 1
            return tuple(identities.values())

    def remaining(self, session_id, browser_id):
        """Non-touching lifetime snapshot, never a credential or renewal."""
        with self.lock:
            self._prune()
            session = self.sessions.get(session_id)
            grant = self.recoveries.get(session_id)
            if session and session.browser_id == browser_id:
                return max(0, min(session.touched + self.idle_seconds,
                                  session.created + self.absolute_seconds) - self.clock())
            if grant and grant.browser_id == browser_id:
                return max(0, grant.expires - self.clock())
            return None

    def live_session(self, session_id, expected=None, *, touch=False):
        """Atomic fence for transient private work; view IDs never authorize access."""
        with self.lock:
            self._prune()
            session = self.sessions.get(session_id)
            if session is None or (expected is not None and session is not expected):
                raise AuthFailure("invalid_credentials")
            if touch:
                session.touched = self.clock()
            return session

    @staticmethod
    def session_view_matches(session, supplied):
        return opaque_equal(session.view_id, supplied)

    def select_session(self, candidates, browser_id):
        """Cookie ordering never decides authority; only a live browser-bound entry does."""
        with self.lock:
            self._prune()
            for candidate in candidates:
                value = self.sessions.get(candidate) or self.recoveries.get(candidate)
                if value and value.browser_id == browser_id:
                    return candidate
            return None

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
            self.check_revision(browser_id, expected_revision)
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
                self._prune()
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
                    if self.sessions.get(session_id) is session:
                        self.terminate(session.browser_id)
                raise
            with self.lock:
                # Expiry/rotation during a bounded network request must still win.
                self._prune()
                if self.sessions.get(session_id) is not session or self._expired(session, self.clock()):
                    self.sessions.pop(session_id, None)
                    future.set_result(None)
                    return
                session.identity = identity
                session.validation = None
                future.set_result(identity)
        except BaseException as exc:
            future.set_exception(exc)
        finally:
            with self.lock:
                if session.validation is future:
                    session.validation = None

    def _current_result(self, session_id, session, identity, touch):
        with self.lock:
            self._prune()
            if self.sessions.get(session_id) is not session:
                return None
            if touch and identity is not None:
                session.touched = self.clock()
            return identity

    def authenticated(self, session_id, browser_id, adapter, *, touch=True):
        session, future, leader = self._begin_validation(session_id, browser_id)
        if session is None:
            return None
        if leader:
            self._finish_validation(session_id, session, future, adapter)
        return self._current_result(session_id, session, future.result(), touch)

    async def authenticated_async(self, session_id, browser_id, adapter, *, touch=True):
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
        return self._current_result(session_id, session, identity, touch)

    async def _own_validation(self, session_id, session, future, adapter):
        try:
            await run_in_threadpool(self._finish_validation, session_id, session, future, adapter)
        except BaseException:
            with self.lock:
                if self.sessions.get(session_id) is session:
                    self.terminate(session.browser_id)
                if session.validation is future:
                    session.validation = None
                if not future.done():
                    future.set_exception(AuthFailure())


class Revocations:
    """No queue or retry; cancellation cannot release a running worker's slot."""
    def __init__(self, *, capacity=16, seconds=10, clock=time.monotonic):
        self.capacity, self.seconds, self.clock = capacity, seconds, clock
        self.active = 0
        self.lock = RLock()
        self.tasks = set()
        # Independent from Starlette's shared validation/request pool. Every admitted
        # batch has a worker permit, so unrelated work cannot queue revocation forever.
        self.limiter = CapacityLimiter(capacity)

    async def after_response(self, adapter, identities):
        from app.adapters.auth import OperationBudget
        if not identities:
            return
        with self.lock:
            if self.active >= self.capacity:
                return
            self.active += 1
        budget = OperationBudget(self.seconds, self.clock)
        task = asyncio.create_task(self._own(adapter, identities, budget))
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        await asyncio.shield(task)

    async def _own(self, adapter, identities, budget):
        try:
            await to_thread.run_sync(self._batch, adapter, identities, budget, limiter=self.limiter)
        finally:
            with self.lock:
                self.active -= 1

    @staticmethod
    def _batch(adapter, identities, budget):
        for identity in identities:
            try:
                budget.remaining()
                adapter.revoke(identity, budget=budget)
            except Exception:
                # Provider details never escape into the response or logs.
                pass
