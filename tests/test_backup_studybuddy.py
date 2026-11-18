"""Synthetic local component checks: no provider, live state or real backup root."""

import hashlib
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import stat
import struct
from types import SimpleNamespace

from cryptography.fernet import Fernet
import pytest

from scripts import backup_studybuddy as backup


class TestProtector:
    __test__ = False

    def __init__(self):
        self.wrapper = Fernet(Fernet.generate_key())

    def protect(self, data):
        return self.wrapper.encrypt(data)

    def unprotect(self, data):
        return self.wrapper.decrypt(data)


def write_json(path, value):
    path.write_bytes(json.dumps(value).encode())


@pytest.fixture
def prepared(tmp_path):
    source, root = tmp_path / "prepared", tmp_path / "encrypted"
    source.mkdir()
    root.mkdir()
    files = {"database/export.sql": b"-- synthetic database\n",
             "storage/private/example.bin": b"\x00synthetic object\xff",
             "state/budget.json": b'{"spent":5,"blocked":true}',
             "state/signing.key": b"synthetic signing copy",
             "state/email.sqlite3": b"synthetic journal copy",
             "state/budget.blocked": b""}
    for name, data in files.items():
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    write_json(source / "prepared.json", {
        "version": 1, "database": ["database/export.sql"], "email": {"enabled": True}, "state": [
            {"role": role, "path": path} for role, path in [
                ("budget", "state/budget.json"), ("signing_key", "state/signing.key"),
                ("email_journal", "state/email.sqlite3"), ("blocked_marker", "state/budget.blocked")]]})
    data = files["storage/private/example.bin"]
    write_json(source / "storage-inventory.json", {"version": 1, "objects": [
        {"path": "storage/private/example.bin", "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}]})
    return source, root


def snapshots(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_actual_windows_dpapi_fernet_roundtrip(prepared, tmp_path):
    if os.name != "nt":
        pytest.skip("DPAPI requires Windows; never skipped on Windows")
    source, root = prepared
    expected = snapshots(source)
    protector = backup.WindowsProtector()
    archive = backup.pack(source, root, protector=protector)
    assert list(root.iterdir()) == [archive]
    assert archive.read_bytes().startswith(backup.MAGIC)
    assert b"synthetic" not in archive.read_bytes()
    assert b"private/example" not in archive.read_bytes()
    destination = tmp_path / "quarantine"
    backup.restore(archive, destination, protector=backup.WindowsProtector())
    assert snapshots(destination) == expected
    assert snapshots(source) == expected
    assert not list(tmp_path.glob(".studybuddy-restore-*"))
    assert len(backup._decrypt(archive.read_bytes(), protector)) == len(expected)


@pytest.mark.parametrize("change", ["missing-db", "missing-state", "missing-inventory", "extra-object", "changed-object", "bad-size", "bad-hash", "missing-role", "duplicate-state", "unknown-state"])
def test_incomplete_or_changed_source_never_publishes(prepared, change):
    source, root = prepared
    if change.startswith("missing-") and change not in {"missing-role"}:
        (source / {"missing-db": "database/export.sql", "missing-state": "state/budget.json",
                   "missing-inventory": "storage-inventory.json"}[change]).unlink()
    elif change == "extra-object":
        (source / "storage/private/unlisted").write_bytes(b"undeclared")
    elif change == "changed-object":
        (source / "storage/private/example.bin").write_bytes(b"changed")
    elif change in {"bad-size", "bad-hash"}:
        path = source / "storage-inventory.json"
        value = json.loads(path.read_bytes())
        value["objects"][0]["size" if change == "bad-size" else "sha256"] = 3
        write_json(path, value)
    else:
        path = source / "prepared.json"
        value = json.loads(path.read_bytes())
        if change == "missing-role":
            value["state"] = value["state"][1:]
        elif change == "duplicate-state":
            value["state"].append(value["state"][0])
        else:
            value["state"][0]["role"] = "unknown"
        write_json(path, value)
    with pytest.raises(Exception):
        backup.pack(source, root, protector=TestProtector())
    assert not list(root.iterdir())


@pytest.mark.parametrize("mutation", ["truncate", "ciphertext", "key-blob", "wrong-key", "oversized-header"])
def test_tamper_or_wrong_key_has_no_extraction(prepared, tmp_path, mutation):
    source, root = prepared
    protector = TestProtector()
    archive = backup.pack(source, root, protector=protector)
    data = bytearray(archive.read_bytes())
    if mutation == "truncate":
        data = data[:-16]
    elif mutation == "ciphertext":
        data[-12] ^= 1
    elif mutation == "key-blob":
        data[15] ^= 1
    elif mutation == "oversized-header":
        data[8:12] = struct.pack(">I", backup.MAX_KEY_BLOB + 1)
    else:
        protector = TestProtector()
    archive.write_bytes(data)
    destination = tmp_path / "quarantine"
    with pytest.raises(Exception):
        backup.restore(archive, destination, protector=protector)
    assert not destination.exists()
    assert not list(tmp_path.glob(".studybuddy-restore-*"))


@pytest.mark.parametrize("unsafe", ["../outside", "/absolute", "C:/absolute", "state\\alias", "state/NUL", "state/x.", "state//x", "state/./x", "state/a:b", "state/CON.txt"])
def test_unsafe_prepared_names(prepared, unsafe):
    source, root = prepared
    path = source / "prepared.json"
    value = json.loads(path.read_bytes())
    value["state"][0]["path"] = unsafe
    write_json(path, value)
    with pytest.raises(backup.BackupError):
        backup.pack(source, root, protector=TestProtector())
    assert not list(root.iterdir())


@pytest.mark.parametrize("mutation", ["traversal", "duplicate", "case-alias", "file-directory", "hash", "missing-entry", "trailing", "header-limit", "count-limit", "symlink-field"])
def test_authenticated_malicious_manifest_rejected(prepared, tmp_path, monkeypatch, mutation):
    source, root = prepared
    data = backup._plaintext(backup._source(source), 1000)
    length = struct.unpack(">I", data[:4])[0]
    header = json.loads(data[4:4 + length])
    body = data[4 + length:]
    if mutation == "traversal":
        header["files"][0]["path"] = "../outside"
    elif mutation in {"duplicate", "case-alias", "file-directory"}:
        header["files"][1]["path"] = header["files"][0]["path"]
        if mutation == "case-alias":
            header["files"][1]["path"] = header["files"][1]["path"].upper()
        elif mutation == "file-directory":
            header["files"][1]["path"] += "/child"
    elif mutation == "hash":
        header["files"][0]["sha256"] = "0" * 64
    elif mutation == "missing-entry":
        header["files"].pop()
    elif mutation == "trailing":
        body += b"unexpected"
    elif mutation == "header-limit":
        monkeypatch.setattr(backup, "MAX_HEADER", 10)
    elif mutation == "count-limit":
        monkeypatch.setattr(backup, "MAX_FILES", 1)
    else:
        header["files"][0]["symlink"] = "../outside"
    header = backup._encoded(header)
    protector = TestProtector()
    archive = root / "malicious.sbb"
    archive.write_bytes(backup._envelope(struct.pack(">I", len(header)) + header + body, protector))
    destination = tmp_path / "quarantine"
    with pytest.raises(Exception):
        backup.restore(archive, destination, protector=protector)
    assert not destination.exists()
    assert not (tmp_path / "outside").exists()
    assert not list(tmp_path.glob(".studybuddy-restore-*"))


def test_duplicate_json_keys_reject(prepared):
    source, root = prepared
    (source / "prepared.json").write_bytes(b'{"version":1,"version":1}')
    with pytest.raises(backup.BackupError):
        backup.pack(source, root, protector=TestProtector())
    assert not list(root.iterdir())


def test_restore_parent_directory_limit_rejects_before_staging(prepared, tmp_path, monkeypatch):
    source, root = prepared
    files = backup._source(source)
    inventory = json.loads(files["storage-inventory.json"])
    for number in range(1000):
        path = f"storage/object-{number}/a/b/c/d/e/empty"
        files[path] = b""
        inventory["objects"].append({"path": path, "size": 0,
                                     "sha256": hashlib.sha256(b"").hexdigest()})
    files["storage-inventory.json"] = backup._encoded(inventory)
    assert len(files) < backup.MAX_FILES
    assert len(files["storage-inventory.json"]) < backup.MAX_METADATA
    protector = TestProtector()
    archive = root / "too-many-directories.sbb"
    archive.write_bytes(backup._envelope(backup._plaintext(files, 1000), protector))

    def unexpected_staging(*args, **kwargs):
        pytest.fail("directory limit must reject before creating restore staging")

    monkeypatch.setattr(backup.tempfile, "mkdtemp", unexpected_staging)
    destination = tmp_path / "quarantine"
    with pytest.raises(backup.BackupError):
        backup.restore(archive, destination, protector=protector)
    assert not destination.exists()
    assert not list(tmp_path.glob(".studybuddy-restore-*"))


def test_explicit_email_disabled_roundtrip(prepared, tmp_path):
    source, root = prepared
    path = source / "prepared.json"
    value = json.loads(path.read_bytes())
    value["email"] = {"enabled": False}
    value["state"] = [item for item in value["state"] if item["role"] != "email_journal"]
    (source / "state/email.sqlite3").unlink()
    write_json(path, value)
    protector = TestProtector()
    archive = backup.pack(source, root, protector=protector)
    destination = tmp_path / "quarantine"
    backup.restore(archive, destination, protector=protector)
    assert snapshots(destination) == snapshots(source)
    assert not (destination / "state/email.sqlite3").exists()


@pytest.mark.parametrize("email", [None, {}, {"enabled": "false"}, {"enabled": False}])
def test_missing_ambiguous_or_disabled_email_with_journal_rejects(prepared, email):
    source, root = prepared
    path = source / "prepared.json"
    value = json.loads(path.read_bytes())
    if email is None:
        del value["email"]
    else:
        value["email"] = email
    write_json(path, value)
    with pytest.raises(backup.BackupError):
        backup.pack(source, root, protector=TestProtector())
    assert not list(root.iterdir())


def test_exact_plaintext_limit_and_reject_excess(prepared, monkeypatch):
    source, root = prepared
    files = backup._source(source)
    size = len(backup._plaintext(files, 1000))
    monkeypatch.setattr(backup, "MAX_PLAINTEXT", size)
    archive = backup.pack(source, root, protector=TestProtector(), now=1000)
    assert archive.exists()
    monkeypatch.setattr(backup, "MAX_PLAINTEXT", size - 1)
    with pytest.raises(backup.BackupError):
        backup.pack(source, root, protector=TestProtector(), now=1000)
    assert list(root.iterdir()) == [archive]


@pytest.mark.parametrize("limit", ["MAX_METADATA", "MAX_HEADER", "MAX_FILES", "MAX_PATH", "MAX_ENCRYPTED"])
def test_bounded_inputs(prepared, monkeypatch, limit):
    source, root = prepared
    monkeypatch.setattr(backup, limit, 1)
    with pytest.raises(Exception):
        backup.pack(source, root, protector=TestProtector())
    assert not list(root.iterdir())


def test_restore_existing_target_and_alias_roots_preserve_state(prepared, tmp_path):
    source, root = prepared
    expected = snapshots(source)
    protector = TestProtector()
    archive = backup.pack(source, root, protector=protector)
    with pytest.raises(backup.BackupError):
        backup.restore(archive, source, protector=protector)
    for output in (source, source / "state", tmp_path):
        with pytest.raises(backup.BackupError):
            backup.pack(source, output, protector=protector)
    assert snapshots(source) == expected
    assert archive.exists()


def test_atomic_pack_failure_cleans_only_owned_partial(prepared, monkeypatch):
    source, root = prepared
    unrelated = root / "unrelated.partial"
    unrelated.write_bytes(b"keep")
    monkeypatch.setattr(backup, "_publish", lambda *args: (_ for _ in ()).throw(OSError("sensitive detail")))
    with pytest.raises(OSError):
        backup.pack(source, root, protector=TestProtector())
    assert list(root.iterdir()) == [unrelated]


@pytest.mark.parametrize("suffix", [".sbb", ".sbb.partial"])
def test_exclusive_output_does_not_replace_collision(prepared, monkeypatch, suffix):
    source, root = prepared
    now = 1_800_000_000
    existing = own(root, 42, suffix, when=now)
    existing.write_bytes(b"existing encrypted bytes")
    monkeypatch.setattr(backup.uuid, "uuid4", lambda: SimpleNamespace(hex=f"{42:032x}"))
    with pytest.raises(FileExistsError):
        backup.pack(source, root, protector=TestProtector(), now=now)
    assert existing.read_bytes() == b"existing encrypted bytes"
    assert list(root.iterdir()) == [existing]


def test_interrupted_write_cleanup(prepared, monkeypatch):
    source, root = prepared
    monkeypatch.setattr(backup.os, "fsync", lambda *args: (_ for _ in ()).throw(OSError("interrupted")))
    with pytest.raises(OSError):
        backup.pack(source, root, protector=TestProtector())
    assert not list(root.iterdir())


def test_restore_staging_failure_and_publication_collision(prepared, tmp_path, monkeypatch):
    source, root = prepared
    protector = TestProtector()
    archive = backup.pack(source, root, protector=protector)
    destination = tmp_path / "quarantine"
    original = backup.os.fsync
    monkeypatch.setattr(backup.os, "fsync", lambda *args: (_ for _ in ()).throw(OSError("write")))
    with pytest.raises(OSError):
        backup.restore(archive, destination, protector=protector)
    assert not destination.exists()
    assert not list(tmp_path.glob(".studybuddy-restore-*"))
    monkeypatch.setattr(backup.os, "fsync", original)
    original_rename = backup.os.rename

    def collision(stage, target):
        target.mkdir()
        (target / "keep").write_bytes(b"existing")
        original_rename(stage, target)

    monkeypatch.setattr(backup.os, "rename", collision)
    with pytest.raises(OSError):
        backup.restore(archive, destination, protector=protector)
    assert snapshots(destination) == {"keep": b"existing"}
    assert not list(tmp_path.glob(".studybuddy-restore-*"))


def own(root, number, suffix=".sbb", when=1_767_225_600):
    stamp = datetime.fromtimestamp(when, timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return root / f"studybuddy-{stamp}-{number:032x}{suffix}"


def test_seven_day_rotation_and_failed_pack(prepared):
    source, root = prepared
    now = 1_800_000_000
    expired = own(root, 1, when=now - backup.RETENTION_SECONDS - 1)
    boundary = own(root, 2, when=now - backup.RETENTION_SECONDS)
    young = own(root, 3, when=now - backup.RETENTION_SECONDS + 1)
    partial = own(root, 4, ".sbb.partial", when=now - backup.RETENTION_SECONDS)
    unrelated = root / "unrelated.sbb"
    directory = own(root, 5)
    directory.mkdir()
    (directory / "keep").write_bytes(b"do not recurse")
    for path, age in [(expired, backup.RETENTION_SECONDS + 1),
                      (boundary, backup.RETENTION_SECONDS), (young, backup.RETENTION_SECONDS - 1),
                      (partial, backup.RETENTION_SECONDS), (unrelated, backup.RETENTION_SECONDS + 1)]:
        path.write_bytes(b"opaque")
        os.utime(path, (now - age, now - age))
    with pytest.raises(Exception):
        backup.pack(source / "absent", root, protector=TestProtector(), now=now)
    assert not expired.exists() and not boundary.exists() and not partial.exists()
    assert young.exists() and unrelated.exists() and (directory / "keep").exists()


def test_rotation_filename_clock_ignores_mtime_and_preserves_invalid_dates(prepared):
    _, root = prepared
    now = 1_800_000_000
    old = own(root, 1, when=now - backup.RETENTION_SECONDS)
    young = own(root, 2, when=now - backup.RETENTION_SECONDS + 1)
    invalid = root / ("studybuddy-20261399T999999Z-" + "a" * 32 + ".sbb")
    for path in (old, young, invalid):
        path.write_bytes(b"opaque")
    os.utime(old, (now, now))
    os.utime(young, (0, 0))
    os.utime(invalid, (0, 0))
    backup.rotate(root, now=now)
    assert not old.exists() and young.exists() and invalid.exists()


def test_reparse_and_hardlinks_are_not_regular():
    base = {"st_mode": stat.S_IFREG, "st_nlink": 1, "st_file_attributes": 0}
    assert backup._regular(SimpleNamespace(**base))
    assert not backup._regular(SimpleNamespace(**(base | {"st_file_attributes": 0x400})))
    assert not backup._regular(SimpleNamespace(**(base | {"st_nlink": 2})))


def test_read_access_timestamp_is_not_a_content_change():
    fields = {"st_dev": 1, "st_ino": 2, "st_mode": stat.S_IFREG, "st_nlink": 1,
              "st_size": 10, "st_mtime_ns": 1000, "st_file_attributes": 0,
              "st_atime_ns": 1000}
    assert backup._same_file(SimpleNamespace(**fields), SimpleNamespace(**(fields | {"st_atime_ns": 2000})))
    assert not backup._same_file(SimpleNamespace(**fields), SimpleNamespace(**(fields | {"st_mtime_ns": 2000})))


def test_links_and_junction_roots_reject(prepared, tmp_path):
    source, root = prepared
    external = tmp_path / "outside"
    external.mkdir()
    keeper = external / "keep"
    keeper.write_bytes(b"unchanged")
    junction = root / "junction"
    if os.name == "nt":
        import _winapi
        _winapi.CreateJunction(str(external), str(junction))
    else:
        junction.symlink_to(external, target_is_directory=True)
    try:
        with pytest.raises(backup.BackupError):
            backup.pack(source, junction, protector=TestProtector())
        with pytest.raises(backup.BackupError):
            backup.restore(keeper, junction / "restore", protector=TestProtector())
        # A recognized name that is a directory junction must never be traversed/deleted.
        link = own(root, 9)
        junction.rename(link)
        junction = link
        backup.rotate(root, now=2_000_000_000)
        assert junction.exists() and keeper.read_bytes() == b"unchanged"
        junction.rename(source / "storage" / "linked-directory")
        junction = source / "storage" / "linked-directory"
        with pytest.raises(backup.BackupError):
            backup.pack(source, root, protector=TestProtector())
        assert keeper.read_bytes() == b"unchanged"
    finally:
        if os.name == "nt":
            junction.rmdir()
        else:
            junction.unlink()


def test_hardlinked_source_and_rotation_preserved(prepared, tmp_path):
    source, root = prepared
    external = tmp_path / "external"
    external.write_bytes(b"keep")
    link = own(root, 10)
    os.link(external, link)
    backup.rotate(root, now=2_000_000_000)
    assert link.read_bytes() == b"keep"
    os.link(external, source / "state" / "alias")
    with pytest.raises(backup.BackupError):
        backup.pack(source, root, protector=TestProtector())


def test_cli_errors_are_content_free(capsys, prepared):
    _, root = prepared
    assert backup.main(["pack", "--source", "private-address@example.invalid", "--root", str(root)]) == 1
    assert capsys.readouterr().out == "studybuddy-backup: backup-failed\n"
    assert backup.main(["restore", "--private-secret"]) == 1
    output = capsys.readouterr()
    assert output.out == "studybuddy-backup: backup-failed\n" and output.err == ""
