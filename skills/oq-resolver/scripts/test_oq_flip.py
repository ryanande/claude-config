#!/usr/bin/env python3
"""Byte-preservation tests for oq_flip (run: python3 test_oq_flip.py).

Proves the surgical flip rewrites ONLY status/promoted-to and leaves every other
line — especially the nested build: block — byte-identical.
"""
import sys

from oq_flip import flip

_fails = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        _fails.append(name)


FIXTURE = """---
id: OQ-0037
title: Some question with a : colon and [brackets] in it
status: open
date: 2026-06-17
author: wyatt.rupp
unblock-by:
  - first item — with em-dash and : colon
  - second item
tags: [exocortex, shell, tooling]
promoted-to: null
build:
  render: never
  list: never
---

# body stays exactly as-is

- bullet
"""

out = flip(FIXTURE, "promoted", promoted_to="RFC-0006")
orig_lines = FIXTURE.splitlines(keepends=True)
new_lines = out.splitlines(keepends=True)

check("line count unchanged", len(orig_lines) == len(new_lines))

changed = [i for i in range(len(orig_lines)) if orig_lines[i] != new_lines[i]]
# exactly the status line (idx 3) and promoted-to line (idx 10) changed
check("exactly 2 lines changed (status + promoted-to)", len(changed) == 2)

new_text = "".join(new_lines)
check("status flipped to promoted", "\nstatus: promoted\n" in new_text)
check("promoted-to set", "\npromoted-to: RFC-0006\n" in new_text)

# the nested build: block is byte-identical
check("build: header preserved", "\nbuild:\n" in new_text)
check("build.render preserved byte-for-byte", "\n  render: never\n" in new_text)
check("build.list preserved byte-for-byte", "\n  list: never\n" in new_text)

# everything that is NOT status/promoted-to is identical
for i in range(len(orig_lines)):
    if i in (3, 10):
        continue
    if orig_lines[i] != new_lines[i]:
        check(f"line {i} preserved", False)
check("all non-flipped lines preserved", all(
    orig_lines[i] == new_lines[i] for i in range(len(orig_lines)) if i not in (3, 10)))

# colon/bracket-bearing lines (title, unblock-by item, tags) untouched
check("title with colon untouched", "title: Some question with a : colon and [brackets] in it\n" in new_text)
check("unblock-by item with colon untouched", "  - first item — with em-dash and : colon\n" in new_text)
check("tags untouched", "tags: [exocortex, shell, tooling]\n" in new_text)

# leave-promoted-to-untouched mode
out2 = flip(FIXTURE, "parked")
check("status-only flip leaves promoted-to null", "\npromoted-to: null\n" in out2)
check("status-only flip changed exactly 1 line",
      sum(1 for a, b in zip(orig_lines, out2.splitlines(keepends=True)) if a != b) == 1)

# guards
def _raises(fn):
    try:
        fn(); return False
    except Exception:
        return True

check("invalid status rejected", _raises(lambda: flip(FIXTURE, "bogus")))
check("no-frontmatter rejected", _raises(lambda: flip("no frontmatter here", "parked")))

# --- measuring: insert-if-absent -------------------------------------------

out_m = flip(FIXTURE, "open", measuring="EVAL-0001")
orig_m = FIXTURE.splitlines(keepends=True)
new_m = out_m.splitlines(keepends=True)

check("measuring insert adds exactly one line", len(new_m) == len(orig_m) + 1)
check("measuring line present", any(l.rstrip("\n") == "measuring: EVAL-0001" for l in new_m))

# inserted immediately after promoted-to (idx 10 in FIXTURE)
check("measuring inserted after promoted-to",
      new_m[11].rstrip("\n") == "measuring: EVAL-0001")

# every other line byte-identical, in order
without = new_m[:11] + new_m[12:]
check("all other lines byte-identical", without == orig_m)

# build: block survives
check("build block intact",
      "build:\n" in out_m and "  render: never\n" in out_m and "  list: never\n" in out_m)

# --- measuring: update-if-present ------------------------------------------

out_m2 = flip(out_m, "open", measuring="EVAL-0002")
new_m2 = out_m2.splitlines(keepends=True)
check("measuring update changes no line count", len(new_m2) == len(new_m))
changed_m2 = [i for i in range(len(new_m)) if new_m[i] != new_m2[i]]
check("measuring update changes exactly 1 line", len(changed_m2) == 1)
check("measuring updated value", new_m2[11].rstrip("\n") == "measuring: EVAL-0002")

# --- measuring: unset leaves file untouched --------------------------------

check("measuring unset is a no-op", flip(FIXTURE, "open") == FIXTURE)

# --- measuring: clearing ---------------------------------------------------

out_m3 = flip(out_m, "open", measuring="")
new_m3 = out_m3.splitlines(keepends=True)
check("measuring cleared to null", new_m3[11].rstrip("\n") == "measuring: null")

# --- measuring: missing anchor is a refusal, not a silent skip --------------

NO_ANCHOR = "---\nid: OQ-8888\nstatus: open\nbuild:\n  render: never\n---\n\nbody\n"
try:
    flip(NO_ANCHOR, "open", measuring="EVAL-0003")
    check("missing promoted-to anchor raises", False)
except ValueError as e:
    check("missing promoted-to anchor raises", "anchor key" in str(e))

print()
if _fails:
    print(f"FAILED ({len(_fails)}): {_fails}")
    sys.exit(1)
print("all oq_flip tests passed")
