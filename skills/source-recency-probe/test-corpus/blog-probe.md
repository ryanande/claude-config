---
title: Fixture — blog-probe (probe-research-blog is registered but undispatched at v2.0)
date: 2026-05-19
fixture: source-recency-probe
expected_check_name: probe-research-blog
expected_status: pass
authored_against: claude-opus-4-7,2025-09-01
sources:
  - id: A1
    title: "Constitutional AI: Harmlessness from AI Feedback"
    url: "https://arxiv.org/abs/2212.08073"
    year: 2022
---

# Fixture — blog-probe

Refreshed to v2.0 semantics. `probe-research-blog` is one of the three probe-strategy kinds `references/query-strategies.md` §Probe-strategy schema registers, but **no v2.0 workflow step dispatches it**: the skill never derives a venue set from `tags:` or a topic-tag catalog, and no path routes a cited source to a research-blog query. The per-blog URL templates in §Per-blog URL templates stay registered and valid for a future dispatch path; this fixture exercises the registration, not a live emission.

The schema-slot query the template would issue for a resolved-and-registered blog (e.g., the Anthropic sitemap, per §registered-query-strategy: probe-research-blog):

```
GET https://www.anthropic.com/sitemap.xml
```

Cache key: `sha256(normalized_url).hexdigest()` per `../../citation-detail-verify/references/cache-contract.md`.

## Expected skill behavior

No workflow step in `SKILL.md` §Workflow dispatches `probe-research-blog` at v2.0. A1 is resolved and walked entirely by §Source resolution / §Citation collection plus the always-on path-A arXiv listing (A1's `primary_category`); no research-blog probe is issued for it. The `probe-research-blog` strategy remains **registered** (§Probe-strategy schema enumerates it, and its URL templates in §Per-blog URL templates are live) but **undispatched** — the skill emits no row of any kind tied to a blog venue, and no network request against `www.anthropic.com` or `openai.com` occurs for this fixture.

Because A1 resolves and its citation walk plus path A yield no surviving candidate, the skill emits exactly one `probed-no-candidates` row for A1 at `status: pass`. Aggregate `verdict: pass`.

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect probe-research-blog in ~/.claude/skills/source-recency-probe/test-corpus/blog-probe.md count >=1` — satisfied by the registered-but-undispatched framing above, not a live dispatch.
