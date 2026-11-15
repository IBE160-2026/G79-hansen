"""Content-free, fail-closed durable reservations. Never refund uncertain calls."""
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
import asyncio
import json
import os
from pathlib import Path
from threading import BoundedSemaphore, RLock
from uuid import uuid4


class BudgetFailure(Exception):
    pass


# No shared web-worker pool and no queue: two owned filesystem operations maximum
# across instances. A cancelled HTTP waiter cannot release a running worker slot.
_workers = ThreadPoolExecutor(max_workers=2, thread_name_prefix='model-budget')
_worker_slots = BoundedSemaphore(2)


class ModelBudget:
    def __init__(self, path):
        self.path = Path(path) if path else None
        self.lock = RLock()

    async def _owned_io(self, operation, *args):
        if not _worker_slots.acquire(blocking=False):
            raise BudgetFailure()
        try:
            worker = _workers.submit(operation, *args)
        except BaseException:
            _worker_slots.release()
            raise
        worker.add_done_callback(lambda _: _worker_slots.release())
        pending = asyncio.wrap_future(worker)
        cancelled = False
        while True:
            try:
                result = await asyncio.shield(pending)
                break
            except asyncio.CancelledError:
                # Keep owning cleanup, including repeated shutdown cancellation.
                cancelled = True
            except BaseException:
                if cancelled:
                    raise asyncio.CancelledError() from None
                raise
        if cancelled:
            raise asyncio.CancelledError()
        return result

    async def reserve_for_dispatch(self):
        def reserve_and_check():
            self.reserve()
            self.check_dispatch()
        await self._owned_io(reserve_and_check)

    async def observe_async(self, input_tokens, output_tokens):
        await self._owned_io(self.observe, input_tokens, output_tokens)

    @staticmethod
    def initial():
        return {'version': 1, 'ceilingMicrousd': 5_000_000, 'reservationMicrousd': 50_000,
                'reservedMicrousd': 0, 'attempts': 0, 'liveChecks': 0, 'blocked': False}

    @classmethod
    def initialize(cls, path):
        path = Path(path)
        # Exclusive creation is intentional: neither restart nor init resets usage.
        with path.open('x', encoding='utf-8') as target:
            target.write(json.dumps(cls.initial(), sort_keys=True))
            target.flush()
            os.fsync(target.fileno())

    @property
    def blocked_path(self):
        if self.path is None:
            raise BudgetFailure()
        return self.path.with_suffix(self.path.suffix + '.blocked')

    def check_dispatch(self):
        try:
            self.blocked_path.stat()
        except FileNotFoundError:
            return
        except OSError:
            raise BudgetFailure() from None
        raise BudgetFailure()

    @contextmanager
    def exclusive(self):
        if self.path is None:
            raise BudgetFailure()
        try:
            with self.lock:
                # Windows can deny even the pre-lock read when another instance
                # holds this byte. Normalize every filesystem/lock failure.
                with self.path.with_suffix(self.path.suffix + '.lock').open('a+b') as lock_file:
                    lock_file.seek(0)
                    if lock_file.read(1) == b'':
                        lock_file.write(b'0'); lock_file.flush()
                    lock_file.seek(0)
                    if os.name == 'nt':
                        import msvcrt
                        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    try:
                        yield
                    finally:
                        lock_file.seek(0)
                        if os.name == 'nt':
                            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                        else:
                            fcntl.flock(lock_file, fcntl.LOCK_UN)
        except OSError:
            raise BudgetFailure() from None

    def read(self):
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError()
                result[key] = value
            return result
        try:
            if self.path.stat().st_size > 1024:
                raise ValueError()
            value = json.loads(self.path.read_text(encoding='utf-8'), object_pairs_hook=unique)
            expected = self.initial()
            if set(value) != set(expected) or any(type(value[key]) is not type(expected[key]) for key in expected):
                raise ValueError()
            if (any(value[key] != expected[key] for key in ('version', 'ceilingMicrousd', 'reservationMicrousd')) or
                not 0 <= value['attempts'] <= 100 or value['reservedMicrousd'] != value['attempts'] * 50_000):
                raise ValueError()
            if not 0 <= value['liveChecks'] <= min(4, value['attempts']):
                raise ValueError()
            try:
                self.check_dispatch()
            except BudgetFailure:
                value['blocked'] = True
            return value
        except (OSError, ValueError, TypeError, AttributeError):
            raise BudgetFailure() from None

    def write(self, value):
        temporary = self.path.with_name(self.path.name + '.' + uuid4().hex + '.tmp')
        try:
            with temporary.open('x', encoding='utf-8') as target:
                target.write(json.dumps(value, sort_keys=True))
                target.flush(); os.fsync(target.fileno())
            self.replace_durably(temporary, self.path)
        except OSError:
            raise BudgetFailure() from None
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def replace_durably(temporary, destination):
        if os.name == 'nt':
            import ctypes
            from ctypes import wintypes
            move = ctypes.WinDLL('kernel32', use_last_error=True).MoveFileExW
            move.argtypes = (wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD)
            move.restype = wintypes.BOOL
            if not move(str(temporary.resolve()), str(destination.resolve()), 0x1 | 0x8):
                raise OSError('durable ledger replacement failed')
        else:
            os.replace(temporary, destination)
            descriptor = os.open(destination.parent, os.O_RDONLY)
            try: os.fsync(descriptor)
            finally: os.close(descriptor)

    def block(self):
        # Independent monotonic latch: anomalous usage must persist even while
        # another instance owns the ledger lock. Its presence always denies use.
        destination = self.blocked_path
        temporary = destination.with_name(destination.name + '.' + uuid4().hex + '.tmp')
        try:
            with temporary.open('x', encoding='ascii') as target:
                target.write('blocked\n'); target.flush(); os.fsync(target.fileno())
            self.replace_durably(temporary, destination)
        except OSError:
            raise BudgetFailure() from None
        finally:
            temporary.unlink(missing_ok=True)

    def reserve(self, *, live_check=False):
        try:
            with self.exclusive():
                value = self.read()
                if value['blocked'] or value['reservedMicrousd'] + 50_000 > value['ceilingMicrousd']:
                    raise BudgetFailure()
                if live_check and value['liveChecks'] >= 4:
                    raise BudgetFailure()
                value['attempts'] += 1; value['reservedMicrousd'] += 50_000
                if live_check:
                    value['liveChecks'] += 1
                self.write(value)
                self.check_dispatch()
        except OSError:
            raise BudgetFailure() from None

    def observe(self, input_tokens, output_tokens):
        if (type(input_tokens) is int and type(output_tokens) is int and
            0 <= input_tokens <= 266_240 and 0 <= output_tokens <= 8000 and
            input_tokens * .1 + output_tokens * .5 <= 50_000):
            return
        self.block()
        try:
            with self.exclusive():
                value = self.read(); value['blocked'] = True; self.write(value)
        except BudgetFailure:
            # The durable latch already blocks every instance and restart.
            pass
        raise BudgetFailure()
