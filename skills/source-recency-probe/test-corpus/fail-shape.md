---
title: Fixture — fail-shape (at least one finding, verdict fail)
date: 2026-05-19
fixture: source-recency-probe
expected_check_name: new-candidate-found
expected_status: fail
authored_against: claude-opus-4-7,2025-09-01
sources:
  - id: A1
    title: "Pre-cutoff foundational paper"
    url: "https://arxiv.org/abs/2401.00001"
    year: 2024
---

# Fixture — fail-shape

Refreshed to v2.0 semantics. A1 resolves on the citation graph (`resolved`) with `primary_category: cs.SE`. Path A is always-on for A1 (an arXiv source) as a second signal alongside the citation walk. Either the OpenAlex cited-by walk (§Citation collection) or the always-on `arxiv:cs.SE` path-A listing (§Probe-strategy schema `probe-arxiv-category`, pinned to A1's own cited title — never a topic vector) surfaces a post-cutoff candidate that is not in `sources[]` (synthetic ground-truth; this fixture does not distinguish which path found it, since both paths join the same §Ranking and caps pool):

- `citation-id`: `arxiv:2511.77777`
- title: "Reviewer-Calibration Audit Across 12-Month Window"
- date: 2025-11-20 (post-cutoff)
- abstract excerpt: "We audit 8,200 reviewer-calibration runs and report systematic bias against post-cutoff submissions…"

## Expected skill behavior

Per `../../citation-detail-verify/references/output-schema.md` §Verdict computation, at least one `fail` row → aggregate `verdict: fail`.

Expected envelope shape:

```json
{
  "version": "1.0",
  "skill": "source-recency-probe",
  "artifact": "<this-fixture-path>",
  "invoked_at": "<ISO-8601 UTC>",
  "verdict": "fail",
  "rows": [
    {
      "citation-id": "arxiv:2511.77777",
      "check-name": "new-candidate-found",
      "status": "fail",
      "cited-value": "[A1]",
      "actual-value": "Reviewer-Calibration Audit Across 12-Month Window",
      "evidence-quote": "We audit 8,200 reviewer-calibration runs and report systematic bias against post-cutoff submissions…"
    }
  ],
  "cache": {"hits": 0, "misses": 5, "writes": 5}
}
```

The emitted-verdict-fail trajectory MUST be detectable.

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect emitted-verdict-fail in ~/.claude/skills/source-recency-probe/test-corpus/fail-shape.md count >=1`.
