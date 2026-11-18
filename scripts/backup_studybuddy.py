"""Bounded local prepared-export bundles; never discovers or imports live state.

See .docs/implementation-artifacts/backup-local-4-1.md for the source contract.
Only encrypted bytes and a DPAPI-protected per-bundle key are written by pack.
All public failures deliberately omit source names, content and exception details.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import sys
import tempfile
import time
import uuid

from cryptography.fernet import Fernet

MAX_PLAINTEXT = 64 * 1024 * 1024
MAX_HEADER = 512 * 1024
MAX_METADATA = 256 * 1024
MAX_FILES = 4096
MAX_PATH = 240
MAX_KEY_BLOB = 16 * 1024
MAX_ENCRYPTED = 4 * ((MAX_PLAINTEXT + 128 + 2) // 3) + MAX_KEY_BLOB + 16
RETENTION_SECONDS = 7 * 24 * 60 * 60
MAGIC = b"SBB1\r\n\x1a\n"
COVERAGE = "prepared export only"
OWN_NAME = re.compile(r"studybuddy-(\d{8}T\d{6}Z)-[0-9a-f]{32}\.sbb(?:\.partial)?\Z")
RESERVED = re.compile(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?\Z", re.I)


class BackupError(Exception):
    def __init__(self):
        super().__init__("backup-failed")


def require(condition):
    if not condition:
        raise BackupError()


class WindowsProtector:
    """DPAPI CurrentUser, no UI, no machine-wide flag or plaintext key file."""

    class Blob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]

    def __init__(self):
        require(os.name == "nt")
        self.crypt = ctypes.WinDLL("crypt32", use_last_error=True)
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        pointer = ctypes.POINTER(self.Blob)
        self.crypt.CryptProtectData.argtypes = [pointer, wintypes.LPCWSTR, pointer,
                                               ctypes.c_void_p, ctypes.c_void_p,
                                               wintypes.DWORD, pointer]
        self.crypt.CryptProtectData.restype = wintypes.BOOL
        self.crypt.CryptUnprotectData.argtypes = [pointer, ctypes.c_void_p, pointer,
                                                 ctypes.c_void_p, ctypes.c_void_p,
                                                 wintypes.DWORD, pointer]
        self.crypt.CryptUnprotectData.restype = wintypes.BOOL
        self.kernel.LocalFree.argtypes = [ctypes.c_void_p]
        self.kernel.LocalFree.restype = ctypes.c_void_p

    def _call(self, data, decrypt):
        require(0 < len(data) <= MAX_KEY_BLOB)
        buffer = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
        incoming = self.Blob(len(data), buffer)
        outgoing = self.Blob()
        function = self.crypt.CryptUnprotectData if decrypt else self.crypt.CryptProtectData
        try:
            require(bool(function(ctypes.byref(incoming), None, None, None, None,
                                  1, ctypes.byref(outgoing))))  # CRYPTPROTECT_UI_FORBIDDEN
            require(0 < outgoing.cbData <= MAX_KEY_BLOB)
            return ctypes.string_at(outgoing.pbData, outgoing.cbData)
        finally:
            if outgoing.pbData:
                self.kernel.LocalFree(ctypes.cast(outgoing.pbData, ctypes.c_void_p))

    def protect(self, data):
        return self._call(data, False)

    def unprotect(self, data):
        return self._call(data, True)


def _regular(info):
    return (stat.S_ISREG(info.st_mode) and info.st_nlink == 1
            and not getattr(info, "st_file_attributes", 0) & 0x400)


def _same_file(left, right):
    # Reading may update access time. Compare identity, content-change and safety
    # fields, rather than rejecting an otherwise unchanged file's access time.
    fields = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns")
    return (all(getattr(left, field) == getattr(right, field) for field in fields)
            and getattr(left, "st_file_attributes", 0) == getattr(right, "st_file_attributes", 0))


def _checked_path(path, *, directory=True):
    """Require an absolute lexical path with no symlink/reparse ancestor."""
    path = Path(path)
    require(path.is_absolute() and ".." not in path.parts)
    for current in [*reversed(path.parents), path]:
        info = current.lstat()
        require(not stat.S_ISLNK(info.st_mode)
                and not getattr(info, "st_file_attributes", 0) & 0x400)
        require(stat.S_ISDIR(info.st_mode) if current != path or directory else _regular(info))
    require(path.resolve() == path)
    return path


def _distinct(left, right):
    require(left != right and left not in right.parents and right not in left.parents)


def _name(value):
    require(isinstance(value, str) and 0 < len(value) <= MAX_PATH)
    require(not value.startswith("/") and "\\" not in value)
    for part in value.split("/"):
        require(part not in ("", ".", "..") and not part.endswith((" ", ".")))
        require(not any(ord(c) < 32 or c in '<>:"|?*' for c in part))
        require(not RESERVED.fullmatch(part))
    return value


def _names(values):
    keys = set()
    directories = set()
    for value in values:
        value = _name(value).casefold()
        require(value not in keys)
        keys.add(value)
        directories.update(_parents(value))
        require(len(directories) <= MAX_FILES)
    for value in keys:
        require(not any(parent in keys for parent in _parents(value)))


def _parents(value):
    parts = value.split("/")
    return ("/".join(parts[:i]) for i in range(1, len(parts)))


def _json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result)
            result[key] = value
        return result
    require(len(data) <= MAX_HEADER)
    return json.loads(data, object_pairs_hook=pairs)


def _encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _read(path, maximum):
    before = path.lstat()
    require(_regular(before) and before.st_size <= maximum)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        require(_regular(opened) and (before.st_dev, before.st_ino) == (opened.st_dev, opened.st_ino))
        data = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
    require(len(data) <= maximum and len(data) == before.st_size
            and (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns))
    require(_regular(after) and _same_file(before, after) and _same_file(path.lstat(), after))
    return data


def _source(root):
    files = {}
    total = 0
    count = 0
    directories = 0
    pending = [root]
    # Reject all links, including unlisted links and empty directory links.
    while pending:
        parent = _checked_path(pending.pop())
        with os.scandir(parent) as entries:
            for entry in entries:
                path = Path(entry.path)
                relative = _name(path.relative_to(root).as_posix())
                info = entry.stat(follow_symlinks=False)
                require(not stat.S_ISLNK(info.st_mode)
                        and not getattr(info, "st_file_attributes", 0) & 0x400)
                if stat.S_ISDIR(info.st_mode):
                    directories += 1
                    require(directories <= MAX_FILES)
                    pending.append(path)
                else:
                    count += 1
                    require(count <= MAX_FILES)
                    data = _read(path, MAX_PLAINTEXT - total)
                    total += len(data)
                    files[relative] = data
    _names(files)
    _contract(files)
    return files


def _contract(files):
    """Exact prepared inventory, deliberately no live-completeness assertion."""
    require("prepared.json" in files and "storage-inventory.json" in files)
    require(len(files["prepared.json"]) <= MAX_METADATA
            and len(files["storage-inventory.json"]) <= MAX_METADATA)
    prepared = _json(files["prepared.json"])
    require(isinstance(prepared, dict) and set(prepared) == {"version", "database", "state", "email"}
            and type(prepared["version"]) is int and prepared["version"] == 1)
    email = prepared["email"]
    require(isinstance(email, dict) and set(email) == {"enabled"} and type(email["enabled"]) is bool)
    database, states = prepared["database"], prepared["state"]
    require(isinstance(database, list) and 1 <= len(database) <= MAX_FILES)
    require(isinstance(states, list) and 2 <= len(states) <= MAX_FILES)
    declared = ["prepared.json", "storage-inventory.json"]
    for path in database:
        require(_name(path).startswith("database/") and path in files and bool(files[path]))
        declared.append(path)
    roles = []
    for item in states:
        require(isinstance(item, dict) and set(item) == {"role", "path"})
        require(item["role"] in {"budget", "signing_key", "email_journal", "blocked_marker", "email_sidecar"})
        path = _name(item["path"])
        require(path.startswith("state/") and path in files)
        roles.append(item["role"])
        declared.append(path)
    require(all(roles.count(role) == 1 for role in ("budget", "signing_key")))
    require(roles.count("email_journal") == (1 if email["enabled"] else 0))
    require(email["enabled"] or "email_sidecar" not in roles)
    inventory = _json(files["storage-inventory.json"])
    require(isinstance(inventory, dict) and set(inventory) == {"version", "objects"}
            and type(inventory["version"]) is int and inventory["version"] == 1)
    require(isinstance(inventory["objects"], list) and len(inventory["objects"]) <= MAX_FILES)
    for item in inventory["objects"]:
        require(isinstance(item, dict) and set(item) == {"path", "size", "sha256"})
        path = _name(item["path"])
        require(path.startswith("storage/") and path in files)
        require(type(item["size"]) is int and item["size"] == len(files[path]))
        require(item["sha256"] == hashlib.sha256(files[path]).hexdigest())
        declared.append(path)
    _names(declared)
    require(set(declared) == set(files))


def _plaintext(files, now):
    manifest = {"version": 1, "coverage": COVERAGE, "created_utc": int(now), "files": [
        {"path": path, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        for path, data in sorted(files.items())]}
    header = _encoded(manifest)
    require(len(header) <= MAX_HEADER)
    require(4 + len(header) + sum(map(len, files.values())) <= MAX_PLAINTEXT)
    return struct.pack(">I", len(header)) + header + b"".join(files[path] for path in sorted(files))


def _validate_plaintext(data):
    require(4 <= len(data) <= MAX_PLAINTEXT)
    length = struct.unpack(">I", data[:4])[0]
    require(0 < length <= MAX_HEADER and length + 4 <= len(data))
    manifest = _json(data[4:4 + length])
    require(isinstance(manifest, dict)
            and set(manifest) == {"version", "coverage", "created_utc", "files"}
            and type(manifest["version"]) is int and manifest["version"] == 1
            and manifest["coverage"] == COVERAGE and type(manifest["created_utc"]) is int)
    entries = manifest["files"]
    require(isinstance(entries, list) and 1 <= len(entries) <= MAX_FILES)
    files = {}
    offset = 4 + length
    paths = []
    for entry in entries:
        require(isinstance(entry, dict) and set(entry) == {"path", "size", "sha256"})
        path, size = _name(entry["path"]), entry["size"]
        require(type(size) is int and 0 <= size <= MAX_PLAINTEXT and offset + size <= len(data))
        content = data[offset:offset + size]
        require(entry["sha256"] == hashlib.sha256(content).hexdigest())
        files[path] = content
        paths.append(path)
        offset += size
    _names(paths)
    require(offset == len(data))
    _contract(files)
    return files


def _envelope(plaintext, protector):
    key = Fernet.generate_key()
    protected = protector.protect(key)
    require(0 < len(protected) <= MAX_KEY_BLOB)
    return MAGIC + struct.pack(">I", len(protected)) + protected + Fernet(key).encrypt(plaintext)


def _decrypt(data, protector):
    require(len(data) <= MAX_ENCRYPTED and data.startswith(MAGIC) and len(data) > 12)
    length = struct.unpack(">I", data[8:12])[0]
    require(0 < length <= MAX_KEY_BLOB and 12 + length < len(data))
    key = protector.unprotect(data[12:12 + length])
    return _validate_plaintext(Fernet(key).decrypt(data[12 + length:]))


def _publish(source, destination):
    # Windows rename is exclusive; POSIX rename would overwrite, so link exclusively.
    if os.name == "nt":
        os.rename(source, destination)
    else:
        os.link(source, destination, follow_symlinks=False)
        source.unlink()


def rotate(root, *, now=None):
    root = _checked_path(root)
    now = time.time() if now is None else now
    with os.scandir(root) as entries:
        for entry in entries:
            match = OWN_NAME.fullmatch(entry.name)
            if not match:
                continue
            try:
                created = datetime.strptime(match.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if created.strftime("%Y%m%dT%H%M%SZ") != match.group(1):
                continue
            path = Path(entry.path)
            before = path.lstat()
            if not _regular(before) or created.timestamp() > now - RETENTION_SECONDS:
                continue
            _checked_path(root)
            require(_same_file(path.lstat(), before))
            path.unlink()  # Never recurse or follow a directory/link.


def pack(source, root, *, protector=None, now=None):
    now = time.time() if now is None else now
    root = _checked_path(root)
    _distinct(Path(source), root)
    rotate(root, now=now)  # Expiry is independent of source/export success.
    source = _checked_path(source)
    _distinct(source, root)
    files = _source(source)
    protector = protector if protector is not None else WindowsProtector()
    encrypted = _envelope(_plaintext(files, now), protector)
    require(_decrypt(encrypted, protector) == files)
    stamp = datetime.fromtimestamp(now, timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = root / f"studybuddy-{stamp}-{uuid.uuid4().hex}.sbb"
    partial = Path(str(destination) + ".partial")
    owned = False
    try:
        _checked_path(root)
        with partial.open("xb") as stream:
            owned = True
            stream.write(encrypted)
            stream.flush()
            os.fsync(stream.fileno())
        require(_decrypt(_read(partial, MAX_ENCRYPTED), protector) == files)
        _checked_path(root)
        _publish(partial, destination)
        return destination
    finally:
        if owned and partial.exists():
            partial.unlink()


def restore(archive, destination, *, protector=None):
    archive = _checked_path(archive, directory=False)
    destination = Path(destination)
    require(destination.is_absolute() and ".." not in destination.parts)
    parent = _checked_path(destination.parent)
    _name(destination.name)
    require(not os.path.lexists(destination))
    _distinct(archive, destination)
    protector = protector if protector is not None else WindowsProtector()
    files = _decrypt(_read(archive, MAX_ENCRYPTED), protector)
    # Nothing is extracted until authentication, every hash and the contract pass.
    stage = Path(tempfile.mkdtemp(prefix=".studybuddy-restore-", dir=parent))
    created_files, created_dirs = [], []
    try:
        for name, content in sorted(files.items()):
            path = stage / name
            missing = []
            current = path.parent
            while current != stage and not current.exists():
                missing.append(current)
                current = current.parent
            for directory in reversed(missing):
                directory.mkdir()
                created_dirs.append(directory)
            with path.open("xb") as stream:
                created_files.append(path)
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
        require(_source(stage) == files)
        _checked_path(parent)
        require(not os.path.lexists(destination))
        # Windows rename refuses any existing destination. On other systems use
        # renameat2 NOREPLACE via no portable fallback: production is Windows only.
        require(os.name == "nt")
        os.rename(stage, destination)
        return destination
    finally:
        if stage.exists():
            for path in reversed(created_files):
                path.unlink()
            for path in reversed(created_dirs):
                path.rmdir()
            stage.rmdir()


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise BackupError()


def main(argv=None):
    try:
        parser = _Parser(description="Local prepared-export quarantine bundles only")
        sub = parser.add_subparsers(dest="command", required=True)
        packing = sub.add_parser("pack")
        packing.add_argument("--source", required=True)
        packing.add_argument("--root", default=r"C:\StudyBuddy-Backup")
        rotating = sub.add_parser("rotate")
        rotating.add_argument("--root", default=r"C:\StudyBuddy-Backup")
        restoring = sub.add_parser("restore")
        restoring.add_argument("--archive", required=True)
        restoring.add_argument("--destination", required=True)
        args = parser.parse_args(argv)
        if args.command == "pack":
            pack(args.source, args.root)
        elif args.command == "rotate":
            rotate(args.root)
        else:
            restore(args.archive, args.destination)
        print(f"studybuddy-backup: {args.command}-passed")
        return 0
    except (Exception, KeyboardInterrupt):
        print("studybuddy-backup: backup-failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
