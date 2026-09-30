---
title: Fixture — conference-probe (probe-named-conference is registered but undispatched at v2.0)
date: 2026-05-19
fixture: source-recency-probe
expected_check_name: probe-named-conference
expected_status: pass
authored_against: claude-opus-4-7,2025-09-01
sources:
  - id: A1
    title: "Reviewer-Calibration Practices in Software Engineering"
    url: "https://arxiv.org/abs/2401.00001"
    year: 2024
---

# Fixture — conference-probe

Refreshed to v2.0 semantics. `probe-named-conference` is one of the three probe-strategy kinds `references/query-strategies.md` §Probe-strategy schema registers, but **no v2.0 workflow step dispatches it**: the skill never derives a venue set from `tags:` or a topic-tag catalog, and no path routes a cited source to a named-conference query. The per-conference URL templates in §Per-conference URL templates stay registered and valid for a future dispatch path; this fixture exercises the registration, not a live emission.

The schema-slot query the template would issue for a resolved-and-registered conference (e.g., NeurIPS via the OpenReview venue-id, per §registered-query-strategy: probe-named-conference):

```
GET https://api2.openreview.net/notes?content.venueid=NeurIPS.cc/2025/Conference&details=replyCount&offset=0&limit=200
```

Cache key: `sha256(normalized_url).hexdigest()` per `../../citation-detail-verify/references/cache-contract.md`.

## Expected skill behavior

No workflow step in `SKILL.md` §Workflow dispatches `probe-named-conference` at v2.0. A1 is resolved and walked entirely by §Source resolution / §Citation collection plus the always-on path-A arXiv listing (A1's `primary_category`); no named-conference probe is issued for it. The `probe-named-conference` strategy remains **registered** (§Probe-strategy schema enumerates it, and its URL templates in §Per-conference URL templates are live) but **undispatched** — the skill emits no row of any kind tied to a conference venue, and no network request against `api2.openreview.net` or `aclanthology.org` occurs for this fixture.

Because A1 resolves and its citation walk plus path A yield no surviving candidate, the skill emits exactly one `probed-no-candidates` row for A1 at `status: pass`. Aggregate `verdict: pass`.

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect probe-named-conference in ~/.claude/skills/source-recency-probe/test-corpus/conference-probe.md count >=1` — satisfied by the registered-but-undispatched framing above, not a live dispatch.
