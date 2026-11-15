"""Synthetic extraction, transport, authority and owned-resource regressions."""

import asyncio
import base64
import json
from itertools import count
import sys
from threading import Event
import time

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api import sources
from app.contracts.sources import ExtractRequest
from app.services.extraction import MAX_BYTES
from app.services.sessions import Registry
from pdf_fixtures import at_size, make_pdf
from scripts.pdf_probe import PageUnit, ProbeResult
from test_auth import FakeAuth, ORIGIN, PAYLOAD, SETTINGS, headers, post, session_cookie, setup


def login(client):
    assert post(client, "login").status_code == 200
    state = client.get("/api/v1/auth/status").json()
    return {"Origin": ORIGIN, "X-CSRF-Token": state["csrfToken"], "X-Session-View": state["sessionViewId"]}


commands = count(1)


def body(text="First\r\n\r\nSecond 😀", **changes):
    return {"schemaVersion": "1.0", "kind": "paste", "settings": {"language": "nb", "detail": "short", "subject": ""},
            "clientRevision": 7, "workspaceId": "source-tests-workspace", "commandSequence": next(commands), "text": text, **changes}


def upload(content, kind="text-file", **changes):
    value = body(kind=kind, **changes)
    value.pop("text")
    value["contentBase64"] = base64.b64encode(content).decode("ascii")
    return value


def send(client, protection, payload=None, **kwargs):
    payload = {**payload, "commandSequence": next(commands)} if payload is not None else body()
    return client.post("/api/v1/sources/extract", headers=protection, json=payload, **kwargs)


def test_canonical_paragraphs_settings_fresh_identity_and_no_retention():
    client, _, registry = setup()
    protection = login(client)
    supplied = body("  First\r\nline \r\n \t\r\nSecond 😀  ", settings={"language": "en", "detail": "detailed", "subject": "IBE160"})
    first = send(client, protection, supplied)
    assert first.status_code == 200
    value = first.json()
    assert value["characterCount"] == len(supplied["text"].replace("\r\n", "\n"))
    assert value["clientRevision"] == 7 and value["settings"] == supplied["settings"]
    assert value["source"]["units"] == [
        {"id": "paragraph-1", "kind": "paragraph", "location": 1, "text": "  First\nline "},
        {"id": "paragraph-2", "kind": "paragraph", "location": 2, "text": "Second 😀  "},
    ]
    assert value["totalPages"] is None and value["unreadablePages"] == [] and value["warnings"] == []
    second = send(client, protection, supplied).json()
    assert second["source"]["id"] != value["source"]["id"]
    assert second["source"]["units"] == value["source"]["units"]
    assert first.headers["cache-control"] == "no-store"
    assert first.headers["referrer-policy"] == "no-referrer"
    assert all("First" not in repr(table) and "IBE160" not in repr(table)
               for table in (registry.sessions, registry.browsers, registry.pending, registry.recoveries))


@pytest.mark.parametrize("text,code", [("😀" * 30000, None), ("x" * 29998 + "\r\n\r", None),
    ("x" * 30000 + "\r", "character_limit"), ("😀" * 30001, "character_limit"),
    (" \r\n\t", "no_readable_text"), ("a\x00b", "invalid_text"), ("a\x7fb", "invalid_text"),
    ("a\x85b", "invalid_text"), ("a\ud800b", "invalid_text")])
def test_character_and_scalar_boundaries(text, code):
    client, _, _ = setup()
    protection = login(client)
    # ASCII JSON escaping also tests isolated-surrogate input safely.
    result = client.post("/api/v1/sources/extract", content=json.dumps(body(text)),
                         headers={**protection, "Content-Type": "application/json"})
    if code:
        assert result.status_code == 422 and result.json()["code"] == code
        assert "source" not in result.json()
    else:
        assert result.status_code == 200 and result.json()["characterCount"] == 30000


@pytest.mark.parametrize("content,code", [(b"\xef\xbb\xbfOne\r\n\rTwo", None), (b"\xff", "invalid_text"),
    (b"\xed\xa0\x80", "invalid_text"), (b"abc\x00", "invalid_text"), (b"  \n", "no_readable_text")])
def test_utf8_text_file_with_optional_bom(content, code):
    client, _, _ = setup()
    result = send(client, login(client), upload(content))
    if code:
        assert result.json()["code"] == code and result.status_code == 422
    else:
        assert result.status_code == 200
        assert [unit["text"] for unit in result.json()["source"]["units"]] == ["One", "Two"]
        assert result.json()["characterCount"] == 8


@pytest.mark.parametrize("change", [{"filename": "secret.txt"}, {"ownerId": "other"}, {"source": {}},
    {"text": None}, {"contentBase64": "YQ=="}, {"clientRevision": True}, {"clientRevision": -1},
    {"clientRevision": 1.0}, {"schemaVersion": "2"}, {"kind": "html"}, {"settings": {"language": "nb", "ownerId": "other"}}])
def test_strict_owner_free_envelope(change):
    client, _, _ = setup()
    response = send(client, login(client), body(**change))
    assert response.status_code == 422 and response.json()["code"] == "invalid_input"
    assert set(response.json()) == {"code", "message", "requestId"}


@pytest.mark.parametrize("encoded", ["Y Q==", "YQ", "YQ===", "YR==", "!!!!", "😀"])
def test_strict_base64(encoded):
    client, _, _ = setup()
    value = upload(b"a"); value["contentBase64"] = encoded
    assert send(client, login(client), value).json()["code"] == "invalid_input"


def test_duplicate_fields_invalid_json_encoding_and_media_type_are_safe():
    client, _, _ = setup()
    protection = login(client)
    for content in [b'{"kind":"paste","kind":"pdf"}', json.dumps(body()).encode("utf-16"), b"\xff", b"["]:
        response = client.post("/api/v1/sources/extract", content=content,
                               headers={**protection, "Content-Type": "application/json"})
        assert response.status_code == 422 and response.json()["code"] == "invalid_input"
    response = client.post("/api/v1/sources/extract", content="PRIVATE_SOURCE", headers=protection)
    assert response.status_code == 422 and "PRIVATE_SOURCE" not in response.text


def test_authority_origin_csrf_and_view_deny_before_body(monkeypatch):
    client, fake, registry = setup()
    protection = login(client)
    async def forbidden(_):
        raise AssertionError("private body was read")
    monkeypatch.setattr(sources, "collect", forbidden)
    for supplied in [{}, {**protection, "Origin": "https://attacker.test"},
                     {**protection, "X-CSRF-Token": "wrong"}]:
        assert send(client, supplied).status_code == 403
    for supplied in [{key: value for key, value in protection.items() if key != "X-Session-View"},
                     {**protection, "X-Session-View": "wrong"}, {**protection, "X-Session-View": b"\xf8"}]:
        assert send(client, supplied).status_code == 401
    other = TestClient(client.app, base_url=ORIGIN)
    other_protection = login(other)
    assert send(other, {**other_protection, "X-Session-View": protection["X-Session-View"]}).status_code == 401
    fake.fail = True
    assert send(client, protection).status_code == 401
    assert not registry.sessions.get(session_cookie(client))


def test_recovery_only_authority_and_view_alone_do_not_authorize(monkeypatch):
    client, fake, registry = setup()
    protection = login(client)
    session_id = session_cookie(client)
    browser_id = client.cookies.get("sb_browser")
    registry.rotate(session_id, browser_id, fake.identity(), recovery=True)
    assert send(client, protection).status_code == 401
    # Even a copied session view is never a credential.
    client.cookies.clear()
    assert send(client, protection).status_code == 403


def test_status_view_is_non_touching_and_changes_on_same_account_login():
    now = [1000.0]
    registry = Registry(clock=lambda: now[0])
    client, _, _ = setup(registry=registry)
    initial = login(client)
    session = registry.sessions[session_cookie(client)]
    now[0] += 15
    assert client.get("/api/v1/auth/status").json()["sessionViewId"] == initial["X-Session-View"]
    assert session.touched == 1000
    assert send(client, initial, body(" ")).status_code == 422
    assert session.touched == 1000
    assert send(client, initial).status_code == 200
    assert session.touched == 1015
    fresh = login(client)
    assert fresh["X-Session-View"] != initial["X-Session-View"]
    assert send(client, initial).status_code == 401


def test_decoded_and_wire_byte_ceilings_are_independent(monkeypatch):
    client, _, _ = setup()
    protection = login(client)
    observed = []
    def parser(content):
        observed.append(len(content))
        return ProbeResult("accepted", "ok", (PageUnit("pdf-page-1", "page", 1, "A"),), 1, (), 1)
    monkeypatch.setattr(sources, "extract_pdf", parser)
    assert send(client, protection, upload(b"a" * MAX_BYTES, kind="pdf")).status_code == 200
    assert send(client, protection, upload(b"a" * (MAX_BYTES + 1), kind="pdf")).json()["code"] == "byte_limit"
    assert observed == [MAX_BYTES]
    for content, length in [(b"{}", str(sources.MAX_WIRE_BYTES + 1)),
                            (b" " * (sources.MAX_WIRE_BYTES + 1), None)]:
        extra = {"Content-Type": "application/json"}
        if length: extra["Content-Length"] = length
        response = client.post("/api/v1/sources/extract", content=iter([content]), headers={**protection, **extra})
        assert response.status_code == 413 and response.json()["code"] == "wire_limit"
    assert send(client, protection).status_code == 200


@pytest.mark.parametrize("transition", ["logout", "rotate", "expire"])
def test_session_end_during_body_prevents_parser_and_success(transition, monkeypatch):
    now = [1000.0]
    registry = Registry(clock=lambda: now[0])
    client, fake, _ = setup(registry=registry)
    protection = login(client)
    old_id = session_cookie(client)
    called = []
    monkeypatch.setattr(sources, "extract_pdf", lambda content: called.append(True))
    async def run():
        async def content():
            yield b" "
            if transition == "logout": registry.terminate(client.cookies.get("sb_browser"))
            elif transition == "rotate": registry.rotate(old_id, client.cookies.get("sb_browser"), fake.identity())
            else: now[0] += registry.idle_seconds
            yield json.dumps(upload(b"%PDF-", kind="pdf")).encode()
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=client.app), base_url=ORIGIN, cookies=client.cookies) as http:
            response = await http.post("/api/v1/sources/extract", headers={**protection, "Content-Type": "application/json"}, content=content())
        assert response.status_code == 401 and "source" not in response.json()
    asyncio.run(run())
    assert called == []
    assert not client.app.state.source_admission.sessions


@pytest.mark.parametrize("transition", ["logout", "rotate", "expire"])
def test_session_end_during_worker_defeats_final_success(transition, monkeypatch):
    now = [1000.0]
    registry = Registry(clock=lambda: now[0])
    client, fake, _ = setup(registry=registry)
    protection = login(client)
    def parser(content):
        if transition == "logout": registry.terminate(client.cookies.get("sb_browser"))
        elif transition == "rotate": registry.rotate(session_cookie(client), client.cookies.get("sb_browser"), fake.identity())
        else: now[0] += registry.idle_seconds
        return ProbeResult("accepted", "ok", (PageUnit("pdf-page-1", "page", 1, "PRIVATE_TEXT"),), 1, (), 12)
    monkeypatch.setattr(sources, "extract_pdf", parser)
    response = send(client, protection, upload(b"%PDF-", kind="pdf"))
    assert response.status_code == 401 and "PRIVATE_TEXT" not in response.text
    assert not client.app.state.source_admission.sessions and not client.app.state.source_admission.pdf_active


def test_short_chunk_reads_body_deadline_disconnect_and_recovery(monkeypatch):
    client, _, _ = setup()
    protection = login(client)
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=client.app), base_url=ORIGIN, cookies=client.cookies) as http:
            async def short():
                for char in json.dumps(body()).encode(): yield bytes([char])
            response = await http.post("/api/v1/sources/extract", headers={**protection, "Content-Type": "application/json"}, content=short())
            assert response.status_code == 200
            monkeypatch.setattr(sources, "BODY_SECONDS", .04)
            async def slow():
                yield b"{"
                await asyncio.sleep(.2)
                yield b"}"
            response = await http.post("/api/v1/sources/extract", headers={**protection, "Content-Type": "application/json"}, content=slow())
            assert response.status_code == 408 and response.json()["code"] == "body_timeout"
            monkeypatch.setattr(sources, "BODY_SECONDS", 5)
            from starlette.requests import ClientDisconnect
            async def disconnected():
                yield b"{"
                raise ClientDisconnect()
            response = await http.post("/api/v1/sources/extract", headers={**protection, "Content-Type": "application/json"}, content=disconnected())
            assert response.status_code == 422
            assert (await http.post("/api/v1/sources/extract", headers=protection, json=body())).status_code == 200
    asyncio.run(run())
    assert not client.app.state.source_admission.sessions


def test_admission_global_per_session_pdf_limiter_and_cancellation_hold_cleanup(monkeypatch):
    client, _, _ = setup()
    protection = login(client)
    second = TestClient(client.app, base_url=ORIGIN); second_headers = login(second)
    third = TestClient(client.app, base_url=ORIGIN); third_headers = login(third)
    entered, release = Event(), Event()
    def parser(content):
        entered.set()
        assert release.wait(3)
        return ProbeResult("accepted", "ok", (PageUnit("pdf-page-1", "page", 1, "Text"),), 1, (), 4)
    monkeypatch.setattr(sources, "extract_pdf", parser)
    async def run():
        transport = httpx.ASGITransport(app=client.app)
        async with httpx.AsyncClient(transport=transport, base_url=ORIGIN, cookies=client.cookies) as http, \
                httpx.AsyncClient(transport=transport, base_url=ORIGIN, cookies=second.cookies) as other, \
                httpx.AsyncClient(transport=transport, base_url=ORIGIN, cookies=third.cookies) as extra:
            task = asyncio.create_task(http.post("/api/v1/sources/extract", headers=protection, json=upload(b"%PDF-", kind="pdf")))
            for _ in range(100):
                if entered.is_set(): break
                await asyncio.sleep(.01)
            assert entered.is_set()
            assert (await http.post("/api/v1/sources/extract", headers=protection, json=body())).status_code == 429
            assert (await other.post("/api/v1/sources/extract", headers=second_headers, json=upload(b"%PDF-", kind="pdf"))).status_code == 429
            assert (await other.post("/api/v1/sources/extract", headers=second_headers, json=body())).status_code == 200
            task.cancel()
            with pytest.raises(asyncio.CancelledError): await task
            assert client.app.state.source_admission.pdf_active
            assert session_cookie(client) in client.app.state.source_admission.sessions
            gate = asyncio.Event(); reading = asyncio.Event()
            async def waiting():
                reading.set(); yield b" "
                await gate.wait(); yield json.dumps(body()).encode()
            second_task = asyncio.create_task(other.post("/api/v1/sources/extract", headers={**second_headers, "Content-Type": "application/json"}, content=waiting()))
            await reading.wait()
            assert (await extra.post("/api/v1/sources/extract", headers=third_headers, json=body())).status_code == 429
            gate.set(); assert (await second_task).status_code == 200
            release.set()
            for _ in range(100):
                if not client.app.state.source_admission.sessions: break
                await asyncio.sleep(.01)
            assert not client.app.state.source_admission.sessions
            assert not client.app.state.source_admission.pdf_active
            assert (await http.post("/api/v1/sources/extract", headers=protection, json=body())).status_code == 200
    try: asyncio.run(run())
    finally: release.set()


@pytest.mark.parametrize("failure", ["timeout", "memory_limit", "worker_failed", "isolation_unavailable"])
def test_worker_failure_is_fixed_private_and_releases_admission(monkeypatch, caplog, failure):
    client, _, _ = setup()
    protection = login(client)
    monkeypatch.setattr(sources, "extract_pdf", lambda _: ProbeResult("rejected", failure))
    response = send(client, protection, upload(b"PRIVATE_PDF", kind="pdf"))
    assert response.status_code in (422, 503)
    assert "PRIVATE_PDF" not in response.text and "PRIVATE_PDF" not in caplog.text
    assert not client.app.state.source_admission.sessions and not client.app.state.source_admission.pdf_active
    assert send(client, protection).status_code == 200


@pytest.mark.skipif(sys.platform != "win32", reason="Actual PDF containment requires Windows Job Objects")
@pytest.mark.parametrize("content,code,expected", [
    (make_pdf(["First", None, "Third", None], image_pages=(4,)), None, [(1, "First"), (3, "Third")]),
    (make_pdf([None, None], image_pages=(2,)), "no_readable_text", None),
    (make_pdf(["Text"], encrypted=True), "encrypted_pdf", None),
    (b"%PDF-1.7\ninvalid", "invalid_pdf", None),
    (make_pdf(["Text"] + [None] * 39), None, [(1, "Text")]),
    (make_pdf(["Text"] + [None] * 40), "page_limit", None),
    (make_pdf(["😀" * 15000, None, "é" * 15000]), None, [(1, "😀" * 15000), (3, "é" * 15000)]),
    (make_pdf(["😀" * 15000, None, "é" * 15001]), "character_limit", None),
    (at_size(make_pdf(["Byte boundary"]), MAX_BYTES), None, [(1, "Byte boundary")]),
])
def test_actual_contained_pdf_integration(content, code, expected, request):
    client, _, _ = setup()
    response = send(client, login(client), upload(content, kind="pdf"))
    if code:
        assert response.status_code == 422 and response.json()["code"] == code
        assert "source" not in response.json()
    else:
        assert response.status_code == 200
        value = response.json()
        assert [(unit["location"], unit["text"]) for unit in value["source"]["units"]] == expected
        assert value["warnings"] and "Bilder, tabeller og figurer" in value["warnings"][0]
        assert value["characterCount"] == sum(len(unit["text"]) for unit in value["source"]["units"])
        if value["totalPages"] == 4:
            assert [unit["location"] for unit in value["source"]["units"]] == [1, 3]
            assert value["unreadablePages"] == [2, 4]
        request.node.user_properties.append(("source_api_observation", json.dumps({
            "inputBytes": len(content), "totalPages": value["totalPages"],
            "characterCount": value["characterCount"], "unreadablePages": value["unreadablePages"]})))
    assert not client.app.state.source_admission.sessions and not client.app.state.source_admission.pdf_active


def test_private_workspace_headers_and_explicit_assets():
    client, _, _ = setup()
    assert client.get("/workspace").headers["cache-control"] == "no-store"
    assert client.get("/assets/workspace.js").status_code == 200
    assert client.get("/app/services/extraction.py").status_code == 404
    assert client.get("/assets/../.env").status_code == 404


@pytest.mark.parametrize("shape", [
    b'{"extra":[' + b'{},' * 19999 + b'{}]}',
    b'{"settings":{"nested":{}}}',
    b'{' + b','.join(b'"k%d":0' % n for n in range(17)) + b'}',
])
def test_structural_graphs_rejected_before_json_object_construction(monkeypatch, shape):
    client, _, _ = setup()
    protection = login(client)
    def forbidden(*args, **kwargs):
        raise AssertionError("arbitrary graph reached JSON construction")
    # Do not replace the shared json module used by HTTPX's response decoder.
    from types import SimpleNamespace
    monkeypatch.setattr(sources, "json", SimpleNamespace(loads=forbidden))
    response = client.post("/api/v1/sources/extract", content=shape,
                           headers={**protection, "Content-Type": "application/json"})
    assert response.status_code == 422 and response.json()["code"] == "invalid_input"
    assert not client.app.state.source_admission.sessions


def test_json_and_preparation_use_independent_workers_and_keep_quoted_structure(monkeypatch):
    import anyio
    from threading import get_ident
    from types import SimpleNamespace
    client, _, _ = setup()
    protection = login(client)
    event_loop = []
    constructed = []
    prepared = []
    original_collect, original_loads = sources.collect, sources.json.loads
    original_prepare = sources.prepare
    def loads(*args, **kwargs):
        constructed.append(get_ident())
        assert get_ident() != event_loop[0]
        return original_loads(*args, **kwargs)
    monkeypatch.setattr(sources, "json", SimpleNamespace(loads=loads))
    def prepare(submitted):
        prepared.append(get_ident())
        assert get_ident() != event_loop[0]
        return original_prepare(submitted)
    monkeypatch.setattr(sources, "prepare", prepare)
    async def saturated(request):
        event_loop.append(get_ident())
        limiter = anyio.to_thread.current_default_thread_limiter()
        prior = limiter.total_tokens
        limiter.total_tokens = 1
        await limiter.acquire()
        try:
            return await asyncio.wait_for(original_collect(request), 2)
        finally:
            limiter.release()
            limiter.total_tokens = prior
    monkeypatch.setattr(sources, "collect", saturated)
    text = 'Literal [] {} : and escaped "quote" \\ brackets'
    response = send(client, protection, body(text))
    assert response.status_code == 200
    assert response.json()["source"]["units"][0]["text"] == text
    assert constructed and prepared
