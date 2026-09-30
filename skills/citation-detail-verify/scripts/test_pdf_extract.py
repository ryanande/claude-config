#!/usr/bin/env python3
"""Fail-closed invariant tests for pdf_extract.py (run: python3 test_pdf_extract.py).

Proves: norm-v1 NFC-normalizes, joins line-break hyphenation (hyphen+whitespace
removed together), deletes remaining hyphen-class chars, and collapses whitespace
runs to one space (word boundaries survive); quote_present/locate match on token
boundaries so a short quote cannot match inside a longer word; the spans-page-break
check (exit 4) is position-correlated, not just both-ends-present, so a coincidental
distant prefix/suffix pair does not false-positive; locate() bridges a key-string hit
back to a raw offset in the original text; check_tool exits False (and reports no
path) when `pdftotext -v` fails, and returns the resolved path on success so extract()
does not re-`which`; extract() writes body.txt only when words > 0, wraps the tmp
write in try/except, and never leaves a tmp file behind on any failure path.
"""
import json
import os
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pdf_extract as px  # noqa: E402
import make_fixture_pdf as mf  # noqa: E402

FIXTURE = os.path.join(HERE, "..", "test-corpus", "fixture-two-page.pdf")
_fails = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        _fails.append(name)


def test_key():
    print("key")
    check("collapses whitespace run to one space (not deleted)", px.key("a b\nc\fd") == "a b c d")
    check("collapses a run of spaces to one", px.key("a   b") == "a b")
    check("joins hyphen + linebreak (line-break hyphenation)", px.key("improve-\n\nments") == "improvements")
    check("deletes U+002D with no following whitespace", px.key("Self-Refine") == "SelfRefine")
    check("deletes hyphens with no join when no whitespace follows", px.key("state-of-the-art") == "stateoftheart")
    check("deletes U+2010 U+2011 U+00AD", px.key("a‐b‑c­d") == "abcd")
    check("preserves case", px.key("Ab") == "Ab")
    check("NFC folds decomposed e-acute", px.key("é") == "é")
    check("keeps en-dash (not hyphen class)", px.key("a–b") == "a–b")


def test_quote_present():
    print("quote_present")
    body = "offer improve-\n\nments, core issues remain\n\nSelf-\n\nRefine label\n\nimpro-\n\n2109\nProceedings of the 64th\n\nvements remain here"
    check("soft split matches", px.quote_present("offer improvements, core issues remain", body) == 0)
    check("hard split matches", px.quote_present("Self-Refine label", body) == 0)
    check("absent phrase -> 1", px.quote_present("not in the body", body) == 1)
    check("furniture-interrupted -> 4", px.quote_present("improvements remain here", body) == 4)
    check("raw substring would have failed", "offer improvements" not in body)
    check("'a cat' does not match inside 'a categorical framework'",
          px.quote_present("a cat", "a categorical framework") == 1)
    check("'in form' does not match inside 'in formal terms'",
          px.quote_present("in form", "in formal terms") == 1)
    check("early coincidental suffix does not hide real interruption", px.quote_present("improvements remain here", "impro-\n\nx here\n\n2109\nProceedings of the 64th\n\nvements remain here") == 4)
    check("fabricated quote sharing only ends -> 1", px.quote_present("offercomplete nonsense text unrelated remain", body) == 1)
    check("interruption near quote end still 4", px.quote_present("core issues remain here", "core issues re-\n\n2109\n\nmain here") == 4)
    check("two separate insertions -> 1", px.quote_present("core issues remain here", "core\n\n2109\n\nissues re-\n\n2110\n\nmain here") == 1)



def test_locate():
    print("locate")
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "body.txt")
        px.extract(FIXTURE, out)
        fixture_txt = open(out, encoding="utf-8").read()
        code, off = px.locate("quorum sensing", fixture_txt)
        check("locate hit -> code 0", code == 0)
        check("offset resolves to the raw match start", fixture_txt[off:off + 6] == "quorum")
        check("page_of on that offset -> page 2", px.page_of(off, fixture_txt) == 2)
        code1, off1 = px.locate("not in the body", fixture_txt)
        check("locate absent -> code 1, offset None", code1 == 1 and off1 is None)
        interrupted = "impro-\n\n2109\nProceedings of the 64th\n\nvements remain here"
        code4, off4 = px.locate("improvements remain here", interrupted)
        check("locate spans-page-break -> code 4, offset None", code4 == 4 and off4 is None)
        check("quote_present delegates to locate's code", px.quote_present("quorum sensing", fixture_txt) == 0)


def test_check_tool():
    print("check_tool")
    ok, ver, path = px.check_tool()
    check("tool present on this machine", ok and ver and path)
    ok2, why, path2 = px.check_tool(env={"PATH": ""})
    check("empty PATH -> absent", ok2 is False and "not on PATH" in why and path2 is None)
    with tempfile.TemporaryDirectory() as d:
        fake = os.path.join(d, "pdftotext")
        with open(fake, "w") as fh:
            fh.write("#!/bin/sh\nexit 1\n")
        os.chmod(fake, os.stat(fake).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        ok3, why3, path3 = px.check_tool(env={"PATH": d})
        check("pdftotext -v exiting non-zero -> False", ok3 is False)
        check("failure path carries no resolved path", path3 is None)


def test_extract():
    print("extract")
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "body.txt")
        rec = px.extract(FIXTURE, out)
        check("status ok", rec["status"] == "ok")
        check("writes body.txt", os.path.exists(out))
        txt = open(out, encoding="utf-8").read()
        check("keeps form feed", "\f" in txt)
        check("soft split present verbatim", "improve-\n" in txt)
        check("words counted", rec["words"] == len(txt.split()))
        check("record names tool and version", rec["tool"] == "pdftotext" and rec["version"] == px.VERSION)
        check("quote across soft split", px.quote_present("soft improvements example", txt) == 0)
        check("quote across hard split", px.quote_present("hard Self-Refine label", txt) == 0)
        out2 = os.path.join(d, "missing.txt")
        rec2 = px.extract(FIXTURE, out2, env={"PATH": ""})
        check("tool-missing status", rec2["status"] == "tool-missing" and rec2["words"] == 0)
        check("tool-missing writes nothing", not os.path.exists(out2))
        out3 = os.path.join(d, "bad.txt")
        bad = os.path.join(d, "bad.pdf")
        with open(bad, "wb") as fh:
            fh.write(b"not a pdf")
        rec3 = px.extract(bad, out3)
        check("corrupt input -> failed", rec3["status"] == "failed")
        check("failed writes nothing", not os.path.exists(out3))
        check("tmp file not left behind", not any(f.endswith(".tmp") or ".tmp." in f for f in os.listdir(d)))
        out5 = os.path.join(d, "nosuchdir", "body.txt")
        rec5 = px.extract(FIXTURE, out5)
        check("unwritable out_path -> failed, not an exception", rec5["status"] == "failed")
        check("no tmp leftover from an unwritable out_path", not os.path.isdir(os.path.join(d, "nosuchdir")))
        blank = os.path.join(d, "blank.pdf")
        saved_p1, saved_p2 = mf.PAGE1, mf.PAGE2
        try:
            mf.PAGE1 = [""]
            mf.PAGE2 = [""]
            with open(blank, "wb") as fh:
                fh.write(mf.build())
        finally:
            mf.PAGE1, mf.PAGE2 = saved_p1, saved_p2
        out4 = os.path.join(d, "blank.txt")
        rec4 = px.extract(blank, out4)
        check("text-less PDF -> ok with words 0", rec4["status"] == "ok" and rec4["words"] == 0)
        check("text-less PDF writes no body.txt", not os.path.exists(out4))


def test_page_of():
    print("page_of")
    t = "page one text\fpage two text\fpage three"
    check("before first ff -> 1", px.page_of(3, t) == 1)
    check("after first ff -> 2", px.page_of(t.index("two"), t) == 2)
    check("after second ff -> 3", px.page_of(len(t) - 1, t) == 3)


def test_cli():
    print("cli")
    script = os.path.join(HERE, "pdf_extract.py")
    r = subprocess.run([sys.executable, script, "check-tool"], capture_output=True, text=True)
    check("check-tool exit 0", r.returncode == 0)
    r = subprocess.run([sys.executable, script, "check-tool"], capture_output=True, text=True, env={"PATH": ""})
    check("check-tool empty PATH exit 3", r.returncode == 3)
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "body.txt")
        r = subprocess.run([sys.executable, script, "extract", FIXTURE, "--out", out], capture_output=True, text=True)
        check("extract exit 0 and JSON", r.returncode == 0 and json.loads(r.stdout)["status"] == "ok")
        r = subprocess.run([sys.executable, script, "quote-present", "--quote", "quorum sensing", out], capture_output=True, text=True)
        check("quote-present exit 0", r.returncode == 0)
        check("quote-present prints a raw offset on a hit", r.stdout.strip().isdigit())
        offset = int(r.stdout.strip())
        r = subprocess.run([sys.executable, script, "quote-present", "--quote", "absent words", out], capture_output=True, text=True)
        check("quote-present absent exit 1", r.returncode == 1)
        check("quote-present prints nothing on a miss", r.stdout.strip() == "")
        r = subprocess.run([sys.executable, script, "page-of", "--offset", str(offset), out], capture_output=True, text=True)
        check("page-of prints 2", r.stdout.strip() == "2")
        bad = os.path.join(d, "bad.pdf")
        with open(bad, "wb") as fh:
            fh.write(b"not a pdf")
        out2 = os.path.join(d, "bad-out.txt")
        r = subprocess.run([sys.executable, script, "extract", bad, "--out", out2], capture_output=True, text=True)
        check("extract on corrupt pdf -> CLI exit 5", r.returncode == 5)
        check("extract on corrupt pdf -> status failed", json.loads(r.stdout)["status"] == "failed")


if __name__ == "__main__":
    test_key()
    test_quote_present()
    test_locate()
    test_check_tool()
    test_extract()
    test_page_of()
    test_cli()
    if _fails:
        print(f"\n{len(_fails)} failing: {_fails}")
        sys.exit(1)
    print("\nall ok")
