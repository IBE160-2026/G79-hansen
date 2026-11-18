"""Offline contracts and security matrix. These do not prove live acceptance."""

from concurrent.futures import ThreadPoolExecutor
import asyncio
from dataclasses import replace
import base64
import hashlib
import json
import logging
import time
from threading import Event
from urllib.parse import urlsplit

from fastapi.testclient import TestClient
import httpx
import httpcore
import pytest

from app.adapters.auth import AuthFailure, BudgetNetworkStream, Identity, OperationBudget, SupabaseAuth
from app.config import Settings
from app.main import RedactAuthQuery, create_app
from app.services.sessions import Pending, Registry, Revocations

ORIGIN = "http://127.0.0.1:8000"
SETTINGS = Settings(True, ORIGIN, "https://example.supabase.co", "sb_publishable_test", True)
OWNER = "11111111-1111-4111-8111-111111111111"
OTHER = "22222222-2222-4222-8222-222222222222"
EMAIL = "tester@example.test"
PASSWORD = "TEST_PASSWORD_MUST_NEVER_BE_ECHOED"
PAYLOAD = {"email": EMAIL, "password": PASSWORD}


class PermissiveEmailAdmission:
    """Explicit legacy-test injection; production adapters never bypass the gate."""
    async def reserve_for_dispatch(self, recipient):
        pass


class FakeAuth:
    """Only injected by tests; no application setting enables this adapter."""
    def __init__(self):
        self.calls = []
        self.redirects = []
        self.fail = False

    def revoke(self, identity, *, budget):
        budget.remaining()
        self.calls.append("revoke")
        if self.fail:
            raise AuthFailure()

    def identity(self, email=EMAIL):
        return Identity(OWNER if email == EMAIL else OTHER, email, "PRIVATE_ACCESS", "PRIVATE_REFRESH", time.time() + 3600)

    def signup(self, email, password, pending, redirect):
        self.calls.append("signup")
        if self.fail:
            raise AuthFailure()
        pending.verifier = "v" * 43 + str(len(self.redirects))
        self.redirects.append(redirect)

    def request_recovery(self, email, pending, redirect):
        self.calls.append("request_recovery")
        if self.fail:
            raise AuthFailure()
        pending.verifier = "r" * 43 + str(len(self.redirects))
        self.redirects.append(redirect)

    def update_password(self, identity, password, *, expires_at):
        self.calls.append("update_password")
        if self.fail:
            raise AuthFailure()

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
    app = create_app(settings, email_admission=PermissiveEmailAdmission(), auth_adapter=fake, registry=registry)
    return TestClient(app, base_url=settings.app_origin or ORIGIN), fake, app.state.auth_registry


def session_cookie(client):
    return next((value for name, value in client.cookies.items() if name.startswith("sb_session")), None)


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
    assert response.json() == {"available": False, "authenticated": False, "recoveryAvailable": False}
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
    assert session_cookie(client) is None
    assert len(registry.pending) == 1
    response = callback(client, fake.redirects[0])
    assert response.status_code == 303
    assert response.headers["location"] == "/account?confirmation=success"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["referrer-policy"] == "no-referrer"
    original = session_cookie(client)
    assert original not in ("PRIVATE_ACCESS", "PRIVATE_REFRESH")
    display = client.get("/api/v1/auth/status").json()
    assert display["authenticated"] and display["email"] == EMAIL
    assert "ownerId" not in display and "token" not in json.dumps(display).lower().replace("csrftoken", "")
    assert post(client, "login").status_code == 200
    assert session_cookie(client) != original
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
    assert session_cookie(client) is None


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
    assert session_cookie(client) != session_cookie(second)
    assert client.get("/api/v1/auth/status").json()["email"] == EMAIL
    assert second.get("/api/v1/auth/status").json()["email"] == "second@example.test"
    fake.fail = True
    retired = session_cookie(client)
    response = client.get("/api/v1/auth/status")
    assert response.status_code == 503
    assert session_cookie(client) == retired
    assert retired not in registry.sessions
    assert "set-cookie" not in response.headers
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
    expected_redirects = [ORIGIN + "/api/v1/auth/callback?state=" + str(index) * 43 for index in range(2)]
    for redirect in expected_redirects:
        attempts.append(Pending("browser", EMAIL, time.time() + 600))
        adapter.signup(EMAIL, PASSWORD, attempts[-1], redirect)
    assert attempts[0].verifier != attempts[1].verifier
    assert redirects == expected_redirects
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
    client = TestClient(create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=existing), base_url=ORIGIN)
    response = post(client)
    assert response.json()["status"] == "check_email"
    assert "PRIVATE" not in response.text and session_cookie(client) is None


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
    client = TestClient(create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=adapter), base_url=ORIGIN)
    response = post(client, "login")
    assert response.status_code in (401, 503)
    assert session_cookie(client) is None
    assert "PRIVATE" not in response.text


@pytest.mark.parametrize("field", ["csrf", "binding"])
def test_raw_non_ascii_protection_input_denies_with_safe_headers(field):
    client, fake, _ = setup()
    protection = headers(client)
    raw_headers = [(name.encode(), value.encode()) for name, value in protection.items()]
    if field == "csrf":
        raw_headers = [(name, b"\xff") if name.lower() == b"x-csrf-token" else (name, value)
                       for name, value in raw_headers]
    else:
        raw_headers.append((b"cookie", b"sb_browser=\xff"))
    response = client.post("/api/v1/auth/login", json=PAYLOAD, headers=raw_headers)
    assert response.status_code == 403
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert not fake.calls


def test_callback_non_ascii_binding_is_rejected_before_exchange():
    client, fake, _ = setup()
    post(client)
    response = client.get(fake.redirects[0] + "&code=PRIVATE_CODE",
                          headers=[(b"cookie", b"sb_browser=\xff")], follow_redirects=False)
    assert response.headers["location"] == "/account?confirmation=invalid"
    assert "exchange" not in fake.calls


def test_complete_sdk_budget_stops_trickled_body_and_closes_stream():
    now, closed = [0.0], []
    class Trickle(httpx.SyncByteStream):
        def __iter__(self):
            for _ in range(20):
                now[0] += 0.3
                yield b" "
        def close(self):
            closed.append(True)
    adapter = SupabaseAuth(SETTINGS, budget_clock=lambda: now[0], operation_seconds=1,
                           transport=httpx.MockTransport(lambda request: httpx.Response(200, stream=Trickle())))
    with pytest.raises(AuthFailure, match="auth_unavailable"):
        adapter.login(EMAIL, PASSWORD)
    assert 1 <= now[0] <= 1.3
    assert closed


def test_real_http_framing_budget_stops_trickle_before_complete_response_headers(monkeypatch):
    now, timeouts, closed = [0.0], [], []
    class TrickleWire(httpcore.NetworkStream):
        def read(self, max_bytes, timeout=None):
            timeouts.append(timeout)
            now[0] += 0.25
            return b"H"  # No complete h11 header or body chunk is ever emitted.
        def write(self, buffer, timeout=None):
            pass
        def start_tls(self, ssl_context, server_hostname=None, timeout=None):
            return self
        def close(self):
            closed.append(True)
    monkeypatch.setattr(httpcore.SyncBackend, "connect_tcp", lambda *args, **kwargs: TrickleWire())
    adapter = SupabaseAuth(SETTINGS, budget_clock=lambda: now[0], operation_seconds=1)
    with pytest.raises(AuthFailure, match="auth_unavailable"):
        adapter.login(EMAIL, PASSWORD)
    assert now[0] == 1
    assert timeouts == [1, 0.75, 0.5, 0.25]
    assert closed


def test_tls_stream_created_after_deadline_is_closed_with_original_stream():
    now, closed = [0.0], []
    class TLSStream:
        def close(self):
            closed.append("tls")
    class PlainStream:
        def start_tls(self, *args, **kwargs):
            now[0] += 2
            return TLSStream()
        def close(self):
            closed.append("plain")
    stream = BudgetNetworkStream(PlainStream(), OperationBudget(1, lambda: now[0]))
    with pytest.raises(AuthFailure):
        stream.start_tls(None)
    assert closed == ["tls", "plain"]


@pytest.mark.parametrize("advance", [0.7, 1.1])
def test_complete_sdk_budget_is_shared_by_token_and_get_user(advance):
    now, calls = [0.0], []
    def transport(request):
        calls.append(request.url.path)
        if request.url.path.endswith("/token"):
            now[0] += advance
            return httpx.Response(200, json=provider_session())
        remaining = 1 - advance
        assert request.extensions["timeout"] == pytest.approx(dict.fromkeys(["connect", "read", "write", "pool"], remaining))
        now[0] += 0.4
        return httpx.Response(200, json=provider_user())
    adapter = SupabaseAuth(SETTINGS, transport=httpx.MockTransport(transport),
                           budget_clock=lambda: now[0], operation_seconds=1)
    with pytest.raises(AuthFailure, match="auth_unavailable"):
        adapter.login(EMAIL, PASSWORD)
    assert len(calls) == (2 if advance < 1 else 1)


@pytest.mark.parametrize("fail", [False, True])
def test_overlapping_status_coalesces_validation_without_caching_later_requests(fail):
    async def scenario():
        app = create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=FakeAuth())
        fake = app.state.auth_adapter
        entered, release = Event(), Event()
        original = fake.validate
        def validate(identity):
            entered.set()
            assert release.wait(3)
            return original(identity)
        fake.validate = validate
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=ORIGIN) as client:
            boot = await client.get("/api/v1/auth/status")
            await client.post("/api/v1/auth/login", json=PAYLOAD,
                              headers={"Origin": ORIGIN, "X-CSRF-Token": boot.json()["csrfToken"]})
            fake.fail = fail
            first = asyncio.create_task(client.get("/api/v1/auth/status"))
            assert await asyncio.to_thread(entered.wait, 2)
            second = asyncio.create_task(client.get("/api/v1/auth/status"))
            await asyncio.sleep(0.05)
            release.set()
            responses = await asyncio.gather(first, second)
            assert fake.calls.count("validate") == 1
            assert [r.status_code for r in responses] == [503 if fail else 200] * 2
            if fail:
                assert not app.state.auth_registry.sessions
            else:
                await client.get("/api/v1/auth/status")
                assert fake.calls.count("validate") == 2
    asyncio.run(scenario())


def test_separate_sessions_validate_concurrently():
    registry, fake = Registry(), FakeAuth()
    bindings = [registry.browser(None)[0] for _ in range(2)]
    sessions = [registry.rotate(None, binding, fake.identity()) for binding in bindings]
    from threading import Barrier
    both = Barrier(2)
    def validate(identity):
        both.wait(timeout=2)
        return identity
    fake.validate = validate
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(lambda pair: registry.authenticated(*pair, fake), zip(sessions, bindings)))
    assert all(result.owner_id == OWNER for result in results)


@pytest.mark.parametrize("flow", ["login", "confirmation"])
def test_near_expiry_binding_covers_new_session_and_pending_attempt(flow):
    now = [1000.0]
    registry, fake = Registry(clock=lambda: now[0], idle_seconds=500, absolute_seconds=100), FakeAuth()
    browser, binding = registry.browser(None)
    now[0] += 99
    if flow == "confirmation":
        state, pending = registry.start_attempt(browser, EMAIL)
        pending.verifier = "v" * 43
        assert binding.expires >= pending.expires
        now[0] += 20
        registry.consume(state, browser)
    else:
        registry.retain_browser(browser)
        now[0] += 20
    session = registry.rotate(None, browser, fake.identity())
    assert binding.expires >= now[0] + 100
    now[0] += 99
    assert registry.authenticated(session, browser, fake)
    now[0] += 1
    assert registry.authenticated(session, browser, fake) is None


def test_elapsed_body_budget_rejects_actually_delayed_stream_before_provider(monkeypatch):
    from app.api import auth
    monkeypatch.setattr(auth, "CREDENTIAL_BODY_SECONDS", 0.03)
    async def scenario():
        fake = FakeAuth()
        app = create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=fake)
        cancelled = []
        async def delayed():
            body = json.dumps(PAYLOAD).encode()
            yield body[:10]
            try:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                cancelled.append(True)
                raise
            yield body[10:]
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=ORIGIN) as client:
            boot = await client.get("/api/v1/auth/status")
            response = await client.post("/api/v1/auth/login", content=delayed(),
                headers={"Origin": ORIGIN, "X-CSRF-Token": boot.json()["csrfToken"], "Content-Type": "application/json"})
            assert response.status_code == 422
            assert response.json()["code"] == "invalid_request"
            assert response.headers["cache-control"] == "no-store"
            assert cancelled
            assert not fake.calls
    asyncio.run(scenario())


def test_cancelled_validation_waiter_cannot_orphan_owner_before_worker_admission():
    import anyio
    async def scenario():
        registry, fake = Registry(), FakeAuth()
        browser = registry.browser(None)[0]
        session = registry.rotate(None, browser, fake.identity())
        limiter = anyio.to_thread.current_default_thread_limiter()
        previous = limiter.total_tokens
        entered, release = Event(), Event()
        def occupy_worker():
            entered.set()
            assert release.wait(3)
        limiter.total_tokens = 1
        try:
            occupied = asyncio.create_task(anyio.to_thread.run_sync(occupy_worker))
            assert await asyncio.to_thread(entered.wait, 2)
            cancelled = asyncio.create_task(registry.authenticated_async(session, browser, fake))
            await asyncio.sleep(0.03)
            assert registry.sessions[session].validation is not None
            cancelled.cancel()
            with pytest.raises(asyncio.CancelledError):
                await cancelled
            follower = asyncio.create_task(registry.authenticated_async(session, browser, fake))
            release.set()
            await occupied
            identity = await asyncio.wait_for(follower, timeout=2)
            assert identity.owner_id == OWNER
            assert fake.calls.count("validate") == 1
            assert registry.sessions[session].validation is None
        finally:
            release.set()
            limiter.total_tokens = previous
    asyncio.run(scenario())


def test_credential_accumulator_checks_bound_before_appending(monkeypatch):
    from app.api import auth
    appended = []
    class TrackedBuffer(bytearray):
        def extend(self, chunk):
            appended.append(len(chunk))
            return super().extend(chunk)
    monkeypatch.setattr(auth, "bytearray", TrackedBuffer, raising=False)
    class Request:
        headers = {"content-type": "application/json"}
        async def stream(self):
            yield b" " * 8192
            yield b"x" * 100000
    with pytest.raises(AuthFailure, match="invalid_request"):
        asyncio.run(auth.credentials(Request()))
    assert appended == [8192]
    class ExactRequest:
        headers = {"content-type": "application/json"}
        async def stream(self):
            body = json.dumps(PAYLOAD).encode()
            yield body + b" " * (8192 - len(body))
    assert asyncio.run(auth.credentials(ExactRequest())).email == EMAIL


@pytest.mark.parametrize("fail", [False, True])
def test_old_status_validation_cannot_erase_new_login_cookie_in_arrival_order(fail):
    async def scenario():
        fake = FakeAuth()
        app = create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=fake)
        entered, release = Event(), Event()
        def validate(identity):
            entered.set()
            assert release.wait(3)
            if fail:
                raise AuthFailure()
            return identity
        fake.validate = validate
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=ORIGIN) as client:
            boot = await client.get("/api/v1/auth/status")
            protection = {"Origin": ORIGIN, "X-CSRF-Token": boot.json()["csrfToken"]}
            await client.post("/api/v1/auth/login", json=PAYLOAD, headers=protection)
            old_cookie = session_cookie(client)
            old_status = asyncio.create_task(client.get("/api/v1/auth/status"))
            assert await asyncio.to_thread(entered.wait, 2)
            login = await client.post("/api/v1/auth/login", json=PAYLOAD, headers=protection)
            new_cookie = session_cookie(client)
            assert new_cookie != old_cookie and login.status_code == 200
            release.set()
            response = await old_status
            assert not response.json().get("authenticated", False)
            assert "sb_session" not in response.headers.get("set-cookie", "")
            assert session_cookie(client) == new_cookie
            assert new_cookie in app.state.auth_registry.sessions
    asyncio.run(scenario())


@pytest.mark.parametrize("error", [False, True])
def test_already_completed_denial_response_cannot_erase_a_later_login(error):
    client, fake, registry = setup()
    protection = headers(client)
    client.post("/api/v1/auth/login", json=PAYLOAD, headers=protection)
    if error:
        fake.fail = True
    else:
        registry.sessions.clear()
    stale = client.get("/api/v1/auth/status")
    fake.fail = False
    client.post("/api/v1/auth/login", json=PAYLOAD, headers=protection)
    newest = session_cookie(client)
    client.cookies.extract_cookies(stale)
    assert session_cookie(client) == newest
    assert "sb_session" not in stale.headers.get("set-cookie", "")


def test_http_signup_passes_each_exact_callback_state_to_real_sdk_transport():
    redirects = []
    def transport(request):
        assert request.url.path.endswith("/signup")
        redirects.append(request.url.params["redirect_to"])
        return httpx.Response(200, json=provider_user(confirmed=False))
    registry = Registry()
    adapter = SupabaseAuth(SETTINGS, transport=httpx.MockTransport(transport))
    client = TestClient(create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=adapter, registry=registry), base_url=ORIGIN)
    post(client)
    post(client)
    assert len(redirects) == 2
    assert redirects == [ORIGIN + "/api/v1/auth/callback?state=" + state for state in registry.pending]
    assert redirects[0] != redirects[1]


@pytest.mark.parametrize("case", ["missing", "unconfirmed", "changed_owner", "changed_email"])
def test_real_sdk_status_retires_invalid_existing_identity_without_cookie_mutation(case):
    status_validation = [False]
    def transport(request):
        if request.url.path.endswith("/token"):
            return httpx.Response(200, json=provider_session())
        user = provider_user()
        if status_validation[0]:
            if case == "missing":
                user = {}
            elif case == "unconfirmed":
                user["email_confirmed_at"] = None
            elif case == "changed_owner":
                user["id"] = OTHER
            elif case == "changed_email":
                user["email"] = "other@example.test"
        return httpx.Response(200, json=user)
    adapter = SupabaseAuth(SETTINGS, transport=httpx.MockTransport(transport))
    registry = Registry()
    client = TestClient(create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=adapter, registry=registry), base_url=ORIGIN)
    assert post(client, "login").status_code == 200
    old_cookie = session_cookie(client)
    status_validation[0] = True
    response = client.get("/api/v1/auth/status")
    assert response.status_code in (401, 503)
    assert not response.json().get("authenticated", False)
    assert old_cookie not in registry.sessions
    assert session_cookie(client) == old_cookie
    assert "sb_session" not in response.headers.get("set-cookie", "")
    assert response.headers["cache-control"] == "no-store"
    assert "PRIVATE" not in response.text


def recovery_grant(client, fake):
    assert post(client, "recovery/request", {"email": EMAIL}).json()["status"] == "check_email"
    response = callback(client, fake.redirects[-1])
    assert response.headers["location"] == "/account?recovery=success"
    return session_cookie(client)


def test_recovery_replaces_local_session_with_restricted_authority_and_requires_login():
    client, fake, registry = setup()
    assert post(client, "login").status_code == 200
    original = session_cookie(client)
    grant = recovery_grant(client, fake)
    assert grant != original and original not in registry.sessions
    assert not registry.sessions and grant in registry.recoveries
    before = list(fake.calls)
    display = client.get("/api/v1/auth/status").json()
    assert display["authenticated"] is False and display["recoveryAvailable"] is True
    assert "email" not in display and fake.calls == before
    updated = post(client, "recovery/password", {"password": PASSWORD})
    assert updated.json() == {"status": "password_updated", "authenticated": False, "recoveryAvailable": False}
    assert "sb_session" not in updated.headers.get("set-cookie", "")
    assert not registry.recoveries and fake.calls.count("update_password") == 1
    assert post(client, "recovery/password", {"password": PASSWORD}).status_code == 401
    assert client.get("/api/v1/auth/status").json()["authenticated"] is False
    assert post(client, "login").status_code == 200
    assert session_cookie(client) != grant


@pytest.mark.parametrize("case", ["wrong_browser", "missing_binding", "missing_state", "missing_code", "missing_verifier", "purpose", "expired", "replay", "restart", "duplicate_state", "implicit"])
def test_recovery_callback_binding_purpose_expiry_and_exact_query(case):
    now = [time.time()]
    client, fake, registry = setup(registry=Registry(clock=lambda: now[0]))
    post(client, "recovery/request", {"email": EMAIL})
    redirect = fake.redirects[-1]
    pending = next(iter(registry.pending.values()))
    if case == "wrong_browser":
        client.cookies.clear()
        headers(client)
    elif case == "missing_binding":
        client.cookies.clear()
    elif case == "missing_verifier":
        pending.verifier = None
    elif case == "purpose":
        pending.purpose = "signup"
    elif case == "expired":
        now[0] += 600
    elif case == "restart":
        registry.pending.clear()
    elif case == "replay":
        callback(client, redirect)
        fake.calls.clear()
    elif case == "duplicate_state":
        redirect += "&state=" + "z" * 43
    elif case == "implicit":
        redirect += "&access_token=PRIVATE_ACCESS"
    if case == "missing_state":
        redirect = ORIGIN + "/api/v1/auth/recovery/callback"
    response = client.get(redirect, follow_redirects=False) if case == "missing_code" else callback(client, redirect)
    assert response.headers["location"] == "/account?recovery=invalid"
    assert "exchange" not in fake.calls
    assert not registry.sessions
    assert response.headers["cache-control"] == "no-store"


def test_recovery_and_signup_share_attempt_limits_but_keep_distinct_verifiers():
    client, fake, registry = setup()
    for action in ["signup", "recovery/request"] * 2:
        assert post(client, action, PAYLOAD if action == "signup" else {"email": EMAIL}).status_code == 200
    assert len(registry.pending) == 4
    assert len({pending.verifier for pending in registry.pending.values()}) == 4
    assert post(client, "recovery/request", {"email": EMAIL}).status_code == 429
    recovery = fake.redirects[1]
    signup_path = recovery.replace("/recovery/callback", "/callback")
    assert callback(client, signup_path).headers["location"] == "/account?confirmation=invalid"
    assert callback(client, recovery).headers["location"] == "/account?recovery=success"
    assert callback(client, fake.redirects[0]).headers["location"] == "/account?confirmation=success"
    assert len(registry.sessions) == 1 and not registry.recoveries


def test_recovery_grants_combined_capacity_expiry_rotation_and_other_users():
    now = [1000.0]
    registry, fake = Registry(clock=lambda: now[0], capacity=2), FakeAuth()
    first, other = [registry.browser(None)[0] for _ in range(2)]
    normal = registry.rotate(None, first, fake.identity())
    other_session = registry.rotate(None, other, fake.identity("other@example.test"))
    with pytest.raises(AuthFailure, match="auth_capacity"):
        registry.rotate(None, first, fake.identity(), recovery=True)
    grant = registry.rotate(normal, first, fake.identity(), recovery=True)
    assert normal not in registry.sessions and other_session in registry.sessions
    assert registry.authenticated(grant, first, fake) is None
    assert not registry.recovery_available(grant, other)
    with pytest.raises(AuthFailure, match="invalid_recovery"):
        registry.claim_recovery(other_session, other)
    assert registry.authenticated(other_session, other, fake)
    now[0] += 600
    assert not registry.recovery_available(grant, first)
    assert other_session in registry.sessions
    assert registry.rotate(None, first, fake.identity(), recovery=True)


@pytest.mark.parametrize("action,payload", [("recovery/request", {"email": EMAIL}), ("recovery/password", {"password": PASSWORD})])
@pytest.mark.parametrize("case", ["origin", "csrf", "extra_owner", "extra_metadata", "malformed", "oversize", "wrong_type"])
def test_recovery_protections_and_strict_bounded_bodies_precede_provider(action, payload, case):
    client, fake, _ = setup()
    protection = headers(client)
    content = json.dumps(payload)
    protection["Content-Type"] = "application/json"
    if case == "origin":
        protection["Origin"] = "https://attacker.test"
    elif case == "csrf":
        protection["X-CSRF-Token"] = "wrong"
    elif case == "extra_owner":
        content = json.dumps({**payload, "ownerId": OTHER})
    elif case == "extra_metadata":
        content = json.dumps({**payload, "user_metadata": {"owner": OTHER}})
    elif case == "malformed":
        content = "{PRIVATE"
    elif case == "oversize":
        content += " " * 8192
    elif case == "wrong_type":
        content = json.dumps({key: 23 for key in payload})
    response = client.post("/api/v1/auth/" + action, headers=protection, content=content)
    assert response.status_code == (403 if case in ("origin", "csrf") else 422)
    assert not fake.calls and "PRIVATE" not in response.text
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("fail", [False, True])
def test_concurrent_password_updates_claim_once_and_late_reply_never_changes_new_login_cookie(fail):
    async def scenario():
        fake, registry = FakeAuth(), Registry()
        entered, release = Event(), Event()
        def update(identity, password, *, expires_at):
            fake.calls.append("update_password")
            entered.set()
            assert release.wait(3)
            if fail:
                raise AuthFailure()
        fake.update_password = update
        app = create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=fake, registry=registry)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=ORIGIN) as client:
            boot = await client.get("/api/v1/auth/status")
            protection = {"Origin": ORIGIN, "X-CSRF-Token": boot.json()["csrfToken"]}
            await client.post("/api/v1/auth/recovery/request", json={"email": EMAIL}, headers=protection)
            await client.get(fake.redirects[-1] + "&code=PRIVATE_CODE")
            pending = asyncio.create_task(client.post("/api/v1/auth/recovery/password", json={"password": PASSWORD}, headers=protection))
            assert await asyncio.to_thread(entered.wait, 2)
            duplicate = await client.post("/api/v1/auth/recovery/password", json={"password": PASSWORD}, headers=protection)
            assert duplicate.status_code == 401
            login = await client.post("/api/v1/auth/login", json=PAYLOAD, headers=protection)
            assert login.status_code == 200
            newest = session_cookie(client)
            release.set()
            response = await pending
            assert response.status_code == (503 if fail else 200)
            if fail:
                assert response.json()["code"] == "recovery_failed"
                assert "kan være endret" in response.json()["message"]
            assert "sb_session" not in response.headers.get("set-cookie", "")
            assert session_cookie(client) == newest
            assert newest in registry.sessions and not registry.recoveries
            assert fake.calls.count("update_password") == 1
    asyncio.run(scenario())


def recovery_token(expires):
    def encoded(value):
        return base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip("=")
    return encoded({"alg": "HS256"}) + "." + encoded({"exp": expires, "sub": OWNER}) + ".c3ludGhldGlj"


def test_http_recovery_exact_sdk_redirect_challenge_actual_verifier_and_password_only_write():
    registry, recoveries, writes = Registry(), [], []
    jwt = recovery_token(int(time.time()) + 3600)
    def transport(request):
        body = json.loads(request.content) if request.content else None
        if request.url.path.endswith("/recover"):
            pending = list(registry.pending.values())[-1]
            assert pending.purpose == "recovery" and "/" not in pending.verifier
            assert body["email"] == EMAIL
            assert body["code_challenge"] == base64.urlsafe_b64encode(hashlib.sha256(pending.verifier.encode()).digest()).decode().rstrip("=")
            assert body["code_challenge_method"] == "s256"
            recoveries.append(request.url.params["redirect_to"])
            return httpx.Response(200, json={})
        if request.url.path.endswith("/token"):
            assert request.url.params["grant_type"] == "pkce"
            index = int(body["auth_code"].removeprefix("PRIVATE_CODE_"))
            assert body == {"auth_code": "PRIVATE_CODE_" + str(index), "code_verifier": verifiers[index]}
            session = provider_session()
            session["access_token"] = jwt
            return httpx.Response(200, json=session)
        assert request.headers["authorization"] == "Bearer " + jwt
        if request.method == "PUT":
            writes.append(body)
            assert body == {"password": PASSWORD}
        return httpx.Response(200, json=provider_user())
    adapter = SupabaseAuth(SETTINGS, transport=httpx.MockTransport(transport))
    client = TestClient(create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=adapter, registry=registry), base_url=ORIGIN)
    for _ in range(2):
        assert post(client, "recovery/request", {"email": EMAIL}).status_code == 200
    assert recoveries == [ORIGIN + "/api/v1/auth/recovery/callback?state=" + state for state in registry.pending]
    verifiers = [p.verifier for p in registry.pending.values()]
    assert verifiers[0] != verifiers[1]
    for index, redirect in enumerate(recoveries):
        assert callback(client, redirect, "PRIVATE_CODE_" + str(index)).headers["location"] == "/account?recovery=success"
        grant = session_cookie(client)
        assert grant in registry.recoveries and not registry.sessions
        display = client.get("/api/v1/auth/status").json()
        assert display["authenticated"] is False and display["recoveryAvailable"] is True
        assert len(registry.pending) == 1 - index
        assert post(client, "recovery/password", {"password": PASSWORD}).status_code == 200
        assert grant not in registry.recoveries and not registry.sessions
    assert writes == [{"password": PASSWORD}] * 2


@pytest.mark.parametrize("case", ["changed_owner", "changed_email", "unconfirmed", "expired_grant", "refreshed_owner", "refreshed_email", "post_write_owner", "write_timeout", "budget_before_write", "budget_after_write"])
def test_sdk_recovery_validates_before_write_and_never_retries_uncertain_updates(case):
    now, paths, writes = [0.0], [], []
    jwt = recovery_token(int(time.time()) + (-10 if case.startswith("refreshed_") else 3600))
    def transport(request):
        paths.append((request.method, request.url.path))
        if request.url.path.endswith("/token"):
            assert request.url.params["grant_type"] == "refresh_token"
            session = provider_session()
            session["access_token"] = recovery_token(int(time.time()) + 3600)
            if case == "refreshed_owner":
                session["user"]["id"] = OTHER
            elif case == "refreshed_email":
                session["user"]["email"] = "other@example.test"
            return httpx.Response(200, json=session)
        user = provider_user()
        if request.method == "PUT":
            writes.append(json.loads(request.content))
            if case == "write_timeout":
                raise httpx.ReadTimeout("PRIVATE_PROVIDER_BODY")
            if case == "post_write_owner":
                user["id"] = OTHER
            if case == "budget_after_write":
                now[0] += 2
        else:
            if case == "changed_owner":
                user["id"] = OTHER
            elif case == "changed_email":
                user["email"] = "other@example.test"
            elif case == "unconfirmed":
                user["email_confirmed_at"] = None
            if case == "budget_before_write":
                now[0] += 0.6
        return httpx.Response(200, json=user)
    adapter = SupabaseAuth(SETTINGS, transport=httpx.MockTransport(transport),
                           budget_clock=lambda: now[0], operation_seconds=1)
    identity = Identity(OWNER, EMAIL, jwt, "PRIVATE_REFRESH", time.time() + 3600)
    with pytest.raises(AuthFailure):
        adapter.update_password(identity, PASSWORD, expires_at=time.time() + (-1 if case == "expired_grant" else 600))
    expected = 1 if case in ("post_write_owner", "write_timeout", "budget_after_write") else 0
    assert len(writes) == expected


def test_recovery_request_nonexistent_account_ack_and_provider_outage_are_safe():
    for provider_status in (200, 404, 503):
        def transport(request):
            return httpx.Response(provider_status, headers={"X-Supabase-Api-Version": "2024-01-01"},
                                  json={} if provider_status == 200 else {"code": "user_not_found" if provider_status == 404 else "unexpected_failure", "message": "PRIVATE_BODY"})
        adapter = SupabaseAuth(SETTINGS, transport=httpx.MockTransport(transport))
        client = TestClient(create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=adapter), base_url=ORIGIN)
        response = post(client, "recovery/request", {"email": EMAIL})
        assert response.status_code == (503 if provider_status == 503 else 200)
        assert "PRIVATE" not in response.text and session_cookie(client) is None


@pytest.mark.parametrize("action,payload", [("recovery/request", {"email": EMAIL}), ("recovery/password", {"password": PASSWORD})])
def test_slow_recovery_body_rejects_before_provider_or_grant_consumption(monkeypatch, action, payload):
    from app.api import auth
    monkeypatch.setattr(auth, "CREDENTIAL_BODY_SECONDS", 0.02)
    async def scenario():
        fake, registry = FakeAuth(), Registry()
        app = create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=fake, registry=registry)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=ORIGIN) as client:
            boot = await client.get("/api/v1/auth/status")
            binding = client.cookies["sb_browser"]
            grant = registry.rotate(None, binding, fake.identity(), recovery=True)
            client.cookies.set("sb_session", grant, domain="127.0.0.1", path="/")
            async def delayed():
                body = json.dumps(payload).encode()
                yield body[:10]
                await asyncio.sleep(0.1)
                yield body[10:]
            response = await client.post("/api/v1/auth/" + action, content=delayed(), headers={
                "Origin": ORIGIN, "X-CSRF-Token": boot.json()["csrfToken"], "Content-Type": "application/json"})
            assert response.status_code == 422 and response.headers["cache-control"] == "no-store"
            assert not fake.calls and grant in registry.recoveries
    asyncio.run(scenario())


@pytest.mark.parametrize("case", ["email", "owner", "unconfirmed", "no_refresh"])
def test_real_sdk_recovery_callback_rejects_invalid_identity_before_grant(case):
    def transport(request):
        if request.url.path.endswith("/recover"):
            return httpx.Response(200, json={})
        if request.url.path.endswith("/token"):
            session = provider_session()
            if case == "no_refresh":
                session.pop("refresh_token")
            return httpx.Response(200, json=session)
        user = provider_user()
        if case == "email":
            user["email"] = "other@example.test"
        elif case == "owner":
            user["id"] = OTHER
        elif case == "unconfirmed":
            user["email_confirmed_at"] = None
        return httpx.Response(200, json=user)
    registry = Registry()
    client = TestClient(create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=SupabaseAuth(SETTINGS, transport=httpx.MockTransport(transport)), registry=registry), base_url=ORIGIN)
    post(client, "recovery/request", {"email": EMAIL})
    state = next(iter(registry.pending))
    response = callback(client, ORIGIN + "/api/v1/auth/recovery/callback?state=" + state)
    assert response.headers["location"] == "/account?recovery=invalid"
    assert not registry.sessions and not registry.recoveries and not registry.pending


def test_expiry_during_recovery_exchange_cannot_create_restricted_authority():
    now = [time.time()]
    client, fake, registry = setup(registry=Registry(clock=lambda: now[0]))
    post(client, "recovery/request", {"email": EMAIL})
    def delayed_exchange(code, pending):
        now[0] = pending.expires
        return fake.identity()
    fake.exchange = delayed_exchange
    assert callback(client, fake.redirects[0]).headers["location"] == "/account?recovery=invalid"
    assert not registry.recoveries and not registry.pending


@pytest.mark.parametrize("changed", ["owner", "email", "none"])
def test_sdk_update_user_implicit_near_expiry_refresh_is_validated_before_put(changed):
    jwt, calls = recovery_token(int(time.time()) + 5), []
    def transport(request):
        calls.append((request.method, request.url.path))
        if request.url.path.endswith("/token"):
            assert request.url.params["grant_type"] == "refresh_token"
            session = provider_session()
            session["access_token"] = recovery_token(int(time.time()) + 3600)
            if changed == "owner":
                session["user"]["id"] = OTHER
            elif changed == "email":
                session["user"]["email"] = "other@example.test"
            return httpx.Response(200, json=session)
        return httpx.Response(200, json=provider_user())
    adapter = SupabaseAuth(SETTINGS, transport=httpx.MockTransport(transport))
    identity = Identity(OWNER, EMAIL, jwt, "PRIVATE_REFRESH", time.time() + 5)
    if changed == "none":
        adapter.update_password(identity, PASSWORD, expires_at=time.time() + 600)
    else:
        with pytest.raises(AuthFailure):
            adapter.update_password(identity, PASSWORD, expires_at=time.time() + 600)
    assert sum(method == "PUT" for method, _ in calls) == (1 if changed == "none" else 0)
    assert sum(path.endswith("/token") for _, path in calls) == 1


@pytest.mark.parametrize("prior", ["anonymous", "normal", "recovery"])
def test_blocked_recovery_exchange_cannot_replace_intervening_login_and_other_attempt_still_works(prior):
    async def scenario():
        fake, registry = FakeAuth(), Registry()
        entered, release = Event(), Event()
        app = create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=fake, registry=registry)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=ORIGIN) as client:
            boot = await client.get("/api/v1/auth/status")
            protection = {"Origin": ORIGIN, "X-CSRF-Token": boot.json()["csrfToken"]}
            if prior == "normal":
                await client.post("/api/v1/auth/login", json=PAYLOAD, headers=protection)
            elif prior == "recovery":
                await client.post("/api/v1/auth/recovery/request", json={"email": EMAIL}, headers=protection)
                await client.get(fake.redirects[-1] + "&code=PRIVATE_CODE")
            for _ in range(2):
                await client.post("/api/v1/auth/recovery/request", json={"email": EMAIL}, headers=protection)
            blocked_link, independent_link = fake.redirects[-2:]
            exchange = fake.exchange
            def blocked_exchange(code, pending):
                if code == "BLOCKED_PRIVATE_CODE":
                    entered.set()
                    assert release.wait(3)
                return exchange(code, pending)
            fake.exchange = blocked_exchange
            blocked = asyncio.create_task(client.get(blocked_link + "&code=BLOCKED_PRIVATE_CODE"))
            assert await asyncio.to_thread(entered.wait, 2)
            response = await client.post("/api/v1/auth/login", json={"email": "other@example.test", "password": PASSWORD}, headers=protection)
            assert response.status_code == 200
            newest = session_cookie(client)
            release.set()
            response = await blocked
            assert response.headers["location"] == "/account?recovery=invalid"
            assert "sb_session" not in response.headers.get("set-cookie", "")
            assert session_cookie(client) == newest
            assert newest in registry.sessions and not registry.recoveries
            display = (await client.get("/api/v1/auth/status")).json()
            assert display["authenticated"] is True and display["email"] == "other@example.test"
            independent = await client.get(independent_link + "&code=PRIVATE_CODE")
            assert independent.headers["location"] == "/account?recovery=success"
            assert newest not in registry.sessions
            grant = session_cookie(client)
            assert grant in registry.recoveries and not registry.sessions
            assert not registry.pending
    asyncio.run(scenario())


@pytest.mark.parametrize("crossing", ["refresh", "validation"])
def test_grant_expiry_during_final_sdk_session_validation_prevents_put(crossing):
    now = [time.time()]
    expires, calls, refreshed = now[0] + 1, [], [False]
    jwt = recovery_token(int(time.time()) + 5)
    def transport(request):
        calls.append((request.method, request.url.path))
        if request.url.path.endswith("/token"):
            refreshed[0] = True
            if crossing == "refresh":
                now[0] = expires
            session = provider_session()
            session["access_token"] = recovery_token(int(time.time()) + 3600)
            return httpx.Response(200, json=session)
        if refreshed[0] and crossing == "validation":
            now[0] = expires
        return httpx.Response(200, json=provider_user())
    adapter = SupabaseAuth(SETTINGS, clock=lambda: now[0], transport=httpx.MockTransport(transport))
    identity = Identity(OWNER, EMAIL, jwt, "PRIVATE_REFRESH", time.time() + 5)
    with pytest.raises(AuthFailure, match="invalid_recovery"):
        adapter.update_password(identity, PASSWORD, expires_at=expires)
    assert refreshed[0] and now[0] == expires
    assert not any(method == "PUT" for method, _ in calls)


def test_failed_recovery_requests_release_pending_slots_and_provider_recovery_allows_retry():
    client, fake, registry = setup()
    fake.fail = True
    for _ in range(5):
        response = post(client, "recovery/request", {"email": EMAIL})
        assert response.status_code == 503 and response.json()["code"] == "auth_unavailable"
        assert not registry.pending
    assert fake.calls.count("request_recovery") == 5
    fake.fail = False
    assert post(client, "recovery/request", {"email": EMAIL}).status_code == 200

    assert len(registry.pending) == 1
    assert callback(client, fake.redirects[-1]).headers["location"] == "/account?recovery=success"
    assert not registry.pending and len(registry.recoveries) == 1


@pytest.mark.parametrize("restricted", [False, True])
def test_logout_ends_all_browser_authority_and_attempts_but_retains_fresh_login(restricted):
    client, fake, registry = setup()
    assert post(client, "login").status_code == 200
    if restricted:
        recovery_grant(client, fake)
    assert post(client).status_code == 200
    old = session_cookie(client)
    binding = client.cookies["sb_browser"]
    protection = headers(client)
    revision = registry.browsers[binding].authority_revision
    response = client.post("/api/v1/auth/logout", json={}, headers=protection)
    assert response.json() == {"authenticated": False, "recoveryAvailable": False}
    assert 'sb_session_' in response.headers["set-cookie"]
    assert "Max-Age=0" in response.headers["set-cookie"]
    assert "HttpOnly" in response.headers["set-cookie"]
    assert response.headers["cache-control"] == "no-store"
    assert not registry.sessions and not registry.recoveries and not registry.pending
    assert registry.browsers[binding].authority_revision > revision
    assert client.cookies["sb_browser"] == binding
    assert fake.calls.count("revoke") == 1
    client.cookies.set("sb_session", old)
    assert client.get("/api/v1/auth/status").json()["authenticated"] is False
    assert client.post("/api/v1/auth/logout", json={}, headers=protection).status_code == 200
    assert post(client, "login").status_code == 200


@pytest.mark.parametrize("case", ["origin", "csrf", "extra", "array", "null", "bytes", "content", "unavailable"])
def test_logout_protection_empty_json_and_configuration_precede_provider(case):
    client, fake, registry = setup()
    post(client, "login")
    protection = headers(client)
    session = session_cookie(client)
    body = b"{}"
    protection["Content-Type"] = "application/json"
    if case == "origin":
        protection["Origin"] = "https://foreign.test"
    elif case == "csrf":
        protection["X-CSRF-Token"] = "wrong"
    elif case == "content":
        protection["Content-Type"] = "text/plain"
    elif case == "unavailable":
        client.app.state.settings = replace(SETTINGS, auth_enabled=False)
    else:
        body = {"extra": b'{"scope":"global"}', "array": b"[]", "null": b"null", "bytes": b" " * 8193}.get(case, body)
    response = client.post("/api/v1/auth/logout", content=body, headers=protection)
    assert response.status_code == (403 if case in ("origin", "csrf") else 503 if case == "unavailable" else 422)
    assert session in registry.sessions
    assert "revoke" not in fake.calls


def test_local_logout_provider_outage_preserves_other_browser_even_for_same_account():
    client, fake, registry = setup()
    second = TestClient(client.app, base_url=ORIGIN)
    installed, revoked = [], []
    def independent_login(email, password):
        identity = replace(fake.identity(email), access_token=f"PRIVATE_ACCESS_{len(installed)}",
                           refresh_token=f"PRIVATE_REFRESH_{len(installed)}")
        installed.append(identity)
        return identity
    def revoke(identity, *, budget):
        revoked.append(identity.access_token)
        raise AuthFailure()
    fake.login, fake.revoke = independent_login, revoke
    for current in (client, second):
        assert post(current, "login").status_code == 200
    second_id = session_cookie(second)
    protection = headers(client)
    fake.fail = True
    assert client.post("/api/v1/auth/logout", json={}, headers=protection).status_code == 200
    assert second_id in registry.sessions
    assert not client.get("/api/v1/auth/status").json()["authenticated"]
    fake.fail = False
    assert second.get("/api/v1/auth/status").json()["email"] == EMAIL
    assert installed[0].owner_id == installed[1].owner_id
    assert installed[0].access_token != installed[1].access_token
    assert revoked == [installed[0].access_token]
    assert registry.sessions[second_id].identity.access_token == installed[1].access_token


def test_passive_status_cannot_renew_idle_but_authenticated_work_can():
    now = [1000.0]
    registry = Registry(clock=lambda: now[0], idle_seconds=30, absolute_seconds=120)
    client, fake, _ = setup(registry=registry)
    post(client, "login")
    session, browser = session_cookie(client), client.cookies["sb_browser"]
    assert client.get("/api/v1/auth/status").json()["expiresInSeconds"] == 30
    now[0] += 20
    assert client.get("/api/v1/auth/status").json()["expiresInSeconds"] == 10
    assert registry.authenticated(session, browser, fake)
    assert client.get("/api/v1/auth/status").json()["expiresInSeconds"] == 30
    now[0] += 30
    assert not client.get("/api/v1/auth/status").json()["authenticated"]
    assert "expiresInSeconds" not in client.get("/api/v1/auth/status").json()


def test_default_maximum_lifetimes_absolute_expiry_and_recovery_snapshot(monkeypatch):
    for key in ("AUTH_IDLE_SECONDS", "AUTH_ABSOLUTE_SECONDS"):
        monkeypatch.delenv(key, raising=False)
    assert Settings.from_env().idle_seconds == Registry().idle_seconds == 1800
    assert Settings.from_env().absolute_seconds == Registry().absolute_seconds == 43200
    monkeypatch.setenv("AUTH_IDLE_SECONDS", "1801")
    monkeypatch.setenv("AUTH_ABSOLUTE_SECONDS", "43201")
    assert Settings.from_env().idle_seconds == 1800
    assert Settings.from_env().absolute_seconds == 43200
    now = [0]
    registry = Registry(clock=lambda: now[0], idle_seconds=100, absolute_seconds=120)
    fake = FakeAuth()
    binding, _ = registry.browser(None)
    session = registry.rotate(None, binding, fake.identity())
    for advance in (80, 110):
        now[0] = advance
        assert registry.authenticated(session, binding, fake)
    assert registry.remaining(session, binding) == 10
    now[0] = 120
    assert registry.authenticated(session, binding, fake) is None
    binding, _ = registry.browser(None)
    grant = registry.rotate(None, binding, fake.identity(), recovery=True)
    assert registry.remaining(grant, binding) == 600


@pytest.mark.parametrize("flow", ["login", "signup", "recovery/request", "signup_callback", "recovery_callback", "validation"])
def test_logout_fences_inflight_authority_after_provider_await(flow):
    async def scenario():
        fake = FakeAuth()
        app = create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=fake)
        entered, release = Event(), Event()
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=ORIGIN) as client:
            boot = await client.get("/api/v1/auth/status")
            protection = {"Origin": ORIGIN, "X-CSRF-Token": boot.json()["csrfToken"]}
            binding = client.cookies["sb_browser"]
            if flow.endswith("callback"):
                purpose = "signup" if flow == "signup_callback" else "recovery"
                await client.post("/api/v1/auth/" + ("signup" if purpose == "signup" else "recovery/request"), json=PAYLOAD if purpose == "signup" else {"email": EMAIL}, headers=protection)
                original = fake.exchange
                def delayed(*args):
                    entered.set()
                    assert release.wait(3)
                    return original(*args)
                fake.exchange = delayed
                url = fake.redirects[-1] + "&code=PRIVATE_CODE"
                pending = asyncio.create_task(client.get(url, follow_redirects=False))
            elif flow == "validation":
                await client.post("/api/v1/auth/login", json=PAYLOAD, headers=protection)
                original = fake.validate
                def delayed(*args):
                    entered.set()
                    assert release.wait(3)
                    return original(*args)
                fake.validate = delayed
                pending = asyncio.create_task(client.get("/api/v1/auth/status"))
            else:
                method = {"login": "login", "signup": "signup", "recovery/request": "request_recovery"}[flow]
                original = getattr(fake, method)
                def delayed(*args):
                    entered.set()
                    assert release.wait(3)
                    return original(*args)
                setattr(fake, method, delayed)
                pending = asyncio.create_task(client.post("/api/v1/auth/" + flow, json={"email": EMAIL} if flow == "recovery/request" else PAYLOAD, headers=protection))
            assert await asyncio.to_thread(entered.wait, 2)
            assert (await client.post("/api/v1/auth/logout", json={}, headers=protection)).status_code == 200
            release.set()
            response = await pending
            assert "sb_session" not in response.headers.get("set-cookie", "")
            registry = app.state.auth_registry
            assert not registry.sessions and not registry.recoveries and not registry.pending
            assert binding in registry.browsers
            if flow in ("login", "signup_callback", "recovery_callback"):
                assert fake.calls.count("revoke") == 1
            fake.login = FakeAuth().login
            assert (await client.post("/api/v1/auth/login", json=PAYLOAD, headers=protection)).status_code == 200
    asyncio.run(scenario())


def test_exact_sdk_revocation_user_jwt_local_scope_no_session_or_refresh():
    requests = []
    def transport(request):
        requests.append(request)
        assert request.method == "POST"
        assert request.url.path == "/auth/v1/logout"
        assert dict(request.url.params) == {"scope": "local"}
        assert request.headers["authorization"] == "Bearer PRIVATE_ACCESS"
        assert request.headers["apikey"] == SETTINGS.supabase_key
        return httpx.Response(204)
    adapter = SupabaseAuth(SETTINGS, transport=httpx.MockTransport(transport))
    adapter.revoke(replace(FakeAuth().identity(), expires_at=0), budget=OperationBudget(10, time.monotonic))
    assert len(requests) == 1


def test_revocation_admission_cancellation_and_shared_batch_deadline(monkeypatch):
    async def scenario():
        now = [0]
        manager = Revocations(clock=lambda: now[0])
        admitted, release = asyncio.Event(), asyncio.Event()
        entered = [0]
        async def blocked(action, *args, **kwargs):
            entered[0] += 1
            if entered[0] == 16:
                admitted.set()
            await release.wait()
            return action(*args)
        monkeypatch.setattr("app.services.sessions.to_thread.run_sync", blocked)
        fake = FakeAuth()
        waiters = [asyncio.create_task(manager.after_response(fake, (fake.identity(),))) for _ in range(16)]
        await asyncio.wait_for(admitted.wait(), 2)
        assert manager.active == 16
        await manager.after_response(fake, (fake.identity(),))
        assert entered[0] == 16
        waiters[0].cancel()
        with pytest.raises(asyncio.CancelledError):
            await waiters[0]
        assert manager.active == 16
        now[0] = 11  # Time spent awaiting worker admission consumes the same budget.
        release.set()
        await asyncio.gather(*waiters[1:])
        await asyncio.gather(*manager.tasks)
        assert manager.active == 0 and "revoke" not in fake.calls
        now[0] = 20
        def revoke(identity, *, budget):
            fake.calls.append("revoke")
            now[0] += 6
            budget.remaining()
        fake.revoke = revoke
        await manager.after_response(fake, (fake.identity(),) * 4)
        assert fake.calls == ["revoke", "revoke"]
    asyncio.run(scenario())


def test_logout_response_is_sent_before_revocation_starts_and_old_cookie_is_denied():
    async def scenario():
        client, fake, registry = setup()
        post(client, "login")
        protection = headers(client)
        binding, old = client.cookies["sb_browser"], session_cookie(client)
        sent = []
        def revoke(identity, *, budget):
            assert any(message["type"] == "http.response.body" and not message.get("more_body") for message in sent)
            start = next(message for message in sent if message["type"] == "http.response.start")
            assert any(key == b"set-cookie" and b"Max-Age=0" in value for key, value in start["headers"])
            assert registry.authenticated(old, binding, fake) is None
            fake.calls.append("revoke")
            raise AuthFailure()
        fake.revoke = revoke
        body = json.dumps({}).encode()
        delivered = False
        async def receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": body, "more_body": False}
            await asyncio.Future()
        async def send(message):
            sent.append(message)
        scope = {"type": "http", "asgi": {"version": "3.0", "spec_version": "2.4"}, "http_version": "1.1", "method": "POST", "scheme": "http", "path": "/api/v1/auth/logout", "raw_path": b"/api/v1/auth/logout", "query_string": b"", "root_path": "", "server": ("127.0.0.1", 8000), "client": ("127.0.0.1", 1), "headers": [(b"host", b"127.0.0.1:8000"), (b"origin", ORIGIN.encode()), (b"x-csrf-token", protection["X-CSRF-Token"].encode()), (b"content-type", b"application/json"), (b"cookie", f"sb_browser={binding}; sb_session={old}".encode())]}
        await client.app(scope, receive, send)
        assert fake.calls.count("revoke") == 1
    asyncio.run(scenario())


def test_expiry_during_validation_fences_authentication_that_started_before_deadline():
    now = [1000]
    registry = Registry(clock=lambda: now[0], idle_seconds=30)
    fake = FakeAuth()
    binding, _ = registry.browser(None)
    session = registry.rotate(None, binding, fake.identity())
    revision = registry.retain_browser(binding)
    state, pending = registry.start_attempt(binding, EMAIL)
    pending.verifier = "v" * 43
    pending = registry.consume(state, binding)
    def validate(identity):
        now[0] += 31
        return identity
    fake.validate = validate
    assert registry.authenticated(session, binding, fake, touch=False) is None
    assert registry.browsers[binding].authority_revision > revision
    for obsolete in (revision, pending.authority_revision):
        with pytest.raises(AuthFailure):
            registry.rotate(None, binding, fake.identity(), expected_revision=obsolete)


@pytest.mark.parametrize("flow", ["login", "signup", "recovery/request"])
def test_logout_during_body_stream_prevents_subsequent_provider_work(flow):
    async def scenario():
        fake = FakeAuth()
        app = create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=fake)
        entered, release = asyncio.Event(), asyncio.Event()
        async def delayed():
            entered.set()
            await release.wait()
            yield json.dumps({"email": EMAIL} if flow == "recovery/request" else PAYLOAD).encode()
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=ORIGIN) as client:
            boot = await client.get("/api/v1/auth/status")
            protection = {"Origin": ORIGIN, "X-CSRF-Token": boot.json()["csrfToken"], "Content-Type": "application/json"}
            request = asyncio.create_task(client.post("/api/v1/auth/" + flow, content=delayed(), headers=protection))
            await asyncio.wait_for(entered.wait(), 2)
            assert (await client.post("/api/v1/auth/logout", json={}, headers=protection)).status_code == 200
            release.set()
            assert (await request).status_code in (401, 503)
            assert not fake.calls
            assert not app.state.auth_registry.pending and not app.state.auth_registry.sessions
    asyncio.run(scenario())


@pytest.mark.parametrize("purpose", ["signup", "recovery"])
def test_provider_denial_fences_unfinished_callback_and_revokes_rejected_identity(purpose):
    async def scenario():
        fake, registry = FakeAuth(), Registry()
        app = create_app(SETTINGS, email_admission=PermissiveEmailAdmission(), auth_adapter=fake, registry=registry)
        entered, release = Event(), Event()
        revoked = []
        fake.revoke = lambda identity, *, budget: revoked.append(identity.access_token)
        original = fake.exchange
        def blocked(code, pending):
            entered.set()
            assert release.wait(3)
            return replace(original(code, pending), access_token="PRIVATE_LATE_IDENTITY")
        fake.exchange = blocked
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=ORIGIN) as client:
            boot = await client.get("/api/v1/auth/status")
            protection = {"Origin": ORIGIN, "X-CSRF-Token": boot.json()["csrfToken"]}
            await client.post("/api/v1/auth/login", json=PAYLOAD, headers=protection)
            await client.post("/api/v1/auth/" + ("signup" if purpose == "signup" else "recovery/request"),
                              json=PAYLOAD if purpose == "signup" else {"email": EMAIL}, headers=protection)
            callback = asyncio.create_task(client.get(fake.redirects[-1] + "&code=PRIVATE_CODE"))
            assert await asyncio.to_thread(entered.wait, 2)
            def denied(identity):
                raise AuthFailure()
            fake.validate = denied
            assert (await client.get("/api/v1/auth/status")).status_code == 503
            release.set()
            late = await callback
            assert late.headers["location"].endswith("=invalid")
            assert "set-cookie" not in late.headers
            assert not registry.sessions and not registry.recoveries
            assert revoked == ["PRIVATE_LATE_IDENTITY"]
    asyncio.run(scenario())


def test_delayed_logout_deletion_preserves_new_cookie_and_ignores_retired_cookie_order():
    client, fake, registry = setup()
    post(client, "login")
    protection = headers(client)
    old_names = dict(client.cookies)
    ended = client.post("/api/v1/auth/logout", json={}, headers=protection)
    assert client.post("/api/v1/auth/login", json=PAYLOAD, headers=protection).status_code == 200
    newest = session_cookie(client)
    newest_names = dict(client.cookies)
    client.cookies.extract_cookies(ended)
    assert session_cookie(client) == newest
    # Both HTTP header orders must select only live, browser-bound authority.
    for cookies in (old_names | newest_names, newest_names | old_names):
        request_cookies = "; ".join(f"{key}={value}" for key, value in cookies.items())
        assert client.get("/api/v1/auth/status", headers={"Cookie": request_cookies}).json()["authenticated"]
    assert newest in registry.sessions
    stranger = TestClient(client.app, base_url=ORIGIN)
    stranger.get("/api/v1/auth/status")
    binding = stranger.cookies["sb_browser"]
    forged = {**newest_names, "sb_browser": binding}
    assert not stranger.get("/api/v1/auth/status", headers={"Cookie": "; ".join(f"{k}={v}" for k, v in forged.items())}).json()["authenticated"]


def test_revocation_has_no_shared_worker_admission_queue():
    import anyio
    async def scenario():
        limiter = anyio.to_thread.current_default_thread_limiter()
        prior = limiter.total_tokens
        limiter.total_tokens = 1
        await limiter.acquire()
        try:
            manager, fake = Revocations(seconds=0.2), FakeAuth()
            await asyncio.wait_for(manager.after_response(fake, (fake.identity(),)), 1)
            assert fake.calls == ["revoke"] and manager.active == 0
        finally:
            limiter.release()
            limiter.total_tokens = prior
    asyncio.run(scenario())


@pytest.mark.parametrize('phase', ['before_resolution', 'after_resolution'])
def test_validation_owner_cancellation_preserves_only_completed_success(monkeypatch, phase):
    """Deterministic portal-close window after worker/Future completion."""
    from app.services import sessions
    from app.services.workspaces import Workspaces
    async def scenario():
        registry, fake = Registry(), FakeAuth()
        browser = registry.browser(None)[0]
        session_id = registry.rotate(None, browser, fake.identity())
        session = registry.live_session(session_id)
        authority = Workspaces(registry)
        authority.command(session_id, session, 'validation-race-workspace', 0, 1, 'invalidate', {'command': 1})
        entered, release = asyncio.Event(), asyncio.Event()
        async def barrier_worker(function, *args):
            if phase == 'after_resolution':
                function(*args)
            entered.set()
            await release.wait()
            if phase == 'before_resolution':
                function(*args)
        monkeypatch.setattr(sessions, 'run_in_threadpool', barrier_worker)
        waiter = asyncio.create_task(registry.authenticated_async(session_id, browser, fake, touch=False))
        await entered.wait()
        owner = next(iter(registry._validation_tasks))
        if phase == 'after_resolution':
            assert (await waiter).owner_id == OWNER
            assert session.validation is None
        owner.cancel()
        await owner
        if phase == 'before_resolution':
            with pytest.raises(AuthFailure): await waiter
            assert session_id not in registry.sessions and session_id not in authority.records
            assert fake.calls.count('validate') == 0
        else:
            assert registry.live_session(session_id) is session
            assert session_id in authority.records
            assert fake.calls.count('validate') == 1
            release.set()
            assert (await registry.authenticated_async(session_id, browser, fake, touch=False)).owner_id == OWNER
    asyncio.run(scenario())
