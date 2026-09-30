#!/usr/bin/env python3
"""screen.py — study-run's structural-real pre-screen (protocol.screen: structural-real).

Fixed skill code. Assigns a provisional REAL only where frontmatter or link
structure decides it; never emits NOISE; never touches design/runbooks/notes.
The provisional label is stored in the ledger only and is never shown to a
spawn. Every screen-contradicted item is a rule-defect signal.
"""
import re
import subprocess

STRUCTURAL_TYPES = ("open-questions", "rfc", "adr", "principles")
CLAUSES = {
    "open-questions": "REAL if `promoted-to` is set, or the question is answered or superseded by a landed ADR / RFC / design; NOISE otherwise.",
    "rfc": "REAL if `superseded-by` is set or a landed (accepted/decided) ADR lists this document in `decided-from`; NOISE if the proposal is still the live position.",
    "adr": "REAL if `superseded-by` is set or a later accepted ADR lists this document in `decided-from`; NOISE if the proposal is still the live position.",
    "principles": "REAL if `superseded-by` is set or a landed ADR lists this document in `decided-from`; NOISE if the proposal is still the live position.",
}
LANDED = {"accepted", "decided"}


def _show(repo, sha, path):
    r = subprocess.run(["git", "-C", repo, "show", f"{sha}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def _fm(text):
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else ""


_UNSET = {"", "null", "~"}


def _field(fm, key):
    m = re.search(rf"^{re.escape(key)}:[ \t]*(.+?)[ \t]*$", fm, re.M)
    val = m.group(1).strip().strip("\"'") if m else ""
    if val.strip("\"'") in _UNSET or val in ("[]", "''", '""'):
        return ""
    return val


def _field_raw(fm, key):
    """Like _field but without the unset-normalisation — needed to detect the
    YAML block-list form, where the inline value after the key is empty."""
    m = re.search(rf"^{re.escape(key)}:[ \t]*(.*)$", fm, re.M)
    return m.group(1).strip() if m else None


def _block_list_entries(fm, key):
    """Collect indented `- ` lines following `key:` when the inline value is empty."""
    lines = fm.split("\n")
    for i, line in enumerate(lines):
        if re.match(rf"^{re.escape(key)}:[ \t]*$", line):
            entries = []
            for follow in lines[i + 1:]:
                m = re.match(r"^[ \t]+-[ \t]*(.+?)\s*$", follow)
                if not m:
                    break
                entries.append(m.group(1).strip().strip("\"'"))
            return entries
    return []


def _decided_from_entries(fm):
    inline = _field(fm, "decided-from")
    if inline:
        stripped = inline.strip("[]")
        return [e.strip().strip("\"'") for e in re.split(r"[,\s]+", stripped) if e.strip().strip("\"'")]
    raw = _field_raw(fm, "decided-from")
    if raw == "":
        return _block_list_entries(fm, "decided-from")
    return []


def _bare_numeric_stem(stem):
    return bool(re.match(r"^\d+\.md$", stem))


def _entry_matches(entry, path, doc_id):
    if entry == path:
        return True
    if doc_id and entry == doc_id:
        return True
    if "/" not in entry:
        basename = path.rsplit("/", 1)[-1]
        if entry == basename and not _bare_numeric_stem(basename):
            return True
    return False


def _cited_by_landed_adr(repo, sha, path, doc_id):
    ls = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "--name-only", sha, "content/adr/"],
                        capture_output=True, text=True).stdout.split()
    for adr in ls:
        if not adr.endswith(".md") or adr.rsplit("/", 1)[-1].startswith("_"):
            continue
        fm = _fm(_show(repo, sha, adr))
        if _field(fm, "status") not in LANDED:
            continue
        entries = _decided_from_entries(fm)
        if any(_entry_matches(e, path, doc_id) for e in entries):
            return True
    return False


def screen_item(repo, sha, path, item_type):
    if item_type not in STRUCTURAL_TYPES:
        return None
    fm = _fm(_show(repo, sha, path))
    if _field(fm, "promoted-to") or _field(fm, "superseded-by"):
        return "REAL"
    if _cited_by_landed_adr(repo, sha, path, _field(fm, "id")):
        return "REAL"
    return None
