"""Offline contracts and security matrix. These do not prove live acceptance."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import base64
import hashlib
import json
import logging
import time
from urllib.parse import urlsplit

from fastapi.testclient import TestClient
import httpx
import pytest

from app.adapters.auth import AuthFailure, Identity, SupabaseAuth
from app.config import Settings
from app.main import RedactAuthQuery, create_app
from app.services.sessions import Pending, Registry

ORIGIN = "http://127.0.0.1:8000"
SETTINGS = Settings(True, ORIGIN, "https://example.supabase.co", "sb_publishable_test", True)
OWNER = "11111111-1111-4111-8111-111111111111"
OTHER = "22222222-2222-4222-8222-222222222222"
EMAIL = "tester@example.test"
PASSWORD = "TEST_PASSWORD_MUST_NEVER_BE_ECHOED"
PAYLOAD = {"email": EMAIL, "password": PASSWORD}


class FakeAuth:
    """Only injected by tests; no application setting enables this adapter."""
    def __init__(self):
        self.calls = []
        self.redirects = []
        self.fail = False

    def identity(self, email=EMAIL):
        return Identity(OWNER if email == EMAIL else OTHER, email, "PRIVATE_ACCESS", "PRIVATE_REFRESH", time.time() + 3600)

    def signup(self, email, password, pending, redirect):
        self.calls.append("signup")
        if self.fail:
            raise AuthFailure()
        pending.verifier = "v" * 43 + str(len(self.redirects))
        self.redirects.append(redirect)

    def login(self, email, password):
        self.calls.append("login")
        if self.fail:
            raise AuthFailure("invalid_credentials")
        return self.identity(email)

    def exchange(self, code, pending):
        self.calls.append("exchange")
        if self.fail:
            raise AuthFailure()
        return self.identity(pending.email)

    def validate(self, identity):
        self.calls.append("validate")
        if self.fail:
            raise AuthFailure()
        return identity

    def refresh(self, identity):
        self.calls.append("refresh")
        if self.fail:
            raise AuthFailure()
        return replace(identity, expires_at=time.time() + 3600)


def setup(settings=SETTINGS, registry=None):
    fake = FakeAuth()
    app = create_app(settings, auth_adapter=fake, registry=registry)
    return TestClient(app, base_url=settings.app_origin or ORIGIN), fake, app.state.auth_registry


def headers(client):
    status = client.get("/api/v1/auth/status")
    return {"Origin": str(client.base_url).rstrip("/"), "X-CSRF-Token": status.json()["csrfToken"]}


def post(client, action="signup", payload=PAYLOAD):
    return client.post(f"/api/v1/auth/{action}", json=payload, headers=headers(client))


def callback(client, redirect, code="PRIVATE_CODE"):
    return client.get(urlsplit(redirect).path + "?" + urlsplit(redirect).query + "&code=" + code, follow_redirects=False)


@pytest.mark.parametrize("settings", [
    Settings(), replace(SETTINGS, auth_enabled=False), replace(SETTINGS, supabase_key=""),
    replace(SETTINGS, supabase_key="sb_secret_PRIVATE"), replace(SETTINGS, supabase_key="malformed"),
    replace(SETTINGS, supabase_url="http://example.supabase.co"), replace(SETTINGS, app_origin="http://example.test"),
    replace(SETTINGS, allow_loopback_http=False), replace(SETTINGS, app_origin=ORIGIN + "/"),
    replace(SETTINGS, app_origin="https://user:password@example.test"),
    replace(SETTINGS, supabase_url="https://example.supabase.co/?secret=value"),
    *[replace(SETTINGS, supabase_key="x." + base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip("=") + ".y")
      for value in [[], None, 42, {"role": "service_role"}]],
])
def test_missing_invalid_or_disabled_configuration_fails_closed_without_provider_calls(settings):
    assert not settings.available
    client, fake, _ = setup(settings)
    response = client.get("/api/v1/auth/status")
    assert response.json() == {"available": False, "authenticated": False}
    assert response.headers["cache-control"] == "no-store"
    assert client.get("/api/v1/demo/fixture").status_code == 200
    assert client.post("/api/v1/demo/generate", json={"schemaVersion": "1.0", "fixtureId": "memory-basics-v1"}).status_code == 200
    assert not fake.calls


def test_explicit_loopback_and_https_configs_and_legacy_anon_key():
    assert SETTINGS.available
    assert replace(SETTINGS, app_origin="https://study.example.test", allow_loopback_http=False).available
    assert replace(SETTINGS, app_origin="http://[::1]:8000").available
    payload = base64.urlsafe_b64encode(b'{"role":"anon"}').decode().rstrip("=")
    assert replace(SETTINGS, supabase_key="header." + payload + ".signature").available


def test_signup_is_generic_and_confirmation_validates_rotates_and_cleans_url():
    client, fake, registry = setup()
    assert post(client).json()["status"] == "check_email"
    assert "sb_session" not in client.cookies
    assert len(registry.pending) == 1
    response = callback(client, fake.redirects[0])
    assert response.status_code == 303
    assert response.headers["location"] == "/account?confirmation=success"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["referrer-policy"] == "no-referrer"
    original = client.cookies["sb_session"]
    assert original not in ("PRIVATE_ACCESS", "PRIVATE_REFRESH")
    display = client.get("/api/v1/auth/status").json()
    assert display["authenticated"] and display["email"] == EMAIL
    assert "ownerId" not in display and "token" not in json.dumps(display).lower().replace("csrftoken", "")
    assert post(client, "login").status_code == 200
    assert client.cookies["sb_session"] != original
    assert original not in registry.sessions
    assert len(registry.sessions) == 1


@pytest.mark.parametrize("case", ["missing_cookie", "wrong_browser", "wrong_state", "missing_code", "duplicate_code", "wrong_purpose", "missing_verifier", "expired", "restart", "implicit"])
def test_bad_callback_rejects_before_exchange(case):
    now = [time.time()]
    registry = Registry(clock=lambda: now[0])
    client, fake, _ = setup(registry=registry)
    post(client)
    redirect = fake.redirects[0]
    pending = next(iter(registry.pending.values()))
    if case == "missing_cookie":
        client.cookies.clear()
    elif case == "wrong_browser":
        client.cookies.clear()
        headers(client)
    elif case == "wrong_state":
        redirect = redirect.split("state=")[0] + "state=" + "z" * 43
    elif case == "wrong_purpose":
        pending.purpose = "recovery"
    elif case == "missing_verifier":
        pending.verifier = None
    elif case == "expired":
        now[0] += 600
    elif case == "restart":
        registry.pending.clear()
    if case == "missing_code":
        response = client.get(redirect, follow_redirects=False)
    elif case == "duplicate_code":
        response = callback(client, redirect + "&code=second")
    elif case == "implicit":
        response = client.get(redirect + "&access_token=PRIVATE", follow_redirects=False)
    else:
        response = callback(client, redirect)
    assert response.headers["location"] == "/account?confirmation=invalid"
    assert "exchange" not in fake.calls
    assert "sb_session" not in client.cookies


def test_overlapping_attempts_and_simultaneous_callbacks_consume_exactly_once():
    client, fake, registry = setup()
    post(client)
    post(client)
    assert len({p.verifier for p in registry.pending.values()}) == 2
    assert fake.redirects[0] != fake.redirects[1]
    with ThreadPoolExecutor(2) as pool:
        responses = list(pool.map(lambda _: callback(client, fake.redirects[0]), range(2)))
    assert sorted(r.headers["location"] for r in responses) == ["/account?confirmation=invalid", "/account?confirmation=success"]
    assert fake.calls.count("exchange") == 1
    assert callback(client, fake.redirects[1]).headers["location"] == "/account?confirmation=success"
    assert fake.calls.count("exchange") == 2
    assert len(registry.pending) == 0
    assert len(registry.sessions) == 1


@pytest.mark.parametrize("action", ["signup", "login"])
@pytest.mark.parametrize("case", ["missing_origin", "wrong_origin", "null_origin", "missing_csrf", "wrong_csrf", "other_browser", "wrong_host", "duplicate_origin"])
def test_origin_csrf_fail_before_provider_call(action, case):
    client, fake, _ = setup()
    protection = headers(client)
    if case == "missing_origin":
        protection.pop("Origin")
    elif case == "wrong_origin":
        protection["Origin"] = "https://attacker.test"
    elif case == "null_origin":
        protection["Origin"] = "null"
    elif case == "missing_csrf":
        protection.pop("X-CSRF-Token")
    elif case == "wrong_csrf":
        protection["X-CSRF-Token"] = "wrong"
    elif case == "other_browser":
        client.cookies.clear()
    elif case == "wrong_host":
        protection["Host"] = "attacker.test"
    elif case == "duplicate_origin":
        protection = list(protection.items()) + [("Origin", ORIGIN)]
    response = client.post(f"/api/v1/auth/{action}", json=PAYLOAD, headers=protection)
    assert response.status_code == 403
    assert response.headers["cache-control"] == "no-store"
    assert PASSWORD not in response.text
    assert not fake.calls


@pytest.mark.parametrize("payload", [{}, {**PAYLOAD, "ownerId": OTHER}, {**PAYLOAD, "password": 123},
    {**PAYLOAD, "password": "short"}, {**PAYLOAD, "email": "bad"}, {**PAYLOAD, "password": "x" * 1025}])
def test_credentials_are_shared_strict_bounded_and_redacted(payload):
    client, fake, _ = setup()
    for action in ["login", "signup"]:
        response = post(client, action, payload)
        assert response.status_code == 422
        assert PASSWORD not in response.text
    assert not fake.calls


def test_malformed_and_oversized_chunked_json_are_rejected_safely():
    client, fake, _ = setup()
    protection = {**headers(client), "Content-Type": "application/json"}
    for body in [b"{broken", (b"x" * 4000 for _ in range(3))]:
        response = client.post("/api/v1/auth/signup", content=body, headers=protection)
        assert response.status_code == 422
    assert not fake.calls


def test_browser_isolation_unknown_sessions_outage_and_restart():
    client, fake, registry = setup()
    second = TestClient(client.app, base_url=ORIGIN)
    assert post(client, "login").status_code == 200
    assert post(second, "login", {**PAYLOAD, "email": "second@example.test"}).status_code == 200
    assert client.cookies["sb_session"] != second.cookies["sb_session"]
    assert client.get("/api/v1/auth/status").json()["email"] == EMAIL
    assert second.get("/api/v1/auth/status").json()["email"] == "second@example.test"
    fake.fail = True
    response = client.get("/api/v1/auth/status")
    assert response.status_code == 503
    assert "sb_session" not in client.cookies
    fake.fail = False
    assert second.get("/api/v1/auth/status").json()["authenticated"]
    registry.sessions.clear()
    assert not second.get("/api/v1/auth/status").json()["authenticated"]
    assert not registry.sessions


def test_capacity_limits_reject_overflow_and_expiry_releases_slots():
    now = [1000.0]
    registry = Registry(clock=lambda: now[0], capacity=2)
    browser, _ = registry.browser(None)
    other, _ = registry.browser(None)
    with pytest.raises(AuthFailure):
        registry.browser(None)
    first, attempt = registry.start_attempt(browser, EMAIL)
    registry.start_attempt(other, EMAIL)
    with pytest.raises(AuthFailure):
        registry.start_attempt(browser, EMAIL)
    identity = FakeAuth().identity()
    a = registry.rotate(None, browser, identity)
    registry.rotate(None, other, identity)
    with pytest.raises(AuthFailure):
        registry.rotate(None, browser, identity)
    assert registry.rotate(a, browser, identity) != a
    now[0] += 600
    registry.start_attempt(browser, EMAIL)
    assert first not in registry.pending
    full = Registry()
    browser, _ = full.browser(None)
    for _ in range(4):
        full.start_attempt(browser, EMAIL)
    with pytest.raises(AuthFailure):
        full.start_attempt(browser, EMAIL)


@pytest.mark.parametrize("expiry", ["idle", "absolute"])
def test_session_expiry_and_refresh_failure_deny_locally(expiry):
    now = [1000.0]
    registry = Registry(clock=lambda: now[0])
    fake = FakeAuth()
    browser, _ = registry.browser(None)
    session_id = registry.rotate(None, browser, fake.identity())
    if expiry == "absolute":
        registry.sessions[session_id].touched = now[0] + 43100
        now[0] += 43200
    else:
        now[0] += 1800
    assert registry.authenticated(session_id, browser, fake) is None
    assert not fake.calls


def test_refresh_serialized_per_session_and_never_changes_owner():
    now = time.time()
    registry = Registry()
    browser, _ = registry.browser(None)
    fake = FakeAuth()
    session_id = registry.rotate(None, browser, replace(fake.identity(), expires_at=now + 10))
    with ThreadPoolExecutor(2) as pool:
        identities = list(pool.map(lambda _: registry.authenticated(session_id, browser, fake), range(2)))
    assert all(i.owner_id == OWNER for i in identities)
    assert fake.calls.count("refresh") == 1
    assert fake.calls.count("validate") == 1
    registry.sessions[session_id].identity.expires_at = now
    fake.fail = True
    with pytest.raises(AuthFailure):
        registry.authenticated(session_id, browser, fake)
    assert session_id not in registry.sessions


def test_cookie_attributes_and_safe_access_log_filter():
    settings = replace(SETTINGS, app_origin="https://study.example.test", allow_loopback_http=False)
    client, fake, _ = setup(settings)
    boot = client.get("/api/v1/auth/status")
    login = client.post("/api/v1/auth/login", json=PAYLOAD, headers={"Origin": settings.app_origin, "X-CSRF-Token": boot.json()["csrfToken"]})
    for response in [boot, login]:
        value = response.headers["set-cookie"]
        assert "HttpOnly" in value and "Secure" in value and "SameSite=lax" in value and "Path=/" in value
        assert "Domain=" not in value and "PRIVATE" not in value
    record = logging.LogRecord("uvicorn.access", logging.INFO, "", 1, '%s - "%s %s HTTP/%s" %s',
        ("127.0.0.1", "GET", "/api/v1/auth/callback?code=PRIVATE_CODE&state=PRIVATE_STATE", "1.1", 303), None)
    RedactAuthQuery().filter(record)
    assert "PRIVATE" not in record.getMessage()
    record.args = ("127.0.0.1", "GET", "/api/v1/auth/%63allback?code=PRIVATE_CODE&state=PRIVATE_STATE", "1.1", 303)
    RedactAuthQuery().filter(record)
    assert "PRIVATE" not in record.getMessage()


def provider_user(owner=OWNER, confirmed=True):
    return {"id": owner, "aud": "authenticated", "role": "authenticated", "email": EMAIL,
            "app_metadata": {}, "user_metadata": {}, "created_at": "2026-01-01T00:00:00Z",
            "email_confirmed_at": "2026-01-01T00:00:00Z" if confirmed else None}


def provider_session():
    return {"access_token": "PRIVATE_ACCESS", "refresh_token": "PRIVATE_REFRESH", "token_type": "bearer",
            "expires_in": 3600, "expires_at": int(time.time()) + 3600, "user": provider_user()}


def test_real_sdk_transport_pkce_exchange_login_validation_and_refresh_contracts():
    calls, redirects = [], []
    def transport(request):
        calls.append(request)
        assert request.headers["apikey"] == SETTINGS.supabase_key
        assert request.extensions["timeout"] == {"connect": 3.0, "read": 5.0, "write": 5.0, "pool": 5.0}
        if request.url.path.endswith("/signup"):
            body = json.loads(request.content)
            pending = attempts[-1]
            assert body["code_challenge"] == base64.urlsafe_b64encode(hashlib.sha256(pending.verifier.encode()).digest()).decode().rstrip("=")
            assert body["code_challenge_method"] == "s256"
            redirects.append(request.url.params["redirect_to"])
            return httpx.Response(200, json=provider_user(confirmed=False))
        if request.url.path.endswith("/user"):
            assert request.headers["authorization"] == "Bearer PRIVATE_ACCESS"
            return httpx.Response(200, json=provider_user())
        body = json.loads(request.content)
        if request.url.params["grant_type"] == "pkce":
            assert body == {"auth_code": "PRIVATE_CODE", "code_verifier": attempts[0].verifier}
        elif request.url.params["grant_type"] == "refresh_token":
            assert body == {"refresh_token": "PRIVATE_REFRESH"}
        else:
            assert request.url.params["grant_type"] == "password"
            assert body["password"] == PASSWORD
        return httpx.Response(200, json=provider_session())
    adapter = SupabaseAuth(SETTINGS, transport=httpx.MockTransport(transport))
    attempts = []
    for _ in range(2):
        attempts.append(Pending("browser", EMAIL, time.time() + 600))
        adapter.signup(EMAIL, PASSWORD, attempts[-1], ORIGIN + "/api/v1/auth/callback?state=test")
    assert attempts[0].verifier != attempts[1].verifier
    identity = adapter.exchange("PRIVATE_CODE", attempts[0])
    assert adapter.login(EMAIL, PASSWORD).owner_id == OWNER
    assert adapter.validate(identity).owner_id == OWNER
    assert adapter.refresh(identity).owner_id == OWNER
    assert len(calls) == 9


def test_sdk_signup_requires_confirmation_and_does_not_enumerate_existing_accounts():
    immediate = SupabaseAuth(SETTINGS, transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json=provider_session())))
    pending = Pending("browser", EMAIL, time.time() + 600)
    with pytest.raises(AuthFailure):
        immediate.signup(EMAIL, PASSWORD, pending, ORIGIN + "/api/v1/auth/callback?state=test")
    existing = SupabaseAuth(SETTINGS, transport=httpx.MockTransport(
        lambda request: httpx.Response(422, headers={"X-Supabase-Api-Version": "2024-01-01"},
                                       json={"code": "user_already_exists", "message": "PRIVATE_PROVIDER_BODY"})))
    client = TestClient(create_app(SETTINGS, auth_adapter=existing), base_url=ORIGIN)
    response = post(client)
    assert response.json()["status"] == "check_email"
    assert "PRIVATE" not in response.text and "sb_session" not in client.cookies


@pytest.mark.parametrize("case", ["unconfirmed", "mismatch", "missing_session", "expired", "missing_refresh", "timeout", "server_error", "malformed", "redirect"])
def test_sdk_rejects_incomplete_mismatched_and_failed_provider_responses_without_secrets(case):
    def transport(request):
        if case == "timeout":
            raise httpx.ReadTimeout("PRIVATE_PROVIDER_BODY")
        if case == "server_error":
            return httpx.Response(503, json={"message": "PRIVATE_PROVIDER_BODY"})
        if case == "redirect":
            return httpx.Response(302, headers={"location": "https://attacker.test/?PRIVATE_ACCESS"})
        if request.url.path.endswith("/user"):
            return httpx.Response(200, json=provider_user(OTHER if case == "mismatch" else OWNER, case != "unconfirmed"))
        data = provider_session()
        if case == "missing_session":
            data = {"user": provider_user()}
        elif case == "expired":
            data["expires_at"] = int(time.time()) - 10
        elif case == "missing_refresh":
            data.pop("refresh_token")
        elif case == "malformed":
            return httpx.Response(200, content=b"PRIVATE_PROVIDER_BODY")
        return httpx.Response(200, json=data)
    adapter = SupabaseAuth(SETTINGS, transport=httpx.MockTransport(transport))
    client = TestClient(create_app(SETTINGS, auth_adapter=adapter), base_url=ORIGIN)
    response = post(client, "login")
    assert response.status_code in (401, 503)
    assert "sb_session" not in client.cookies
    assert "PRIVATE" not in response.text
