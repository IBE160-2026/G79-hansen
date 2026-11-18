"""Durable, content-free shared signup/recovery reservations; never refund."""

import asyncio
import hashlib
import hmac
import math
import os
from pathlib import Path
import secrets
import sqlite3
import stat
from threading import BoundedSemaphore
import time

from starlette.concurrency import run_in_threadpool

from app.adapters.auth import AuthFailure


WINDOW_SECONDS = 3600
MAX_FILE_BYTES = 65536
_slots = BoundedSemaphore(2)
_jobs = set()
_SCHEMA = (
    "CREATE TABLE metadata (id INTEGER PRIMARY KEY CHECK (id = 1), "
    "version INTEGER NOT NULL, secret BLOB NOT NULL, last_seen REAL NOT NULL)",
    "CREATE TABLE reservations (recipient BLOB PRIMARY KEY NOT NULL, reserved_at REAL NOT NULL)",
)


def _timestamp(value):
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 253402300799


class EmailAdmission:
    def __init__(self, path, *, clock=time.time):
        self.path = Path(path).absolute() if path else None
        self.clock = clock

    @classmethod
    def initialize(cls, path, *, clock=time.time):
        """Explicit offline creation only. Even failed initialization is never reset."""
        path = Path(path).absolute()
        now = clock()
        if not _timestamp(now):
            raise AuthFailure()
        try:
            # Refuse stale sidecars too: they may belong to prior uncertain state.
            if any(Path(str(path) + suffix).exists() for suffix in ('-journal', '-wal', '-shm')):
                raise OSError()
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(descriptor)
            connection = cls(path)._connect()
            try:
                connection.execute('PRAGMA page_size = 4096')
                connection.execute('PRAGMA max_page_count = 16')
                connection.execute('BEGIN EXCLUSIVE')
                for statement in _SCHEMA:
                    connection.execute(statement)
                connection.execute('PRAGMA user_version = 1')
                connection.execute('INSERT INTO metadata VALUES (1, 1, ?, ?)', (secrets.token_bytes(32), now))
                connection.commit()
            finally:
                connection.close()
            if os.name != 'nt':
                descriptor = os.open(path.parent, os.O_RDONLY)
                try:
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
        except (OSError, sqlite3.Error, ValueError):
            raise AuthFailure() from None

    def _connect(self):
        if self.path is None:
            raise AuthFailure()
        info = self.path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_FILE_BYTES:
            raise AuthFailure()
        for suffix in ('-journal', '-wal', '-shm'):
            sidecar = Path(str(self.path) + suffix)
            if sidecar.exists():
                info = sidecar.lstat()
                if (suffix != '-journal' or not stat.S_ISREG(info.st_mode) or
                        info.st_size > MAX_FILE_BYTES):
                    raise AuthFailure()
        # mode=rw is essential: a missing journal must never become fresh state.
        connection = sqlite3.connect(self.path.as_uri() + '?mode=rw', uri=True, timeout=0,
                                     isolation_level=None)
        try:
            connection.execute('PRAGMA busy_timeout = 0')
            connection.execute('PRAGMA synchronous = FULL')
            connection.execute('PRAGMA fullfsync = ON')
            connection.execute('PRAGMA trusted_schema = OFF')
            connection.execute('PRAGMA max_page_count = 16')
            return connection
        except BaseException:
            connection.close()
            raise

    def _validate(self, connection, now):
        schema = connection.execute(
            "SELECT sql FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
        if schema != [(statement,) for statement in _SCHEMA]:
            raise AuthFailure()
        if (connection.execute('PRAGMA user_version').fetchone() != (1,) or
                connection.execute('PRAGMA journal_mode').fetchone() != ('delete',) or
                connection.execute('PRAGMA page_size').fetchone() != (4096,) or
                connection.execute('PRAGMA page_count').fetchone()[0] > 16 or
                connection.execute('PRAGMA quick_check').fetchall() != [('ok',)]):
            raise AuthFailure()
        metadata = connection.execute('SELECT id, version, secret, last_seen FROM metadata LIMIT 2').fetchall()
        rows = connection.execute('SELECT recipient, reserved_at FROM reservations LIMIT 3').fetchall()
        if len(metadata) != 1 or len(rows) > 2:
            raise AuthFailure()
        identifier, version, secret, last_seen = metadata[0]
        if (type(identifier) is not int or identifier != 1 or type(version) is not int or version != 1 or
                type(secret) is not bytes or len(secret) != 32 or not _timestamp(last_seen) or
                not _timestamp(now) or now < last_seen):
            raise AuthFailure()
        for digest, timestamp in rows:
            if (type(digest) is not bytes or len(digest) != 32 or not _timestamp(timestamp) or
                    timestamp > last_seen):
                raise AuthFailure()
        return secret

    def _inspection_state(self):
        if self.path is None:
            raise AuthFailure()
        info = self.path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_FILE_BYTES:
            raise AuthFailure()
        for suffix in ('-journal', '-wal', '-shm'):
            try:
                Path(str(self.path) + suffix).lstat()
            except FileNotFoundError:
                continue
            raise AuthFailure()
        return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns

    def inspect_ready(self):
        """Validate existing state without recovery, reservation or clock updates."""
        connection = None
        try:
            before = self._inspection_state()
            # immutable prevents even SQLite's read-side recovery/sidecar writes.
            # Refuse uncertain or concurrently changed state instead of repairing it.
            connection = sqlite3.connect(self.path.as_uri() + '?mode=ro&immutable=1', uri=True,
                                         timeout=0, isolation_level=None)
            connection.execute('PRAGMA trusted_schema = OFF')
            connection.execute('PRAGMA query_only = ON')
            connection.execute('BEGIN')
            self._validate(connection, self.clock())
            if self._inspection_state() != before:
                raise AuthFailure()
        except (OSError, sqlite3.Error, ValueError, OverflowError):
            raise AuthFailure() from None
        finally:
            if connection is not None:
                connection.close()

    def reserve(self, recipient):
        """Commit before dispatch; errors deliberately reveal no state or addresses."""
        connection = None
        try:
            if not isinstance(recipient, str) or not 3 <= len(recipient) <= 254:
                raise AuthFailure()
            connection = self._connect()
            connection.execute('BEGIN IMMEDIATE')
            now = self.clock()
            secret = self._validate(connection, now)
            digest = hmac.digest(secret, recipient.strip().casefold().encode('utf-8'), hashlib.sha256)
            connection.execute('DELETE FROM reservations WHERE reserved_at <= ?', (now - WINDOW_SECONDS,))
            rows = connection.execute('SELECT recipient FROM reservations LIMIT 3').fetchall()
            denied = len(rows) >= 2 or (digest,) in rows
            connection.execute('UPDATE metadata SET last_seen = ? WHERE id = 1', (now,))
            if not denied:
                connection.execute('INSERT INTO reservations VALUES (?, ?)', (digest, now))
            connection.commit()
            if denied:
                raise AuthFailure('auth_capacity')
        except (OSError, sqlite3.Error, ValueError, OverflowError):
            raise AuthFailure() from None
        finally:
            if connection is not None:
                connection.close()

    async def reserve_for_dispatch(self, recipient):
        # Admit before the shared threadpool: at most two journal jobs, no queue.
        if not _slots.acquire(blocking=False):
            raise AuthFailure('auth_capacity')

        async def owned_reservation():
            try:
                await run_in_threadpool(self.reserve, recipient)
            finally:
                _slots.release()

        def finished(job):
            _jobs.discard(job)
            if not job.cancelled():
                job.exception()  # A cancelled HTTP waiter must not cause error logging.

        # Own scheduling as well as IO: cancellation before a worker starts cannot
        # leak a slot or release one while its reservation is still in progress.
        job = asyncio.create_task(owned_reservation())
        _jobs.add(job)
        job.add_done_callback(finished)
        await asyncio.shield(job)
