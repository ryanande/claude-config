#!/usr/bin/env python3
"""prescan_extractor.py — body-mention extractor for study-design's D1 pre-scan.

Two aggregate jobs only: derive the maximal evidence-scope and the identities
that feed the infeasibility count C. Decides nothing about an individual
item. Behaviour is fixed by test_prescan_extractor.py; the design spec
(docs/superpowers/specs/2026-09-06-study-skills-eval-0003-retro-design.md §3)
names only inputs, map, output, and invariant.

CLI (run in this order — every stage is code, none is hand-computed):
  prescan_extractor.py derive-owners --bodies bodies.json --publication-url URL [--declared-owners a,b]
  prescan_extractor.py repo-map --owners a,b --out repo-map.json
  prescan_extractor.py extract --bodies bodies.json --repo-map repo-map.json \
      --publication-url URL [--harness-url URL] [--declared-owners a,b] --out report.json
"""
import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys

# The name group is GREEDY (not lazy) so a dotted repo name (`next.js`, `repo.name`) is
# captured whole rather than truncated at its first dot — a lazy quantifier stops as soon
# as the lookahead's terminator class (which must include '.' to end a sentence) is
# satisfied, which happens at the FIRST dot in a dotted name. Trailing ".git" and a single
# trailing sentence-period are stripped afterward by _clean_repo_name, not by the regex.
GITHUB_URL = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)(?=[/#?\s)\]`'\",;:]|$)")
OTHER_URL = re.compile(r"https://(?!github\.com/)([a-z0-9.-]+)/[^\s)\]`'\"]+")
TEAM = re.compile(r"(?<![\w/])@([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")
HARNESS = re.compile(r"~/\.claude")
# a "pair" is <owner>/<name> where owner is a known owner; checked against the owner set, so
# path-like tokens (content/adr) never match because 'content' is not an owner.
PAIR_TMPL = r"(?<![\w/@-])({owners})/([A-Za-z0-9_.-]+)(?![\w/-])"
# bare-name delimiters: not preceded/followed by a word char, '-', '_' or '/'; backticks are fine
BARE_TMPL = r"(?<![\w/\-])({names})(?![\w/\-])"


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _clean_repo_name(n):
    """Strip a URL-form repo name's trailing '.git' suffix, or else a single trailing
    sentence-ending '.' — the GITHUB_URL name group is greedy and captures a dotted repo
    name (`repo.name`) whole, including whichever of these two follows it in running
    prose. A repo name genuinely ending in a literal '.' is not a real GitHub naming
    shape, so a lone trailing dot is always sentence punctuation here."""
    if n.endswith(".git"):
        return n[:-4]
    if n.endswith("."):
        return n[:-1]
    return n


def owner_of(url):
    m = GITHUB_URL.match(url.strip())
    if not m:
        raise SystemExit(f"publication url is not a github url: {url}")
    return m.group(1)


def derive_owners(bodies, publication_url):
    """Owners = {publication owner} ∪ {owners named by a GitHub URL anywhere in the
    census}. A bare `<Owner>/<name>` PAIR (no URL) can only CONFIRM an owner already
    named by a URL somewhere in the same census — it never introduces an owner on its
    own. This replaces a corpus-specific denylist of capitalised-word "dichotomy" pairs
    (`CI/Actions`, `PASS/FAIL`, `RFC/ADR`, ...) that are prose, not GitHub mentions: none
    of those words is ever URL-confirmed, so under this rule they are never candidates
    in the first place — no denylist needed to keep them out.
    """
    owners = [owner_of(publication_url)]
    url_owners = {owners[0]}
    for b in bodies:
        for m in GITHUB_URL.finditer(b["body"]):
            o = m.group(1)
            url_owners.add(o)
            if o not in owners:
                owners.append(o)
    for b in bodies:
        for m in re.finditer(r"(?<![\w/@.-])([A-Z][A-Za-z0-9_-]+)/([A-Za-z0-9_.-]+)(?![\w/-])", b["body"]):
            cand = m.group(1)
            if (cand in url_owners
                    and cand not in owners
                    and cand.lower() not in {"content", "assets", "docs", "skills", "repos", "src", "bin"}):
                owners.append(cand)
    return owners


class MissingOwnerMap(Exception):
    """A derived or declared owner has no entry in the repo map. Fail closed: re-run repo-map."""


def _names_by_owner(repo_map):
    return {o: {r["name"]: r["url"] for r in d["repos"]} for o, d in repo_map["owners"].items()}


def extract(bodies, repo_map, publication_url, harness_url=None, declared_owners=None):
    names = _names_by_owner(repo_map)
    owners = derive_owners(bodies, publication_url)
    for o in declared_owners or []:
        if o not in owners:
            owners.append(o)
    missing = [o for o in owners if o not in names]
    if missing:
        raise MissingOwnerMap(f"repo-map has no entry for owner(s) {missing}; re-run repo-map --owners {','.join(owners)}")
    idents, unres, excl = {}, {}, {}

    def add(d, key, item, **kw):
        row = d.setdefault(key, {**kw, "item_ids": []})
        if item not in row["item_ids"]:
            row["item_ids"].append(item)

    pair_re = re.compile(PAIR_TMPL.format(owners="|".join(re.escape(o) for o in owners)))
    all_names = sorted({n for o in names for n in names[o]}, key=len, reverse=True)
    bare_re = re.compile(BARE_TMPL.format(names="|".join(re.escape(n) for n in all_names))) if all_names else None
    yielding = set()

    for b in bodies:
        item, text = b["item_id"], b["body"]
        consumed = []  # spans already attributed to a stronger form

        def take(span):
            consumed.append(span)

        def free(span):
            return not any(s[0] <= span[0] < s[1] or s[0] < span[1] <= s[1] for s in consumed)

        for m in TEAM.finditer(text):
            add(excl, m.group(0), item, mention=m.group(0), reason="team-mention")
            take(m.span())
        for m in GITHUB_URL.finditer(text):
            o, n = m.group(1), _clean_repo_name(m.group(2))
            take(m.span())
            if o in names and n in names[o]:
                add(idents, f"{o}/{n}", item, identity=f"{o}/{n}", url=f"https://github.com/{o}/{n}.git",
                    owner=o, name=n, form="url")
                yielding.add(item)
            else:
                add(unres, f"{o}/{n}", item, identity=f"{o}/{n}", disposition="pair-unresolved")
        for m in OTHER_URL.finditer(text):
            take(m.span())
            add(unres, m.group(0), item, identity=m.group(0), disposition="not-a-repository")
        for m in HARNESS.finditer(text):
            take(m.span())
            if harness_url:
                add(idents, "harness-runtime", item, identity="harness-runtime", url=harness_url,
                    owner=owner_of(harness_url), name=_clean_repo_name(GITHUB_URL.match(harness_url).group(2)),
                    form="harness")
                yielding.add(item)
            else:
                add(unres, "~/.claude", item, identity="~/.claude", disposition="owner-unknown")
        for m in pair_re.finditer(text):
            if not free(m.span()):
                continue
            o, n = m.group(1), m.group(2)
            take(m.span())
            if o in names and n in names[o]:
                add(idents, f"{o}/{n}", item, identity=f"{o}/{n}", url=names[o][n] if names[o][n].endswith(".git")
                    else names[o][n] + ".git", owner=o, name=n, form="pair")
                yielding.add(item)
            else:
                add(unres, f"{o}/{n}", item, identity=f"{o}/{n}", disposition="pair-unresolved")
        if bare_re:
            for m in bare_re.finditer(text):
                if not free(m.span()):
                    continue
                n = m.group(1)
                a, z = m.span()
                backticked = a > 0 and z < len(text) and text[a - 1] == "`" and text[z] == "`"
                if not ("-" in n or "_" in n or backticked):
                    continue  # hyphen-or-backtick rule: a plain word in prose is not a repository mention
                # Scoped to `owners` (not the full repo-map) so an identity is never
                # attributed to an owner absent from the returned `owners` list — the
                # `o in names` guard is dropped because the MissingOwnerMap check above
                # already proved every o in `owners` is a names key. This branch is
                # genuinely reachable: `owners` can be a strict subset of the repo-map's
                # owners (e.g. a repo-map fetched broader than the census derived), unlike
                # the old `for o in names` scan where every bare match was by construction
                # drawn from `names` and could never miss.
                holders = [o for o in owners if n in names[o]]
                if not holders:
                    continue
                take(m.span())
                if len(holders) == 1:
                    o = holders[0]
                    add(idents, f"{o}/{n}", item, identity=f"{o}/{n}", url=names[o][n] if names[o][n].endswith(".git")
                        else names[o][n] + ".git", owner=o, name=n, form="bare")
                    yielding.add(item)
                else:
                    add(unres, n, item, identity=n, disposition="ambiguous-name")

    def rows(d):
        out = []
        for v in d.values():
            v = dict(v)
            v["item_ids"] = sorted(v["item_ids"])
            if "disposition" in v:
                v["items_citing"] = len(v["item_ids"])
            out.append(v)
        return sorted(out, key=lambda r: r.get("identity", r.get("mention")))

    return {"owners": owners, "identities": rows(idents), "unresolved": rows(unres),
            "excluded_mentions": rows(excl), "bodies_yielding": len(yielding)}


def fetch_repo_map(owners):
    login = subprocess.run(["gh", "api", "user", "-q", ".login"], capture_output=True, text=True, check=True).stdout.strip()
    m = {"fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
         "gh_login": login, "owners": {}}
    for o in owners:
        rows = json.loads(subprocess.run(["gh", "repo", "list", o, "--limit", "1000", "--json", "name,url"],
                                         capture_output=True, text=True, check=True).stdout)
        m["owners"][o] = {"count": len(rows), "repos": sorted(rows, key=lambda r: r["name"])}
    return m


def main(argv=None):
    ap = argparse.ArgumentParser(prog="prescan_extractor.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    do = sub.add_parser("derive-owners")
    do.add_argument("--bodies", required=True)
    do.add_argument("--publication-url", required=True)
    do.add_argument("--declared-owners", default="")
    rm = sub.add_parser("repo-map")
    rm.add_argument("--owners", required=True)
    rm.add_argument("--out", required=True)
    ex = sub.add_parser("extract")
    ex.add_argument("--bodies", required=True)
    ex.add_argument("--repo-map", required=True)
    ex.add_argument("--publication-url", required=True)
    ex.add_argument("--harness-url")
    ex.add_argument("--declared-owners", default="")
    ex.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "derive-owners":
        owners = derive_owners(json.load(open(a.bodies)), a.publication_url)
        for o in [x for x in a.declared_owners.split(",") if x]:
            if o not in owners:
                owners.append(o)
        print(json.dumps(owners))
    elif a.cmd == "repo-map":
        m = fetch_repo_map(a.owners.split(","))
        json.dump(m, open(a.out, "w"), indent=1)
        print(sha256_file(a.out))
    else:
        bodies = json.load(open(a.bodies))
        rmap = json.load(open(a.repo_map))
        rep = extract(bodies, rmap, a.publication_url, a.harness_url,
                      [o for o in a.declared_owners.split(",") if o])
        rep["repo_map_sha256"] = sha256_file(a.repo_map)
        json.dump(rep, open(a.out, "w"), indent=1)
        print(json.dumps({"owners": rep["owners"], "identities": len(rep["identities"]),
                          "unresolved": len(rep["unresolved"]), "bodies_yielding": rep["bodies_yielding"]}))


if __name__ == "__main__":
    main()
