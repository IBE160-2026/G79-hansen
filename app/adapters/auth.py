"""Request-scoped Supabase SDK boundary. No provider object escapes this module."""

from contextlib import contextmanager
from dataclasses import dataclass, field
import logging
import time
from uuid import UUID

import httpx
import httpcore
from supabase import ClientOptions, create_client
from supabase_auth.errors import AuthApiError
from supabase_auth.types import AuthResponse

from app.config import Settings

# httpx INFO includes complete URLs (including PKCE redirect state). Never emit them.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


class AuthFailure(Exception):
    def __init__(self, code="auth_unavailable"):
        self.code = code
        super().__init__(code)


@dataclass(repr=False)
class Identity:
    owner_id: str
    email: str
    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    expires_at: float


class AttemptStorage:
    """One SDK PKCE entry in its already-bounded pending-attempt registry."""
    def __init__(self, pending):
        self.pending = pending

    def get_item(self, key):
        if not key.endswith("-code-verifier") or not self.pending.verifier:
            return None
        suffix = "/PASSWORD_RECOVERY" if self.pending.purpose == "recovery" else ""
        return self.pending.verifier + suffix

    def set_item(self, key, value):
        if not key.endswith("-code-verifier") or not isinstance(value, str):
            raise AuthFailure()
        verifier, separator, purpose = value.partition("/")
        expected = "PASSWORD_RECOVERY" if self.pending.purpose == "recovery" else ""
        if (not 43 <= len(verifier) <= 128 or not verifier.isascii() or
                purpose != expected or bool(separator) != bool(expected)):
            raise AuthFailure()
        # The SDK stores a purpose suffix; the token endpoint needs the actual verifier.
        self.pending.verifier = verifier

    def remove_item(self, key):
        if key.endswith("-code-verifier"):
            self.pending.verifier = None


class OperationBudget:
    """One elapsed deadline across every request and streamed response in an SDK call."""
    def __init__(self, seconds, clock):
        self.clock, self.deadline = clock, clock() + seconds

    def remaining(self):
        remaining = self.deadline - self.clock()
        if remaining <= 0:
            raise AuthFailure()
        return remaining


class BudgetStream(httpx.SyncByteStream):
    def __init__(self, stream, budget):
        self.stream, self.budget = stream, budget

    def __iter__(self):
        try:
            iterator = iter(self.stream)
            while True:
                self.budget.remaining()
                try:
                    chunk = next(iterator)
                except StopIteration:
                    break
                self.budget.remaining()
                yield chunk
        except BaseException:
            self.close()
            raise

    def close(self):
        self.stream.close()


class BudgetTransport(httpx.BaseTransport):
    def __init__(self, transport, budget):
        self.transport, self.budget = transport, budget

    def handle_request(self, request):
        remaining = self.budget.remaining()
        request.extensions["timeout"] = {
            phase: min(limit, remaining)
            for phase, limit in request.extensions["timeout"].items()
        }
        response = self.transport.handle_request(request)
        try:
            self.budget.remaining()
        except BaseException:
            response.close()
            raise
        response.stream = BudgetStream(response.stream, self.budget)
        return response

    def close(self):
        self.transport.close()


class BudgetNetworkStream(httpcore.NetworkStream):
    """Recheck the deadline below HTTP framing, including partial-header reads."""
    def __init__(self, stream, budget):
        self.stream, self.budget = stream, budget

    def _call(self, action, *args, timeout=None, **kwargs):
        try:
            remaining = self.budget.remaining()
            result = action(*args, timeout=min(timeout, remaining) if timeout is not None else remaining, **kwargs)
            self.budget.remaining()
            return result
        except BaseException:
            self.close()
            raise

    def read(self, max_bytes, timeout=None):
        return self._call(self.stream.read, max_bytes, timeout=timeout)

    def write(self, buffer, timeout=None):
        self._call(self.stream.write, buffer, timeout=timeout)

    def start_tls(self, ssl_context, server_hostname=None, timeout=None):
        stream = None
        try:
            remaining = self.budget.remaining()
            stream = self.stream.start_tls(ssl_context, server_hostname=server_hostname,
                                          timeout=min(timeout, remaining) if timeout is not None else remaining)
            self.budget.remaining()
            return BudgetNetworkStream(stream, self.budget)
        except BaseException:
            if stream is not None:
                stream.close()
            self.close()
            raise

    def get_extra_info(self, info):
        return self.stream.get_extra_info(info)

    def close(self):
        self.stream.close()


class BudgetNetworkBackend(httpcore.SyncBackend):
    def __init__(self, budget):
        self.budget = budget

    def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        remaining = self.budget.remaining()
        stream = super().connect_tcp(host, port, timeout=min(timeout, remaining) if timeout is not None else remaining,
                                     local_address=local_address, socket_options=socket_options)
        wrapped = BudgetNetworkStream(stream, self.budget)
        try:
            self.budget.remaining()
        except BaseException:
            wrapped.close()
            raise
        return wrapped


class SupabaseAuth:
    def __init__(self, settings: Settings, *, transport=None, clock=time.time,
                 budget_clock=time.monotonic, operation_seconds=10):
        self.settings, self.transport, self.clock = settings, transport, clock
        self.budget_clock, self.operation_seconds = budget_clock, operation_seconds

    @contextmanager
    def client(self, storage=None, *, budget=None):
        # An SDK and HTTP client per operation: never share mutable auth state.
        budget = budget if budget is not None else OperationBudget(self.operation_seconds, self.budget_clock)
        limits = httpx.Limits(max_connections=2, max_keepalive_connections=0)
        transport = self.transport
        if transport is None:
            transport = httpx.HTTPTransport(retries=0, limits=limits, trust_env=False)
            # HTTPX has no public backend-injection option. This narrow integration
            # is pinned by uv.lock and exercised through the real HTTP framing tests.
            transport._pool._network_backend = BudgetNetworkBackend(budget)
        transport = BudgetTransport(transport, budget)
        with httpx.Client(timeout=httpx.Timeout(5.0, connect=3.0),
                          limits=limits,
                          follow_redirects=False, trust_env=False, transport=transport) as http:
            try:
                options = ClientOptions(auto_refresh_token=False, persist_session=False,
                                        flow_type="pkce", httpx_client=http)
                if storage is not None:
                    options.storage = storage
                sdk = create_client(self.settings.supabase_url, self.settings.supabase_key, options)
                yield sdk.auth
                budget.remaining()
            except AuthFailure:
                raise
            except AuthApiError as exc:
                # Never propagate SDK exception text, request bodies or tokens.
                code = "invalid_credentials" if exc.status in (400, 401, 403, 422) else "auth_unavailable"
                raise AuthFailure(code) from None
            except Exception:
                raise AuthFailure() from None

    def signup(self, email, password, pending, redirect):
        with self.client(AttemptStorage(pending)) as auth:
            try:
                response = auth.sign_up({"email": email, "password": password,
                                         "options": {"email_redirect_to": redirect}})
            except AuthApiError as exc:
                if exc.code in ("user_already_exists", "email_exists"):
                    return  # Same check-email response; never expose account existence.
                raise
            # Confirmation must be enabled; an auto-confirmed project is a setup error.
            if response.session is not None or not pending.verifier:
                raise AuthFailure()
            # Signup's user object is deliberately never used as identity.

    def _validated(self, auth, response, expected_email=None, expected_owner=None):
        session = response.session
        if not session or not session.access_token or not session.refresh_token:
            raise AuthFailure("invalid_credentials")
        checked = auth.get_user(session.access_token)
        user = checked.user if checked else None
        if not user or not user.email or not user.email_confirmed_at:
            raise AuthFailure("invalid_credentials")
        try:
            owner = str(UUID(user.id))
        except (ValueError, TypeError, AttributeError):
            raise AuthFailure("invalid_credentials") from None
        if (not response.user or not session.user or
                response.user.id != owner or session.user.id != owner or
                not response.user.email or response.user.email.casefold() != user.email.casefold() or
                not session.user.email or session.user.email.casefold() != user.email.casefold() or
                (expected_owner is not None and owner != expected_owner) or
                (expected_email is not None and user.email.casefold() != expected_email.casefold()) or
                not isinstance(session.expires_at, (int, float)) or session.expires_at <= self.clock()):
            raise AuthFailure("invalid_credentials")
        return Identity(owner, user.email, session.access_token, session.refresh_token, session.expires_at)

    def login(self, email, password):
        with self.client() as auth:
            response = auth.sign_in_with_password({"email": email, "password": password})
            return self._validated(auth, response, expected_email=email)

    def exchange(self, code, pending):
        with self.client() as auth:
            response = auth.exchange_code_for_session({"auth_code": code, "code_verifier": pending.verifier})
            return self._validated(auth, response, expected_email=pending.email)

    def request_recovery(self, email, pending, redirect):
        with self.client(AttemptStorage(pending)) as auth:
            try:
                auth.reset_password_for_email(email, {"redirect_to": redirect})
            except AuthApiError as exc:
                if exc.code in ("user_not_found", "email_not_found"):
                    return  # The same acknowledgement as an existing account.
                raise AuthFailure() from None
            if not pending.verifier:
                raise AuthFailure()

    def update_password(self, identity, password, *, expires_at):
        with self.client() as auth:
            # set_session can refresh. Validate that resulting authority before writing.
            response = auth.set_session(identity.access_token, identity.refresh_token)
            current = self._validated(auth, response, expected_email=identity.email,
                                      expected_owner=identity.owner_id)
            get_session = auth.get_session
            def mutation_session():
                # update_user calls get_session, which can itself refresh a token
                # inside the SDK's expiry margin. Validate that final authority too.
                session = get_session()
                if session is None:
                    raise AuthFailure("invalid_recovery")
                self._validated(auth, AuthResponse(session=session, user=session.user),
                                expected_email=identity.email, expected_owner=identity.owner_id)
                if self.clock() >= expires_at:
                    raise AuthFailure("invalid_recovery")
                return session
            auth.get_session = mutation_session
            try:
                updated = auth.update_user({"password": password})
            finally:
                auth.get_session = get_session
            user = updated.user if updated else None
            if (not user or user.id != current.owner_id or not user.email_confirmed_at or
                    not user.email or user.email.casefold() != current.email.casefold()):
                raise AuthFailure()

    def validate(self, identity):
        with self.client() as auth:
            checked = auth.get_user(identity.access_token)
            user = checked.user if checked else None
            if (not user or user.id != identity.owner_id or not user.email_confirmed_at or
                    not user.email or user.email.casefold() != identity.email.casefold()):
                raise AuthFailure("invalid_credentials")
        return identity

    def refresh(self, identity):
        with self.client() as auth:
            response = auth.refresh_session(identity.refresh_token)
            return self._validated(auth, response, expected_email=identity.email, expected_owner=identity.owner_id)

    def revoke(self, identity, *, budget):
        # admin.sign_out is a direct user-JWT request, despite the SDK name.
        # Never install a session, refresh, or use the default global scope.
        with self.client(budget=budget) as auth:
            auth.admin.sign_out(identity.access_token, scope="local")
