#!/usr/bin/env python3
"""Tests for screen.py — the structural-real screen assigns REAL or nothing, never NOISE."""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import screen as sc  # noqa: E402

_fails = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        _fails.append(name)


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True).stdout.strip()


repo = tempfile.mkdtemp()
subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
git(repo, "config", "user.email", "t@t"); git(repo, "config", "user.name", "t")


def put(path, text):
    full = os.path.join(repo, path); os.makedirs(os.path.dirname(full), exist_ok=True); open(full, "w").write(text)


put("content/open-questions/0001.md", "---\nid: \"0001\"\nstatus: open\npromoted-to: RFC-0010\n---\nq\n")
put("content/open-questions/0002.md", "---\nid: \"0002\"\nstatus: open\n---\nq\n")
put("content/rfc/0010.md", "---\nid: RFC-0010\nstatus: draft\nsuperseded-by: RFC-0012\n---\nr\n")
put("content/rfc/0011.md", "---\nid: RFC-0011\nstatus: draft\n---\nr\n")
put("content/adr/0018.md", "---\nid: ADR-0018\nstatus: accepted\ndecided-from: [RFC-0011]\n---\na\n")
put("content/design/x.md", "---\nstatus: draft\npromoted-to: y\n---\nd\n")

# Stem-substring collision: ADR decided-from cites content/rfc/0021.md (full path
# form) — an OQ at content/open-questions/0021.md shares the bare numeric stem
# "0021.md" but is NOT itself cited.
put("content/open-questions/0021.md", "---\nid: \"0021\"\nstatus: open\n---\nq\n")
put("content/rfc/0021.md", "---\nid: RFC-0021\nstatus: draft\n---\nr\n")
put("content/adr/0020-path.md",
    "---\nid: ADR-0020\nstatus: accepted\ndecided-from: [content/rfc/0021.md]\n---\na\n")
put("content/rfc/0012-empty.md", "---\nid: RFC-0012E\nstatus: draft\nsuperseded-by: []\n---\nr\n")
put("content/rfc/0013-emptystr.md", "---\nid: RFC-0013E\nstatus: draft\npromoted-to: \"\"\n---\nr\n")
put("content/rfc/0014-null.md", "---\nid: RFC-0014N\nstatus: draft\npromoted-to: null\n---\nr\n")
put("content/rfc/0015-list.md", "---\nid: RFC-0015L\nstatus: draft\nsuperseded-by: [RFC-0012]\n---\nr\n")
put("content/adr/0019-block.md",
    "---\nid: ADR-0019\nstatus: accepted\ndecided-from:\n  - RFC-0016\n  - RFC-0017\n---\na\n")
put("content/rfc/0016.md", "---\nid: RFC-0016\nstatus: draft\n---\nr\n")
put("content/rfc/0017.md", "---\nid: RFC-0017\nstatus: draft\n---\nr\n")

git(repo, "add", "."); git(repo, "commit", "-q", "-m", "c"); sha = git(repo, "rev-parse", "HEAD")

check("types fixed", sc.STRUCTURAL_TYPES == ("open-questions", "rfc", "adr", "principles"))
check("clauses cover exactly the structural types", set(sc.CLAUSES) == set(sc.STRUCTURAL_TYPES))
check("promoted-to set -> REAL", sc.screen_item(repo, sha, "content/open-questions/0001.md", "open-questions") == "REAL")
check("plain open OQ -> None, never NOISE", sc.screen_item(repo, sha, "content/open-questions/0002.md", "open-questions") is None)
check("superseded-by set -> REAL", sc.screen_item(repo, sha, "content/rfc/0010.md", "rfc") == "REAL")
check("cited by landed ADR decided-from -> REAL", sc.screen_item(repo, sha, "content/rfc/0011.md", "rfc") == "REAL")
check("design type never screened even with promoted-to", sc.screen_item(repo, sha, "content/design/x.md", "design") is None)
check("returns only REAL or None", all(sc.screen_item(repo, sha, p, t) in ("REAL", None) for p, t in
                                       [("content/rfc/0010.md", "rfc"), ("content/rfc/0011.md", "rfc")]))

# Finding 1: stem-substring collision — decided-from cites the RFC's full path only;
# an OQ sharing the bare numeric stem must NOT be falsely matched.
check("stem-collision OQ not cited by ADR -> None", sc.screen_item(repo, sha, "content/open-questions/0021.md", "open-questions") is None)
check("stem-collision RFC actually cited -> REAL", sc.screen_item(repo, sha, "content/rfc/0021.md", "rfc") == "REAL")

# Finding 2: empty-list / empty-string / null unset-value normalisation
check("superseded-by: [] -> None (not truthy)", sc.screen_item(repo, sha, "content/rfc/0012-empty.md", "rfc") is None)
check("promoted-to: \"\" -> None", sc.screen_item(repo, sha, "content/rfc/0013-emptystr.md", "rfc") is None)
check("promoted-to: null -> None", sc.screen_item(repo, sha, "content/rfc/0014-null.md", "rfc") is None)
check("superseded-by: [RFC-0012] -> REAL", sc.screen_item(repo, sha, "content/rfc/0015-list.md", "rfc") == "REAL")

# Minor: YAML block-list form of decided-from
check("block-list decided-from cites RFC-0016 -> REAL", sc.screen_item(repo, sha, "content/rfc/0016.md", "rfc") == "REAL")
check("block-list decided-from cites RFC-0017 -> REAL", sc.screen_item(repo, sha, "content/rfc/0017.md", "rfc") == "REAL")

print(f"\n{len(_fails)} failure(s)")
sys.exit(1 if _fails else 0)
