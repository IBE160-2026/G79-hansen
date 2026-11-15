"""Versioned canonical projections and process-only HMAC authority."""
import base64
import hashlib
import hmac
import json
import secrets


def canonical(value):
    if hasattr(value, 'model_dump'):
        value = value.model_dump(mode='json', by_alias=True)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def acceptance_projection(value):
    result = value.model_dump(mode='json', by_alias=True)
    for key in ('sourceProof', 'commandSequence'):
        result.pop(key, None)
    return result


class Proofs:
    def __init__(self):
        self._secret = secrets.token_bytes(32)

    def sign(self, purpose, claims):
        payload = canonical({'purpose': purpose, 'schemaVersion': '1.0', **claims})
        encoded = base64.urlsafe_b64encode(payload).rstrip(b'=')
        signature = hmac.digest(self._secret, encoded, 'sha256')
        return (encoded + b'.' + base64.urlsafe_b64encode(signature).rstrip(b'=')).decode('ascii')

    def verify(self, purpose, token):
        from app.services.workspaces import WorkspaceFailure
        try:
            if not isinstance(token, str) or not token.isascii() or len(token) > 8192:
                raise ValueError()
            encoded, supplied = token.encode('ascii').split(b'.')
            expected = base64.urlsafe_b64encode(hmac.digest(self._secret, encoded, 'sha256')).rstrip(b'=')
            if not hmac.compare_digest(supplied, expected):
                raise ValueError()
            value = json.loads(base64.urlsafe_b64decode(encoded + b'=' * (-len(encoded) % 4)))
            if value.get('purpose') != purpose or value.get('schemaVersion') != '1.0':
                raise ValueError()
            return value
        except (ValueError, TypeError, UnicodeError, KeyError):
            raise WorkspaceFailure('invalid_proof') from None
