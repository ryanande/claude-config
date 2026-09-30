#!/usr/bin/env python3
"""recheck.py — study-run's mechanical checks. The runner adjudicates nothing; this does.

Pure functions plus git-backed helpers. Behaviour pinned by test_recheck.py.
Design: docs/superpowers/specs/2026-09-06-study-skills-eval-0003-retro-design.md §3
(cap, ordered-3way, gate+rederive, ledger, precision-contrast, liveness) and
docs/superpowers/specs/2026-09-07-d2-d3-protocol-keys-design.md (D2 match and
manifest legs, D3 arm assignment, enrolment ledger, phase derivation, arm leak).
"""
import argparse
import datetime
import hashlib
import hmac
import json
import math
import os
import re
import subprocess
import sys

LABELS = ("REAL", "NOISE", "UNRESOLVED")
# D2 `protocol.match-rule` carries this text verbatim into the frozen block, exactly as
# screen.py's CLAUSES carry D1's per-type clause text. `match` names the mode; this is its rule.
MATCH_RULE = (
    "An emitted row matches a planted defect when its path equals the defect's path, its "
    "line range overlaps the defect's region by at least one line, and its class equals the "
    "defect's class. A row matching no defect over a clean region is a false positive; a "
    "defect matched by no row is a false negative. Anything else is residual and is "
    "adjudicated: does the emitted row describe this planted defect?"
)
ARM_MODES = ("hmac-sha256-parity",)
PHASES = ("enrol", "score")
# An arm token is scanned for literally by arm_leak, so a short or common word
# over-triggers on ordinary review prose and drives a whole run to UNRESOLVED —
# a freeze-time lever. Refused at design time and re-checked here.
ARM_TOKEN_MIN = 4
ARM_TOKEN_DENY = {"real", "noise", "true", "false", "none", "null", "yes", "no",
                  "path", "line", "quote", "item", "arm", "test", "main", "code",
                  "optional", "required", "changed", "added", "removed"}
PRECEDENCE = ["gate-failure", "rederivation-dissent", "labeler-contradiction",
              "failed-tiebreak", "both-unresolved"]
# the real corpus wraps this phrase across a line break ("…for\n[OQ-0002](…)") — whitespace-tolerant by design
SUBJECT_RE = re.compile(r"emitted\s+by\s+`/study-design`\s+for\s+\[(OQ-\d{4})\]", re.I)
RESULTS_HEAD = re.compile(r"^## (Findings|Results)\s*$", re.M)
# a run appends "### Run …" under ## Findings (EVAL-0001 at f9ca43b); an unrun document reads "Not yet run."
RUN_HEAD = re.compile(r"^### Run\b", re.M)


def cap(n):
    return math.ceil(0.10 * n) + math.ceil(0.05 * n)


def precision(final, census):
    if census == 0:
        return 0.0
    return sum(1 for v in final.values() if v == "REAL") / census


def disagree(a, b):
    if a == b:
        return a, False
    if {a, b} == {"REAL", "NOISE"}:
        return "UNRESOLVED", False
    x = a if b == "UNRESOLVED" else b
    return x, True


def apply_tiebreak(x, t):
    return x if t == x else "UNRESOLVED"


def _git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)


def gate_label(label, trees, clause_set, item_type):
    fails = []
    want = next((r["clause"] for r in clause_set if r["type"] == item_type), None)
    if want is None:
        fails.append(f"clause-set has no row for type {item_type}")
    elif label.get("clause") != want:
        fails.append("clause does not match clause-set row")
    if label.get("label") == "UNRESOLVED" and not label.get("evidence"):
        return fails
    if label.get("label") in ("REAL", "NOISE") and not label.get("evidence"):
        fails.append("REAL/NOISE label carries no evidence")
        return fails
    for i, ev in enumerate(label.get("evidence", [])):
        remote = ev.get("remote")
        if remote not in trees:
            fails.append(f"evidence[{i}] remote not in scope: {remote}")
            continue
        path, sha = trees[remote]
        if _git(path, "cat-file", "-e", f"{sha}:{ev.get('path', '')}").returncode != 0:
            fails.append(f"evidence[{i}] path absent at {sha[:7]}: {ev.get('path')}")
            continue
        q = ev.get("quote")
        if not q:
            fails.append(f"evidence[{i}] has no quote")
            continue
        text = _git(path, "show", f"{sha}:{ev['path']}").stdout
        if q not in text:
            fails.append(f"evidence[{i}] quote not verbatim in {ev['path']}")
    return fails


def unresolved_source(rec):
    if rec.get("gate_failures"):
        return "gate-failure"
    if rec.get("rederive") is not None and rec.get("final_before") is not None and rec["rederive"] != rec["final_before"]:
        return "rederivation-dissent"
    a, b = rec.get("a"), rec.get("b")
    if {a, b} == {"REAL", "NOISE"}:
        return "labeler-contradiction"
    if "tiebreak" in rec and b is not None and "UNRESOLVED" in (a, b) and rec["tiebreak"] != (a if b == "UNRESOLVED" else b):
        return "failed-tiebreak"
    if a == "UNRESOLVED" and b == "UNRESOLVED":
        return "both-unresolved"
    reasons = [r for r in rec.get("reasons", []) if r]
    return f"labeler-reason:{reasons[0]}" if reasons else "labeler-reason:null"


def validate_ledger(rows):
    errors, flagged, unverified = [], set(), []
    attempts = {}
    for i, r in enumerate(rows):
        missing = [k for k in ("item", "slot", "attempt", "state") if k not in r]
        if missing:
            errors.append(f"row {i}: missing key(s) {missing}")
            continue
        key = (r["item"], r["slot"])
        attempts.setdefault(key, set()).add(r["attempt"])
        if r["state"] == "done":
            if not r.get("verdict-path"):
                errors.append(f"{r['item']}/{r['slot']} done row has no verdict-path")
            rep = r.get("reported-model", "unknown")
            if rep == "unknown":
                unverified.append(f"{r['item']}/{r['slot']}")
            elif rep != r["model"]:
                errors.append(f"{r['item']}/{r['slot']} reported model {rep} != requested {r['model']}")
            if len(attempts[key]) > 1 or r["attempt"] > 1:
                flagged.add(r["item"])
    return {"flagged_items": sorted(flagged), "unverified_slots": unverified, "errors": errors}


def _overlaps(a, b):
    """Half-open [start, end) line ranges, inclusive of a single shared line."""
    return a[0] < b[1] and b[0] < a[1]


def _region(d):
    r = d.get("region") or []
    if len(r) != 2:
        raise ValueError(f"region must be [start, end): {d.get('item_id')!r}")
    return int(r[0]), int(r[1])


def match(rows, manifest):
    """D2's `match: region-overlap+class-equality`. Mechanical; no spawn.

    rows: emitted rows, each {path, region: [start, end), class}.
    manifest: answer-key rows, each {item_id, path, region, class, planted: bool}.

    Returns matched pairs, false negatives, false positives, and the residual —
    the only part a spawn ever sees.
    """
    planted = [d for d in manifest if d.get("planted")]
    clean = [d for d in manifest if not d.get("planted")]
    matched, hit_rows, hit_defects = [], set(), set()
    for i, row in enumerate(rows):
        for d in planted:
            if row.get("path") != d.get("path") or row.get("class") != d.get("class"):
                continue
            if _overlaps((int(row["region"][0]), int(row["region"][1])), _region(d)):
                matched.append({"row": i, "item_id": d["item_id"]})
                hit_rows.add(i)
                hit_defects.add(d["item_id"])
                break
    false_negatives = [d["item_id"] for d in planted if d["item_id"] not in hit_defects]
    false_positives, residual_rows = [], []
    for i, row in enumerate(rows):
        if i in hit_rows:
            continue
        over_clean = any(
            row.get("path") == d.get("path")
            and _overlaps((int(row["region"][0]), int(row["region"][1])), _region(d))
            for d in clean
        )
        (false_positives if over_clean else residual_rows).append(i)
    # A residual DEFECT is one a spawn can actually be asked about: some unmatched
    # emitted row on its own path is a candidate for it. A planted defect with no
    # such row is a decided false negative — routing it to a spawn would let
    # judgment relabel a clean miss as a hit, and the defect-neighbourhood pack
    # (which requires the emitted row verbatim) would be unconstructible.
    residual_paths = {rows[i].get("path") for i in residual_rows}
    residual_defects = [d["item_id"] for d in planted
                        if d["item_id"] in set(false_negatives) and d.get("path") in residual_paths]
    return {"matched": matched, "false_negatives": false_negatives,
            "false_positives": false_positives,
            "residual_rows": residual_rows, "residual_defects": residual_defects}


def manifest_sha256(path):
    """The answer key's freeze. Hash the FILE BYTES, not a re-serialised parse."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_check(manifest, defect_classes, repo, sha, expect_sha256=None, manifest_path=None,
                   skill_runs=None):
    """D2 Step 3a. Every leg per-design-steps.md lists, in code:

    the manifest's sha256 (the answer-key freeze — without it an operator can
    demote the defects the skill missed to `clean` after seeing the output and
    recall jumps), each row's shape and id uniqueness, per-class counts with no
    zero-planted class, every row's path present at the corpus `sha`, and
    `spawn-budget.skill-runs` against the distinct artifact count.
    """
    errors = []
    if expect_sha256 is not None:
        if manifest_path is None:
            errors.append("manifest sha256 expected but no manifest path given to hash")
        else:
            got = manifest_sha256(manifest_path)
            if got != expect_sha256:
                errors.append(f"manifest sha256 {got} != frozen {expect_sha256}")
    seen, ids = {}, set()
    for d in manifest:
        for k in ("item_id", "path", "region", "class"):
            if k not in d:
                errors.append(f"manifest row missing key {k}: {d.get('item_id', '?')}")
        iid = d.get("item_id")
        if iid in ids:
            errors.append(f"duplicate manifest item_id: {iid} — inflates the class counts")
        ids.add(iid)
        r = d.get("region")
        if not (isinstance(r, (list, tuple)) and len(r) == 2
                and all(isinstance(x, int) and not isinstance(x, bool) for x in r)
                and r[0] < r[1]):
            # a degenerate or reversed region can never overlap, so every false
            # positive over it silently becomes residual — a precision lever
            errors.append(f"manifest row {iid}: region must be [start, end) integers with start < end, got {r!r}")
        key = d.get("class")
        bucket = seen.setdefault(key, {"planted": 0, "clean-controls": 0})
        bucket["planted" if d.get("planted") else "clean-controls"] += 1
    for row in defect_classes:
        c = row.get("class")
        if c not in seen:
            errors.append(f"defect-classes names {c!r}, absent from the manifest")
            continue
        for k in ("planted", "clean-controls"):
            if int(row.get(k, -1)) != seen[c][k]:
                errors.append(f"defect-classes {c!r} {k}={row.get(k)} != manifest {seen[c][k]}")
        if int(row.get("planted", 0)) == 0:
            errors.append(f"defect-classes {c!r} has planted: 0 — recall is unmeasurable")
    for c in seen:
        if not any(row.get("class") == c for row in defect_classes):
            errors.append(f"manifest class {c!r} absent from defect-classes")
    for path in sorted({d.get("path") for d in manifest if d.get("path")}):
        if _git(repo, "cat-file", "-e", f"{sha}:{path}").returncode != 0:
            errors.append(f"manifest path absent at {sha[:7]}: {path}")
    artifacts = len({d.get("path") for d in manifest if d.get("path")})
    if skill_runs is not None and int(skill_runs) != artifacts:
        errors.append(f"spawn-budget.skill-runs {skill_runs} != distinct manifest artifacts {artifacts}")
    return {"classes": seen, "artifacts": artifacts, "errors": errors}


def blind_scope_check(blind_scope, publication_remote, export_dirs=()):
    """D2's blindness legs. Repository granularity alone is NOT sufficient.

    Three things leak the answer key even with the manifest in another repository:
    the corpus repo's own HISTORY (the commit that planted the defects IS the
    answer key, and `git log -p` over the corpus recovers it), sibling paths in
    the same repo (this suite's own D2 fixture publishes the per-class counts
    verbatim), and an unscoped entry handing over the whole tree. So a blind-scope
    entry must be PATH-SCOPED, and what the skill under test actually reads must
    be a history-free export of that path, not a checkout or clone.
    """
    errors = []
    for e in blind_scope:
        if e.get("remote") == publication_remote:
            errors.append(f"publication remote in blind-scope: {publication_remote}")
        if not e.get("path"):
            errors.append(f"blind-scope entry is not path-scoped: {e.get('remote')}")
        if not e.get("ref"):
            errors.append(f"blind-scope entry has no pinned ref: {e.get('remote')}")
    for d in export_dirs:
        for meta in (".git", ".gitmodules"):
            if os.path.exists(os.path.join(d, meta)):
                errors.append(f"blind-scope export carries {meta} — history reveals the planted commit: {d}")
    return {"ok": not errors, "errors": errors}


def validate_arms(arms):
    """An arm token is scanned for literally by arm_leak. A short or common word
    over-triggers on ordinary prose and is a freeze-time lever for driving a run
    to UNRESOLVED, so the tokens are constrained rather than free text."""
    errors = []
    if not isinstance(arms, (list, tuple)) or len(arms) != 2:
        return {"ok": False, "errors": ["hmac-sha256-parity takes exactly two arms"]}
    for a in arms:
        s = str(a)
        if len(s) < ARM_TOKEN_MIN:
            errors.append(f"arm token {s!r} is shorter than {ARM_TOKEN_MIN} characters")
        if s.lower() in ARM_TOKEN_DENY:
            errors.append(f"arm token {s!r} is a common word — arm_leak would over-trigger on it")
    if str(arms[0]).lower() == str(arms[1]).lower():
        errors.append("the two arm tokens differ only by case")
    return {"ok": not errors, "errors": errors}


def assign_arm(identifier, key, arms):
    """D3's `arm-assignment.mode: hmac-sha256-parity`, keyed on the FREEZING COMMIT.

    The key is not an author-supplied salt. A salt the study author generates can
    be ground at freeze time against a known identifier window until the
    assignment they want falls out, and the block publishes it, so every author
    can also precompute their own arm. The freezing commit's SHA is fixed by the
    tamper guard, is not chosen (grinding it means grinding commits whose content
    is the block being hashed), and needs no field of its own.
    """
    v = validate_arms(arms)
    if not v["ok"]:
        raise ValueError("; ".join(v["errors"]))
    k = str(key)
    if len(k) < 40 or any(c not in "0123456789abcdefABCDEF" for c in k):
        raise ValueError("arm-assignment key must be a full 40-hex-character commit SHA")
    d = hmac.new(k.lower().encode(), str(identifier).encode(), hashlib.sha256).digest()
    return arms[d[-1] & 1]


def validate_enrolment(rows, prior_rows, mode, key, arms):
    """D3 Step 3a: the enrolment ledger is append-only, its arms are reproduced, and
    it carries no outcome. No sha256 can be pinned at freeze, so this is the guard.

    `prior_rows` is the ledger blob at the PREVIOUS registration branch's head, not
    a caller's idea of history: with an empty prior every append-only leg is
    vacuous, so a ledger rewritten down to one hand-picked row would validate.
    """
    errors = []
    if mode not in ARM_MODES:
        errors.append(f"arm-assignment.mode {mode!r} is not implemented (have {list(ARM_MODES)})")
        return {"rows": len(rows), "last_identifier": None, "gaps": [], "errors": errors}
    errors += validate_arms(arms)["errors"]
    if len(rows) < len(prior_rows):
        errors.append(f"enrolment ledger shrank: {len(rows)} < {len(prior_rows)}")
    for i, prior in enumerate(prior_rows):
        if i < len(rows) and rows[i] != prior:
            errors.append(f"enrolment row {i} changed after it was appended")
    seen, numeric = set(), []
    for i, r in enumerate(rows):
        missing = [k for k in ("identifier", "arm") if k not in r]
        if missing:
            errors.append(f"enrolment row {i}: missing key(s) {missing}")
            continue
        # An enrol pass must not carry the interim result. An operator holding the
        # running per-arm delta can stop enrolling when the interim suits them —
        # optional stopping the phase derivation does not detect.
        for peek in ("outcome", "arm_split", "delta"):
            if r.get(peek) is not None:
                errors.append(f"enrolment row {i}: carries {peek!r} — outcomes are read at score time only")
        if r["identifier"] in seen:
            errors.append(f"enrolment row {i}: duplicate identifier {r['identifier']!r}")
        seen.add(r["identifier"])
        if not errors or True:
            try:
                want = assign_arm(r["identifier"], key, arms)
            except ValueError as e:
                errors.append(f"enrolment row {i}: {e}")
                continue
            if r["arm"] != want:
                errors.append(f"enrolment row {i}: arm {r['arm']!r} != recomputed {want!r}")
        m = re.search(r"(\d+)\s*$", str(r["identifier"]))
        if m:
            numeric.append(int(m.group(1)))
    # A skipped identifier is how an operator bumps an incrementable counter to move
    # their own arm. Reported as a deviation, not a refusal — a real gap also arises
    # from an ineligible artifact.
    gaps = []
    if len(numeric) > 1:
        lo, hi = min(numeric), max(numeric)
        gaps = sorted(set(range(lo, hi + 1)) - set(numeric))
    return {"rows": len(rows), "last_identifier": rows[-1].get("identifier") if rows else None,
            "gaps": gaps, "errors": errors}


def derive_phase(rows, target_n, deadline, today, validation=None):
    """D3's phase is DERIVED from the frozen stopping rule, never caller-supplied.

    `rows` must have validated: an unvalidated ledger padded with empty objects
    reaches `target-n` and yields `score`, which is the early score pass the
    refusal list forbids. `today` is a parameter for tests only — the CLI takes no
    flag for it, because a caller-supplied date IS that early pass.
    """
    if validation is not None and validation.get("errors"):
        raise ValueError("cannot derive a phase from a ledger that did not validate: "
                         + "; ".join(validation["errors"]))
    n = validation["rows"] if validation is not None else len(rows)
    d = datetime.date.fromisoformat(deadline)
    t = datetime.date.fromisoformat(today)
    p = "score" if n >= int(target_n) or t >= d else "enrol"
    assert p in PHASES
    return p


def arm_leak(label, arms):
    """D3's blinding-breach gate leg.

    Scans the WHOLE serialised label, minus `clause` — the frozen rule text is
    identical for every label, so an arm token appearing there would fail all of
    them. A key-by-key scan leaves `notes`, `unresolved_reason` and evidence
    `path` as untouched leak channels.

    This leg catches LITERAL tokens only; a paraphrase passes. Blinding is
    delivered by the pack, which strips the arm markers before the spawn ever
    reads the artifact. This is a backstop, not the mechanism.
    """
    body = {k: v for k, v in label.items() if k != "clause"}
    low = json.dumps(body, default=str).lower()
    named = [a for a in arms if str(a).lower() in low]
    return {"ok": not named,
            "errors": [f"label names arm {a!r} — blinding breached" for a in named]}


def contrast(final_primary, flagged_other):
    real = [k for k, v in final_primary.items() if v == "REAL"]
    noise = [k for k, v in final_primary.items() if v == "NOISE"]
    rd = sum(1 for k in real if k not in flagged_other) / len(real) if real else 0.0
    nd = sum(1 for k in noise if k not in flagged_other) / len(noise) if noise else 0.0
    return {"noise_dropped": nd, "real_dropped": rd, "passes": (nd - rd) >= 0.10}


def is_ancestor(repo, commit, ref):
    return _git(repo, "merge-base", "--is-ancestor", commit, ref).returncode == 0


_FENCE_RE = re.compile(r"^(```|~~~).*?^\1\s*$", re.M | re.S)


def _strip_fences(text):
    return _FENCE_RE.sub("", text)


def live_studies(repo, dirs=("content/evals", "content/benchmarks"), ref="main"):
    out = []
    added = _git(repo, "log", ref, "--diff-filter=A", "--name-only", "--format=", "--", *dirs).stdout.split()
    for path in sorted(set(p for p in added if p.endswith(".md") and not p.split("/")[-1].startswith("_"))):
        at_head = _git(repo, "cat-file", "-e", f"{ref}:{path}").returncode == 0
        if at_head:
            text = _git(repo, "show", f"{ref}:{path}").stdout
        else:
            last = _git(repo, "log", ref, "-1", "--format=%H", "--", path).stdout.strip()
            text = _git(repo, "show", f"{last}^:{path}").stdout
        stripped = _strip_fences(text)
        m = SUBJECT_RE.search(stripped)
        if not m:
            continue
        fm = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        withdrawn = bool(fm and re.search(r"^withdrawn:\s*\S", fm.group(1), re.M))
        results = False
        h = RESULTS_HEAD.search(stripped)
        if h:
            body = stripped[h.end():].split("\n## ")[0]
            results = bool(RUN_HEAD.search(body))
        if not withdrawn and not results:
            out.append({"path": path, "oq": m.group(1), "removed": not at_head})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="recheck.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gate")
    for k in ("--labels-dir", "--trees", "--clause-set", "--sample", "--out"):
        g.add_argument(k, required=True)
    # D3 arm blinding: when the arms are named, a rationale mentioning either one fails the gate.
    # required: an omitted --arms means no blinding breach can ever be detected,
    # while every other gate leg is required. Pass `none` for outcome.adjudicated: false.
    g.add_argument("--arms", required=True)
    mt = sub.add_parser("match")
    for k in ("--rows", "--manifest", "--out"):
        mt.add_argument(k, required=True)
    mf = sub.add_parser("manifest")
    for k in ("--manifest", "--defect-classes", "--repo", "--sha", "--manifest-sha256",
              "--blind-scope", "--publication-remote", "--corpus-remote", "--corpus-ref"):
        mf.add_argument(k, required=True)
    mf.add_argument("--skill-runs", type=int, required=True)
    mf.add_argument("--export-dir", action="append", default=[])
    en = sub.add_parser("enrolment")
    # --prior required: with an empty prior every append-only leg is vacuous.
    # It is the ledger blob at the previous registration branch's head —
    # `git show <prior-branch>:<ledger path>`, not the caller's own idea of history.
    for k in ("--ledger", "--prior", "--mode", "--key", "--arms"):
        en.add_argument(k, required=True)
    ph = sub.add_parser("phase")
    for k in ("--ledger", "--prior", "--mode", "--key", "--arms", "--deadline"):
        ph.add_argument(k, required=True)
    ph.add_argument("--target-n", type=int, required=True)
    l = sub.add_parser("ledger"); l.add_argument("--ledger", required=True)
    m = sub.add_parser("metric"); m.add_argument("--final", required=True); m.add_argument("--census", type=int, required=True)
    m.add_argument("--contrast")
    v = sub.add_parser("liveness"); v.add_argument("--repo", required=True)
    a = ap.parse_args(argv)
    fail = False
    if a.cmd == "gate":
        trees = {k: tuple(v) for k, v in json.load(open(a.trees)).items()}
        cs = json.load(open(a.clause_set))
        types = {r["item_id"]: r["type"] for r in json.load(open(a.sample))}
        res = {}
        for f in sorted(os.listdir(a.labels_dir)):
            if not f.endswith(".json"):
                continue
            item = f.split(".")[0]
            label = json.load(open(os.path.join(a.labels_dir, f)))
            fails = gate_label(label, trees, cs, types.get(item, ""))
            if a.arms != "none":
                fails = fails + arm_leak(label, json.loads(a.arms))["errors"]
            res[f] = fails
        json.dump(res, open(a.out, "w"), indent=1)
        print(json.dumps({"labels": len(res), "failing": sum(1 for v in res.values() if v)}))
    elif a.cmd == "match":
        out = match(json.load(open(a.rows)), json.load(open(a.manifest)))
        json.dump(out, open(a.out, "w"), indent=1)
        print(json.dumps({k: len(v) for k, v in out.items()}))
    elif a.cmd == "manifest":
        out = manifest_check(json.load(open(a.manifest)), json.load(open(a.defect_classes)),
                             a.repo, a.sha, expect_sha256=a.manifest_sha256,
                             manifest_path=a.manifest, skill_runs=a.skill_runs)
        d = blind_scope_check(json.load(open(a.blind_scope)), a.publication_remote, a.export_dir)
        out["blind_scope_ok"] = d["ok"]
        out["errors"] = out["errors"] + d["errors"]
        if not is_ancestor(a.repo, a.sha, a.corpus_ref):
            out["errors"].append(f"corpus-ref.sha {a.sha[:7]} is not an ancestor of {a.corpus_ref}")
        out["corpus_remote"] = a.corpus_remote
        fail = bool(out["errors"])
        print(json.dumps(out, indent=1))
    elif a.cmd == "enrolment":
        out = validate_enrolment(json.load(open(a.ledger)), json.load(open(a.prior)),
                                 a.mode, a.key, json.loads(a.arms))
        fail = bool(out["errors"])
        print(json.dumps(out, indent=1))
    elif a.cmd == "phase":
        rows = json.load(open(a.ledger))
        v = validate_enrolment(rows, json.load(open(a.prior)), a.mode, a.key, json.loads(a.arms))
        today = datetime.date.today().isoformat()
        try:
            out = {"phase": derive_phase(rows, a.target_n, a.deadline, today, validation=v),
                   "today": today, "rows": v["rows"], "gaps": v["gaps"]}
        except ValueError as e:
            out = {"phase": None, "today": today, "errors": [str(e)]}
            fail = True
        print(json.dumps(out, indent=1))
    elif a.cmd == "ledger":
        print(json.dumps(validate_ledger(json.load(open(a.ledger))), indent=1))
    elif a.cmd == "metric":
        final = json.load(open(a.final))
        out = {"precision": precision(final, a.census), "cap": cap(a.census),
               "unresolved": sum(1 for v in final.values() if v == "UNRESOLVED")}
        if a.census == 0:
            out["note"] = "empty census"
        if a.contrast:
            out["contrast"] = {k: contrast(final, set(v)) for k, v in json.load(open(a.contrast)).items()}
        print(json.dumps(out, indent=1))
    else:
        print(json.dumps(live_studies(a.repo), indent=1))
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
