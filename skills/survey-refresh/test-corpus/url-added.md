---
title: Fixture — url-added (single advisory row recommending a recency probe)
date: 2026-05-20
fixture: survey-refresh
expected_check_name: detected-url-added
expected_status: pass
---

# Fixture — url-added

Invocation against any survey with non-empty `sources[]`. The skill emits exactly one advisory `detected-url-added` row (`citation-id: advisory:source-recency-probe`, `status: pass`) whose `evidence-quote` tells the author to run `/source-recency-probe`. No venue inference from `tags:` occurs.

## Invocation

```
/survey-refresh research-docs/content/survey/llm-review-landscape.md
```

Path only. No optional flags.

## Survey state at invocation (excerpt)

```yaml
---
title: "Landscape — LLM-based code review"
tags: [llm-review, code-quality, software-engineering]
sources:
  - "[S1] arXiv 2510.55555 — LLM Reviewer Effectiveness — https://arxiv.org/abs/2510.55555"
---
```

The survey's `sources[]` carries one paper. The skill does not read `tags:` for this row — the single advisory row fires on any non-empty `sources[]` regardless of tag content.

## Expected skill behavior

1. Read frontmatter; confirm `sources[]` is non-empty.
2. Emit exactly one `detected-url-added` row: `citation-id: advisory:source-recency-probe`, `status: pass` (informational row; no in-survey defect to remediate).
3. Other probes (URL-removed, citation-stale, last-refreshed-bumped) run independently; out of scope for this fixture.

## Expected envelope shape (relevant row)

```json
{
  "version": "1.0",
  "skill": "survey-refresh",
  "artifact": "research-docs/content/survey/llm-review-landscape.md",
  "invoked_at": "2026-05-20T00:00:00Z",
  "verdict": "pass",
  "rows": [
    {
      "citation-id": "advisory:source-recency-probe",
      "check-name": "detected-url-added",
      "status": "pass",
      "cited-value": "",
      "actual-value": "run /source-recency-probe to surface post-cutoff candidates from the citation graph of sources[]",
      "evidence-quote": "Run /source-recency-probe --artifact research-docs/content/survey/llm-review-landscape.md --authored-against claude-opus-4-7,2025-09-01 to surface post-cutoff candidates from the citation graph of sources[]."
    }
  ]
}
```

Wire `version` is `"1.0"`. `cited-value` is the literal empty string per Stage 1 lock §Required row fields rule for new-candidate rows.

## Success-criteria evidence

This fixture grounds one brief DSL row:

- `detect detected-url-added in ~/.claude/skills/survey-refresh/test-corpus/url-added.md count >=1`

Literal token `detected-url-added` appears in this fixture body at least once.

## Cross-skill composition evidence

The skill does NOT invoke `/source-recency-probe` as a nested call. The row's `evidence-quote` instructs the author to run `/source-recency-probe` as a follow-on invocation. Per Decision 7 — composable but independent. Stage 3 D7 precedent.
