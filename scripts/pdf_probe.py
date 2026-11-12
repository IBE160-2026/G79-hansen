"""Local PDF feasibility probe. No application routes or source logging.

Only Windows Job Object isolation is implemented and verified by this experiment.
The parent assigns a hard commit limit before giving the worker any PDF bytes.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import sysconfig
import time
from typing import BinaryIO

MAX_BYTES = 10 * 1024 * 1024
MAX_PAGES = 40
MAX_CHARACTERS = 30_000
MEMORY_BYTES = 512 * 1024 * 1024
TIMEOUT_SECONDS = 10.0
ERROR_MESSAGES = {
    "isolation_unavailable": "Windows Job Object memory isolation is unavailable; extraction was refused.",
    "byte_limit": "Input exceeds the 10 MiB limit.",
    "page_limit": "Input exceeds the 40 physical page limit.",
    "character_limit": "Extracted text exceeds 30,000 Unicode code points.",
    "no_readable_text": "No page contains usable extracted text.",
    "invalid_pdf": "Input is not a readable, valid PDF.",
    "encrypted_pdf": "Encrypted PDFs are unsupported.",
    "input_unavailable": "Input could not be read.",
    "timeout": "Worker exceeded its extraction deadline.",
    "memory_limit": "Worker could not allocate within its memory limit.",
    "worker_failed": "Worker failed; no source was accepted.",
    "dependency_unavailable": "Install the locked pdf-experiment dependency group.",
}


@dataclass(frozen=True)
class PageUnit:
    id: str
    kind: str
    location: int
    text: str


@dataclass(frozen=True)
class ProbeResult:
    status: str
    code: str
    units: tuple[PageUnit, ...] = ()
    total_pages: int | None = None
    unreadable_pages: tuple[int, ...] = ()
    character_count: int | None = None
    coverage_notice: str | None = None
    resources: dict = field(default_factory=dict)

    def public_summary(self) -> dict:
        """The CLI deliberately has no option to expose source text or paths."""
        return {
            "status": self.status,
            "code": self.code,
            "message": ERROR_MESSAGES.get(self.code),
            "totalPages": self.total_pages,
            "readablePages": [unit.location for unit in self.units],
            "unreadablePages": list(self.unreadable_pages),
            "characterCount": self.character_count,
            "coverageNotice": self.coverage_notice,
            "resources": self.resources,
        }


class IsolationUnavailable(Exception):
    pass


class _WindowsJob:
    """Small ctypes wrapper; no optional dependency or RSS polling fallback."""

    def __init__(self, *, _create=True):
        if sys.platform != "win32":
            raise IsolationUnavailable
        import ctypes as c
        from ctypes import wintypes as w

        class Basic(c.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", c.c_int64),
                ("PerJobUserTimeLimit", c.c_int64),
                ("LimitFlags", w.DWORD),
                ("MinimumWorkingSetSize", c.c_size_t),
                ("MaximumWorkingSetSize", c.c_size_t),
                ("ActiveProcessLimit", w.DWORD),
                ("Affinity", c.c_size_t),
                ("PriorityClass", w.DWORD),
                ("SchedulingClass", w.DWORD),
            ]

        class Extended(c.Structure):
            _fields_ = [
                ("BasicLimitInformation", Basic),
                ("IoInfo", c.c_uint64 * 6),
                ("ProcessMemoryLimit", c.c_size_t),
                ("JobMemoryLimit", c.c_size_t),
                ("PeakProcessMemoryUsed", c.c_size_t),
                ("PeakJobMemoryUsed", c.c_size_t),
            ]

        self.c, self.Extended = c, Extended
        self.api = c.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "CreateJobObjectW": ([c.c_void_p, w.LPCWSTR], w.HANDLE),
            "SetInformationJobObject": ([w.HANDLE, c.c_int, c.c_void_p, w.DWORD], w.BOOL),
            "QueryInformationJobObject": ([w.HANDLE, c.c_int, c.c_void_p, w.DWORD, c.c_void_p], w.BOOL),
            "AssignProcessToJobObject": ([w.HANDLE, w.HANDLE], w.BOOL),
            "OpenProcess": ([w.DWORD, w.BOOL, w.DWORD], w.HANDLE),
            "TerminateJobObject": ([w.HANDLE, w.UINT], w.BOOL),
            "CloseHandle": ([w.HANDLE], w.BOOL),
        }
        for name, (args, restype) in signatures.items():
            function = getattr(self.api, name)
            function.argtypes, function.restype = args, restype
        self.handle = None
        if not _create:
            return
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise IsolationUnavailable
        info = Extended()
        # Active process limit + process/job commit caps + kill on last handle close.
        info.BasicLimitInformation.LimitFlags = 0x8 | 0x100 | 0x200 | 0x2000
        info.BasicLimitInformation.ActiveProcessLimit = 1
        info.ProcessMemoryLimit = info.JobMemoryLimit = MEMORY_BYTES
        if not self.api.SetInformationJobObject(self.handle, 9, c.byref(info), c.sizeof(info)):
            self.close()
            raise IsolationUnavailable

    def current_process_is_capped(self) -> bool:
        info = self.Extended()
        if not self.api.QueryInformationJobObject(
            None, 9, self.c.byref(info), self.c.sizeof(info), None
        ):
            return False
        flags = 0x8 | 0x100 | 0x200 | 0x2000
        return (
            info.BasicLimitInformation.LimitFlags & flags == flags
            and info.BasicLimitInformation.ActiveProcessLimit == 1
            and 0 < info.ProcessMemoryLimit <= MEMORY_BYTES
            and 0 < info.JobMemoryLimit <= MEMORY_BYTES
        )
    def assign(self, pid: int) -> None:
        handle = self.api.OpenProcess(0x100 | 0x1, False, pid)
        if not handle:
            raise IsolationUnavailable
        try:
            if not self.api.AssignProcessToJobObject(self.handle, handle):
                raise IsolationUnavailable
        finally:
            self.api.CloseHandle(handle)

    def peak_bytes(self) -> int | None:
        info = self.Extended()
        if self.api.QueryInformationJobObject(
            self.handle, 9, self.c.byref(info), self.c.sizeof(info), None
        ):
            return info.PeakProcessMemoryUsed
        return None

    def terminate(self) -> None:
        if self.handle:
            self.api.TerminateJobObject(self.handle, 1)

    def close(self) -> None:
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


def _failure(code: str, resources: dict | None = None) -> ProbeResult:
    # Rejections never retain an accepted prefix, even if failure followed page 1.
    return ProbeResult("rejected", code, resources=resources or {})


def probe_stream(stream: BinaryIO) -> ProbeResult:
    """Read at most the ceiling plus one byte; never trust a caller's size hint."""
    data = bytearray()
    try:
        while len(data) <= MAX_BYTES:
            chunk = stream.read(MAX_BYTES + 1 - len(data))
            if not isinstance(chunk, bytes):
                return _failure("input_unavailable")
            if not chunk:
                break
            data.extend(chunk)
    except (OSError, ValueError):
        return _failure("input_unavailable")
    if len(data) > MAX_BYTES:
        return _failure("byte_limit")
    if not data or not data.startswith(b"%PDF-"):
        return _failure("invalid_pdf")
    return _run_isolated(bytes(data))


def probe_pdf(path: str | os.PathLike) -> ProbeResult:
    try:
        with open(path, "rb") as stream:
            return probe_stream(stream)
    except (OSError, ValueError):
        return _failure("input_unavailable")


def _run_isolated(data: bytes, *, _workload: str = "parse", _timeout: float = TIMEOUT_SECONDS) -> ProbeResult:
    """Internal containment harness; test workloads never invoke the PDF parser."""
    start = time.monotonic()
    process = None
    job = None
    code = "worker_failed"
    response = None
    observations = {
        "isolation": None,
        "memoryLimitBytes": MEMORY_BYTES,
        "timeoutSeconds": _timeout,
        "workerStarted": False,
        "workerReaped": False,
        "peakWorkerCommitBytes": None,
    }
    try:
        try:
            job = _WindowsJob()
        except OSError as error:
            raise IsolationUnavailable from error
        process = subprocess.Popen(
            # Windows venv python.exe is a redirector which creates another
            # process. Launch the actual interpreter to retain the one-process cap.
            [sys._base_executable, "-I", str(Path(__file__).resolve()), "--_worker", _workload,
             sysconfig.get_path("purelib")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        observations["workerStarted"] = True
        # The worker waits on stdin. No pypdf import, byte decoding or parsing yet.
        job.assign(process.pid)
        observations["isolation"] = "windows-job-object"
        remaining = _timeout - (time.monotonic() - start)
        if remaining <= 0:
            raise subprocess.TimeoutExpired(process.args, _timeout)
        output, _ = process.communicate(data, timeout=remaining)
        if process.returncode == 0 and len(output) <= 1_000_000:
            response = json.loads(output)
            code = response["code"]
    except IsolationUnavailable:
        code = "isolation_unavailable"
    except subprocess.TimeoutExpired:
        code = "timeout"
    except (OSError, ValueError, KeyError, TypeError):
        code = "worker_failed"
    finally:
        if job is not None:
            job.terminate()
        if process is not None:
            # Also covers assignment failures, before the process joined the job.
            if process.poll() is None:
                process.kill()
            process.wait()
            for pipe in (process.stdin, process.stdout):
                if pipe is not None:
                    pipe.close()
            observations["workerReaped"] = True
        if job is not None:
            observations["peakWorkerCommitBytes"] = job.peak_bytes()
            job.close()
        observations["elapsedSeconds"] = round(time.monotonic() - start, 4)
    if code != "ok" or response is None:
        return _failure(code, observations)
    try:
        return ProbeResult(
            "accepted", "ok", tuple(PageUnit(**unit) for unit in response["units"]),
            response["total_pages"], tuple(response["unreadable_pages"]),
            response["character_count"], response["coverage_notice"], observations,
        )
    except (TypeError, KeyError):
        return _failure("worker_failed", observations)


def _extract(data: bytes) -> dict:
    # Imports and all parser allocations take place inside the capped worker.
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data), strict=True)
    if reader.is_encrypted:
        return {"code": "encrypted_pdf"}
    total = len(reader.pages)
    if total > MAX_PAGES:
        return {"code": "page_limit"}
    units, unreadable = [], []
    count = 0
    for position, page in enumerate(reader.pages, 1):
        text = (page.extract_text() or "").replace("\r\n", "\n").replace("\r", "\n")
        count += len(text)
        if count > MAX_CHARACTERS:
            return {"code": "character_limit"}
        if text.strip():
            units.append(asdict(PageUnit(f"pdf-page-{position}", "page", position, text)))
        else:
            unreadable.append(position)
    if not units:
        return {"code": "no_readable_text"}
    notice = "Only extracted text is covered; images are not interpreted."
    if unreadable:
        notice = (
            "Partial coverage: physical pages " + ", ".join(map(str, unreadable))
            + " have no usable extracted text. Only extracted text is covered; images are not interpreted."
        )
    return {
        "code": "ok", "units": units, "total_pages": total,
        "unreadable_pages": unreadable, "character_count": count,
        "coverage_notice": notice,
    }


def _worker(workload: str, package_path: str) -> int:
    # Parent-controlled stdin is the gate: assignment must succeed before writing.
    data = sys.stdin.buffer.read(MAX_BYTES + 1)
    if not data:
        return 1
    try:
        capped = _WindowsJob(_create=False).current_process_is_capped()
    except (IsolationUnavailable, OSError):
        capped = False
    if not capped:
        sys.stdout.write(json.dumps({"code": "isolation_unavailable"}))
        return 0
    # -I ignores ambient PYTHONPATH/user packages; use this checkout's locked venv.
    sys.path.insert(0, package_path)
    import contextlib
    import logging

    logging.disable(logging.CRITICAL)
    try:
        with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            if workload == "timeout":
                time.sleep(60)
                return 1
            if workload == "memory":
                # A single committed allocation greater than the configured cap.
                allocation = bytearray(MEMORY_BYTES + 1024 * 1024)
                return int(bool(allocation))
            if workload == "crash":
                os._exit(17)
            if workload != "parse":
                return 1
            result = _extract(data)
    except MemoryError:
        result = {"code": "memory_limit"}
    except ImportError:
        result = {"code": "dependency_unavailable"}
    except Exception:
        result = {"code": "invalid_pdf"}
    sys.stdout.write(json.dumps(result, ensure_ascii=True))
    return 0


def main() -> int:
    if len(sys.argv) == 4 and sys.argv[1] == "--_worker":
        return _worker(sys.argv[2], sys.argv[3])
    parser = argparse.ArgumentParser(
        description="Probe a local PDF in a capped Windows worker; output contains no source text or filename."
    )
    parser.add_argument("pdf", help="local PDF path (not included in JSON output)")
    args = parser.parse_args()
    result = probe_pdf(args.pdf)
    print(json.dumps(result.public_summary(), ensure_ascii=True))
    return 0 if result.status == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
