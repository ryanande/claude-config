#!/usr/bin/env python3
"""Deterministic two-page fixture PDF for pdf_extract.py tests. Stdlib only.

Each line is its own text object 60 pt below the previous so pdftotext default
mode does NOT dehyphenate — it emits the hyphen, a blank line, then the
continuation, matching real two-column PDFs.

Page 1 has a soft-hyphen split ("improve-" / "ments") and a hard-hyphen split
("Self-" / "Refine"). Page 2 has a known phrase. Run:
    python3 make_fixture_pdf.py > ../test-corpus/fixture-two-page.pdf
"""
import sys

PAGE1 = ["This is a soft improve-", "ments example and a hard Self-", "Refine label."]
PAGE2 = ["Page two carries the anchor phrase quorum sensing."]


def stream(lines):
    body = []
    for i, ln in enumerate(lines):
        esc = ln.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        body.append("BT /F1 12 Tf 72 %d Td (%s) Tj ET" % (720 - 60 * i, esc))
    return "\n".join(body).encode("latin-1")


def build():
    objs = []
    objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objs.append(b"<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>")
    s1 = stream(PAGE1)
    objs.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 7 0 R >> >> >>")
    objs.append(b"<< /Length %d >>\nstream\n" % len(s1) + s1 + b"\nendstream")
    s2 = stream(PAGE2)
    objs.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 6 0 R /Resources << /Font << /F1 7 0 R >> >> >>")
    objs.append(b"<< /Length %d >>\nstream\n" % len(s2) + s2 + b"\nendstream")
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, o in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + o + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n" % (len(objs) + 1)
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    return bytes(out)


if __name__ == "__main__":
    sys.stdout.buffer.write(build())
