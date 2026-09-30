---
title: Fixture — last-refreshed-bumped (refresh-log table consistent with frontmatter bump)
date: 2026-05-20
fixture: survey-refresh
expected_check_name: detected-last-refreshed-bumped
expected_status: pass
---

# Fixture — last-refreshed-bumped

Invocation against a survey whose `last-refreshed:` frontmatter value was bumped AND whose `## Refresh log` table has a corresponding most-recent row dated ≥ the new `last-refreshed:` value. Per Decision 12, the skill emits a `detected-last-refreshed-bumped` row with `status: pass` when the bump is consistent.

## Invocation

```
/survey-refresh research-docs/content/survey/llm-review-landscape.md
```

Path only.

## Survey state at invocation

```yaml
---
title: "Landscape — LLM-based code review"
last-refreshed: 2026-05-15
sources:
  - "[S1] arXiv 2510.55555 — https://arxiv.org/abs/2510.55555"
---
```

Survey body (relevant excerpt):

```markdown
## Refresh log

| Date | Change |
|------|--------|
| 2025-11-01 | Initial scaffold. |
| 2026-05-15 | Re-walked sources[]; bumped last-refreshed; added [S2] arXiv 2602.99999. |
```

The most-recent row's date (`2026-05-15`) equals the frontmatter `last-refreshed:` value — consistent bump.

## Expected skill behavior

1. Read frontmatter; capture `last-refreshed: 2026-05-15`.
2. Locate the `## Refresh log` section; parse the markdown table; capture the most-recent row's date (`2026-05-15`).
3. Per Decision 12: compare. Most-recent ≥ frontmatter → consistent → `status: pass`.
4. Emit `detected-last-refreshed-bumped` row per `../references/refresh-report-schema.md` §`detected-last-refreshed-bumped`.

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
      "citation-id": "last-refreshed",
      "check-name": "detected-last-refreshed-bumped",
      "status": "pass",
      "cited-value": "2026-05-15",
      "actual-value": "2026-05-15",
      "evidence-quote": "| 2026-05-15 | Re-walked sources[]; bumped last-refreshed; added [S2] arXiv 2602.99999. |"
    }
  ]
}
```

Wire `version` is `"1.0"`. `cited-value` is the frontmatter `last-refreshed:` value; `actual-value` is the most-recent refresh-log row's date.

## Success-criteria evidence

This fixture grounds one brief DSL row:

- `detect detected-last-refreshed-bumped in ~/.claude/skills/survey-refresh/test-corpus/last-refreshed-bumped.md count >=1`

Literal token `detected-last-refreshed-bumped` appears in this fixture body at least once.

## Failure-mode counterpart

A mismatch case (e.g., `last-refreshed: 2026-05-15` but most-recent table row `2026-03-15`) would emit the same row with `status: fail`. A missing `## Refresh log` table entirely would emit with `status: unverifiable`. Both alternate trajectories are documented in `../references/refresh-report-schema.md` §`last-refreshed:` verification rule.
