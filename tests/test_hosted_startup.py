"""Synthetic offline startup contracts; never use real env/state or port 8000."""

import base64
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
from unittest.mock import Mock

import pytest

from app.adapters.auth import AuthFailure
from app.config import Settings
from app.services.email_admission import EmailAdmission
from app.services.model_budget import ModelBudget
from scripts import hosted_server as hosted
from test_email_admission import legacy_journal


ROOT = Path(__file__).resolve().parents[1]
PROJECT = 'abcdefghijklmnopqrst'
SETTINGS = Settings(auth_enabled=True, app_origin='https://study.test:10000',
                    supabase_url=f'https://{PROJECT}.supabase.co',
                    supabase_key='sb_publishable_' + 'a' * 32)
EXPIRE_BACKUPS = hosted.expire_backups


def anon_key(role='anon'):
    def encode(value):
        return base64.urlsafe_b64encode(json.dumps(value).encode()).rstrip(b'=').decode()
    return encode({'alg': 'HS256', 'typ': 'JWT'}) + '.' + encode({'role': role}) + '.c2ln'


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    # Any ordinary preflight probe is replaced, including successful checks.
    monkeypatch.setattr(hosted, 'probe_port', Mock())
    monkeypatch.setattr(hosted, 'expire_backups', Mock())
    monkeypatch.setattr(Settings, 'from_env', classmethod(lambda cls: SETTINGS))
    application_import = Mock(side_effect=AssertionError('application must not be imported'))
    monkeypatch.setattr(hosted, 'load_application', application_import)
    return application_import


def effective(monkeypatch, settings):
    monkeypatch.setattr(Settings, 'from_env', classmethod(lambda cls: settings))


@pytest.fixture
def enabled(tmp_path):
    budget, key, journal = (tmp_path / name for name in ('budget.json', 'key', 'email.sqlite3'))
    ModelBudget.initialize(budget)
    key.write_text('a' * 64, encoding='ascii')
    EmailAdmission.initialize(journal, clock=lambda: 1000)
    return replace(SETTINGS, model_enabled=True, openai_api_key='sk-' + 'a' * 40,
                   model_budget_path=str(budget), save_enabled=True, save_backend_key_path=str(key),
                   supabase_s3_region='eu-west-3', supabase_s3_key_id=PROJECT,
                   supabase_s3_anon_key=anon_key(), auth_email_admission_path=str(journal))


def snapshot(directory):
    return {path.name: (path.read_bytes(), path.stat().st_mtime_ns)
            for path in directory.iterdir() if path.is_file()}


def test_check_all_features_is_read_only(enabled, tmp_path, monkeypatch, offline, capsys):
    effective(monkeypatch, enabled)
    before = snapshot(tmp_path)
    assert hosted.main(['--check']) == 0
    assert snapshot(tmp_path) == before
    assert capsys.readouterr().out == 'hosted-startup: check-passed\n'
    offline.assert_not_called()
    hosted.probe_port.assert_called_once_with()
    hosted.expire_backups.assert_not_called()


def test_disabled_email_is_explicit_and_launch_is_fixed(monkeypatch, offline, capsys):
    application, run = object(), Mock()
    offline.side_effect = None
    offline.return_value = application
    # Import uvicorn normally before substituting its entry point; run is never real.
    import uvicorn
    monkeypatch.setattr(uvicorn, 'run', run)
    assert hosted.main([]) == 0
    offline.assert_called_once_with()
    run.assert_called_once_with(application, host='127.0.0.1', port=8000, workers=1,
                               reload=False, proxy_headers=True, forwarded_allow_ips='127.0.0.1',
                               access_log=False, timeout_keep_alive=5,
                               log_config=None, log_level='critical')
    assert 'email-disabled (password login available)' in capsys.readouterr().out


def test_retention_runs_after_preflight_before_import_and_server(monkeypatch, offline):
    import uvicorn
    events = []
    monkeypatch.setattr(hosted, 'preflight', lambda settings: events.append('preflight'))
    hosted.expire_backups.side_effect = lambda: events.append('expiry')
    offline.side_effect = lambda: events.append('app') or object()
    monkeypatch.setattr(uvicorn, 'run', lambda *args, **kwargs: events.append('server'))
    assert hosted.main([]) == 0
    assert events == ['preflight', 'expiry', 'app', 'server']


def test_preflight_failure_never_runs_retention(offline, capsys):
    hosted.probe_port.side_effect = hosted.StartupFailure('port-busy')
    assert hosted.main([]) == 1
    hosted.expire_backups.assert_not_called()
    offline.assert_not_called()


def test_retention_uses_existing_policy_at_fixed_root(monkeypatch):
    from scripts import backup_studybuddy
    rotate = Mock()
    monkeypatch.setattr(backup_studybuddy, 'rotate', rotate)
    EXPIRE_BACKUPS()
    rotate.assert_called_once_with(Path(r'C:\StudyBuddy-Backup'))


@pytest.mark.parametrize('error', [OSError('SECRET_SENTINEL'), RuntimeError('SECRET_SENTINEL')])
def test_retention_failure_is_safe_and_prevents_application(monkeypatch, offline, capsys, error):
    import uvicorn
    from scripts import backup_studybuddy
    monkeypatch.setattr(backup_studybuddy, 'rotate', Mock(side_effect=error))
    monkeypatch.setattr(hosted, 'expire_backups', EXPIRE_BACKUPS)
    run = Mock()
    monkeypatch.setattr(uvicorn, 'run', run)
    assert hosted.main([]) == 1
    assert capsys.readouterr().out == ('hosted-startup: email-disabled (password login available)\n'
                                      'hosted-startup: backup-retention-failed\n')
    offline.assert_not_called()
    run.assert_not_called()


@pytest.mark.parametrize('changes', [
    {'auth_enabled': False}, {'app_origin': 'http://study.test:10000'},
    {'app_origin': 'https://study.test:bad'}, {'app_origin': 'https://study.test/path'},
    {'app_origin': 'https://study.test\n'}, {'supabase_url': 'https://provider.test\t'},
    {'allow_loopback_http': True}, {'supabase_url': 'http://provider.test'},
    {'supabase_key': 'sb_secret_SECRET_SENTINEL'},
    {'supabase_key': 'sb_publishable_YOUR_PUBLISHABLE_KEY'},
    {'supabase_key': 'sb_publishable_' + 'a' * 32 + '\nSECRET_SENTINEL'},
    {'supabase_key': 'a.b.c'}, {'supabase_key': anon_key('service_role')},
])
def test_unsafe_configuration_never_imports_app(changes, monkeypatch, offline, capsys):
    effective(monkeypatch, replace(SETTINGS, **changes))
    assert hosted.main([]) == 1
    assert capsys.readouterr().out == 'hosted-startup: configuration-invalid\n'
    offline.assert_not_called()
    hosted.probe_port.assert_not_called()


def test_valid_legacy_anon_configuration(monkeypatch):
    effective(monkeypatch, replace(SETTINGS, supabase_key=anon_key()))
    assert hosted.main(['--check']) == 0


@pytest.mark.parametrize('kind', ['missing-budget', 'directory', 'bad-budget', 'model-key', 'model-placeholder',
                                  'missing-key', 'bad-key', 'region', 'project', 's3-secret',
                                  's3-publishable', 'missing-email', 'bad-email', 'future-email',
                                  'same-path', 'hardlink'])
def test_enabled_feature_failures_preserve_all_state(enabled, kind, tmp_path, monkeypatch, offline, capsys):
    settings = enabled
    budget, key, journal = map(Path, (settings.model_budget_path, settings.save_backend_key_path,
                                    settings.auth_email_admission_path))
    if kind == 'missing-budget':
        budget.unlink()
    elif kind == 'directory':
        settings = replace(settings, model_budget_path=str(tmp_path))
    elif kind == 'bad-budget':
        budget.write_text('SECRET_SENTINEL')
    elif kind in ('model-key', 'model-placeholder'):
        settings = replace(settings, openai_api_key=('SECRET_SENTINEL' if kind == 'model-key'
                                                    else 'sk-YOUR_EXISTING_OPENAI_API_KEY'))
    elif kind == 'missing-key':
        key.unlink()
    elif kind == 'bad-key':
        key.write_text('SECRET_SENTINEL')
    elif kind == 'region':
        settings = replace(settings, supabase_s3_region='eu-central-1')
    elif kind == 'project':
        settings = replace(settings, supabase_s3_key_id='z' * 20)
    elif kind in ('s3-secret', 's3-publishable'):
        settings = replace(settings, supabase_s3_anon_key=(anon_key('service_role') if kind == 's3-secret'
                                                        else SETTINGS.supabase_key))
    elif kind == 'missing-email':
        journal.unlink()
    elif kind == 'bad-email':
        journal.write_text('SECRET_SENTINEL')
    elif kind == 'future-email':
        with sqlite3.connect(journal) as connection:
            connection.execute('UPDATE metadata SET last_seen = 253402300799')
    elif kind == 'same-path':
        settings = replace(settings, save_backend_key_path=str(budget))
    elif kind == 'hardlink':
        key.unlink()
        key.hardlink_to(budget)
    effective(monkeypatch, settings)
    before = snapshot(tmp_path)
    assert hosted.main([]) == 1
    assert snapshot(tmp_path) == before
    output = capsys.readouterr()
    assert 'SECRET_SENTINEL' not in output.out + output.err
    assert str(tmp_path) not in output.out + output.err
    offline.assert_not_called()
    hosted.probe_port.assert_not_called()


@pytest.mark.parametrize('kind', ['blocked', 'blocked-sidecar', 'exhausted'])
def test_blocked_or_exhausted_budget_preserved_and_generation_stays_denied(enabled, kind, tmp_path,
                                                                         monkeypatch, offline):
    path = Path(enabled.model_budget_path)
    budget = ModelBudget(path)
    if kind == 'blocked-sidecar':
        budget.blocked_path.write_text('blocked')
    else:
        value = json.loads(path.read_text())
        if kind == 'blocked':
            value['blocked'] = True
        else:
            value.update(attempts=100, reservedMicrousd=5_000_000)
        path.write_text(json.dumps(value))
    effective(monkeypatch, enabled)
    before = snapshot(tmp_path)
    assert hosted.main(['--check']) == 0
    assert snapshot(tmp_path) == before
    offline.assert_not_called()
    # reserve is deliberately not called: its lock sidecar would be a mutation.
    state = budget.read()
    assert state['blocked'] or state['reservedMicrousd'] == state['ceilingMicrousd']
    assert snapshot(tmp_path) == before


def test_collision_is_safe_and_never_imports_app(monkeypatch, offline, capsys):
    hosted.probe_port.side_effect = hosted.StartupFailure('port-busy')
    assert hosted.main([]) == 1
    assert capsys.readouterr().out == 'hosted-startup: port-busy\n'
    offline.assert_not_called()


def test_probe_closes_socket_without_listening(monkeypatch):
    # Exercise the real probe function only with a fake socket, never real port8000.
    import importlib.util
    spec = importlib.util.spec_from_file_location('synthetic_hosted_probe', ROOT / 'scripts/hosted_server.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    probe = Mock()
    probe.__enter__ = Mock(return_value=probe)
    probe.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(module.socket, 'socket', Mock(return_value=probe))
    module.probe_port()
    probe.bind.assert_called_once_with(('127.0.0.1', 8000))
    probe.listen.assert_not_called()
    probe.__exit__.assert_called_once()
    probe.bind.side_effect = OSError('SECRET_SENTINEL')
    with pytest.raises(module.StartupFailure, match='^port-busy$'):
        module.probe_port()


def test_unexpected_error_and_arguments_are_sanitized(monkeypatch, capsys, offline):
    assert hosted.main(['--SECRET_SENTINEL']) == 1
    hosted.probe_port.side_effect = RuntimeError('SECRET_SENTINEL')
    assert hosted.main([]) == 1
    assert capsys.readouterr().out == ('hosted-startup: arguments-invalid\n'
                                      'hosted-startup: launch-failed\n')
    offline.assert_not_called()


@pytest.mark.parametrize('kind', ['valid', 'missing', 'malformed', 'clock', 'schema', 'wal', 'journal', 'shm'])
def test_email_inspection_preserves_bytes_metadata_and_sidecars(tmp_path, kind):
    path = tmp_path / 'synthetic.sqlite3'
    EmailAdmission.initialize(path, clock=lambda: 1000)
    service = EmailAdmission(path, clock=lambda: 1001)
    if kind == 'missing':
        path.unlink()
    elif kind == 'malformed':
        path.write_bytes(b'SECRET_SENTINEL')
    elif kind == 'clock':
        service = EmailAdmission(path, clock=lambda: 999)
    elif kind == 'schema':
        with sqlite3.connect(path) as connection:
            connection.execute('CREATE TABLE unexpected (value TEXT)')
    elif kind in ('wal', 'journal', 'shm'):
        Path(str(path) + '-' + kind).write_bytes(b'SECRET_SENTINEL')
    before = snapshot(tmp_path)
    if kind == 'valid':
        assert service.inspect_ready() is None
    else:
        with pytest.raises(AuthFailure, match='^auth_unavailable$'):
            service.inspect_ready()
    assert snapshot(tmp_path) == before


def test_inspection_sqlite_error_is_normalized(tmp_path, monkeypatch):
    path = tmp_path / 'synthetic.sqlite3'
    EmailAdmission.initialize(path, clock=lambda: 1000)
    def fail(*args, **kwargs):
        raise sqlite3.OperationalError('SECRET_SENTINEL')
    monkeypatch.setattr(sqlite3, 'connect', fail)
    with pytest.raises(AuthFailure, match='^auth_unavailable$'):
        EmailAdmission(path).inspect_ready()


def test_hosted_rejects_legacy_until_explicit_upgrade_then_inspects_without_mutation(
        enabled, tmp_path, monkeypatch, offline, capsys):
    path = Path(enabled.auth_email_admission_path)
    path.unlink()
    legacy_journal(path)
    effective(monkeypatch, enabled)
    before = snapshot(tmp_path)
    assert hosted.main(['--check']) == 1
    assert capsys.readouterr().out == 'hosted-startup: email-state-invalid\n'
    assert snapshot(tmp_path) == before
    hosted.probe_port.assert_not_called()
    assert EmailAdmission.upgrade(path)
    before = snapshot(tmp_path)
    assert hosted.main(['--check']) == 0
    assert snapshot(tmp_path) == before
    offline.assert_not_called()


def powershell():
    executable = shutil.which('powershell.exe')
    if not executable:
        pytest.skip('Windows PowerShell unavailable')
    return executable


def native_environment():
    # Never inherit credentials or uv/dotenv overrides from the operator process.
    return {name: os.environ[name] for name in ('PATH', 'SystemRoot', 'TEMP', 'TMP',
                                               'USERPROFILE', 'LOCALAPPDATA', 'APPDATA')
            if name in os.environ}


def test_literal_environment_and_ambient_precedence(tmp_path, monkeypatch):
    for name in hosted._ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv('APP_ORIGIN', 'https://ambient.test:10000')
    path = tmp_path / 'synthetic.env'
    path.write_text('export AUTH_ENABLED=true # comment\n'
                    'APP_ORIGIN="https://file.test:10000"\n'
                    "MODEL_BUDGET_PATH='C:\\state\\existing.json'\n"
                    'AUTH_EMAIL_ADMISSION_PATH=\n'
                    'SUPABASE_PUBLISHABLE_KEY=$(Set-Content executed.txt bad)\n', encoding='utf-8')
    hosted.load_environment(path)
    assert os.environ['APP_ORIGIN'] == 'https://ambient.test:10000'
    assert os.environ['AUTH_ENABLED'] == 'true'
    assert os.environ['MODEL_BUDGET_PATH'] == 'C:\\state\\existing.json'
    assert os.environ['AUTH_EMAIL_ADMISSION_PATH'] == ''
    assert os.environ['SUPABASE_PUBLISHABLE_KEY'] == '$(Set-Content executed.txt bad)'
    assert not (ROOT / 'executed.txt').exists()


@pytest.mark.parametrize('content', ['APP_ORIGIN="SECRET_SENTINEL',
                                    'APP_ORIGIN="closed"SECRET_SENTINEL"',
                                    'AUTH_ENABLED=true\nAUTH_ENABLED=false',
                                    'AUTH_ENABLED=true\nUNKNOWN=SECRET_SENTINEL',
                                    'AUTH_ENABLED=true\nOPENAI_API_KEY=SECRET_SENTINEL\x00',
                                    'AUTH_ENABLED=true\nOPENAI_API_KEY=SECRET_SENTINEL\x01',
                                    'AUTH_ENABLED=true\nOPENAI_API_KEY=SECRET_SENTINEL\x7f',
                                    'OPENAI_API_KEY=' + 'x' * 65536])
def test_bad_env_is_atomic_safe_and_never_imports_or_probes(tmp_path, monkeypatch, content, offline, capsys):
    monkeypatch.delenv('AUTH_ENABLED', raising=False)
    path = tmp_path / 'synthetic.env'
    path.write_text(content, encoding='utf-8')
    assert hosted.main(['--env-file', str(path), '--check']) == 1
    assert 'AUTH_ENABLED' not in os.environ
    assert capsys.readouterr().out == 'hosted-startup: environment-invalid\n'
    offline.assert_not_called()
    hosted.probe_port.assert_not_called()


def test_powershell_syntax():
    script = str(ROOT / 'scripts/start-hosted.ps1').replace("'", "''")
    command = ("$tokens=$null; $parseErrors=$null; "
               f"[void][System.Management.Automation.Language.Parser]::ParseFile('{script}',"
               "[ref]$tokens,[ref]$parseErrors); if ($parseErrors.Count) { exit 1 }")
    result = subprocess.run([powershell(), '-NoProfile', '-Command', command],
                            capture_output=True, timeout=15, env=native_environment())
    assert result.returncode == 0


@pytest.mark.parametrize('kind', ['missing', 'unsafe', 'malformed', 'hostile-path'])
def test_wrapper_rejects_synthetic_env_safely_without_server(tmp_path, kind):
    if not shutil.which('uv'):
        pytest.skip('installed uv unavailable')
    sentinel = tmp_path / 'executed.txt'
    path = tmp_path / ("hostile $(Set-Content executed.txt bad);'`.env"
                       if kind == 'hostile-path' else 'synthetic.env')
    if kind != 'missing':
        path.write_text('AUTH_ENABLED=false\n' +
                        ('SUPABASE_PUBLISHABLE_KEY="SECRET_SENTINEL\n' if kind == 'malformed'
                         else 'SUPABASE_PUBLISHABLE_KEY=SECRET_SENTINEL\n'), encoding='utf-8')
    result = subprocess.run([powershell(), '-NoProfile', '-ExecutionPolicy', 'Bypass',
                             '-File', str(ROOT / 'scripts/start-hosted.ps1'),
                             '-EnvFile', str(path), '-Check'], cwd=tmp_path,
                            capture_output=True, timeout=30, env=native_environment())
    assert result.returncode != 0
    output = (result.stdout + result.stderr).decode(errors='replace')
    assert 'hosted-startup:' in output
    assert 'SECRET_SENTINEL' not in output and str(tmp_path) not in output
    assert not sentinel.exists() and not (ROOT / 'executed.txt').exists()
