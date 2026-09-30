#!/usr/bin/env python3
"""Proposal-time citation-candidate capture — stdlib-only, fail-closed.

Writes the `candidates.jsonl` sidecar that EVAL-0001 / EVAL-0002 in
research-docs sample from. One JSON object per proposed candidate; a verify
stage later fills the four disposition fields of that one record, exactly once.
The record contract, sidecar location, and discovery rule are locked in
`../references/candidates-contract.md`; this file is the executable form.

Dual-write: every record lands in (a) the artifact sidecar
`<repo>/<artifact>.candidates.jsonl` — the committed, reviewable record — and
(b) a machine-local per-session spool `<spool>/<session_id>.jsonl` that
survives an aborted run whose worktree is torn down before commit.

Pure functions take + return text/dicts; the CLI wraps them:

  python3 candidates.py append --repo <root> --artifact <path> --stage gather \
      --title "<t>" [--id A12] [--url <u>] [--sentence "<s>"] \
      --source-in-context false [--published-year N] [--cited-by-count N] \
      [--reference-class standard-reference|arxiv-preprint|other]
  python3 candidates.py append --repo <root> --artifact <path> --from-json <file>
  python3 candidates.py append-disposition --repo <root> --artifact <path> \
      (--record-id <id> | --candidate-id <id> [--url <u>]) \
      --disposition dropped-at-reread --stage oq-resolver [--label Major]
  python3 candidates.py list --repo <root> [--artifact <path>]

Refusals exit 2 with `REFUSE: <reason>` on stderr and write nothing.
Invariant tests: `python3 test_candidates.py`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

VERSION = "1.0"
SUFFIX = ".candidates.jsonl"
DEFAULT_SPOOL = "~/.claude/skills/citation-detail-verify/candidates"

STAGES = ("gather", "gap-find", "recency-probe-candidate", "other")
DISPOSITIONS = (
    "proposed",
    "dropped-at-reread",
    "dropped-at-citation-detail-verify",
    "corrected-at-fullread",
    "landed",
    "withdrawn",
)
DISPOSITION_STAGES = (
    "survey-author",
    "oq-resolver",
    "citation-detail-verify",
    "load-bearing-fullread",
)
LABELS = ("Exact", "Minor", "Major")
REFERENCE_CLASSES = ("standard-reference", "arxiv-preprint", "other")
DISPOSITION_FIELDS = ("disposition", "disposition_stage", "label", "dispositioned_at")


class Refuse(Exception):
    """A fail-closed refusal. Nothing has been written when this is raised."""


# --------------------------------------------------------------------------
# session id
# --------------------------------------------------------------------------

def resolve_session_id(env: Optional[Dict[str, str]] = None) -> str:
    """Same read order as cache-contract.md §meta.json shape. Empty-string is
    NOT a session id — it would match every other empty entry."""
    env = os.environ if env is None else env
    for key in ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID"):
        val = env.get(key, "")
        if val:
            return val
    raise Refuse("no session id: neither CLAUDE_SESSION_ID nor CLAUDE_CODE_SESSION_ID is set")


# --------------------------------------------------------------------------
# paths
# --------------------------------------------------------------------------

def sidecar_path(repo: str, artifact: str) -> str:
    if os.path.isabs(artifact) or artifact.startswith(".."):
        raise Refuse(f"artifact must be a repo-relative path, got {artifact!r}")
    return os.path.join(repo, artifact + SUFFIX)


def spool_path(session_id: str, spool_dir: Optional[str] = None) -> str:
    base = spool_dir or os.environ.get("CANDIDATES_SPOOL") or DEFAULT_SPOOL
    return os.path.join(os.path.expanduser(base), session_id + ".jsonl")


# --------------------------------------------------------------------------
# records
# --------------------------------------------------------------------------

def _now_iso(now: Optional[datetime]) -> str:
    dt = now or datetime.now(timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record_id_for(session_id: str, artifact: str, stage: str, cid: str, url: str, proposed_at: str) -> str:
    raw = "|".join([session_id, artifact, stage, cid, url, proposed_at])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def make_record(session_id: str, artifact: str, stage: str, title: str, cid: str = "",
                url: str = "", sentence: str = "", source_in_context: bool = False,
                published_year: Optional[int] = None, cited_by_count: Optional[int] = None,
                reference_class: Optional[str] = None, now: Optional[datetime] = None) -> dict:
    """Build one `proposed` record. Raises Refuse on any invalid input."""
    if stage not in STAGES:
        raise Refuse(f"invalid stage {stage!r}; one of {list(STAGES)}")
    if not (cid or url):
        raise Refuse("a candidate needs at least one of id / url_or_identifier")
    if not isinstance(source_in_context, bool):
        raise Refuse("source_in_context must be a bool")
    if reference_class is not None and reference_class not in REFERENCE_CLASSES:
        raise Refuse(f"invalid reference_class {reference_class!r}; one of {list(REFERENCE_CLASSES)}")
    proposed_at = _now_iso(now)
    return {
        "version": VERSION,
        "record_id": record_id_for(session_id, artifact, stage, cid, url, proposed_at),
        "session_id": session_id,
        "artifact": artifact,
        "stage": stage,
        "proposed_at": proposed_at,
        "candidate": {"id": cid, "title": title, "url_or_identifier": url},
        "sentence": sentence,
        "source_in_context": source_in_context,
        "source_meta": {
            "published_year": published_year,
            "openalex_cited_by_count": cited_by_count,
            "reference_class": reference_class,
        },
        "disposition": "proposed",
        "disposition_stage": None,
        "label": None,
        "dispositioned_at": None,
    }


def dumps(rec: dict) -> str:
    return json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n"


def parse_lines(text: str) -> List[dict]:
    """Parse a sidecar. A malformed line is a refusal — never silently skipped."""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            raise Refuse(f"blank line {n} in sidecar; refusing to write")
        try:
            rec = json.loads(line)
        except ValueError as e:
            raise Refuse(f"malformed line {n} in sidecar ({e}); refusing to write")
        if not isinstance(rec, dict) or rec.get("version") != VERSION or "record_id" not in rec:
            raise Refuse(f"line {n} is not a v{VERSION} candidate record; refusing to write")
        out.append(rec)
    return out


def _read(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def _is_dup(existing: List[dict], rec: dict) -> bool:
    c = rec["candidate"]
    for e in existing:
        ec = e["candidate"]
        if (e["session_id"] == rec["session_id"] and e["stage"] == rec["stage"]
                and ec["id"] == c["id"] and ec["url_or_identifier"] == c["url_or_identifier"]):
            return True
    return False


def append_text(text: str, rec: dict) -> str:
    """Pure: return `text` + one record line. Refuses a duplicate. Existing
    bytes are never altered (the caller appends the difference)."""
    existing = parse_lines(text)
    if _is_dup(existing, rec):
        raise Refuse("duplicate: same session, stage, id and url already recorded")
    if text and not text.endswith("\n"):
        raise Refuse("sidecar does not end with a newline; refusing to append")
    return text + dumps(rec)


def _append_file(path: str, rec: dict) -> None:
    text = _read(path)
    new = append_text(text, rec)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(new[len(text):])
        f.flush()
        os.fsync(f.fileno())


def append(repo: str, artifact: str, rec: dict, spool_dir: Optional[str] = None) -> Tuple[str, str]:
    """Dual-write one record: artifact sidecar first, then the session spool.
    Both refusals are checked before either file is touched."""
    side = sidecar_path(repo, artifact)
    spool = spool_path(rec["session_id"], spool_dir)
    append_text(_read(side), rec)  # refusal check, no write
    append_text(_read(spool), rec)
    _append_file(side, rec)
    _append_file(spool, rec)
    return side, spool


# --------------------------------------------------------------------------
# disposition
# --------------------------------------------------------------------------

def select_record(records: List[dict], record_id: Optional[str] = None,
                  candidate_id: Optional[str] = None, url: Optional[str] = None) -> dict:
    """Exactly one still-`proposed` record must match, else refuse."""
    if record_id:
        hits = [r for r in records if r["record_id"] == record_id]
        if len(hits) != 1:
            raise Refuse(f"record_id {record_id!r} matches {len(hits)} records (expected 1)")
    else:
        if not (candidate_id or url):
            raise Refuse("append-disposition needs --record-id or --candidate-id/--url")
        hits = [r for r in records
                if (not candidate_id or r["candidate"]["id"] == candidate_id)
                and (not url or r["candidate"]["url_or_identifier"] == url)
                and r["disposition"] == "proposed"]
        if len(hits) == 0:
            raise Refuse("no still-proposed record matches; a disposition is never fabricated")
        if len(hits) > 1:
            ids = ",".join(r["record_id"] for r in hits)
            raise Refuse(f"ambiguous: {len(hits)} still-proposed records match ({ids}); pass --record-id")
    rec = hits[0]
    if rec["disposition"] != "proposed":
        raise Refuse(f"record {rec['record_id']} already dispositioned "
                     f"({rec['disposition']}); a disposition is written once, never overwritten")
    return rec


def disposition_text(text: str, disposition: str, stage: str, label: Optional[str],
                     record_id: Optional[str] = None, candidate_id: Optional[str] = None,
                     url: Optional[str] = None, now: Optional[datetime] = None) -> Tuple[str, str]:
    """Pure: return (new_text, record_id) with ONLY the matched record's four
    disposition fields rewritten. Every other line is byte-identical."""
    if disposition not in DISPOSITIONS or disposition == "proposed":
        raise Refuse(f"invalid disposition {disposition!r}; one of {[d for d in DISPOSITIONS if d != 'proposed']}")
    if stage not in DISPOSITION_STAGES:
        raise Refuse(f"invalid disposition_stage {stage!r}; one of {list(DISPOSITION_STAGES)}")
    if label is not None and label not in LABELS:
        raise Refuse(f"invalid label {label!r}; one of {list(LABELS)}")
    records = parse_lines(text)
    target = select_record(records, record_id, candidate_id, url)
    lines = text.splitlines(keepends=True)
    out = []
    for line, rec in zip(lines, records):
        if rec is target:
            new = dict(rec)
            new.update({"disposition": disposition, "disposition_stage": stage,
                        "label": label, "dispositioned_at": _now_iso(now)})
            out.append(dumps(new))
        else:
            out.append(line)
    return "".join(out), target["record_id"]


def _atomic_write(path: str, text: str) -> None:
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def append_disposition(repo: str, artifact: str, disposition: str, stage: str, label: Optional[str],
                       record_id: Optional[str] = None, candidate_id: Optional[str] = None,
                       url: Optional[str] = None, spool_dir: Optional[str] = None,
                       now: Optional[datetime] = None) -> str:
    """Disposition the one matched record in the sidecar, then mirror the same
    record in its session spool (spool miss is tolerated: the spool is a
    safety net, the sidecar is the record). Returns the record_id."""
    side = sidecar_path(repo, artifact)
    text = _read(side)
    if not text:
        raise Refuse(f"no sidecar at {side}; a disposition is never fabricated")
    new_text, rid = disposition_text(text, disposition, stage, label, record_id, candidate_id, url, now)
    _atomic_write(side, new_text)
    rec = next(r for r in parse_lines(new_text) if r["record_id"] == rid)
    spool = spool_path(rec["session_id"], spool_dir)
    spool_text = _read(spool)
    if spool_text:
        try:
            spool_new, _ = disposition_text(spool_text, disposition, stage, label, record_id=rid, now=now)
            _atomic_write(spool, spool_new)
        except Refuse:
            pass  # record not spooled here (other machine) or already mirrored
    return rid


# --------------------------------------------------------------------------
# discovery (study-run Step 5)
# --------------------------------------------------------------------------

def tracked_sidecars(repo: str) -> List[str]:
    """Discovery rule: sidecars TRACKED at HEAD of the research-docs checkout.
    Untracked or uncommitted sidecars are not sample."""
    out = subprocess.run(["git", "-C", repo, "ls-files", "--", "*" + SUFFIX],
                         capture_output=True, text=True, check=True).stdout
    return sorted(p for p in out.splitlines() if p)


def list_records(repo: str, artifact: Optional[str] = None, spool_dir: Optional[str] = None,
                 include_spool: bool = True) -> List[dict]:
    """Tracked-sidecar records (source=tracked) plus spool records not already
    committed (source=spool). Never pooled silently: `source` tags each row."""
    seen = set()
    out = []
    for rel in tracked_sidecars(repo):
        if artifact and rel != artifact + SUFFIX:
            continue
        for rec in parse_lines(_read(os.path.join(repo, rel))):
            seen.add(rec["record_id"])
            row = dict(rec)
            row["source"] = "tracked"
            row["sidecar"] = rel
            out.append(row)
    if include_spool:
        base = os.path.expanduser(spool_dir or os.environ.get("CANDIDATES_SPOOL") or DEFAULT_SPOOL)
        if os.path.isdir(base):
            for name in sorted(os.listdir(base)):
                if not name.endswith(".jsonl"):
                    continue
                for rec in parse_lines(_read(os.path.join(base, name))):
                    if rec["record_id"] in seen:
                        continue
                    if artifact and rec["artifact"] != artifact:
                        continue
                    row = dict(rec)
                    row["source"] = "spool"
                    row["sidecar"] = os.path.join(base, name)
                    out.append(row)
    return out


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _bool(s: str) -> bool:
    if s in ("true", "True", "1"):
        return True
    if s in ("false", "False", "0"):
        return False
    raise argparse.ArgumentTypeError("expected true|false")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="candidates.jsonl sidecar helper (fail-closed)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("append", help="record one proposed candidate (or a JSON batch)")
    a.add_argument("--repo", required=True, help="research-docs checkout root (worktree ok)")
    a.add_argument("--artifact", required=True, help="repo-relative path of the artifact")
    a.add_argument("--stage", choices=STAGES)
    a.add_argument("--title", default="")
    a.add_argument("--id", default="", dest="cid")
    a.add_argument("--url", default="")
    a.add_argument("--sentence", default="")
    a.add_argument("--source-in-context", type=_bool, default=None)
    a.add_argument("--published-year", type=int, default=None)
    a.add_argument("--cited-by-count", type=int, default=None)
    a.add_argument("--reference-class", choices=REFERENCE_CLASSES, default=None)
    a.add_argument("--from-json", help="file holding a JSON array of candidate objects "
                                       "(stage,title,id,url,sentence,source_in_context,"
                                       "published_year,cited_by_count,reference_class)")
    a.add_argument("--spool-dir", default=None)

    d = sub.add_parser("append-disposition", help="disposition ONE still-proposed record")
    d.add_argument("--repo", required=True)
    d.add_argument("--artifact", required=True)
    d.add_argument("--record-id", default=None)
    d.add_argument("--candidate-id", default=None)
    d.add_argument("--url", default=None)
    d.add_argument("--disposition", required=True, choices=[x for x in DISPOSITIONS if x != "proposed"])
    d.add_argument("--stage", required=True, choices=DISPOSITION_STAGES)
    d.add_argument("--label", choices=LABELS, default=None)
    d.add_argument("--spool-dir", default=None)

    ls = sub.add_parser("list", help="discover records (tracked sidecars + uncommitted spool)")
    ls.add_argument("--repo", required=True)
    ls.add_argument("--artifact", default=None)
    ls.add_argument("--spool-dir", default=None)
    ls.add_argument("--tracked-only", action="store_true")

    args = ap.parse_args(argv)
    try:
        if args.cmd == "append":
            session_id = resolve_session_id()
            if args.from_json:
                with open(args.from_json, encoding="utf-8") as f:
                    batch = json.load(f)
                if not isinstance(batch, list):
                    raise Refuse("--from-json must hold a JSON array")
                items = batch
            else:
                if args.stage is None or args.source_in_context is None:
                    raise Refuse("--stage and --source-in-context are required without --from-json")
                items = [{"stage": args.stage, "title": args.title, "id": args.cid, "url": args.url,
                          "sentence": args.sentence, "source_in_context": args.source_in_context,
                          "published_year": args.published_year, "cited_by_count": args.cited_by_count,
                          "reference_class": args.reference_class}]
            recs = [make_record(session_id, args.artifact, it.get("stage", ""), it.get("title", ""),
                                it.get("id", "") or "", it.get("url", "") or "", it.get("sentence", "") or "",
                                it.get("source_in_context", None) if "source_in_context" in it else None,
                                it.get("published_year"), it.get("cited_by_count"), it.get("reference_class"))
                    for it in items]
            for rec in recs:
                append(args.repo, args.artifact, rec, args.spool_dir)
                print(rec["record_id"])
        elif args.cmd == "append-disposition":
            resolve_session_id()  # a disposition is also a session-attributed write
            rid = append_disposition(args.repo, args.artifact, args.disposition, args.stage, args.label,
                                     args.record_id, args.candidate_id, args.url, args.spool_dir)
            print(rid)
        elif args.cmd == "list":
            rows = list_records(args.repo, args.artifact, args.spool_dir, include_spool=not args.tracked_only)
            json.dump(rows, sys.stdout, sort_keys=True, ensure_ascii=False, indent=1)
            sys.stdout.write("\n")
    except Refuse as e:
        sys.stderr.write(f"REFUSE: {e}\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
