#!/usr/bin/env python3
"""Fail-closed invariant tests for candidates.py (run: python3 test_candidates.py).

Proves: append writes exactly one line and never alters prior bytes; no
session id means no write; duplicates refuse; append-disposition rewrites only
the matched record's four disposition fields, once, atomically; malformed
sidecars refuse; discovery sees tracked sidecars only, plus spool rows that are
not yet committed, each tagged by source.
"""
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import candidates as c  # noqa: E402

_fails = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        _fails.append(name)


def raises(fn, needle=""):
    try:
        fn()
        return False
    except c.Refuse as e:
        return needle in str(e)


NOW = datetime(2026, 9, 6, 12, 0, 0, tzinfo=timezone.utc)
SID = "sess-abc"
ART = "content/survey/foo.md"

tmp = tempfile.mkdtemp()
REPO = os.path.join(tmp, "rd")
SPOOL = os.path.join(tmp, "spool")
os.makedirs(os.path.join(REPO, "content", "survey"))
subprocess.run(["git", "-C", REPO, "init", "-q"], check=True)
subprocess.run(["git", "-C", REPO, "config", "user.email", "t@t"], check=True)
subprocess.run(["git", "-C", REPO, "config", "user.name", "t"], check=True)

# --- session id ---------------------------------------------------------------
check("session id from CLAUDE_SESSION_ID", c.resolve_session_id({"CLAUDE_SESSION_ID": "a"}) == "a")
check("fallback to CLAUDE_CODE_SESSION_ID",
      c.resolve_session_id({"CLAUDE_CODE_SESSION_ID": "b"}) == "b")
check("preferred wins over fallback",
      c.resolve_session_id({"CLAUDE_SESSION_ID": "a", "CLAUDE_CODE_SESSION_ID": "b"}) == "a")
check("neither set refuses", raises(lambda: c.resolve_session_id({}), "no session id"))
check("empty string is not a session id",
      raises(lambda: c.resolve_session_id({"CLAUDE_SESSION_ID": "", "CLAUDE_CODE_SESSION_ID": ""}), "no session id"))

# --- make_record --------------------------------------------------------------
r1 = c.make_record(SID, ART, "gather", "Paper One", cid="A1", url="https://arxiv.org/abs/1",
                   sentence="Smith et al. establish X [A1].", source_in_context=False, now=NOW)
check("record has version", r1["version"] == "1.0")
check("record_id is 12 hex", len(r1["record_id"]) == 12 and all(ch in "0123456789abcdef" for ch in r1["record_id"]))
check("disposition starts proposed", r1["disposition"] == "proposed" and r1["disposition_stage"] is None
      and r1["label"] is None and r1["dispositioned_at"] is None)
check("proposed_at ISO UTC seconds", r1["proposed_at"] == "2026-09-06T12:00:00Z")
check("source_meta present with nulls", r1["source_meta"] == {"published_year": None,
                                                              "openalex_cited_by_count": None,
                                                              "reference_class": None})
check("required keys", set(r1) == {"version", "record_id", "session_id", "artifact", "stage", "proposed_at",
                                   "candidate", "sentence", "source_in_context", "source_meta",
                                   "disposition", "disposition_stage", "label", "dispositioned_at"})
check("invalid stage refuses", raises(lambda: c.make_record(SID, ART, "bogus", "t", cid="A1"), "invalid stage"))
check("id-and-url both empty refuses", raises(lambda: c.make_record(SID, ART, "gather", "t"), "at least one"))
check("non-bool source_in_context refuses",
      raises(lambda: c.make_record(SID, ART, "gather", "t", cid="A1", source_in_context=None), "bool"))
check("invalid reference_class refuses",
      raises(lambda: c.make_record(SID, ART, "gather", "t", cid="A1", reference_class="x"), "reference_class"))
check("id-only proposal with empty sentence allowed",
      c.make_record(SID, ART, "recency-probe-candidate", "t", url="arXiv:2510.1", now=NOW)["sentence"] == "")
check("absolute artifact refuses", raises(lambda: c.sidecar_path(REPO, "/etc/x"), "repo-relative"))
check("sidecar path", c.sidecar_path(REPO, ART) == os.path.join(REPO, ART + ".candidates.jsonl"))

# --- append (pure) --------------------------------------------------------------
t1 = c.append_text("", r1)
check("append writes one line", t1.count("\n") == 1 and json.loads(t1) == r1)
check("line is sorted-key JSON", t1 == json.dumps(r1, sort_keys=True, ensure_ascii=False) + "\n")
r2 = c.make_record(SID, ART, "gap-find", "Paper Two", cid="A2", url="https://arxiv.org/abs/2",
                   sentence="Second sentence.", source_in_context=False, now=NOW)
t2 = c.append_text(t1, r2)
check("append preserves prior bytes", t2.startswith(t1) and t2.count("\n") == 2)
check("duplicate refuses", raises(lambda: c.append_text(t2, r1), "duplicate"))
r1b = c.make_record(SID, ART, "gap-find", "Paper One", cid="A1", url="https://arxiv.org/abs/1", now=NOW)
check("same candidate at a different stage is not a duplicate", c.append_text(t2, r1b).count("\n") == 3)
check("malformed line refuses", raises(lambda: c.append_text("{not json\n", r1), "malformed"))
check("blank line refuses", raises(lambda: c.append_text(t1 + "\n", r2), "blank"))
check("missing trailing newline refuses", raises(lambda: c.append_text(t1.rstrip("\n"), r2), "newline"))
check("non-record line refuses", raises(lambda: c.append_text('{"x":1}\n', r2), "not a v1.0"))

# --- append (files, dual-write) ------------------------------------------------
side, spool = c.append(REPO, ART, r1, spool_dir=SPOOL)
check("sidecar created next to artifact", side == os.path.join(REPO, ART + ".candidates.jsonl") and os.path.exists(side))
check("spool created per session", spool == os.path.join(SPOOL, SID + ".jsonl") and os.path.exists(spool))
before = open(side, "rb").read()
c.append(REPO, ART, r2, spool_dir=SPOOL)
after = open(side, "rb").read()
check("file append never rewrites existing bytes", after.startswith(before) and after.count(b"\n") == 2)
check("spool mirrors sidecar", open(spool, "rb").read() == after)
check("duplicate file append refuses and writes nothing",
      raises(lambda: c.append(REPO, ART, r1, spool_dir=SPOOL), "duplicate") and open(side, "rb").read() == after)

# --- disposition (pure) -----------------------------------------------------------
LATER = datetime(2026, 9, 6, 13, 0, 0, tzinfo=timezone.utc)
new, rid = c.disposition_text(t2, "dropped-at-reread", "survey-author", "Major", candidate_id="A1", now=LATER)
check("disposition returns matched record_id", rid == r1["record_id"])
old_lines, new_lines = t2.splitlines(keepends=True), new.splitlines(keepends=True)
check("line count unchanged", len(old_lines) == len(new_lines) == 2)
check("only one line changed", sum(a != b for a, b in zip(old_lines, new_lines)) == 1)
check("other line byte-identical", new_lines[1] == old_lines[1])
d = json.loads(new_lines[0])
check("four disposition fields set", (d["disposition"], d["disposition_stage"], d["label"], d["dispositioned_at"])
      == ("dropped-at-reread", "survey-author", "Major", "2026-09-06T13:00:00Z"))
unchanged = {k: v for k, v in d.items() if k not in c.DISPOSITION_FIELDS}
check("all non-disposition fields untouched", unchanged == {k: v for k, v in r1.items() if k not in c.DISPOSITION_FIELDS})
check("second disposition refuses (write once)",
      raises(lambda: c.disposition_text(new, "landed", "survey-author", None, record_id=rid), "already dispositioned"))
check("no still-proposed match refuses (never fabricate)",
      raises(lambda: c.disposition_text(new, "landed", "survey-author", None, candidate_id="A9"), "no still-proposed"))
check("invalid disposition refuses",
      raises(lambda: c.disposition_text(t2, "proposed", "survey-author", None, candidate_id="A1"), "invalid disposition"))
check("invalid disposition_stage refuses",
      raises(lambda: c.disposition_text(t2, "landed", "someone", None, candidate_id="A1"), "invalid disposition_stage"))
check("invalid label refuses",
      raises(lambda: c.disposition_text(t2, "landed", "survey-author", "Great", candidate_id="A1"), "invalid label"))
check("neither selector refuses",
      raises(lambda: c.disposition_text(t2, "landed", "survey-author", None), "needs --record-id"))
# ambiguity: same candidate proposed twice (two sessions) → must pass --record-id
r1s2 = c.make_record("sess-2", ART, "gather", "Paper One", cid="A1", url="https://arxiv.org/abs/1", now=LATER)
t3 = c.append_text(t2, r1s2)
check("ambiguous candidate-id refuses and names record ids",
      raises(lambda: c.disposition_text(t3, "landed", "survey-author", None, candidate_id="A1"), r1s2["record_id"]))
new3, rid3 = c.disposition_text(t3, "landed", "survey-author", "Exact", record_id=r1s2["record_id"], now=LATER)
check("record-id disambiguates", rid3 == r1s2["record_id"] and new3.splitlines()[0] == t3.splitlines()[0])
check("unknown record-id refuses",
      raises(lambda: c.disposition_text(t3, "landed", "survey-author", None, record_id="000000000000"), "matches 0"))

# --- disposition (files) --------------------------------------------------------
side_before = open(side, "rb").read()
rid_f = c.append_disposition(REPO, ART, "dropped-at-citation-detail-verify", "citation-detail-verify", "Minor",
                             candidate_id="A2", spool_dir=SPOOL, now=LATER)
side_after = open(side, "rb").read()
check("file disposition changes exactly one line",
      side_after.splitlines()[0] == side_before.splitlines()[0] and side_after.splitlines()[1] != side_before.splitlines()[1])
check("spool mirrored the disposition", open(spool, "rb").read() == side_after)
check("no tmp file left behind", not any(n.endswith(".tmp") or ".tmp." in n for n in os.listdir(os.path.dirname(side))))
check("disposition on missing sidecar refuses",
      raises(lambda: c.append_disposition(REPO, "content/nope.md", "landed", "survey-author", None, candidate_id="A1",
                                          spool_dir=SPOOL), "no sidecar"))
check("returned record id", rid_f == r2["record_id"])

# --- discovery -----------------------------------------------------------------
check("untracked sidecar is not sample", c.tracked_sidecars(REPO) == [])
rows = c.list_records(REPO, spool_dir=SPOOL)
check("uncommitted rows surface via spool, tagged", len(rows) == 2 and all(r["source"] == "spool" for r in rows))
subprocess.run(["git", "-C", REPO, "add", "-A"], check=True)
subprocess.run(["git", "-C", REPO, "commit", "-q", "-m", "sidecar"], check=True)
check("tracked sidecar discovered", c.tracked_sidecars(REPO) == [ART + ".candidates.jsonl"])
rows = c.list_records(REPO, spool_dir=SPOOL)
check("committed rows tagged tracked, spool duplicates suppressed",
      len(rows) == 2 and all(r["source"] == "tracked" for r in rows))
check("dispositioned state visible in list", {r["disposition"] for r in rows} == {"proposed", "dropped-at-citation-detail-verify"})
# a spool-only row from an aborted run (another artifact, never committed)
r_abort = c.make_record(SID, "content/notes/aborted.md", "gather", "Ghost", cid="A1", url="u", now=NOW)
c.append(REPO, "content/notes/aborted.md", r_abort, spool_dir=SPOOL)
rows = c.list_records(REPO, spool_dir=SPOOL)
check("spool-only row from uncommitted run kept, tagged spool",
      sum(r["source"] == "spool" for r in rows) == 1 and sum(r["source"] == "tracked" for r in rows) == 2)
check("--tracked-only excludes spool", len(c.list_records(REPO, spool_dir=SPOOL, include_spool=False)) == 2)
check("artifact filter", len(c.list_records(REPO, artifact=ART, spool_dir=SPOOL)) == 2)

# --- CLI: refuse without session id, nothing written ---------------------------
env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID")}
env["CANDIDATES_SPOOL"] = SPOOL
art2 = "content/survey/bar.md"
p = subprocess.run([sys.executable, os.path.join(HERE, "candidates.py"), "append", "--repo", REPO,
                    "--artifact", art2, "--stage", "gather", "--title", "T", "--id", "A1",
                    "--source-in-context", "false"], env=env, capture_output=True, text=True)
check("CLI refuses without session id (exit 2)", p.returncode == 2 and "REFUSE: no session id" in p.stderr)
check("CLI refusal wrote nothing", not os.path.exists(os.path.join(REPO, art2 + ".candidates.jsonl")))
env["CLAUDE_CODE_SESSION_ID"] = "cli-sess"
p = subprocess.run([sys.executable, os.path.join(HERE, "candidates.py"), "append", "--repo", REPO,
                    "--artifact", art2, "--stage", "gather", "--title", "T", "--id", "A1", "--url", "u",
                    "--sentence", "S [A1].", "--source-in-context", "false", "--published-year", "2019",
                    "--cited-by-count", "1500", "--reference-class", "standard-reference"],
                   env=env, capture_output=True, text=True)
check("CLI append succeeds", p.returncode == 0 and len(p.stdout.strip()) == 12)
rec = json.loads(open(os.path.join(REPO, art2 + ".candidates.jsonl")).read())
check("CLI source_meta captured", rec["source_meta"] == {"published_year": 2019, "openalex_cited_by_count": 1500,
                                                         "reference_class": "standard-reference"})
batch = os.path.join(tmp, "batch.json")
json.dump([{"stage": "gap-find", "title": "B1", "id": "A2", "url": "u2", "sentence": "s2", "source_in_context": False},
           {"stage": "gap-find", "title": "B2", "id": "A3", "url": "u3", "sentence": "s3", "source_in_context": False}],
          open(batch, "w"))
p = subprocess.run([sys.executable, os.path.join(HERE, "candidates.py"), "append", "--repo", REPO,
                    "--artifact", art2, "--from-json", batch], env=env, capture_output=True, text=True)
check("CLI batch append writes two records", p.returncode == 0 and len(p.stdout.split()) == 2
      and open(os.path.join(REPO, art2 + ".candidates.jsonl")).read().count("\n") == 3)
p = subprocess.run([sys.executable, os.path.join(HERE, "candidates.py"), "append-disposition", "--repo", REPO,
                    "--artifact", art2, "--candidate-id", "A2", "--disposition", "corrected-at-fullread",
                    "--stage", "load-bearing-fullread", "--label", "Minor"], env=env, capture_output=True, text=True)
check("CLI append-disposition succeeds", p.returncode == 0)
p = subprocess.run([sys.executable, os.path.join(HERE, "candidates.py"), "list", "--repo", REPO, "--artifact", art2],
                   env=env, capture_output=True, text=True)
listed = json.loads(p.stdout)
check("CLI list returns spool rows for uncommitted artifact", len(listed) == 3 and all(r["source"] == "spool" for r in listed))

print()
if _fails:
    print(f"FAILED ({len(_fails)}): {_fails}")
    sys.exit(1)
print("all candidates tests passed")
