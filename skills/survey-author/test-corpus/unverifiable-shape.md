---
title: Fixture — unverifiable-shape (WebFetch cannot probe seed URL; verdict unverifiable)
date: 2026-05-19
fixture: survey-author
expected_check_name: applied-tier-1-rubric
expected_status: unverifiable
---

# Fixture — unverifiable-shape

Invocation seeded with a URL the WebFetch content probe cannot reach (paywalled PDF behind login, JS-only single-page app, or HTTP ≥4xx response). The tier cannot be classified mechanically; the scaffold still emits with the URL labeled `tier: unverifiable`, and the Stage 3 driver carries one row with `status: unverifiable`.

Per `../references/output-schema.md` §Verdict computation, any `unverifiable` row (with no `fail` row) drives the aggregate verdict to `unverifiable`.

## Invocation

```
/survey-author --question "What does the evidence say about closed-system code review?" --tags llm-review --target-repo research-docs --seed-urls https://paywalled-journal.example.com/article/123.pdf
```

The seed URL matches no tier-1 / tier-2 pattern in pass-1, so the skill would normally classify as tier-3 default (no pass-2 needed). HOWEVER — for fixtures where the URL must surface as `unverifiable`, the rubric per `../references/source-tier-rubric.md` §Unverifiable triggers on WebFetch failure mode. This fixture assumes the URL returns HTTP 403 on probe.

## Expected skill behavior

Per `../references/source-tier-rubric.md` §Failure modes and dispositions, WebFetch failure on a candidate URL routes to tier label `unverifiable`. The scaffold writes the URL with `tier: unverifiable` so the human author can manually re-tier after verification.

The emitted-verdict-unverifiable trajectory yields the envelope below.

## Expected envelope shape

```json
{
  "version": "1.0",
  "skill": "survey-author",
  "artifact": "research-docs/content/survey/closed-system-code-review.md",
  "invoked_at": "<ISO-8601 UTC>",
  "verdict": "unverifiable",
  "rows": [
    {
      "criterion-id": "applied-tier-1-rubric",
      "status": "unverifiable",
      "evidence-quote": "paywalled-journal.example.com/article/123.pdf returned HTTP 403 on WebFetch probe; tier cannot be classified mechanically"
    }
  ]
}
```

## Success-criteria evidence

This fixture grounds the brief DSL row: `detect emitted-verdict-unverifiable in ~/.claude/skills/survey-author/test-corpus/unverifiable-shape.md count >=1`.

The literal token `emitted-verdict-unverifiable` appears in this fixture body at least once, satisfying the author-time literal-token grep gate.

## Corpus-wide invariant evidence

The scaffolded body that would result from this invocation contains the required sections per `../references/output-schema.md` §Required section structure. No decision-statement section appears (per §Forbidden section titles).
