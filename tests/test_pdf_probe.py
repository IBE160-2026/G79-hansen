import io
import json
import subprocess
import sys

import pytest

pytest.importorskip("pypdf", reason="Install the optional locked pdf-experiment dependency group")

from app.contracts.learning import Source
from pdf_fixtures import at_size, make_pdf
from scripts import pdf_probe as probe

WINDOWS = pytest.mark.skipif(sys.platform != "win32", reason="Only Windows Job Object isolation is implemented")


def extract(data):
    return probe.probe_stream(io.BytesIO(data))


def assert_rejected(result, code):
    assert result.status == "rejected"
    assert result.code == code
    assert result.units == ()
    assert result.total_pages is None
    assert result.character_count is None
    assert result.coverage_notice is None


def record_observation(request, data, result):
    request.node.user_properties.append((
        "pdf_observation", json.dumps({"inputBytes": len(data), **result.public_summary()})
    ))


@WINDOWS
def test_physical_pages_gaps_real_image_and_contract(request):
    data = make_pdf(["First", None, "Third", None], image_pages=(4,))
    assert b"/Subtype /Image" in data
    assert data == make_pdf(["First", None, "Third", None], image_pages=(4,))
    first, second = extract(data), extract(data)
    record_observation(request, data, first)
    assert first.code == "ok"
    assert first.total_pages == 4
    assert first.unreadable_pages == (2, 4)
    assert [unit.location for unit in first.units] == [1, 3]
    assert [unit.id for unit in first.units] == ["pdf-page-1", "pdf-page-3"]
    assert first.units == second.units
    assert first.character_count == len("FirstThird")
    assert "2, 4" in first.coverage_notice
    assert "Only extracted text" in first.coverage_notice
    source = Source.model_validate({
        "id": "synthetic", "title": "Synthetic",
        "units": [vars(unit) for unit in first.units],
    })
    assert source.units[1].location == 3
    assert first.resources["workerReaped"] is True
    assert 0 < first.resources["peakWorkerCommitBytes"] <= probe.MEMORY_BYTES


@WINDOWS
def test_mixed_text_image_page_retains_extracted_text_limitation():
    data = make_pdf(["Readable text"], image_pages=(1,))
    assert b"/Subtype /Image" in data
    result = extract(data)
    assert result.code == "ok"
    assert result.unreadable_pages == ()
    assert result.units[0].text == "Readable text\n"
    assert result.public_summary()["coverageNotice"] == (
        "Only extracted text is covered; images are not interpreted."
    )


@WINDOWS
@pytest.mark.parametrize("pages,image_pages", [([None], ()), ([None, None], (1, 2)), ([" \t\n"], ())])
def test_no_usable_text(pages, image_pages):
    assert_rejected(extract(make_pdf(pages, image_pages=image_pages)), "no_readable_text")


@WINDOWS
@pytest.mark.parametrize("pages,code", [(40, "ok"), (41, "page_limit")])
def test_physical_page_boundary_includes_blank_pages(pages, code, request):
    data = make_pdf(["Text"] + [None] * (pages - 1))
    result = extract(data)
    assert result.code == code
    if code == "ok":
        record_observation(request, data, result)
        assert result.total_pages == 40
        assert result.unreadable_pages == tuple(range(2, 41))
    else:
        assert_rejected(result, code)


@WINDOWS
@pytest.mark.parametrize("count,code", [(30_000, "ok"), (30_001, "character_limit")])
def test_unicode_character_boundary_across_pages(count, code, request):
    # U+1F600 occupies four UTF-8 bytes and two UTF-16 code units, one Python code point.
    first, last = "\U0001f600" * 15_000, "\u00e9" * (count - 15_000)
    data = make_pdf([first, None, last])
    result = extract(data)
    assert result.code == code
    if code == "ok":
        record_observation(request, data, result)
        assert result.character_count == count
        assert [u.text for u in result.units] == [first, last]
        assert sum(len(u.text.encode("utf-8")) for u in result.units) > count
    else:
        assert_rejected(result, code)


@WINDOWS
def test_normalizes_line_endings_before_counting_without_labels_or_separators():
    result = extract(make_pdf(["A\r\nB\rC\nD", "E"]))
    assert result.code == "ok"
    assert [unit.text for unit in result.units] == ["A\nB\nC\nD", "E"]
    assert result.character_count == 8
    # The raw string exceeds 30,000, but canonical normalized text is exactly at the limit.
    boundary = extract(make_pdf(["X\r\n" * 10_000, "Y" * 10_000]))
    assert boundary.code == "ok"
    assert boundary.character_count == 30_000


@WINDOWS
def test_exact_byte_boundary_proceeds_to_validation(request):
    data = at_size(make_pdf(["Exact boundary"]), probe.MAX_BYTES)
    result = extract(data)
    record_observation(request, data, result)
    assert result.code == "ok"
    assert result.resources["workerStarted"] is True
    # Being exactly at the byte boundary does not make malformed bytes valid.
    assert_rejected(extract(at_size(b"%PDF-invalid", probe.MAX_BYTES)), "invalid_pdf")


def test_excess_bytes_are_bounded_and_never_start_worker(monkeypatch):
    class ObservedStream(io.BytesIO):
        def read(self, size=-1):
            assert size == probe.MAX_BYTES + 1
            return super().read(size)

    def forbidden(*args, **kwargs):
        pytest.fail("Excess input reached the worker")

    monkeypatch.setattr(probe, "_run_isolated", forbidden)
    result = probe.probe_stream(ObservedStream(b"%PDF-" + b"X" * (probe.MAX_BYTES + 100)))
    assert_rejected(result, "byte_limit")


def test_short_reads_do_not_accept_a_valid_prefix_before_excess_bytes(monkeypatch):
    prefix = make_pdf(["Valid prefix"])

    class ShortReadStream(io.BytesIO):
        def read(self, size=-1):
            return super().read(min(size, len(prefix)))

    monkeypatch.setattr(probe, "_run_isolated", lambda *_: pytest.fail("Excess short-read input reached parser"))
    result = probe.probe_stream(ShortReadStream(at_size(prefix, probe.MAX_BYTES + 1)))
    assert_rejected(result, "byte_limit")


@WINDOWS
def test_short_reads_collect_the_whole_valid_pdf():
    class ShortReadStream(io.BytesIO):
        def read(self, size=-1):
            return super().read(min(size, 17))

    result = probe.probe_stream(ShortReadStream(make_pdf(["Complete text"])))
    assert result.code == "ok"
    assert result.units[0].text == "Complete text"


@pytest.mark.parametrize("data", [b"", b"Not a PDF PRIVATE_SENTINEL", b"{broken}"])
def test_non_pdf_input_never_starts_worker(data, monkeypatch):
    monkeypatch.setattr(probe, "_run_isolated", lambda *_: pytest.fail("Invalid header reached parser"))
    assert_rejected(extract(data), "invalid_pdf")


@WINDOWS
@pytest.mark.parametrize("data", [b"%PDF-1.7\nPRIVATE_SENTINEL", b"%PDF-1.7\n%%EOF"])
def test_malformed_pdf_is_content_free(data, capfd):
    result = extract(data)
    assert_rejected(result, "invalid_pdf")
    assert "PRIVATE_SENTINEL" not in json.dumps(result.public_summary())
    assert capfd.readouterr() == ("", "")


@WINDOWS
def test_page_extraction_failure_discards_readable_prefix():
    from pypdf import PdfReader, PdfWriter
    from pypdf.errors import PdfStreamError
    from pypdf.generic import DecodedStreamObject, NameObject

    writer = PdfWriter()
    writer.append_pages_from_reader(PdfReader(io.BytesIO(make_pdf(["Readable first page", "Second page"]))))
    broken = DecodedStreamObject()
    # A literal string missing its closing ')' raises in the locked content parser.
    broken.set_data(b"BT /F1 12 Tf (unterminated Tj ET")
    writer.pages[1][NameObject("/Contents")] = writer._add_object(broken)
    output = io.BytesIO()
    writer.write(output)
    data = output.getvalue()
    reader = PdfReader(io.BytesIO(data), strict=True)
    assert len(reader.pages) == 2
    assert reader.pages[0].extract_text() == "Readable first page"
    with pytest.raises(PdfStreamError):
        reader.pages[1].extract_text()

    result = probe.probe_stream(io.BytesIO(data))
    assert_rejected(result, "invalid_pdf")
    assert result.unreadable_pages == ()
    assert result.resources["workerStarted"] is True
    assert result.resources["workerReaped"] is True


@WINDOWS
def test_encrypted_pdf_is_explicitly_rejected_without_password_workflow():
    data = make_pdf(["PRIVATE_SENTINEL"], encrypted=True)
    assert data == make_pdf(["PRIVATE_SENTINEL"], encrypted=True)
    assert_rejected(extract(data), "encrypted_pdf")


@WINDOWS
@pytest.mark.parametrize("workload,code,timeout", [
    ("timeout", "timeout", 10), ("memory", "memory_limit", 10), ("crash", "worker_failed", 10),
])
def test_real_containment_workloads_cleanup_and_subsequent_success(workload, code, timeout, request):
    # Controlled workloads establish containment, independently of parser performance.
    result = probe._run_isolated(b"gate", _workload=workload, _timeout=timeout)
    request.node.user_properties.append(("containment_result", json.dumps(result.public_summary())))
    assert_rejected(result, code)
    assert result.resources["workerStarted"] is True
    assert result.resources["workerReaped"] is True
    assert result.resources["elapsedSeconds"] < timeout + 3
    assert 0 < result.resources["peakWorkerCommitBytes"] <= probe.MEMORY_BYTES
    following = extract(make_pdf(["Still works"]))
    assert following.code == "ok"
    assert following.resources["workerReaped"] is True


@WINDOWS
def test_compressed_stream_parser_observation_is_contained(request):
    # This is a real pypdf observation, not proof that all hostile PDFs behave alike.
    data = make_pdf(["End"], stress_operations=1_500_000)
    assert len(data) < 10_000
    result = extract(data)
    request.node.user_properties.append(("compressed_stream_result", json.dumps(result.public_summary())))
    assert result.code in {"ok", "timeout", "memory_limit", "worker_failed", "invalid_pdf"}
    assert result.resources["workerReaped"] is True
    assert result.resources["elapsedSeconds"] < probe.TIMEOUT_SECONDS + 3
    assert 0 < result.resources["peakWorkerCommitBytes"] <= probe.MEMORY_BYTES
    if result.code == "ok":
        assert result.character_count == 3
        assert result.units[0].text == "End"
    else:
        assert result.units == ()
    assert extract(make_pdf(["After stress"])).code == "ok"


@pytest.mark.parametrize("error_type", [probe.IsolationUnavailable, OSError])
def test_isolation_setup_failure_is_closed(monkeypatch, error_type):
    def unavailable():
        raise error_type

    monkeypatch.setattr(probe, "_WindowsJob", unavailable)
    monkeypatch.setattr(probe.subprocess, "Popen", lambda *_a, **_k: pytest.fail("Worker started without cap"))
    result = extract(make_pdf(["PRIVATE_SENTINEL"]))
    assert_rejected(result, "isolation_unavailable")
    assert result.resources["workerStarted"] is False


@WINDOWS
def test_process_start_oserror_remains_worker_failure(monkeypatch):
    def unavailable(*args, **kwargs):
        raise OSError

    monkeypatch.setattr(probe.subprocess, "Popen", unavailable)
    result = extract(make_pdf(["Text"]))
    assert_rejected(result, "worker_failed")
    assert result.resources["workerStarted"] is False


@WINDOWS
def test_job_assignment_failure_reaps_gated_worker(monkeypatch):
    def unavailable(*args):
        raise probe.IsolationUnavailable

    monkeypatch.setattr(probe._WindowsJob, "assign", unavailable)
    result = extract(make_pdf(["PRIVATE_SENTINEL"]))
    assert_rejected(result, "isolation_unavailable")
    assert result.resources["workerStarted"] is True
    assert result.resources["workerReaped"] is True


@pytest.mark.skipif(sys.platform == "win32", reason="Unsupported platform assertion")
def test_unsupported_platform_fails_closed():
    assert_rejected(extract(make_pdf(["Text"])), "isolation_unavailable")


@WINDOWS
def test_cli_safe_json_and_nonzero_failure(tmp_path):
    path = tmp_path / "PRIVATE_FILENAME_SENTINEL.pdf"
    path.write_bytes(make_pdf(["PRIVATE_TEXT_SENTINEL", None]))
    command = [sys.executable, "scripts/pdf_probe.py", str(path)]
    accepted = subprocess.run(command, capture_output=True, text=True, timeout=15)
    assert accepted.returncode == 0
    summary = json.loads(accepted.stdout)
    assert summary["readablePages"] == [1]
    assert summary["unreadablePages"] == [2]
    assert "PRIVATE" not in accepted.stdout + accepted.stderr
    assert "text" not in summary
    path.write_bytes(b"%PDF-1.7\nPRIVATE_TEXT_SENTINEL")
    rejected = subprocess.run(command, capture_output=True, text=True, timeout=15)
    assert rejected.returncode != 0
    assert json.loads(rejected.stdout)["code"] == "invalid_pdf"
    assert "PRIVATE" not in rejected.stdout + rejected.stderr
    assert accepted.stderr == rejected.stderr == ""


def test_missing_input_has_safe_code(tmp_path):
    assert_rejected(probe.probe_pdf(tmp_path / "PRIVATE_MISSING.pdf"), "input_unavailable")


@WINDOWS
def test_direct_worker_entry_refuses_uncapped_parsing():
    import sysconfig

    result = subprocess.run(
        [sys._base_executable, "-I", "scripts/pdf_probe.py", "--_worker", "parse", sysconfig.get_path("purelib")],
        input=make_pdf(["PRIVATE_SENTINEL"]), capture_output=True, timeout=15,
    )
    assert json.loads(result.stdout) == {"code": "isolation_unavailable"}
    assert result.stderr == b""
