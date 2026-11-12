"""Request-scoped Supabase SDK boundary. No provider object escapes this module."""

from contextlib import contextmanager
from dataclasses import dataclass, field
import logging
import time
from uuid import UUID

import httpx
from supabase import ClientOptions, create_client
from supabase_auth.errors import AuthApiError

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
        return self.pending.verifier if key.endswith("-code-verifier") else None

    def set_item(self, key, value):
        if not key.endswith("-code-verifier") or not isinstance(value, str) or not 43 <= len(value) <= 128:
            raise AuthFailure()
        self.pending.verifier = value

    def remove_item(self, key):
        if key.endswith("-code-verifier"):
            self.pending.verifier = None


class SupabaseAuth:
    def __init__(self, settings: Settings, *, transport=None, clock=time.time):
        self.settings, self.transport, self.clock = settings, transport, clock

    @contextmanager
    def client(self, storage=None):
        # An SDK and HTTP client per operation: never share mutable auth state.
        with httpx.Client(timeout=httpx.Timeout(5.0, connect=3.0),
                          limits=httpx.Limits(max_connections=2, max_keepalive_connections=0),
                          follow_redirects=False, trust_env=False, transport=self.transport) as http:
            try:
                options = ClientOptions(auto_refresh_token=False, persist_session=False,
                                        flow_type="pkce", httpx_client=http)
                if storage is not None:
                    options.storage = storage
                sdk = create_client(self.settings.supabase_url, self.settings.supabase_key, options)
                yield sdk.auth
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
