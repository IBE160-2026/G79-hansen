"""Explicit read-only connection probe; never imports app configuration or exports."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

from scripts.backup_studybuddy import MAX_KEY_BLOB, WindowsProtector, _checked_path, _read

DEFAULT_CREDENTIAL = r"C:\StudyBuddy-Backup\.database-password.dpapi"
MAX_PASSWORD = 1024
PROCESS_TIMEOUT = 20
# The project suffix routes the pooler login; PostgreSQL's actual role is postgres.
EXPECTED_OUTPUT = b"postgres|postgres\n"

# Password is consumed as literal stdin data, never inserted into this script.
# This uses the already running local client only; no setup/restart is performed.
CLIENT_SCRIPT = """set -eu
IFS= read -r PGPASSWORD
export PGPASSWORD
unset PGHOSTADDR PGSERVICE PGSERVICEFILE PGPASSFILE PGOPTIONS PGSSLCERT PGSSLKEY PGSSLCRL PGSSLCRLDIR PGREQUIREPEER PGTARGETSESSIONATTRS PGCHANNELBINDING PGSSLMINPROTOCOLVERSION PGSSLMAXPROTOCOLVERSION
export PGHOST=aws-0-eu-west-3.pooler.supabase.com PGPORT=5432
export PGDATABASE=postgres PGUSER=postgres.fssrvicgmijksgozgfoj
export PGSSLMODE=verify-full PGSSLROOTCERT=system PGCONNECT_TIMEOUT=8
export PGCLIENTENCODING=UTF8 PGAPPNAME=studybuddy-backup-connection-check
exec psql -X -w -qAt -v ON_ERROR_STOP=1 -c 'BEGIN READ ONLY; SELECT current_database(), current_user; ROLLBACK;'
"""
CLIENT_COMMAND = (
    "wsl.exe", "-d", "SUREUbuntu", "--exec", "docker", "exec", "-i",
    "supabase_db_studybuddy-save-local", "sh", "-c", CLIENT_SCRIPT,
)


class ConnectionError(Exception):
    def __init__(self, category):
        self.category = category
        super().__init__(category)


def check_connection(credential=DEFAULT_CREDENTIAL, *, protector=None, runner=None):
    """Injection ports are for synthetic tests; production uses DPAPI and subprocess."""
    try:
        path = _checked_path(Path(credential), directory=False)
        encrypted = _read(path, MAX_KEY_BLOB)
        protector = WindowsProtector() if protector is None else protector
        password = protector.unprotect(encrypted)
        if not 0 < len(password) <= MAX_PASSWORD or any(c in password for c in (b"\r", b"\n", b"\0")):
            raise ValueError()
        password.decode("utf-8", errors="strict")
    except (Exception, KeyboardInterrupt):
        raise ConnectionError("credential-invalid") from None
    runner = subprocess.run if runner is None else runner
    try:
        result = runner(list(CLIENT_COMMAND), input=password + b"\n", stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL, timeout=PROCESS_TIMEOUT, check=False,
                        shell=False)
    except subprocess.TimeoutExpired:
        raise ConnectionError("connection-timeout") from None
    except (Exception, KeyboardInterrupt):
        raise ConnectionError("connection-failed") from None
    if result.returncode != 0:
        raise ConnectionError("connection-failed")
    if result.stdout != EXPECTED_OUTPUT:
        raise ConnectionError("connection-result-invalid")


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ConnectionError("arguments-invalid")


def main(argv=None):
    try:
        parser = _Parser(add_help=False, allow_abbrev=False)
        parser.add_argument("--credential", default=DEFAULT_CREDENTIAL)
        args = parser.parse_args(argv)
        check_connection(args.credential)
        print("studybuddy-backup: connection-ok")
        return 0
    except ConnectionError as error:
        print(f"studybuddy-backup: {error.category}")
    except (Exception, KeyboardInterrupt):
        print("studybuddy-backup: connection-failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
