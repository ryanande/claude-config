#!/usr/bin/env python3
"""Behaviour tests for prescan_extractor.py (run: python3 test_prescan_extractor.py).

The extractor serves two aggregate jobs — deriving the maximal evidence-scope
and the infeasibility count C — and decides nothing per item. These tests pin
the identity forms, owner derivation and dispositions the design spec
deferred to code, then replay the EVAL-0003 census as a golden fixture.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prescan_extractor as px  # noqa: E402

FIX = os.path.join(HERE, "fixtures")
PUB = "https://github.com/Wyatt-Rupp_prepass/research-docs.git"
HARNESS = "https://github.com/Wyatt-Rupp_prepass/claude-config.git"
_fails = []


def check(name, cond):
    print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        _fails.append(name)


def body(item_id, text, typ="notes"):
    return {"item_id": item_id, "path": f"content/{typ}/{item_id}.md", "type": typ, "body": text}


def tiny_map(**owners):
    return {"gh_login": "t", "fetched_at": "x",
            "owners": {o: {"count": len(n), "repos": [{"name": x, "url": f"https://github.com/{o}/{x}"} for x in n]}
                       for o, n in owners.items()}}


MAP = tiny_map(**{"Wyatt-Rupp_prepass": ["research-docs", "exocortex", "dx-knowledge-mirror", "claude-config"],
                  "PrePass": ["dx-aicentral", "dx-knowledge-mirror", "ADRs", "repo.name"]})


def run(bodies, harness=HARNESS, declared=()):
    return px.extract(bodies, MAP, PUB, harness, list(declared))


print("owner derivation")
check("publication owner always present",
      px.derive_owners([body("i1", "nothing here")], PUB) == ["Wyatt-Rupp_prepass"])
check("pair alone cannot introduce an owner",
      px.derive_owners([body("i1", "see PrePass/dx-aicentral")], PUB) == ["Wyatt-Rupp_prepass"])
check("url form adds its owner",
      "PrePass" in px.derive_owners([body("i1", "https://github.com/PrePass/dx-aicentral/blob/main/x")], PUB))
check("pair confirms an owner already named by a URL elsewhere in the census",
      set(px.derive_owners([body("i1", "https://github.com/PrePass/x"),
                             body("i2", "see PrePass/dx-aicentral")], PUB)) == {"Wyatt-Rupp_prepass", "PrePass"})
check("a path-like token does not add an owner",
      px.derive_owners([body("i1", "content/adr/0003.md and repos/foo")], PUB) == ["Wyatt-Rupp_prepass"])
try:
    px.extract([body("i1", "see https://github.com/Elsewhere/thing")], MAP, PUB, HARNESS, [])
    check("owner missing from repo map raises, never silently filtered", False)
except px.MissingOwnerMap as e:
    check("owner missing from repo map raises, never silently filtered", "Elsewhere" in str(e))
try:
    px.extract([body("i1", "x")], MAP, PUB, HARNESS, ["Declared"])
    check("declared owner missing from repo map raises", False)
except px.MissingOwnerMap:
    check("declared owner missing from repo map raises", True)

print("self-contained forms")
r = run([body("i1", "https://github.com/PrePass/dx-aicentral.git")])
check("url resolves to owner/name", [i["identity"] for i in r["identities"]] == ["PrePass/dx-aicentral"])
check("url normalised with .git", r["identities"][0]["url"] == "https://github.com/PrePass/dx-aicentral.git")
check("form recorded", r["identities"][0]["form"] == "url")
check("dotted GitHub name captured whole (owner_of on a raw URL)",
      px.GITHUB_URL.search("https://github.com/vercel/next.js.git").group(2) == "next.js.git")
r = run([body("i1", "https://github.com/PrePass/repo.name.git")])
check("dotted repo name normalised from .git suffix",
      [i["identity"] for i in r["identities"]] == ["PrePass/repo.name"])
r = run([body("i1", "see https://github.com/PrePass/repo.name.")])
check("dotted repo name not truncated by a trailing sentence period",
      [i["identity"] for i in r["identities"]] == ["PrePass/repo.name"])
r = run([body("i1", "https://github.com/PrePass/dx-aicentral/blob/main/x")])
check("dotted-name-capable url still stops at the next path segment",
      [i["identity"] for i in r["identities"]] == ["PrePass/dx-aicentral"])
r = run([body("i1", "in PrePass/dx-aicentral we")], declared=["PrePass"])
check("pair resolves", [i["identity"] for i in r["identities"]] == ["PrePass/dx-aicentral"])
r = run([body("i1", "in PrePass/nonesuch we")], declared=["PrePass"])
check("pair with unknown name is pair-unresolved",
      r["identities"] == [] and r["unresolved"][0]["disposition"] == "pair-unresolved")
r = run([body("i1", "https://gitlab.com/x/y")])
check("non-github url is not-a-repository", r["unresolved"][0]["disposition"] == "not-a-repository")

print("bare names")
r = run([body("i1", "the `exocortex` repo")])
check("backticked bare name resolves", [i["identity"] for i in r["identities"]] == ["Wyatt-Rupp_prepass/exocortex"])
check("bare form recorded", r["identities"][0]["form"] == "bare")
r = run([body("i1", "exocortex-data is separate")])
check("hyphen-joined longer token does not match", r["identities"] == [])
r = run([body("i1", "Exocortex is separate")])
check("case-exact: capitalised does not match", r["identities"] == [])
r = run([body("i1", "the exocortex repo")])
check("plain-word name without backticks is not a mention (hyphen-or-backtick rule)", r["identities"] == [])
r = run([body("i1", "see dx-aicentral for the rules")], declared=["PrePass"])
check("hyphenated name resolves without backticks", [i["identity"] for i in r["identities"]] == ["PrePass/dx-aicentral"])
r = run([body("i1", "see dx-knowledge-mirror")], declared=["PrePass"])
check("name under two owners is ambiguous-name",
      r["identities"] == [] and r["unresolved"][0]["disposition"] == "ambiguous-name")
r = run([body("i1", "the ADRs directory")], declared=["PrePass"])
check("plain-word map name in prose is not a mention (the ADRs collision)", r["identities"] == [] and r["unresolved"] == [])
r = run([body("i1", "the `ADRs` repository")], declared=["PrePass"])
check("backticked plain-word map name resolves", [i["identity"] for i in r["identities"]] == ["PrePass/ADRs"])
r = run([body("i1", "PrePass/dx-knowledge-mirror is the one")], declared=["PrePass"])
check("pair disambiguates a two-owner name",
      [i["identity"] for i in r["identities"]] == ["PrePass/dx-knowledge-mirror"])
r = run([body("i1", "the `ADRs` repository")])
check("bare-name resolution scoped to `owners` — an owner absent from owners cannot be attributed",
      r["identities"] == [] and r["unresolved"] == [])

print("harness runtime and exclusions")
r = run([body("i1", "deployed under ~/.claude/skills")])
check("~/.claude maps to harness-runtime url",
      r["identities"][0]["identity"] == "harness-runtime" and r["identities"][0]["url"] == HARNESS)
r = run([body("i1", "deployed under ~/.claude/skills")], harness=None)
check("~/.claude without harness url is owner-unknown", r["unresolved"][0]["disposition"] == "owner-unknown")
r = run([body("i1", "ping @PrePass/architecture")])
check("team mention excluded with reason", r["excluded_mentions"][0]["reason"] == "team-mention"
      and r["identities"] == [] and r["unresolved"] == [])

print("aggregation")
r = run([body("i1", "`exocortex`"), body("i2", "`exocortex` and PrePass/dx-aicentral"), body("i3", "nothing")])
ex = next(i for i in r["identities"] if i["identity"] == "Wyatt-Rupp_prepass/exocortex")
check("item ids aggregated per identity", ex["item_ids"] == ["i1", "i2"])
check("bodies_yielding counts bodies with >=1 identity", r["bodies_yielding"] == 2)
check("declared owner appended when mapped",
      "PrePass" in run([body("i1", "x")], declared=["PrePass"])["owners"])

print("EVAL-0003 golden replay")
bodies = json.load(open(os.path.join(FIX, "eval-0003-bodies-324be92.json")))
rmap = json.load(open(os.path.join(FIX, "eval-0003-repo-map.json")))
r = px.extract(bodies, rmap, PUB, HARNESS, [])
exp = json.load(open(os.path.join(FIX, "eval-0003-expected.json")))
check("53 bodies", len(bodies) == 53)
check("owners census-derived", r["owners"] == ["Wyatt-Rupp_prepass", "PrePass"])
check("35 of 53 bodies yield an identity", r["bodies_yielding"] == 35)
check("fifteen identities", len(r["identities"]) == 15)
scope = [i for i in r["identities"] if i["identity"] != "harness-runtime"] + \
        [i for i in r["identities"] if i["identity"] == "harness-runtime"]
check("fourteen scope entries plus harness-runtime",
      len([i for i in r["identities"] if i["identity"] != "harness-runtime"]) == 14)
check("dx-knowledge-mirror ambiguous",
      any(u["identity"] == "dx-knowledge-mirror" and u["disposition"] == "ambiguous-name" for u in r["unresolved"]))
check("research-skills named in no body",
      not any(i["identity"].endswith("/research-skills") for i in r["identities"]))
check("golden identities match", sorted(i["identity"] for i in r["identities"]) == sorted(exp["identities"]))
check("golden unresolved match",
      sorted((u["identity"], u["disposition"]) for u in r["unresolved"]) ==
      sorted((u["identity"], u["disposition"]) for u in exp["unresolved"]))
check("golden excluded match",
      sorted(e["mention"] for e in r["excluded_mentions"]) == sorted(exp["excluded_mentions"]))

print(f"\n{len(_fails)} failure(s)")
sys.exit(1 if _fails else 0)
