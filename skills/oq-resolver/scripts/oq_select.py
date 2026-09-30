#!/usr/bin/env python3
"""OQ-resolver selector — deterministic, stdlib-only.

Reads the open-questions corpus of `research-docs` at `origin/main` (never the
local working tree — the canonical checkout may be on an unrelated branch) and
emits a JSON selection decision for `/oq-resolver`.

Split for testability (mirrors the exocortex `worker-select` purity):
  - `parse_frontmatter` / `validate_oq_id` / `tractability` / `select` are PURE
    (no git, no network) and are exercised by `test_oq_select.py`.
  - `main` is the only impurity: it shells out to `git show` (no shell — argv
    list, so the zsh `$ref:$path` history-expansion footgun cannot apply) to
    build the rows, then calls `select`.

The selector performs the MECHANICAL gate only (status allowlist, non-empty
unblock-by, --oq regex, the conservative needs-our-own-data skip). The
judgement gates — zombie (unblock-by already satisfied) and the final
disposition — are the SKILL's job, not this script's.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Optional

OQ_DIR = "content/open-questions"
OQ_ID_RE = re.compile(r"^(?:OQ-)?([0-9]{4})$")

# Conservative skip-only heuristic: flag ONLY an unblock-by that needs OUR OWN
# internal data or a time-window external research can neither produce nor
# inform (e.g. OQ-0023 "90 days of per-skill churn", OQ-0024 "first MAJOR
# cycle"). Design/mechanism OQs (lint-vs-wrapper, warn-fatigue, …) are NOT
# flagged — external precedent informs them (false-skip is safe, false-promote
# is not, but over-skipping defeats the skill, so this stays deliberately tight).
NEEDS_OWN_DATA_PATTERNS = [
    re.compile(r"\b\d+\s+days\b", re.I),               # "90 days"
    re.compile(r"post-v\d", re.I),                      # "post-v1.0.0"
    re.compile(r"\bMAJOR\b.*\b(cycle|release)\b", re.I),  # "first MAJOR release cycle"
    re.compile(r"\brelease cycle\b", re.I),
    re.compile(r"per-skill\s+(commit\s+)?(cadence|churn)", re.I),
    re.compile(r"churn\s+(ratio|data)", re.I),
]


def parse_frontmatter(text: str) -> dict:
    """Minimal hand-rolled frontmatter parse (no YAML dep), mirroring the
    exocortex `_frontmatter` flat-scalar + block-list approach. Extracts only
    the fields the selector needs: status, date, tags, unblock_by (list)."""
    out: dict = {"status": None, "date": None, "tags": [], "unblock_by": [],
                 "measuring": None}
    if not text.startswith("---"):
        return out
    end = text.find("\n---", 3)
    block = text[3:end] if end != -1 else text
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if key == "status":
            out["status"] = val or None
        elif key == "measuring":
            out["measuring"] = None if val in ("", "null", "~") else val
        elif key == "date":
            out["date"] = val or None
        elif key == "tags":
            if val.startswith("["):
                inner = val.strip("[]")
                out["tags"] = [t.strip().strip("'\"") for t in inner.split(",") if t.strip()]
        elif key in ("unblock-by", "unblock_by"):
            if val and val not in ("[]", "|", ">"):
                # rare inline form
                out["unblock_by"] = [val]
            else:
                items = []
                j = i + 1
                while j < len(lines) and re.match(r"^\s+-\s+", lines[j]):
                    items.append(re.sub(r"^\s+-\s+", "", lines[j]).strip())
                    j += 1
                out["unblock_by"] = items
                i = j
                continue
        i += 1
    return out


def validate_oq_id(raw: str) -> Optional[str]:
    """Return the canonical 4-digit id (e.g. '0037') or None if malformed.
    Gate before any path/git interpolation."""
    if raw is None:
        return None
    m = OQ_ID_RE.match(raw.strip())
    return m.group(1) if m else None


def tractability(unblock_by: list[str]) -> str:
    """'needs-our-own-data' (skip) or 'ok'. Conservative skip-only."""
    blob = " \n ".join(unblock_by)
    for pat in NEEDS_OWN_DATA_PATTERNS:
        if pat.search(blob):
            return "needs-our-own-data"
    return "ok"


def classify(row: dict) -> tuple[bool, str]:
    """Pure mechanical gate for one row. Returns (selectable, reason)."""
    if row.get("status") != "open":
        return False, f"status={row.get('status')!r} (allowlist requires open)"
    measuring = row.get("measuring")
    if measuring:
        return False, f"measuring={measuring} (study in flight)"
    ub = row.get("unblock_by") or []
    if not ub:
        return False, "empty unblock-by"
    tract = tractability(ub)
    if tract != "ok":
        return False, tract
    return True, "selectable"


def select(rows: list[dict], oq: Optional[str] = None) -> dict:
    """Pure selection over rows. `oq` (canonical 4-digit id) pins one OQ.

    A row is a dict: {id, status, date, tags, unblock_by, source_path}.
    Returns {action: resolve|none, oq_id, reason, filtered:[{id,reason}]}.
    """
    by_id = {r["id"]: r for r in rows}
    filtered = []

    if oq is not None:
        r = by_id.get(oq)
        if r is None:
            return {"action": "none", "oq_id": None,
                    "reason": f"--oq {oq}: no such OQ on origin/main", "filtered": []}
        ok, reason = classify(r)
        if not ok:
            return {"action": "none", "oq_id": None,
                    "reason": f"--oq {oq}: {reason}", "filtered": []}
        return {"action": "resolve", "oq_id": oq, "reason": "pinned via --oq",
                "filtered": []}

    candidates = []
    for r in rows:
        ok, reason = classify(r)
        if ok:
            candidates.append(r)
        else:
            # only surface genuinely-skipped OPEN OQs (status-excluded ones are noise)
            if r.get("status") == "open":
                filtered.append({"id": r["id"], "reason": reason})
    if not candidates:
        return {"action": "none", "oq_id": None,
                "reason": "no selectable open OQ", "filtered": filtered}
    # oldest date first (ties broken by id for determinism)
    candidates.sort(key=lambda r: (r.get("date") or "9999-99-99", r["id"]))
    pick = candidates[0]
    return {"action": "resolve", "oq_id": pick["id"],
            "reason": f"oldest selectable open OQ (date={pick.get('date')})",
            "filtered": filtered}


# --- impure boundary --------------------------------------------------------

def _git_show(repo: str, ref_path: str) -> str:
    # argv list → no shell → the zsh `$ref:$path` history-expansion footgun
    # (reference_zsh_git_show_history_expansion) cannot apply here.
    return subprocess.run(["git", "-C", repo, "show", ref_path],
                          capture_output=True, text=True, check=True).stdout


def _resolve_research_docs() -> Optional[str]:
    root = os.environ.get("DX_ARCH_META_ROOT")
    if root:
        cand = os.path.join(root, "repos", "research-docs")
        if os.path.isdir(cand):
            return cand
    return None


def _build_rows(repo: str) -> list[dict]:
    listing = subprocess.run(
        ["git", "-C", repo, "ls-tree", "--name-only", "origin/main", f"{OQ_DIR}/"],
        capture_output=True, text=True, check=True).stdout
    rows = []
    for path in listing.splitlines():
        if not re.search(r"/\d{4}-", path):
            continue
        idm = re.search(r"/(\d{4})-", path)
        if not idm:
            continue
        fm = parse_frontmatter(_git_show(repo, f"origin/main:{path}"))
        rows.append({"id": idm.group(1), "status": fm["status"], "date": fm["date"],
                     "tags": fm["tags"], "unblock_by": fm["unblock_by"],
                     "source_path": path})
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="OQ-resolver selector")
    ap.add_argument("cmd", choices=["select", "rows"], help="select | rows")
    ap.add_argument("--oq", default=None, help="pin a specific OQ id (NNNN or OQ-NNNN)")
    ap.add_argument("--repo", default=None, help="research-docs path (else $DX_ARCH_META_ROOT/repos/research-docs)")
    args = ap.parse_args(argv)

    oq = None
    if args.oq is not None:
        oq = validate_oq_id(args.oq)
        if oq is None:
            print(json.dumps({"action": "none", "oq_id": None,
                              "reason": f"malformed --oq {args.oq!r}; expected NNNN or OQ-NNNN",
                              "filtered": []}))
            return 0

    repo = args.repo or _resolve_research_docs()
    if not repo or not os.path.isdir(repo):
        print(json.dumps({"action": "none", "oq_id": None,
                          "reason": "research-docs not resolvable (set DX_ARCH_META_ROOT or --repo)",
                          "filtered": []}))
        return 0

    rows = _build_rows(repo)
    if args.cmd == "rows":
        print(json.dumps(rows, indent=2))
        return 0
    print(json.dumps(select(rows, oq=oq)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
