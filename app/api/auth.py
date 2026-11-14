"""Same-origin, cookie/CSRF protected authentication endpoints."""

import asyncio
import re
from uuid import uuid4
from urllib.parse import urlencode

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from starlette.concurrency import run_in_threadpool

from app.adapters.auth import AuthFailure

router = APIRouter(prefix="/api/v1/auth")
BROWSER_COOKIE = "sb_browser"
SESSION_COOKIE = "sb_session"
CREDENTIAL_BODY_SECONDS = 5.0
MESSAGES = {
    "auth_unavailable": "Innlogging er ikke tilgjengelig nå. Prøv igjen senere.",
    "invalid_credentials": "Kunne ikke logge inn. Kontroller e-post, passord og bekreftelsen på e-post.",
    "invalid_request": "Kontroller e-post og passord og prøv igjen.",
    "request_rejected": "Forespørselen ble avvist. Last siden på nytt og prøv igjen.",
    "auth_capacity": "For mange pågående forsøk. Vent litt og prøv igjen.",
    "invalid_recovery": "Gjenopprettingslenken er ugyldig eller utløpt. Be om en ny lenke og åpne den i samme nettleser.",
    "recovery_failed": "Passordendringen kunne ikke bekreftes. Passordet kan være endret. Prøv å logge inn, eller be om en ny lenke.",
}


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=1024, repr=False)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value):
        value = value.strip()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("invalid_email")
        return value


class RecoveryEmail(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    email: str = Field(min_length=3, max_length=254)
    valid_email = field_validator("email")(Credentials.valid_email.__func__)


class RecoveryPassword(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    password: str = Field(min_length=8, max_length=1024, repr=False)


def error(code, status=None):
    if status is None:
        status = {"invalid_credentials": 401, "request_rejected": 403,
                  "invalid_request": 422, "auth_capacity": 429, "invalid_recovery": 401}.get(code, 503)
    return JSONResponse({"code": code, "message": MESSAGES.get(code, MESSAGES["auth_unavailable"]),
                         "requestId": str(uuid4())}, status_code=status)


def context(request):
    return request.app.state.settings, request.app.state.auth_registry, request.app.state.auth_adapter


def correct_host(request, settings):
    return str(request.base_url).rstrip("/") == settings.app_origin


def protected(request, settings, registry):
    origins = request.headers.getlist("origin")
    tokens = request.headers.getlist("x-csrf-token")
    return (correct_host(request, settings) and origins == [settings.app_origin] and
            len(tokens) == 1 and registry.csrf_valid(request.cookies.get(BROWSER_COOKIE), tokens[0]))


def cookie(response, name, value, settings):
    response.set_cookie(name, value, httponly=True, secure=settings.secure_cookies,
                        samesite="lax", path="/")


def clear_session(response, settings):
    response.delete_cookie(SESSION_COOKIE, path="/", secure=settings.secure_cookies,
                           httponly=True, samesite="lax")


async def credentials(request, schema=Credentials):
    # Bound actual streamed bytes, including chunked requests, before parsing or SDK work.
    raw = bytearray()
    try:
        async with asyncio.timeout(CREDENTIAL_BODY_SECONDS):
            async for chunk in request.stream():
                if len(chunk) > 8192 - len(raw):
                    raise AuthFailure("invalid_request")
                raw.extend(chunk)
    except TimeoutError:
        raise AuthFailure("invalid_request") from None
    if request.headers.get("content-type", "").split(";")[0].strip() != "application/json":
        raise AuthFailure("invalid_request")
    try:
        return schema.model_validate_json(raw)
    except ValidationError:
        raise AuthFailure("invalid_request") from None


@router.get("/status")
async def status(request: Request):
    settings, registry, adapter = context(request)
    if not settings.available:
        return JSONResponse({"available": False, "authenticated": False, "recoveryAvailable": False})
    if not correct_host(request, settings):
        return error("request_rejected")
    try:
        browser_id, browser = registry.browser(request.cookies.get(BROWSER_COOKIE))
        identity = await registry.authenticated_async(request.cookies.get(SESSION_COOKIE), browser_id, adapter)
        display = {"available": True, "authenticated": identity is not None, "csrfToken": browser.csrf,
                   "recoveryAvailable": registry.recovery_available(request.cookies.get(SESSION_COOKIE), browser_id)}
        if identity:
            display["email"] = identity.email
        response = JSONResponse(display)
        cookie(response, BROWSER_COOKIE, browser_id, settings)
        # Status never mutates sb_session. Even a completed denial response can
        # arrive after a newer login response and otherwise erase its cookie.
        return response
    except AuthFailure as exc:
        return error(exc.code)


async def submit(request, action):
    settings, registry, adapter = context(request)
    if not protected(request, settings, registry):
        return error("request_rejected")
    if not settings.available:
        return error("auth_unavailable")
    state = None
    try:
        submitted = await credentials(request)
        browser_id = request.cookies[BROWSER_COOKIE]
        if action == "signup":
            state, pending = registry.start_attempt(browser_id, submitted.email)
            redirect = settings.app_origin + "/api/v1/auth/callback?" + urlencode({"state": state})
            await run_in_threadpool(adapter.signup, submitted.email, submitted.password, pending, redirect)
            return JSONResponse({"status": "check_email", "message": "Hvis kontoen kan opprettes, får du en e-post. Åpne bekreftelsen i nettleseren der du startet registreringen."})
        registry.retain_browser(browser_id)
        identity = await run_in_threadpool(adapter.login, submitted.email, submitted.password)
        session_id = registry.rotate(request.cookies.get(SESSION_COOKIE), browser_id, identity)
        response = JSONResponse({"authenticated": True, "email": identity.email})
        cookie(response, SESSION_COOKIE, session_id, settings)
        return response
    except AuthFailure as exc:
        if state:
            registry.discard_attempt(state)
        return error(exc.code)


@router.post("/signup")
async def signup(request: Request):
    return await submit(request, "signup")


@router.post("/login")
async def login(request: Request):
    return await submit(request, "login")


@router.get("/callback")
async def callback(request: Request):
    return await complete_callback(request, "signup")


@router.get("/recovery/callback")
async def recovery_callback(request: Request):
    return await complete_callback(request, "recovery")


async def complete_callback(request, purpose):
    settings, registry, adapter = context(request)
    outcome = "recovery" if purpose == "recovery" else "confirmation"
    response = RedirectResponse(f"/account?{outcome}=invalid", status_code=303)
    if not settings.available or not correct_host(request, settings):
        return response
    params = request.query_params
    if (set(params) != {"state", "code"} or len(params.getlist("state")) != 1 or
            len(params.getlist("code")) != 1 or not 1 <= len(params["code"]) <= 2048 or
            not 40 <= len(params["state"]) <= 128):
        return response
    try:
        browser_id = request.cookies.get(BROWSER_COOKIE)
        pending = registry.consume(params["state"], browser_id, purpose)
        identity = await run_in_threadpool(adapter.exchange, params["code"], pending)
        if registry.clock() >= pending.expires:
            return response
        session_id = registry.rotate(request.cookies.get(SESSION_COOKIE), browser_id, identity,
                                     recovery=purpose == "recovery",
                                     expected_revision=pending.authority_revision if purpose == "recovery" else None)
        response = RedirectResponse(f"/account?{outcome}=success", status_code=303)
        cookie(response, SESSION_COOKIE, session_id, settings)
        return response
    except AuthFailure:
        return response


@router.post("/recovery/request")
async def recovery_request(request: Request):
    settings, registry, adapter = context(request)
    if not protected(request, settings, registry):
        return error("request_rejected")
    if not settings.available:
        return error("auth_unavailable")
    state = None
    try:
        submitted = await credentials(request, RecoveryEmail)
        browser_id = request.cookies[BROWSER_COOKIE]
        state, pending = registry.start_attempt(browser_id, submitted.email, "recovery")
        redirect = settings.app_origin + "/api/v1/auth/recovery/callback?" + urlencode({"state": state})
        await run_in_threadpool(adapter.request_recovery, submitted.email, pending, redirect)
        return JSONResponse({"status": "check_email", "message": "Hvis kontoen finnes, får du en e-post. Åpne lenken i samme nettleser innen 10 minutter."})
    except AuthFailure as exc:
        if state:
            registry.discard_attempt(state)
        return error(exc.code if exc.code in ("invalid_request", "auth_capacity") else "auth_unavailable")


@router.post("/recovery/password")
async def recovery_password(request: Request):
    settings, registry, adapter = context(request)
    if not protected(request, settings, registry):
        return error("request_rejected")
    if not settings.available:
        return error("auth_unavailable")
    admitted = False
    try:
        submitted = await credentials(request, RecoveryPassword)
        grant = registry.claim_recovery(request.cookies.get(SESSION_COOKIE), request.cookies[BROWSER_COOKIE])
        admitted = True
        await run_in_threadpool(adapter.update_password, grant.identity, submitted.password, expires_at=grant.expires)
        # The spent cookie is harmless. Clearing it could erase a newer login cookie.
        return JSONResponse({"status": "password_updated", "authenticated": False, "recoveryAvailable": False})
    except AuthFailure as exc:
        return error("recovery_failed" if admitted else exc.code)
