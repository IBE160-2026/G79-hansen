"""Synthetic credentials only; WSL/provider execution is forbidden in this suite."""

import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

import pytest

from scripts import backup_studybuddy as backup
from scripts import check_backup_connection as connection


CAPTURE = Path(__file__).resolve().parents[1] / "scripts" / "save-backup-password.ps1"
REAL_RUN = subprocess.run
SYNTHETIC = "synthetic-\u00e6\U0001f511-'\"\\$(`);! password"


@pytest.fixture(autouse=True)
def forbid_real_client(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("WSL/provider execution is forbidden")
    monkeypatch.setattr(connection.subprocess, "run", forbidden)


def encoded(value):
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def powershell(code):
    if os.name != "nt":
        pytest.skip("PowerShell/DPAPI checks require Windows")
    executable = shutil.which("powershell.exe")
    assert executable, "Windows PowerShell 5 must be available"
    code = "$ProgressPreference = 'SilentlyContinue'\n" + code
    return REAL_RUN([executable, "-NoLogo", "-NoProfile", "-NonInteractive",
                     "-EncodedCommand", base64.b64encode(code.encode("utf-16-le")).decode("ascii")],
                    capture_output=True, timeout=20, check=False)


def capture(arguments, password=SYNTHETIC, *, prompt_allowed=True, cancel=False):
    # Only synthetic input enters this test-only Read-Host shadow. No real prompts.
    return powershell(f"""
$ErrorActionPreference = 'Stop'
$global:backupSyntheticPassword = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded(password)}'))
function Read-Host {{
    param([string]$Prompt, [switch]$AsSecureString)
    if (-not ${str(prompt_allowed).lower()} -or -not $AsSecureString) {{ throw 'unexpected prompt' }}
    if (${str(cancel).lower()}) {{ throw 'synthetic cancellation' }}
    $value = [Security.SecureString]::new()
    foreach ($character in $global:backupSyntheticPassword.ToCharArray()) {{ $value.AppendChar($character) }}
    return $value
}}
$target = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded(str(CAPTURE))}'))
$testArguments = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded(json.dumps(arguments))}')) | ConvertFrom-Json
& $target @testArguments
""")


def assert_capture_result(result, ok):
    assert result.returncode == (0 if ok else 1)
    assert result.stdout.strip() == (b"studybuddy-backup: password-saved" if ok else
                                      b"studybuddy-backup: password-save-failed")
    assert result.stderr == b""


def test_powershell_syntax_parses():
    result = powershell(f"""
$target = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{encoded(str(CAPTURE))}'))
$tokens = $null
$parseErrors = $null
$null = [Management.Automation.Language.Parser]::ParseFile($target, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count -ne 0) {{ exit 1 }}
""")
    assert result.returncode == 0 and result.stdout == b"" and result.stderr == b""


def test_actual_windows_dpapi_capture_and_python_unwrap(tmp_path):
    destination = tmp_path / "ciphertext with [literal] ' quotes.dpapi"
    result = capture(["-Destination", str(destination)])
    assert_capture_result(result, True)
    encrypted = destination.read_bytes()
    assert SYNTHETIC.encode("utf-8") not in encrypted
    assert backup.WindowsProtector().unprotect(encrypted) == SYNTHETIC.encode("utf-8")
    assert list(tmp_path.iterdir()) == [destination]


def test_capture_never_replaces_existing_file_or_prompts(tmp_path):
    destination = tmp_path / "existing.dpapi"
    destination.write_bytes(b"synthetic existing ciphertext")
    assert_capture_result(capture(["-Destination", str(destination)], prompt_allowed=False), False)
    assert destination.read_bytes() == b"synthetic existing ciphertext"


@pytest.mark.parametrize("password", ["", "synthetic\nvalue", "synthetic\rvalue", "synthetic\0value",
                                      "x" * 1025, "\u00e6" * 513])
def test_capture_rejects_empty_line_controls_and_limits(tmp_path, password):
    destination = tmp_path / "rejected.dpapi"
    assert_capture_result(capture(["-Destination", str(destination)], password), False)
    assert not list(tmp_path.iterdir())


def test_capture_cancel_is_sanitized_and_writes_nothing(tmp_path):
    assert_capture_result(capture(["-Destination", str(tmp_path / "cancel.dpapi")], cancel=True), False)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("arguments", [
    ["-Destination"], ["-Other", "synthetic-sensitive-value"],
    ["-Destination", "relative.dpapi"], ["-Destination", "C:relative.dpapi"],
    ["-Destination", "\\\\server\\share\\synthetic.dpapi"],
    ["-Destination", "C:\\absent\\..\\synthetic.dpapi"],
    ["-Destination", "C:\\absent\\synthetic.dpapi:stream"],
    ["-Destination", "C:\\absent\\NUL"], ["-Destination", "C:\\absent\\trailing."],
])
def test_capture_bad_arguments_are_value_free(arguments):
    assert_capture_result(capture(arguments, prompt_allowed=False), False)


def test_capture_reparse_parent_is_rejected(tmp_path):
    if os.name != "nt":
        pytest.skip("Windows junction test")
    import _winapi
    outside = tmp_path / "synthetic-target"
    outside.mkdir()
    link = tmp_path / "junction"
    _winapi.CreateJunction(str(outside), str(link))
    try:
        assert_capture_result(capture(["-Destination", str(link / "reject.dpapi")], prompt_allowed=False), False)
        assert not list(outside.iterdir())
    finally:
        link.rmdir()


class SyntheticProtector:
    def __init__(self, plaintext=SYNTHETIC.encode("utf-8")):
        self.plaintext = plaintext

    def unprotect(self, encrypted):
        assert encrypted == b"synthetic ciphertext"
        return self.plaintext


@pytest.fixture
def credential(tmp_path):
    path = tmp_path / "synthetic.dpapi"
    path.write_bytes(b"synthetic ciphertext")
    return path


def test_fixed_endpoint_readonly_tls_and_stdin_transport(credential):
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0, stdout=connection.EXPECTED_OUTPUT)

    connection.check_connection(credential, protector=SyntheticProtector(), runner=runner)
    assert len(calls) == 1
    command, kwargs = calls[0]
    assert command[:10] == ["wsl.exe", "-d", "SUREUbuntu", "--exec", "docker", "exec", "-i",
                           "supabase_db_studybuddy-save-local", "sh", "-c"]
    assert len(command) == 11
    script = command[-1]
    assert 'IFS= read -r PGPASSWORD\nexport PGPASSWORD' in script
    assert 'PGHOST=aws-0-eu-west-3.pooler.supabase.com PGPORT=5432' in script
    assert 'PGDATABASE=postgres PGUSER=postgres.fssrvicgmijksgozgfoj' in script
    assert 'PGSSLMODE=verify-full PGSSLROOTCERT=system PGCONNECT_TIMEOUT=8' in script
    assert 'PGSERVICE PGSERVICEFILE PGPASSFILE PGOPTIONS' in script
    assert "psql -X -w -qAt -v ON_ERROR_STOP=1 -c 'BEGIN READ ONLY; SELECT current_database(), current_user; ROLLBACK;'" in script
    assert SYNTHETIC not in ' '.join(command)
    assert kwargs == {"input": SYNTHETIC.encode("utf-8") + b"\n", "stdout": subprocess.PIPE,
                      "stderr": subprocess.DEVNULL, "timeout": 20, "check": False, "shell": False}


@pytest.mark.parametrize("password", [b"", b"x\ny", b"x\ry", b"x\0y", b"\xff", b"x" * 1025])
def test_invalid_plaintext_never_starts_client(credential, password):
    with pytest.raises(connection.ConnectionError, match="^credential-invalid$"):
        connection.check_connection(credential, protector=SyntheticProtector(password))


@pytest.mark.parametrize("state", ["missing", "directory", "oversized", "hardlink", "relative", "corrupt"])
def test_credential_read_is_bounded_regular_single_link_and_absolute(credential, tmp_path, state):
    path = credential
    if state == "missing":
        path = tmp_path / "missing"
    elif state == "directory":
        path = tmp_path
    elif state == "oversized":
        path.write_bytes(b"x" * (backup.MAX_KEY_BLOB + 1))
    elif state == "hardlink":
        os.link(path, tmp_path / "alias")
    elif state == "relative":
        path = Path("synthetic-relative.dpapi")
    else:
        path.write_bytes(b"synthetic corrupt DPAPI")
    with pytest.raises(connection.ConnectionError, match="^credential-invalid$"):
        connection.check_connection(path, protector=SyntheticProtector())


@pytest.mark.parametrize("failure", ["timeout", "tls", "password", "missing-client"])
def test_client_failure_is_sanitized_without_retry(credential, failure):
    calls = []

    def runner(*args, **kwargs):
        calls.append(1)
        if failure == "timeout":
            raise subprocess.TimeoutExpired("synthetic secret", 20, output=b"private", stderr=b"private")
        if failure == "missing-client":
            raise OSError("synthetic private client diagnostics")
        # TLS and password errors both discard raw diagnostics and fail closed.
        return SimpleNamespace(returncode=2, stdout=b"synthetic private output")

    with pytest.raises(connection.ConnectionError) as error:
        connection.check_connection(credential, protector=SyntheticProtector(), runner=runner)
    assert str(error.value) == ("connection-timeout" if failure == "timeout" else "connection-failed")
    assert len(calls) == 1


@pytest.mark.parametrize("output", [b"", b"postgres|wrong-user\n", b"wrong-db|postgres\n",
                                    b"postgres|postgres.fssrvicgmijksgozgfoj\n",
                                    connection.EXPECTED_OUTPUT + b"extra\n"])
def test_wrong_query_output_fails_closed(credential, output):
    def runner(*args, **kwargs):
        return SimpleNamespace(returncode=0, stdout=output)
    with pytest.raises(connection.ConnectionError, match="^connection-result-invalid$"):
        connection.check_connection(credential, protector=SyntheticProtector(), runner=runner)


def test_cli_defaults_literal_path_and_safe_summaries(monkeypatch, capsys, credential):
    calls = []
    monkeypatch.setattr(connection, "check_connection", calls.append)
    assert connection.main([]) == 0
    assert calls == [r"C:\StudyBuddy-Backup\.database-password.dpapi"]
    assert capsys.readouterr().out == "studybuddy-backup: connection-ok\n"
    assert connection.main(["--credential", str(credential)]) == 0
    assert calls[-1] == str(credential)
    assert capsys.readouterr().out == "studybuddy-backup: connection-ok\n"
    assert connection.main(["--synthetic-secret"]) == 1
    output = capsys.readouterr()
    assert output.out == "studybuddy-backup: arguments-invalid\n" and output.err == ""


@pytest.mark.parametrize("category", ["credential-invalid", "connection-timeout", "connection-failed",
                                      "connection-result-invalid"])
def test_cli_failure_categories_have_no_details(monkeypatch, capsys, category):
    def fail(*args):
        raise connection.ConnectionError(category) from RuntimeError(SYNTHETIC)
    monkeypatch.setattr(connection, "check_connection", fail)
    assert connection.main([]) == 1
    output = capsys.readouterr()
    assert output.out == f"studybuddy-backup: {category}\n" and output.err == ""


def test_real_corrupt_dpapi_is_safely_rejected(credential):
    if os.name != "nt":
        pytest.skip("DPAPI requires Windows")
    with pytest.raises(connection.ConnectionError, match="^credential-invalid$"):
        connection.check_connection(credential)
