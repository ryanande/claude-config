#!/usr/bin/env python3
"""Surgical OQ-status flip — stdlib-only, byte-preserving.

The disposition writes ONLY the `status` (and `promoted-to`) lines of an OQ's
frontmatter; every other byte — critically the nested `build: {render, list}`
block — must survive untouched. A flat `key:value` round-trip would drop or
corrupt the nested block (see `references/disposition.md`). This helper does a
TARGETED line replacement: it rewrites only the matched `status:`/`promoted-to:`
lines inside the frontmatter and leaves all other bytes identical.

Pure (`flip` takes + returns text). CLI wraps it for the skill:
  python3 oq_flip.py --file <path> --status promoted [--promoted-to RFC-0006]

Usage from the skill: read the OQ, call flip, Write the result back (in the
worktree). Invariant test: `python3 test_oq_flip.py`.
"""
from __future__ import annotations

import argparse
import re
import sys
from typing import Optional

_VALID_STATUS = {"open", "parked", "promoted", "dropped"}
_UNSET = object()


def _frontmatter_bounds(text: str) -> tuple[int, int]:
    """Return (start, end) line indices (exclusive end) of the frontmatter body,
    i.e. the lines BETWEEN the opening and closing `---`. Raise if absent."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\n") != "---":
        raise ValueError("no frontmatter: file does not start with ---")
    for i in range(1, len(lines)):
        if lines[i].rstrip("\n") == "---":
            return 1, i
    raise ValueError("no frontmatter: unterminated --- block")


def flip(text: str, new_status: str, promoted_to=_UNSET, measuring=_UNSET) -> str:
    """Return `text` with ONLY the frontmatter `status:` (and, when given,
    `promoted-to:`) line values rewritten. Every other byte is preserved.

    `promoted_to` unset → leave the promoted-to line untouched.
    `promoted_to=None`/"" → set it to `null`. Otherwise set it to the value.
    Raises if status is invalid, or the keys are missing/duplicated.
    """
    if new_status not in _VALID_STATUS:
        raise ValueError(f"invalid status {new_status!r}; one of {sorted(_VALID_STATUS)}")
    lines = text.splitlines(keepends=True)
    start, end = _frontmatter_bounds(text)

    def _rewrite(key: str, value: str, required: bool) -> None:
        # group(1) = "key:" (with any leading indent), group(2) = the old value
        # text (no newline), group(3) = the preserved line ending.
        pat = re.compile(rf"^(\s*{re.escape(key)}:)([^\n]*?)(\r?\n?)$")
        hits = [i for i in range(start, end) if pat.match(lines[i])]
        if not hits:
            if required:
                raise ValueError(f"frontmatter key {key!r} not found")
            return
        if len(hits) > 1:
            raise ValueError(f"frontmatter key {key!r} appears {len(hits)} times; refusing")
        i = hits[0]
        m = pat.match(lines[i])
        # rewrite only the value; preserve "key:", a single separating space, and
        # the original line ending. All other lines are left byte-identical.
        lines[i] = f"{m.group(1)} {value}{m.group(3)}"

    def _rewrite_or_insert(key: str, value: str, after_key: str) -> None:
        """Rewrite `key`'s value if present in the frontmatter; otherwise insert
        `key: value` on the line immediately following `after_key`. Every other
        line stays byte-identical. Insertion is the only path that changes the
        line count."""
        nonlocal end
        pat = re.compile(rf"^(\s*{re.escape(key)}:)([^\n]*?)(\r?\n?)$")
        hits = [i for i in range(start, end) if pat.match(lines[i])]
        if len(hits) > 1:
            raise ValueError(f"frontmatter key {key!r} appears {len(hits)} times; refusing")
        if hits:
            i = hits[0]
            m = pat.match(lines[i])
            lines[i] = f"{m.group(1)} {value}{m.group(3)}"
            return
        anchor = re.compile(rf"^\s*{re.escape(after_key)}:")
        anchors = [i for i in range(start, end) if anchor.match(lines[i])]
        if not anchors:
            raise ValueError(f"cannot insert {key!r}: anchor key {after_key!r} not found")
        at = anchors[-1] + 1
        ending = "\r\n" if lines[anchors[-1]].endswith("\r\n") else "\n"
        lines.insert(at, f"{key}: {value}{ending}")
        end += 1

    _rewrite("status", new_status, required=True)
    if promoted_to is not _UNSET:
        _rewrite("promoted-to", "null" if not promoted_to else promoted_to, required=False)
    if measuring is not _UNSET:
        _rewrite_or_insert("measuring", "null" if not measuring else measuring,
                           after_key="promoted-to")
    return "".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Surgical OQ status/promoted-to flip")
    ap.add_argument("--file", required=True)
    ap.add_argument("--status", required=True, choices=sorted(_VALID_STATUS))
    ap.add_argument("--promoted-to", default=None,
                    help="set promoted-to (omit to leave untouched; empty → null)")
    ap.add_argument("--measuring", default=None,
                    help="set measuring (omit to leave untouched; empty → null); "
                         "inserted after promoted-to when the key is absent")
    ap.add_argument("--in-place", action="store_true", help="write back to --file")
    args = ap.parse_args(argv)
    with open(args.file, encoding="utf-8") as f:
        text = f.read()
    pt = _UNSET if args.promoted_to is None else args.promoted_to
    ms = _UNSET if args.measuring is None else args.measuring
    out = flip(text, args.status, promoted_to=pt, measuring=ms)
    if args.in_place:
        with open(args.file, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
