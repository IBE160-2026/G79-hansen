"""Deterministic synthetic PDFs, generated in memory/temporary test directories only."""

import io

from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject, ByteStringObject, DecodedStreamObject, DictionaryObject,
    NameObject, NumberObject,
)


class _DeterministicWriter(PdfWriter):
    def generate_file_identifiers(self):
        # Test data only. Never use predictable identifiers for private encryption.
        self._ID = ArrayObject([ByteStringObject(b"synthetic-pdf-v1!")] * 2)


def _stream(writer, data: bytes, *, compressed=False):
    stream = DecodedStreamObject()
    stream.set_data(data)
    return writer._add_object(stream.flate_encode() if compressed else stream)


def make_pdf(pages: list[str | None], *, image_pages=(), encrypted=False, stress_operations=0) -> bytes:
    """None means blank; image_pages contains one-based physical positions.

    A ToUnicode font maps synthetic character codes to UTF-16BE, including
    supplementary characters, so tests measure extracted Unicode rather than bytes.
    """
    writer = _DeterministicWriter()
    for position, text in enumerate(pages, 1):
        page = writer.add_blank_page(width=612, height=792)
        resources = DictionaryObject()
        commands = b""
        if text:
            alphabet = list(dict.fromkeys(text))
            if len(alphabet) > 255:
                raise ValueError("Fixture alphabet is limited to 255 distinct code points")
            encoding = {char: index for index, char in enumerate(alphabet, 1)}
            mappings = "\n".join(
                f"<{encoding[char]:02x}> <{char.encode('utf-16-be').hex()}>" for char in alphabet
            )
            cmap = (
                "/CIDInit /ProcSet findresource begin 12 dict begin begincmap\n"
                "/CIDSystemInfo << /Registry (Synthetic) /Ordering (Test) /Supplement 0 >> def\n"
                "/CMapName /Synthetic def /CMapType 2 def\n"
                "1 begincodespacerange <00> <ff> endcodespacerange\n"
                f"{len(alphabet)} beginbfchar\n{mappings}\nendbfchar\n"
                "endcmap CMapName currentdict /CMap defineresource pop end end"
            ).encode("ascii")
            font = DictionaryObject({
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
                NameObject("/Encoding"): NameObject("/WinAnsiEncoding"),
                NameObject("/ToUnicode"): _stream(writer, cmap),
            })
            resources[NameObject("/Font")] = DictionaryObject({NameObject("/F1"): writer._add_object(font)})
            encoded = bytes(encoding[char] for char in text).hex().encode("ascii")
            commands = b"BT /F1 12 Tf 1 0 0 1 40 700 Tm <" + encoded + b"> Tj ET\n"
        if position in image_pages:
            image = DecodedStreamObject()
            image.set_data(b"\x12\x34\x56")
            image.update({
                NameObject("/Type"): NameObject("/XObject"),
                NameObject("/Subtype"): NameObject("/Image"),
                NameObject("/Width"): NumberObject(1),
                NameObject("/Height"): NumberObject(1),
                NameObject("/ColorSpace"): NameObject("/DeviceRGB"),
                NameObject("/BitsPerComponent"): NumberObject(8),
            })
            resources[NameObject("/XObject")] = DictionaryObject({
                NameObject("/Im1"): writer._add_object(image.flate_encode())
            })
            commands += b"q 100 0 0 100 40 500 cm /Im1 Do Q\n"
        if stress_operations and position == 1:
            commands = b"q Q\n" * stress_operations + commands
        page[NameObject("/Resources")] = resources
        if commands:
            page[NameObject("/Contents")] = _stream(writer, commands, compressed=bool(stress_operations))
    if encrypted:
        writer.encrypt("synthetic-password", algorithm="RC4-128")
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def at_size(pdf: bytes, size: int) -> bytes:
    """PDF permits trailing whitespace; retain a valid document at the byte boundary."""
    if size < len(pdf):
        raise ValueError("Requested size is smaller than the generated PDF")
    return pdf + b"\n" * (size - len(pdf))


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Write one synthetic physical-page fixture locally.")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    args.destination.write_bytes(make_pdf(["Physical page one", None, "Physical page three", None], image_pages=(4,)))
