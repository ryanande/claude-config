#!/usr/bin/env python3
"""Tests for recheck.py (run: python3 test_recheck.py). Gate legs run over a temp git repo."""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import recheck as rc  # noqa: E402

_fails = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        _fails.append(name)


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True).stdout.strip()


def mkrepo():
    d = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", "-b", "main", d], check=True)
    git(d, "config", "user.email", "t@t"); git(d, "config", "user.name", "t")
    return d


def commit_file(repo, path, text, msg="c"):
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(text)
    git(repo, "add", path); git(repo, "commit", "-q", "-m", msg)
    return git(repo, "rev-parse", "HEAD")


print("cap and precision")
check("cap(53) = 9", rc.cap(53) == 9)
check("cap(100) = 15", rc.cap(100) == 15)
check("cap(1) = 2", rc.cap(1) == 2)
final = {f"i{k}": "REAL" for k in range(60)}
final.update({f"n{k}": "NOISE" for k in range(25)})
final.update({f"u{k}": "UNRESOLVED" for k in range(15)})
check("precision over full census", rc.precision(final, 100) == 0.60)

print("disagreement ordered-3way")
check("REAL/NOISE contradiction", rc.disagree("REAL", "NOISE") == ("UNRESOLVED", False))
check("NOISE/UNRESOLVED needs tiebreak", rc.disagree("NOISE", "UNRESOLVED") == ("NOISE", True))
check("UNRESOLVED/REAL needs tiebreak", rc.disagree("UNRESOLVED", "REAL") == ("REAL", True))
check("both UNRESOLVED stays", rc.disagree("UNRESOLVED", "UNRESOLVED") == ("UNRESOLVED", False))
check("agreement no tiebreak", rc.disagree("NOISE", "NOISE") == ("NOISE", False))
check("tiebreak = X resolves X", rc.apply_tiebreak("NOISE", "NOISE") == "NOISE")
check("tiebreak other leaves UNRESOLVED", rc.apply_tiebreak("NOISE", "REAL") == "UNRESOLVED")
check("tiebreak UNRESOLVED leaves UNRESOLVED", rc.apply_tiebreak("NOISE", "UNRESOLVED") == "UNRESOLVED")

print("gate")
repo = mkrepo()
sha = commit_file(repo, "content/rfc/0010.md", "---\nstatus: draft\n---\nThe two-layer gate is not built yet.\n")
trees = {"https://github.com/o/r.git": (repo, sha)}
cs = [{"type": "rfc", "clause": "RFC clause"}, {"type": "adr", "clause": "ADR clause"}]
ok_label = {"label": "NOISE", "clause": "RFC clause",
            "evidence": [{"remote": "https://github.com/o/r.git", "path": "content/rfc/0010.md",
                          "quote": "not built yet", "what": "x"}]}
check("good label passes", rc.gate_label(ok_label, trees, cs, "rfc") == [])
bad_path = json.loads(json.dumps(ok_label)); bad_path["evidence"][0]["path"] = "content/rfc/9999.md"
check("missing path fails", any("path" in f for f in rc.gate_label(bad_path, trees, cs, "rfc")))
bad_quote = json.loads(json.dumps(ok_label)); bad_quote["evidence"][0]["quote"] = "is built"
check("quote not verbatim fails", any("quote" in f for f in rc.gate_label(bad_quote, trees, cs, "rfc")))
bad_clause = json.loads(json.dumps(ok_label)); bad_clause["clause"] = "ADR clause"
check("clause mismatch fails", any("clause" in f for f in rc.gate_label(bad_clause, trees, cs, "rfc")))
no_quote = json.loads(json.dumps(ok_label)); del no_quote["evidence"][0]["quote"]
check("missing quote fails", any("quote" in f for f in rc.gate_label(no_quote, trees, cs, "rfc")))
bad_remote = json.loads(json.dumps(ok_label)); bad_remote["evidence"][0]["remote"] = "https://github.com/o/other.git"
check("remote not in scope fails", any("remote" in f for f in rc.gate_label(bad_remote, trees, cs, "rfc")))
unres = {"label": "UNRESOLVED", "clause": "RFC clause", "evidence": [], "unresolved_reason": "out-of-scope"}
check("UNRESOLVED with no evidence passes gate", rc.gate_label(unres, trees, cs, "rfc") == [])
real_no_evidence = {"label": "REAL", "clause": "RFC clause", "evidence": []}
check("REAL with empty evidence fails gate with 'no evidence' message",
      any("no evidence" in f for f in rc.gate_label(real_no_evidence, trees, cs, "rfc")))
noise_missing_evidence_key = {"label": "NOISE", "clause": "RFC clause"}
check("NOISE with no evidence key fails gate with 'no evidence' message",
      any("no evidence" in f for f in rc.gate_label(noise_missing_evidence_key, trees, cs, "rfc")))

print("unresolved_source precedence")
check("gate first", rc.unresolved_source({"gate_failures": ["x"], "rederive": "REAL", "final_before": "NOISE"}) == "gate-failure")
check("rederive dissent", rc.unresolved_source({"gate_failures": [], "rederive": "REAL", "final_before": "NOISE"}) == "rederivation-dissent")
check("contradiction", rc.unresolved_source({"gate_failures": [], "a": "REAL", "b": "NOISE"}) == "labeler-contradiction")
check("failed tiebreak", rc.unresolved_source({"gate_failures": [], "a": "NOISE", "b": "UNRESOLVED", "tiebreak": "REAL"}) == "failed-tiebreak")
check("both unresolved", rc.unresolved_source({"gate_failures": [], "a": "UNRESOLVED", "b": "UNRESOLVED",
                                                "reasons": ["out-of-scope", "insufficient-evidence"]}) == "both-unresolved")
check("single labeler reason", rc.unresolved_source({"gate_failures": [], "a": "UNRESOLVED", "b": None,
                                                      "reasons": ["out-of-scope"]}) == "labeler-reason:out-of-scope")

print("ledger")
rows = [
    {"item": "i1", "slot": "A", "attempt": 1, "model": "opus", "spawn-id": "s1", "state": "launched", "trigger": None},
    {"item": "i1", "slot": "A", "attempt": 1, "model": "opus", "spawn-id": "s1", "state": "done",
     "verdict-path": "labels/i1.A.json", "reported-model": "opus"},
    {"item": "i2", "slot": "A", "attempt": 1, "model": "opus", "spawn-id": "s2", "state": "launched", "trigger": None},
    {"item": "i2", "slot": "A", "attempt": 2, "model": "opus", "spawn-id": "s3", "state": "launched", "trigger": "timeout"},
    {"item": "i2", "slot": "A", "attempt": 2, "model": "opus", "spawn-id": "s3", "state": "done",
     "verdict-path": "labels/i2.A.json", "reported-model": "unknown"},
    {"item": "i3", "slot": "B", "attempt": 1, "model": "sonnet", "spawn-id": "s4", "state": "done",
     "verdict-path": "labels/i3.B.json", "reported-model": "opus"},
    {"item": "i4", "slot": "B", "attempt": 1, "model": "sonnet", "spawn-id": "s5", "state": "done"},
]
v = rc.validate_ledger(rows)
check("re-attempted item flagged regardless of trigger", v["flagged_items"] == ["i2"])
check("unknown model recorded as unverified slot", "i2/A" in v["unverified_slots"])
check("model mismatch is an error", any("i3" in e and "model" in e for e in v["errors"]))
check("done without verdict path is an error", any("i4" in e and "verdict" in e for e in v["errors"]))

print("contrast")
prim = {"a": "REAL", "b": "REAL", "c": "NOISE", "d": "NOISE", "e": "NOISE", "f": "UNRESOLVED"}
c = rc.contrast(prim, flagged_other={"a", "b", "c", "f"})
check("noise dropped 2/3", abs(c["noise_dropped"] - 2 / 3) < 1e-9)
check("real dropped 0/2", c["real_dropped"] == 0.0)
check("passes at >=0.10", c["passes"] is True)
c2 = rc.contrast(prim, flagged_other={"c", "d", "e", "f"})
check("dropping only REAL fails", c2["passes"] is False)

print("ancestry and liveness")
repo = mkrepo()
c1 = commit_file(repo, "content/evals/_index.md", "index\n")
# corpus shape (origin/main content/evals/*.md lines 17-18, 200-202): the subject line WRAPS, and an unrun
# document's Findings body reads "Not yet run." — the test must use that shape, not a tidier one
doc = ("---\nid: EVAL-0009\n---\nPre-registered study emitted by `/study-design` for\n"
       "[OQ-0002](/open-questions/0002-staleness-thresholds-per-type/). Provisional id.\n"
       "```yaml\npre-registration:\n  design: D1\n```\n## Findings\n\nNot yet run.\n")
c2 = commit_file(repo, "content/evals/eval-0009.md", doc)
check("freezing commit is ancestor of main", rc.is_ancestor(repo, c2, "main"))
git(repo, "checkout", "-q", "-b", "side"); c3 = commit_file(repo, "x.md", "x\n"); git(repo, "checkout", "-q", "main")
check("side commit is not ancestor of main", not rc.is_ancestor(repo, c3, "main"))
live = rc.live_studies(repo)
check("unrun document is live for its subject OQ", [(l["path"], l["oq"]) for l in live] == [("content/evals/eval-0009.md", "OQ-0002")])
git(repo, "rm", "-q", "content/evals/eval-0009.md"); git(repo, "commit", "-q", "-m", "revert away")
check("removed without withdrawn stays live", len(rc.live_studies(repo)) == 1 and rc.live_studies(repo)[0]["removed"] is True)
commit_file(repo, "content/evals/eval-0010.md", doc.replace("EVAL-0009", "EVAL-0010").replace("---\nid", "---\nwithdrawn: design-flaw-found\nid"))
check("withdrawn document is not live", not any(l["path"].endswith("eval-0010.md") for l in rc.live_studies(repo)))
commit_file(repo, "content/evals/eval-0011.md", doc.replace("EVAL-0009", "EVAL-0011").replace("Not yet run.", "### Run attempt 2026-09-06 (`/study-run`)\n\nverdict: deferred"))
check("document with a ### Run section is not live", not any(l["path"].endswith("eval-0011.md") for l in rc.live_studies(repo)))
commit_file(repo, "content/evals/eval-0012.md", doc.replace("EVAL-0009", "EVAL-0012").replace("Not yet run.", "What surprised us. What didn't."))
check("template placeholder body is still live", any(l["path"].endswith("eval-0012.md") for l in rc.live_studies(repo)))

print("precision on empty census")
check("precision({}, 0) == 0.0", rc.precision({}, 0) == 0.0)

print("ledger malformed row")
rows_bad = [
    {"item": "i5", "slot": "A", "attempt": 1, "model": "opus", "spawn-id": "s6", "state": "done",
     "verdict-path": "labels/i5.A.json", "reported-model": "opus"},
    {"item": "i6", "slot": "A", "state": "done", "verdict-path": "labels/i6.A.json", "reported-model": "opus"},
]
v_bad = rc.validate_ledger(rows_bad)
check("malformed row produces exactly one error naming the missing key",
      sum(1 for e in v_bad["errors"] if "row 1" in e and "attempt" in e) == 1)
check("well-formed row in same ledger still processed", "i5" not in v_bad["flagged_items"] and
      not any("i5" in e for e in v_bad["errors"]))

print("liveness fenced-block safety")
fenced_doc = ("---\nid: EVAL-0013\n---\nPre-registered study emitted by `/study-design` for\n"
              "[OQ-0002](/open-questions/0002-staleness-thresholds-per-type/). Provisional id.\n"
              "```yaml\npre-registration:\n  design: D1\n```\n## Findings\n\nNot yet run.\n\n"
              "Format example:\n```\n### Run attempt 2026-09-06 (`/study-run`)\n```\n")
commit_file(repo, "content/evals/eval-0013.md", fenced_doc)
check("unrun doc with fenced ### Run example stays live",
      any(l["path"].endswith("eval-0013.md") for l in rc.live_studies(repo)))
real_run_doc = fenced_doc.replace("EVAL-0013", "EVAL-0014").replace(
    "Not yet run.", "### Run attempt 2026-09-06 (`/study-run`)\n\nverdict: deferred")
commit_file(repo, "content/evals/eval-0014.md", real_run_doc)
check("doc with real unfenced ### Run subsection is not live",
      not any(l["path"].endswith("eval-0014.md") for l in rc.live_studies(repo)))

print("D2/D3 gate reuse — the single-entry \"*\" rule set")
d2repo = mkrepo()
d2sha = commit_file(d2repo, "test-corpus/seeded-a.md", "line one\nthe title is wrong here\nline three\n")
trees_star = {"https://x/corpus.git": (d2repo, d2sha)}
cs_star = [{"type": "*", "clause": rc.MATCH_RULE}]
label_ok = {"label": "REAL", "clause": rc.MATCH_RULE,
            "evidence": [{"remote": "https://x/corpus.git", "path": "test-corpus/seeded-a.md",
                          "quote": "the title is wrong here", "what": "the row describes this defect"}]}
check("wildcard rule set gates a well-formed D2 residual label",
      rc.gate_label(label_ok, trees_star, cs_star, "*") == [])
check("a residual REAL label with no evidence fails the gate",
      any("no evidence" in e for e in rc.gate_label(
          {"label": "REAL", "clause": rc.MATCH_RULE, "evidence": []}, trees_star, cs_star, "*")))
check("a clause that is not the frozen match-rule fails the gate",
      any("clause-set row" in e for e in rc.gate_label(
          dict(label_ok, clause="something else"), trees_star, cs_star, "*")))
check("an item type absent from the rule set fails the gate",
      any("no row for type" in e for e in rc.gate_label(label_ok, trees_star, cs_star, "rfc")))

print("D2 match — region overlap and class equality")
manifest = [
    {"item_id": "d1", "path": "a.md", "region": [10, 20], "class": "dead-url", "planted": True},
    {"item_id": "d2", "path": "a.md", "region": [40, 50], "class": "title-drift", "planted": True},
    {"item_id": "d3", "path": "b.md", "region": [10, 20], "class": "dead-url", "planted": True},
    {"item_id": "c1", "path": "a.md", "region": [80, 90], "class": "dead-url", "planted": False},
]
rows = [
    {"path": "a.md", "region": [15, 25], "class": "dead-url"},      # matches d1
    {"path": "a.md", "region": [82, 84], "class": "dead-url"},      # over a clean control
    {"path": "a.md", "region": [41, 42], "class": "dead-url"},      # right region, wrong class -> residual
]
m = rc.match(rows, manifest)
check("overlapping same-class row matches its planted defect", m["matched"] == [{"row": 0, "item_id": "d1"}])
check("a row over a clean control is a false positive", m["false_positives"] == [1])
check("a wrong-class row over a planted region is residual, not a false positive", m["residual_rows"] == [2])
check("unmatched planted defects are false negatives", m["false_negatives"] == ["d2", "d3"])
check("only a path-adjacent unmatched defect is residual", m["residual_defects"] == ["d2"])
check("a defect on a path with no unmatched row is a decided false negative, never adjudicated",
      "d3" in m["false_negatives"] and "d3" not in m["residual_defects"])
check("a single shared line counts as overlap",
      rc.match([{"path": "a.md", "region": [19, 30], "class": "dead-url"}], manifest)["matched"] != [])
check("an adjacent non-overlapping range does not match",
      rc.match([{"path": "a.md", "region": [20, 30], "class": "dead-url"}], manifest)["matched"] == [])
check("a row on another path does not match its class-mate",
      rc.match([{"path": "c.md", "region": [15, 25], "class": "dead-url"}], manifest)["matched"] == [])

print("D2 manifest_check")
classes_ok = [{"class": "dead-url", "planted": 2, "clean-controls": 1},
              {"class": "title-drift", "planted": 1, "clean-controls": 0}]
mrepo = mkrepo()
msha = commit_file(mrepo, "a.md", "x\n")
commit_file(mrepo, "b.md", "y\n")
msha = git(mrepo, "rev-parse", "HEAD")
mpath = os.path.join(mrepo, "manifest.json")
open(mpath, "w").write(json.dumps(manifest))
digest = rc.manifest_sha256(mpath)
mc = rc.manifest_check(manifest, classes_ok, mrepo, msha, expect_sha256=digest,
                       manifest_path=mpath, skill_runs=2)
check("manifest_check passes on a frozen, well-formed manifest", mc["errors"] == [])
check("manifest_check counts distinct artifacts", mc["artifacts"] == 2)
check("a manifest edited after freeze is refused by sha256",
      any("sha256" in e for e in rc.manifest_check(manifest, classes_ok, mrepo, msha,
          expect_sha256="0" * 64, manifest_path=mpath, skill_runs=2)["errors"]))
check("an expected sha256 with no file to hash is refused, never skipped",
      any("no manifest path" in e for e in rc.manifest_check(manifest, classes_ok, mrepo, msha,
          expect_sha256=digest, manifest_path=None, skill_runs=2)["errors"]))
check("skill-runs unequal to the distinct artifact count is refused",
      any("skill-runs" in e for e in rc.manifest_check(manifest, classes_ok, mrepo, msha,
          expect_sha256=digest, manifest_path=mpath, skill_runs=9)["errors"]))
check("a zero-planted class is refused",
      any("planted: 0" in e for e in rc.manifest_check(
          manifest + [{"item_id": "c2", "path": "a.md", "region": [95, 99], "class": "anchor", "planted": False}],
          classes_ok + [{"class": "anchor", "planted": 0, "clean-controls": 1}], mrepo, msha)["errors"]))
check("a count mismatch against the manifest is refused",
      any("!= manifest" in e for e in rc.manifest_check(
          manifest, [{"class": "dead-url", "planted": 5, "clean-controls": 1},
                     {"class": "title-drift", "planted": 1, "clean-controls": 0}], mrepo, msha)["errors"]))
check("a manifest class absent from defect-classes is refused",
      any("absent from defect-classes" in e for e in rc.manifest_check(
          manifest, [{"class": "dead-url", "planted": 2, "clean-controls": 1}], mrepo, msha)["errors"]))
check("a manifest path absent at the pinned sha is refused",
      any("path absent at" in e for e in rc.manifest_check(
          [dict(manifest[0], path="gone.md")], [{"class": "dead-url", "planted": 1, "clean-controls": 0}],
          mrepo, msha)["errors"]))
check("a degenerate region is refused — it could never overlap, hiding false positives",
      any("start < end" in e for e in rc.manifest_check(
          [dict(manifest[3], region=[80, 80])], classes_ok, mrepo, msha)["errors"]))
check("a non-integer region is refused",
      any("start < end" in e for e in rc.manifest_check(
          [dict(manifest[3], region="lines 1-5")], classes_ok, mrepo, msha)["errors"]))
check("a duplicate item_id is refused — it inflates the class counts",
      any("duplicate manifest item_id" in e for e in rc.manifest_check(
          manifest + [manifest[0]], classes_ok, mrepo, msha)["errors"]))

print("D2 blindness — repository granularity is not sufficient")
PUB = "https://github.com/o/research-docs.git"
CORPUS = "https://github.com/o/research-skills.git"
scoped = [{"remote": CORPUS, "ref": "072ddd2", "path": "skills/x/test-corpus/seeded/"}]
check("a path-scoped corpus-only blind scope passes", rc.blind_scope_check(scoped, PUB)["ok"])
check("a blind scope carrying the publication remote is refused",
      not rc.blind_scope_check(scoped + [{"remote": PUB, "ref": "a", "path": "p"}], PUB)["ok"])
check("an unscoped blind-scope entry is refused — the whole repo leaks sibling paths",
      any("not path-scoped" in e for e in rc.blind_scope_check(
          [{"remote": CORPUS, "ref": "072ddd2"}], PUB)["errors"]))
check("a blind-scope entry with no pinned ref is refused",
      any("no pinned ref" in e for e in rc.blind_scope_check(
          [{"remote": CORPUS, "path": "p"}], PUB)["errors"]))
export_with_history = mkrepo()
check("an export carrying .git is refused — history reveals the planted commit",
      any(".git" in e for e in rc.blind_scope_check(scoped, PUB, [export_with_history])["errors"]))
clean_export = tempfile.mkdtemp()
open(os.path.join(clean_export, "seeded-a.md"), "w").write("x\n")
check("a history-free export passes", rc.blind_scope_check(scoped, PUB, [clean_export])["ok"])

print("D3 arm hygiene")
ARMS = ["mandatory-critic", "optional-critic"]
check("well-formed arm tokens validate", rc.validate_arms(ARMS)["ok"])
check("a short arm token is refused — arm_leak would over-trigger",
      any("shorter than" in e for e in rc.validate_arms(["A", "B"])["errors"]))
check("a common-word arm token is refused",
      any("common word" in e for e in rc.validate_arms(["optional", "mandatory-critic"])["errors"]))
check("three arms are refused", not rc.validate_arms(["a", "b", "c"])["ok"])
check("arm tokens differing only by case are refused",
      any("only by case" in e for e in rc.validate_arms(["Alpha-arm", "alpha-arm"])["errors"]))

print("D3 arm assignment — keyed on the freezing commit, not an author salt")
KEY = "7624ca8135783f663ce54419f3f62bd2aebac7be"
check("assign_arm is deterministic", rc.assign_arm("PR-101", KEY, ARMS) == rc.assign_arm("PR-101", KEY, ARMS))
check("assign_arm returns one of the named arms", rc.assign_arm("PR-101", KEY, ARMS) in ARMS)
check("both arms are reachable across identifiers",
      len({rc.assign_arm(f"PR-{i}", KEY, ARMS) for i in range(40)}) == 2)
check("a different freezing commit can move an identifier's arm",
      any(rc.assign_arm("PR-101", f"{i:040x}", ARMS) != rc.assign_arm("PR-101", KEY, ARMS)
          for i in range(8)))
for bad, why in (("", "empty key"), ("ab" * 8, "short key"), ("z" * 40, "non-hex key")):
    try:
        rc.assign_arm("PR-1", bad, ARMS)
        check(f"{why} is refused", False)
    except ValueError:
        check(f"{why} is refused", True)
try:
    rc.assign_arm("PR-1", KEY, ["A", "B"])
    check("assign_arm refuses invalid arms", False)
except ValueError:
    check("assign_arm refuses invalid arms", True)

print("D3 enrolment ledger")
MODE = "hmac-sha256-parity"
led = [{"identifier": f"PR-{i}", "arm": rc.assign_arm(f"PR-{i}", KEY, ARMS)} for i in range(1, 4)]
check("an append-only ledger with reproducible arms validates",
      rc.validate_enrolment(led, led[:2], MODE, KEY, ARMS)["errors"] == [])
v_all = rc.validate_enrolment(led, [], MODE, KEY, ARMS)
check("validate_enrolment reports the row count and last identifier",
      v_all["rows"] == 3 and v_all["last_identifier"] == "PR-3")
check("an unimplemented arm mode is refused, not assumed to be HMAC parity",
      any("not implemented" in e for e in rc.validate_enrolment(led, [], "coin-flip", KEY, ARMS)["errors"]))
check("a hand-edited arm is refused",
      any("!= recomputed" in e for e in rc.validate_enrolment(
          [dict(led[0], arm=ARMS[0] if led[0]["arm"] == ARMS[1] else ARMS[1])] + led[1:],
          [], MODE, KEY, ARMS)["errors"]))
check("a rewritten prior row is refused",
      any("changed after it was appended" in e for e in rc.validate_enrolment(
          [{"identifier": "PR-9", "arm": rc.assign_arm("PR-9", KEY, ARMS)}] + led[1:],
          led[:2], MODE, KEY, ARMS)["errors"]))
check("a shrunken ledger is refused",
      any("shrank" in e for e in rc.validate_enrolment(led[:1], led, MODE, KEY, ARMS)["errors"]))
check("a ledger rewritten down to one hand-picked row is refused against its real prior",
      rc.validate_enrolment([led[2]], led, MODE, KEY, ARMS)["errors"] != [])
check("a duplicate identifier is refused",
      any("duplicate identifier" in e for e in rc.validate_enrolment(led + [led[0]], [], MODE, KEY, ARMS)["errors"]))
check("an enrolment row carrying an outcome is refused — that is the peek channel",
      any("outcomes are read at score time" in e for e in rc.validate_enrolment(
          [dict(led[0], outcome="escaped")] + led[1:], [], MODE, KEY, ARMS)["errors"]))
check("an enrolment row carrying an arm split is refused",
      any("arm_split" in e for e in rc.validate_enrolment(
          [dict(led[0], arm_split={"a": 1})] + led[1:], [], MODE, KEY, ARMS)["errors"]))
gapped = [led[0], led[2]]
check("a skipped identifier is reported as a gap, not silently accepted",
      rc.validate_enrolment(gapped, [], MODE, KEY, ARMS)["gaps"] == [2])
check("a contiguous ledger reports no gaps", v_all["gaps"] == [])

print("D3 phase derivation")
check("an unreached target before the deadline is enrol",
      rc.derive_phase(led, 60, "2027-01-01", "2026-09-07") == "enrol")
check("a reached target is score", rc.derive_phase(led, 3, "2027-01-01", "2026-09-07") == "score")
check("a passed deadline is score even under target",
      rc.derive_phase(led, 60, "2026-09-01", "2026-09-07") == "score")
check("the deadline itself is score", rc.derive_phase(led, 60, "2026-09-07", "2026-09-07") == "score")
check("a validated ledger's own row count drives the phase",
      rc.derive_phase(led, 3, "2027-01-01", "2026-09-07", validation=v_all) == "score")
padded = led + [{} for _ in range(60)]
v_bad_led = rc.validate_enrolment(padded, [], MODE, KEY, ARMS)
try:
    rc.derive_phase(padded, 60, "2027-01-01", "2026-09-07", validation=v_bad_led)
    check("a ledger padded with empty rows cannot derive a score phase", False)
except ValueError:
    check("a ledger padded with empty rows cannot derive a score phase", True)

print("D3 arm-leak gate leg")
check("a rationale naming neither arm passes",
      rc.arm_leak({"rationale": "the follow-up commit reverts the change"}, ARMS)["ok"])
check("a rationale naming an arm is refused",
      not rc.arm_leak({"rationale": "this PR was in the mandatory-critic group"}, ARMS)["ok"])
check("an arm named inside an evidence quote is refused",
      not rc.arm_leak({"rationale": "clean", "evidence": [{"quote": "the optional-critic path"}]}, ARMS)["ok"])
check("an arm named in a field no key-list scan would reach is refused",
      not rc.arm_leak({"rationale": "clean", "notes": "mandatory-critic", "unresolved_reason": None}, ARMS)["ok"])
check("an arm named in an evidence path is refused",
      not rc.arm_leak({"rationale": "clean",
                       "evidence": [{"path": "docs/optional-critic.md", "quote": "x"}]}, ARMS)["ok"])
check("the frozen clause text is excluded from the scan, so it cannot fail every label",
      rc.arm_leak({"rationale": "clean", "clause": "did the mandatory-critic arm reduce escapes?"}, ARMS)["ok"])

print("stdlib only")
check("recheck.py imports only standard-library modules",
      set(re.findall(r"^import (\w+)", open(os.path.join(HERE, "recheck.py")).read(), re.M))
      <= {"argparse", "datetime", "hashlib", "hmac", "json", "math", "os", "re", "subprocess", "sys"})

print(f"\n{len(_fails)} failure(s)")
sys.exit(1 if _fails else 0)
