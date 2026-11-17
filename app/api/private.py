"""Protected private protocol helpers; authenticate before reading bounded bodies."""
import asyncio
import json
from fastapi.responses import JSONResponse
from starlette.requests import ClientDisconnect
from uuid import uuid4
from app.adapters.auth import AuthFailure
from app.adapters.model import ModelFailure
from app.api.auth import BROWSER_COOKIE, context, current_session, protected
from app.api.sources import unique_object

MESSAGES = {
    'library_unavailable': 'Dokumentene kunne ikke hentes. Materialet er beholdt. Prøv igjen.',
    'document_unknown': 'Dokumentet er ikke tilgjengelig for kontoen. Materialet er beholdt.',
    'file_unavailable': 'Originalfilen kunne ikke hentes eller kontrolleres. Prøv igjen.',
    'save_unavailable': 'Lagring er ikke konfigurert. Materialet er beholdt.',
    'save_pending': 'Lagringen er ikke bekreftet. Behold materialet og prøv samme lagring igjen.',
    'save_capacity': 'En lagring pågår. Vent litt og prøv igjen.',
    'save_mismatch': 'Lagringen samsvarer ikke med det opprinnelige materialet. Materialet er beholdt.',
    'save_conflict': 'Dokumentet er endret. Hent lagret versjon eller lagre som nytt.',
    'save_expired': 'Lagringen er utløpt. Bare opprydding er tilgjengelig.',
    'save_unknown': 'Denne lagringen finnes ikke for kontoen.',
    'file_required': 'Velg den samme originalfilen for å fortsette lagringen.',
    'session_ended': 'Tilgangen er avsluttet. Logg inn på nytt.',
    'request_rejected': 'Forespørselen ble avvist. Last siden på nytt og prøv igjen.',
    'generation_failed': 'Læringsmaterialet kunne ikke lages. Behold materialet og prøv igjen.',
    'model_unavailable': 'Generering er ikke konfigurert. Materialet er beholdt.',
    'budget_unavailable': 'Budsjettet er utilgjengelig eller brukt opp. Materialet er beholdt.',
    'generation_timeout': 'Genereringen tok for lang tid. Prøv igjen eksplisitt.',
    'generation_capacity': 'For mye materiale behandles nå. Vent litt og prøv igjen.',
    'workspace_capacity': 'For mange arbeidsområder er åpne. Logg ut og inn for en ny økt.',
    'invalid_proof': 'Kildekontrollen er utløpt eller endret. Kontroller materialet på nytt.',
    'stale_workspace': 'Materialet er endret. Kontroller det på nytt.',
    'command_replayed': 'Denne handlingen er allerede registrert. Prøv igjen med en ny handling.',
    'invalid_input': 'Forespørselen er ugyldig. Kontroller materialet på nytt.',
    'body_timeout': 'Opplastingen tok for lang tid. Prøv igjen.',
    'wire_limit': 'Forespørselen er for stor. Ingen del er godtatt.',
    'provider_input_limit': 'Materialet passer ikke innenfor genereringsgrensen. Ingen forespørsel er sendt.',
}


def error(code, *, save_disabled=False):
    if code not in MESSAGES:
        code = 'generation_failed'
    status = {'session_ended': 401, 'request_rejected': 403, 'generation_capacity': 429,
              'workspace_capacity': 429, 'generation_timeout': 504, 'model_unavailable': 503,
              'budget_unavailable': 503, 'generation_failed': 503, 'body_timeout': 408,
              'wire_limit': 413, 'stale_workspace': 409, 'command_replayed': 409,
              'save_unavailable': 503, 'save_pending': 503, 'save_capacity': 429,
              'save_conflict': 409, 'save_mismatch': 409, 'save_expired': 410, 'save_unknown': 404,
              'library_unavailable': 503, 'document_unknown': 404, 'file_unavailable': 503}.get(code, 422)
    payload = {'code': code, 'message': MESSAGES[code], 'requestId': str(uuid4())}
    if save_disabled and code == 'save_unavailable':
        payload['saveDisabled'] = True
    return JSONResponse(payload, status_code=status)


async def authenticate(request):
    settings, registry, adapter = context(request)
    if not protected(request, settings, registry):
        raise ModelFailure('request_rejected')
    if not settings.available:
        raise AuthFailure()
    session_id = current_session(request)
    identity = await registry.authenticated_async(session_id, request.cookies.get(BROWSER_COOKIE), adapter, touch=False)
    session = registry.live_session(session_id)
    views = request.headers.getlist('x-session-view')
    if identity is None or len(views) != 1 or not registry.session_view_matches(session, views[0]):
        raise AuthFailure()
    return session_id, session


def decode(raw, contract, member_limit=50_100, structure_limit=10_100):
    quoted = escaped = False
    depth = members = structures = 0
    for char in raw:
        if quoted:
            if escaped: escaped = False
            elif char == 92: escaped = True
            elif char == 34: quoted = False
        elif char == 34: quoted = True
        elif char in (91, 123):
            depth += 1; structures += 1
            if depth > 8 or structures > structure_limit:
                raise ModelFailure('invalid_input')
        elif char in (93, 125): depth -= 1
        elif char == 58:
            members += 1
            if members > member_limit:
                raise ModelFailure('invalid_input')
    try:
        return contract.model_validate(json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object),
                                       by_alias=True, by_name=False)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise ModelFailure('invalid_input') from None


async def collect(request, contract, *, limit=2 * 1024 * 1024, member_limit=50_100, structure_limit=10_100):
    if request.headers.get('content-type', '').split(';')[0].strip() != 'application/json':
        raise ModelFailure('invalid_input')
    lengths = request.headers.getlist('content-length')
    if lengths and (len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit()):
        raise ModelFailure('invalid_input')
    if lengths and int(lengths[0]) > limit:
        raise ModelFailure('wire_limit')
    raw = bytearray()
    try:
        async with asyncio.timeout(5):
            async for chunk in request.stream():
                if len(chunk) > limit - len(raw):
                    raise ModelFailure('wire_limit')
                raw.extend(chunk)
    except TimeoutError:
        raise ModelFailure('body_timeout') from None
    except ClientDisconnect:
        raise ModelFailure('invalid_input') from None
    return decode(raw, contract, member_limit, structure_limit)
