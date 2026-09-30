#!/usr/bin/env python3
"""SUPERSEDED 2026-09-05 — the provider changed to OpenAlex; the Semantic Scholar API key
is not licensable for this org. Kept as provenance for the spike that closed that path.
See docs/superpowers/specs/2026-09-05-source-recency-probe-citation-graph-design.md §5.

Feasibility spike for source-recency-probe v2 (Semantic Scholar citation graph).

Checks five properties the design depends on and prints a PASS/FAIL line per property:
  1. unauthenticated rate limit: can we make 30 requests at 3.5 s spacing without a 429?
  2. newest-first ordering across pages of /paper/{id}/citations
  3. `next` semantics at end of result set (absent or null on the last page)
  4. per-page ceiling: does limit=1000 return up to 1000 rows?
  5. title-search precision: does /paper/search?query=<exact title>&limit=1 return the same paperId as the arXiv key for three known papers?

Usage: S2_API_KEY=<optional> python3 spike_s2.py
Never shipped as part of the skill; provenance only.
"""
import json, os, sys, time, urllib.request, urllib.parse, urllib.error

BASE = "https://api.semanticscholar.org/graph/v1"
KEY = os.environ.get("S2_API_KEY")
SPACING = 1.0 if KEY else 3.5
KNOWN = [  # (arXiv id, exact title) — verified 2026-09-05 in the design spec §5
    ("2310.01798", "Large Language Models Cannot Self-Correct Reasoning Yet"),
    ("2402.08115", "On the Self-Verification Limitations of Large Language Models on Reasoning and Planning Tasks"),
    ("2404.13076", "LLM Evaluators Recognize and Favor Their Own Generations"),
]

def get(path, params):
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"x-api-key": KEY} if KEY else {})
    time.sleep(SPACING)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, None

def norm(t):
    return "".join(c.lower() for c in t if c.isalnum() or c == " ").split()

results = {}

# 1. rate limit: 30 requests
codes = [get("/paper/arXiv:2310.01798", {"fields": "title"})[0] for _ in range(30)]
results["rate-limit-30-requests"] = ("PASS" if all(c == 200 for c in codes) else "FAIL", codes)

# 2 + 4: ordering and page ceiling on a heavily cited paper (3 pages)
offset, pages, ordered = 0, [], True
for _ in range(3):
    code, body = get("/paper/arXiv:2310.01798/citations",
                     {"fields": "publicationDate,citationCount", "limit": 1000, "offset": offset})
    if code != 200 or body is None:
        results["pagination"] = ("FAIL", f"HTTP {code} at offset {offset}"); break
    dates = [c["citingPaper"].get("publicationDate") or "" for c in body["data"]]
    pages.append((len(dates), dates[0] if dates else None, dates[-1] if dates else None))
    if len(pages) > 1 and pages[-2][2] and dates and dates[0] > pages[-2][2]:
        ordered = False
    if body.get("next") is None:
        break
    offset = body["next"]
results["newest-first-across-pages"] = ("PASS" if ordered else "FAIL", pages)
results["page-ceiling-1000"] = ("PASS" if pages and pages[0][0] == 1000 else "FAIL", pages[0][0] if pages else None)

# 3: `next` semantics — walk a paper with FEWER than 1000 citers to its true end.
# arXiv:2402.08115 (S3) had a few hundred citers on 2026-09-05; the terminal page must
# return fewer rows than `limit` AND carry no `next` (absent or null).
code, body = get("/paper/arXiv:2402.08115/citations", {"fields": "publicationDate", "limit": 1000, "offset": 0})
if code == 200 and body is not None:
    terminal = len(body["data"]) < 1000 and body.get("next") is None
    results["next-semantics"] = ("PASS" if terminal else "FAIL",
                                 {"rows": len(body["data"]), "next": body.get("next")})
else:
    results["next-semantics"] = ("FAIL", f"HTTP {code}")

# 5. title-search precision
hits = []
for ax, title in KNOWN:
    c1, by_key = get(f"/paper/arXiv:{ax}", {"fields": "paperId,title"})
    c2, by_search = get("/paper/search", {"query": title, "limit": 1, "fields": "paperId,title"})
    ok = (c1 == 200 and c2 == 200 and by_search and by_search.get("data")
          and by_search["data"][0]["paperId"] == by_key["paperId"]
          and norm(by_search["data"][0]["title"]) == norm(title))
    hits.append((ax, bool(ok), c1, c2))
results["title-search-precision-3-of-3"] = ("PASS" if all(h[1] for h in hits) else "FAIL", hits)

print(json.dumps({"mode": "api-key" if KEY else "unauthenticated", "results": results}, indent=1))
sys.exit(0 if all(v[0] == "PASS" for v in results.values()) else 1)
