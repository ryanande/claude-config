#!/usr/bin/env python3
"""PDF text extraction and norm-v1 quote matching for the shared fetch cache.

Executable form of cache-contract.md v1.4 §Extracted text match key and the
miss-path extraction step. Stdlib only; shells out to poppler `pdftotext` in
default reading-order mode (never -layout). Absence of the tool is a recorded
status, never an exception.

CLI:
  python3 pdf_extract.py check-tool                        # exit 0 present, or 3 absent
  python3 pdf_extract.py extract <pdf> [--out <txt>]      # exit 0 ok / 3 tool-missing / 5 failed;
                                                            # writes body.txt only when words > 0;
                                                            # prints the JSON record
  python3 pdf_extract.py key < text                       # norm-v1 key to stdout
  python3 pdf_extract.py quote-present --quote <q> <txt>  # exit 0 present, 1 absent, 4 spans-page-break;
                                                            # on exit 0 also prints the raw offset
  python3 pdf_extract.py page-of --offset <n> <txt>       # 1-based page number for a raw offset
Invariant tests: python3 test_pdf_extract.py
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata

VERSION = "norm-v1"
TOOL = "pdftotext"
TIMEOUT_S = 60
HYPHENS = "-‐‑­"
_HYPHEN_WS_RE = re.compile("[" + HYPHENS + r"]\s+")
_HYPHEN_RE = re.compile("[" + HYPHENS + "]")
_WS_RE = re.compile(r"\s+")
END_CHARS = 5


def key(text: str) -> str:
    """norm-v1 key, in order: (1) NFC-normalize; (2) join line-break
    hyphenation — a hyphen-class char followed by whitespace is removed
    together with the whitespace ("improve-\\n\\nments" -> "improvements");
    (3) delete any remaining hyphen-class chars ("Self-Refine" ->
    "SelfRefine", "state-of-the-art" -> "stateoftheart"); (4) collapse
    whitespace runs (incl. form feed) to ONE space and strip. Case is
    preserved and word boundaries survive as single spaces, so matching
    stays token-boundary anchored (see quote_present/locate)."""
    s = unicodedata.normalize("NFC", text)
    s = _HYPHEN_WS_RE.sub("", s)
    s = _HYPHEN_RE.sub("", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def _key_with_offsets(text: str) -> tuple:
    """Same transform as key(), but also returns offsets[i] = the raw index
    in `text` that produced key_str[i] — the key->raw offset bridge `locate`
    needs to resolve `page N`. Mirrors key()'s four steps character-by-
    character so the two stay in lockstep."""
    s = unicodedata.normalize("NFC", text)
    n = len(s)
    chars = []
    offs = []
    i = 0
    while i < n:
        c = s[i]
        if c in HYPHENS:
            j = i + 1
            if j < n and s[j].isspace():
                while j < n and s[j].isspace():
                    j += 1
                i = j
                continue
            i += 1
            continue
        if c.isspace():
            start = i
            while i < n and s[i].isspace():
                i += 1
            chars.append(" ")
            offs.append(start)
            continue
        chars.append(c)
        offs.append(i)
        i += 1
    while chars and chars[0] == " ":
        chars.pop(0)
        offs.pop(0)
    while chars and chars[-1] == " ":
        chars.pop()
        offs.pop()
    return "".join(chars), offs


def locate(quote: str, text: str):
    """norm-v1 match with a raw-offset bridge. Returns (code, offset):
    code 0 = quote key is a token-boundary-anchored substring of text key,
    offset = the raw index in `text` of the match start; code 1 = absent,
    offset None; code 4 = the quote key splits at exactly one point into a
    head and a tail (each at least END_CHARS key chars) that occur in order
    in the text key with at most 2x the quote's key length of inserted text
    between them (spans a page break — furniture-interrupted) but the full
    quote is not a hit, offset None.
    Matching is anchored at (?<!\\w)...(?!\\w) token boundaries -- word-char
    boundaries, not whitespace-only ones, so a short quote cannot match
    inside a longer word (e.g. "a cat" does not match "a categorical")
    while a quote ending right before ordinary trailing punctuation
    ("quorum sensing." in running body text) still hits."""
    kq = key(quote)
    kt, offs = _key_with_offsets(text)
    if not kq:
        return 1, None
    m = re.search(r"(?<!\w)" + re.escape(kq) + r"(?!\w)", kt)
    if m:
        return 0, offs[m.start()]
    if len(kq) >= 2 * END_CHARS:
        for i in range(END_CHARS, len(kq) - END_CHARS + 1):
            head, tail = kq[:i], kq[i:]
            for pm in re.finditer(r"(?<!\w)" + re.escape(head), kt):
                p = pm.start()
                start = p + len(head)
                q = kt.find(tail, start)
                if q == -1:
                    continue
                gap = q - start
                if not (0 < gap <= 2 * len(kq)):
                    continue
                end = q + len(tail)
                if end < len(kt) and re.match(r"\w", kt[end]):
                    continue
                return 4, None
    return 1, None


def quote_present(quote: str, text: str) -> int:
    """0 = present (token-boundary anchored); 1 = absent;
    4 = both ends match, positionally close, but the whole does not (interrupted)."""
    return locate(quote, text)[0]


def check_tool(env=None) -> tuple:
    """Returns (ok, message, path). `path` is the resolved binary path on
    success (so extract() can reuse it instead of a second `which`), or
    None on any failure — no PATH entry, or a non-zero `-v` exit."""
    env = os.environ if env is None else env
    path = shutil.which(TOOL, path=env.get("PATH", ""))
    if not path:
        return False, f"{TOOL} not on PATH", None
    try:
        r = subprocess.run([path, "-v"], capture_output=True, text=True, timeout=10, env=dict(env))
    except Exception as e:  # noqa: BLE001
        return False, f"{TOOL} present but -v failed: {e}", None
    if r.returncode != 0:
        return False, f"{TOOL} -v exited {r.returncode}", None
    out = (r.stderr or r.stdout).strip()
    ver = out.splitlines()[0] if out else path
    return True, ver, path


def extract(pdf_path: str, out_path=None, env=None) -> dict:
    """Run pdftotext (default mode) on pdf_path. On ok, write out_path atomically
    (tmp + rename) ONLY when words > 0 — a text-less PDF is status "ok",
    words 0, no body.txt. Never raises for tool absence, tool failure, or a
    write failure; those are statuses, and any tmp file is unlinked."""
    env = os.environ if env is None else env
    rec = {"tool": TOOL, "status": "failed", "words": 0, "version": VERSION}
    ok, _, tool = check_tool(env)
    if not ok:
        rec["status"] = "tool-missing"
        return rec
    try:
        r = subprocess.run([tool, "-enc", "UTF-8", pdf_path, "-"], capture_output=True, timeout=TIMEOUT_S, env=dict(env))
    except subprocess.TimeoutExpired:
        return rec
    if r.returncode != 0:
        return rec
    text = r.stdout.decode("utf-8", errors="replace")
    rec["status"] = "ok"
    rec["words"] = len(text.split())
    if out_path and rec["words"] > 0:
        tmp = f"{out_path}.tmp.{os.getpid()}"
        try:
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.write(text)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, out_path)
        except OSError:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            rec["status"] = "failed"
            rec["words"] = 0
    return rec


def page_of(offset: int, text: str) -> int:
    return text.count("\f", 0, max(0, offset)) + 1


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pdf_extract.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check-tool")
    e = sub.add_parser("extract"); e.add_argument("pdf"); e.add_argument("--out")
    sub.add_parser("key")
    q = sub.add_parser("quote-present"); q.add_argument("--quote", required=True); q.add_argument("txt")
    p = sub.add_parser("page-of"); p.add_argument("--offset", type=int, required=True); p.add_argument("txt")
    a = ap.parse_args(argv)
    if a.cmd == "check-tool":
        ok, msg, _ = check_tool()
        print(msg)
        return 0 if ok else 3
    if a.cmd == "extract":
        rec = extract(a.pdf, a.out)
        print(json.dumps(rec, sort_keys=True))
        return {"ok": 0, "tool-missing": 3, "failed": 5}[rec["status"]]
    if a.cmd == "key":
        sys.stdout.write(key(sys.stdin.read()))
        return 0
    text = open(a.txt, encoding="utf-8", errors="replace").read()
    if a.cmd == "quote-present":
        code, offset = locate(a.quote, text)
        if code == 0:
            print(offset)
        return code
    print(page_of(a.offset, text))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
