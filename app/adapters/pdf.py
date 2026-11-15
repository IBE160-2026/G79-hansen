"""Application adapter: PDF parsing always stays in the contained probe worker."""

from io import BytesIO

from scripts.pdf_probe import ProbeResult, probe_stream


def extract_pdf(content: bytes) -> ProbeResult:
    # probe_stream owns the Job Object, hard memory cap, deadline and reaping.
    # It fails closed on platforms without that containment.
    return probe_stream(BytesIO(content))
