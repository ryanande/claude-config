---
title: Fixture — fail-shape (refresh detected a problem, verdict fail)
date: 2026-05-20
fixture: survey-refresh
expected_check_name: any
expected_status: fail
---

# Fixture — fail-shape

Invocation against a survey where at least one URL in `sources[]` is dead (HTTP 404). Per Stage 1 output-schema §Verdict computation, at least one `fail` row → envelope verdict `fail`. Aggregate verdict is `fail`.

## Invocation

```
/survey-refresh research-docs/content/survey/llm-review-landscape.md
```

Path only.

## Survey state at invocation (excerpt)

```yaml
---
title: "Landscape — LLM-based code review"
last-refreshed: 2026-05-15
sources:
  - "[S1] arXiv 2510.55555 — https://arxiv.org/abs/2510.55555"
  - "[S2] Acme Corp blog — Reviewer Bot v1 — https://acme.example.com/blog/reviewer-bot-v1"
---
```

`[S2]` host retired the URL since scaffold time — HTTP 404 at refresh.

## Expected skill behavior

`[S1]` returns HTTP 200 with unchanged body — no row. `[S2]` returns HTTP 404 → `detected-url-removed` row with `status: fail`. `## Refresh log` table verification produces a separate `detected-last-refreshed-bumped` row (out of scope for this fixture's verdict-fail focus).

The emitted-verdict-fail trajectory yields the envelope below.

## Expected envelope shape

```json
{
  "version": "1.0",
  "skill": "survey-refresh",
  "artifact": "research-docs/content/survey/llm-review-landscape.md",
  "invoked_at": "2026-05-20T00:00:00Z",
  "verdict": "fail",
  "rows": [
    {
      "citation-id": "[S2]",
      "check-name": "detected-url-removed",
      "status": "fail",
      "cited-value": "live",
      "actual-value": "404",
      "evidence-quote": "Not Found"
    }
  ],
  "cache": {"hits": 0, "misses": 2, "writes": 2}
}
```

Wire `version` is `"1.0"`.

## Success-criteria evidence

This fixture grounds one brief DSL row:

- `detect emitted-verdict-fail in ~/.claude/skills/survey-refresh/test-corpus/fail-shape.md count >=1`

Literal token `emitted-verdict-fail` appears in this fixture body at least once.

## Sidecar disposition evidence

The skill writes the envelope to `research-docs/content/survey/refresh-report-2026-05-20.md`. The input survey doc is byte-identical before and after the skill run. The author reads the sidecar, judges the `[S2]` removal (replace with archived URL? supersede with a different vendor blog? drop the citation?), and updates the survey body manually. Per Decision 9.
