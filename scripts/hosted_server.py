"""Read-only hosted preflight, followed only on success by foreground serving."""

import base64
import json
import os
from pathlib import Path
import re
import socket
import stat
import sys

from app.config import Settings


_ENV_NAMES = frozenset('''AUTH_ENABLED APP_ORIGIN SUPABASE_URL SUPABASE_PUBLISHABLE_KEY
AUTH_ALLOW_LOOPBACK_HTTP AUTH_IDLE_SECONDS AUTH_ABSOLUTE_SECONDS MODEL_ENABLED
OPENAI_API_KEY MODEL_BUDGET_PATH SAVE_ENABLED SAVE_BACKEND_KEY_PATH SUPABASE_S3_REGION
SUPABASE_S3_KEY_ID SUPABASE_S3_ANON_KEY AUTH_EMAIL_ADMISSION_PATH'''.split())


class StartupFailure(Exception):
    pass


def load_environment(filename):
    """Bounded, literal dotenv subset; never interpolate or print input lines."""
    try:
        path = Path(filename)
        if not stat.S_ISREG(path.lstat().st_mode):
            raise ValueError()
        with path.open('rb') as source:
            content = source.read(65537)
        if len(content) > 65536 or b'\0' in content:
            raise ValueError()
        values = {}
        text = content.decode('utf-8-sig')
        if any((ord(character) < 32 and character not in '\r\n') or
               127 <= ord(character) <= 159 for character in text):
            raise ValueError()
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            match = re.fullmatch(r'(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)', line)
            if not match or match[1] not in _ENV_NAMES or match[1] in values:
                raise ValueError()
            value = match[2].strip()
            if value.startswith(('"', "'")):
                quoted = re.fullmatch(r'''(?:"([^"]*)"|'([^']*)')\s*(?:#.*)?''', value)
                if not quoted:
                    raise ValueError()
                value = quoted[1] if quoted[1] is not None else quoted[2]
            else:
                value = value.split('#', 1)[0].rstrip()
                if '"' in value or "'" in value:
                    raise ValueError()
            values[match[1]] = value
        # Parse the entire file before affecting effective configuration.
        for name, value in values.items():
            os.environ.setdefault(name, value)
    except (OSError, ValueError, UnicodeError):
        raise StartupFailure('environment-invalid') from None


def _placeholder(value):
    return any(word in value.lower() for word in
               ('your', 'placeholder', 'replace', 'changeme', 'example', 'dummy'))


def _public_key(value, *, legacy_only=False):
    if len(value) > 4096 or _placeholder(value):
        return False
    if not legacy_only and re.fullmatch(r'sb_publishable_[A-Za-z0-9_-]{16,}', value):
        return True
    if not re.fullmatch(r'[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', value):
        return False
    try:
        header, payload, signature = (base64.b64decode(part + '=' * (-len(part) % 4),
                                     altchars=b'-_', validate=True) for part in value.split('.'))
        claims = json.loads(payload)
        return (json.loads(header).get('alg') == 'HS256' and bool(signature) and
                isinstance(claims, dict) and claims.get('role') == 'anon')
    except (ValueError, TypeError, AttributeError, UnicodeError):
        return False


def _state_paths(settings):
    configured = (settings.model_budget_path, settings.save_backend_key_path,
                  settings.auth_email_admission_path)
    active = (settings.model_enabled, settings.save_enabled, bool(configured[2]))
    paths = []
    try:
        for value, required in zip(configured, active):
            path = Path(value).absolute() if value else None
            if required and (path is None or not stat.S_ISREG(path.lstat().st_mode)):
                raise StartupFailure('state-invalid')
            if path is not None:
                for other in paths:
                    if path.resolve() == other.resolve() or (
                            path.exists() and other.exists() and path.samefile(other)):
                        raise StartupFailure('state-invalid')
                paths.append(path)
    except (OSError, ValueError, RuntimeError):
        raise StartupFailure('state-invalid') from None


def probe_port():
    """Bind briefly without listening; never interact with an existing listener."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
                probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            probe.bind(('127.0.0.1', 8000))
    except OSError:
        raise StartupFailure('port-busy') from None


def preflight(settings):
    if (not settings.available or not settings.secure_cookies or settings.allow_loopback_http or
            any(character.isspace() or ord(character) < 32
                for character in settings.app_origin + settings.supabase_url) or
            not _public_key(settings.supabase_key)):
        raise StartupFailure('configuration-invalid')
    _state_paths(settings)
    if settings.model_enabled:
        from app.services.model_budget import ModelBudget
        try:
            if (not settings.model_available or _placeholder(settings.openai_api_key) or
                    not re.fullmatch(r'sk-[A-Za-z0-9_-]{20,512}', settings.openai_api_key)):
                raise ValueError()
            # Preserve valid blocked/exhausted state. The existing generation
            # gate denies dispatch; login and saved documents remain reachable.
            ModelBudget(settings.model_budget_path).read()
        except Exception:
            raise StartupFailure('model-state-invalid') from None
    if settings.save_enabled:
        try:
            settings.save_backend_key()
            project = settings.supabase_s3_key_id
            if (settings.supabase_s3_region != 'eu-west-3' or
                    not re.fullmatch(r'[a-z0-9]{20}', project) or
                    settings.supabase_url != 'https://' + project + '.supabase.co' or
                    not _public_key(settings.supabase_s3_anon_key, legacy_only=True)):
                raise ValueError()
        except Exception:
            raise StartupFailure('save-state-invalid') from None
    if settings.auth_email_admission_path:
        from app.services.email_admission import EmailAdmission
        try:
            EmailAdmission(settings.auth_email_admission_path).inspect_ready()
        except Exception:
            raise StartupFailure('email-state-invalid') from None
    probe_port()


def load_application():
    # The existing module app is constructed only after successful preflight.
    from app.main import app
    return app


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    env_file = None
    if len(args) in (2, 3) and args[0] == '--env-file':
        env_file, args = args[1], args[2:]
    if args not in ([], ['--check']):
        print('hosted-startup: arguments-invalid')
        return 1
    try:
        if env_file is not None:
            load_environment(env_file)
        settings = Settings.from_env()
        preflight(settings)
        if not settings.auth_email_admission_path:
            print('hosted-startup: email-disabled (password login available)')
        if args == ['--check']:
            print('hosted-startup: check-passed')
            return 0
        # app.main's existing module application uses these same effective settings.
        # Importing it earlier would construct the app before the safety checks.
        application = load_application()
        import uvicorn
        uvicorn.run(application, host='127.0.0.1', port=8000, workers=1, reload=False,
                    proxy_headers=True, forwarded_allow_ips='127.0.0.1', access_log=False,
                    timeout_keep_alive=5, log_config=None, log_level='critical')
        return 0
    except StartupFailure as error:
        print('hosted-startup: ' + str(error))
    except KeyboardInterrupt:
        return 130
    except BaseException:
        # Never display dotenv input, settings, paths or exception/provider details.
        print('hosted-startup: launch-failed')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
