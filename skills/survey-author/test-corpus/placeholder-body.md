---
title: Fixture — placeholder-body (scaffold written but evidence walk never ran; verdict fail)
date: 2026-07-30
fixture: survey-author
expected_check_name: ran-evidence-walk
expected_status: fail
---

# Fixture — placeholder-body

Invocation that completes the scaffold (workflow step 6) and stops there — the survey doc is written, the frontmatter is well-formed, the seed URLs are tier-classified, and every body section still carries the one-sentence author prompt the template emitted. Per local divergence 3 (`../SKILL.md` header) and workflow step 7, this is an **incomplete invocation, not a completed scaffold**, and the aggregate verdict is `fail`.

This fixture is local to this config. It has no counterpart in the upstream skill, which treats the scaffold as the deliverable.

## Invocation

```
/survey-author --question "What does the evidence say about LLM-based code-review effectiveness?" --tags llm-review --target-repo research-docs --seed-urls https://arxiv.org/abs/2510.55555
```

A well-formed invocation. Nothing in the input triggers a refusal surface, and nothing about the arguments makes the walk impossible — the failure is a skipped phase, not a bad request.

## Expected skill behavior

Steps 1–6 succeed: the seed URL classifies tier 1 cleanly and the doc lands at `research-docs/content/survey/<slug>.md`. Step 7 then does not run, so `## Landscape`, `## Comparison`, and `## Open questions` are delivered carrying template prompts rather than authored content, `## Method` names no query families, and `sources:` contains only the single seed URL with no walk-discovered entries.

The skill MUST detect this at **step 10**, not at step 9. That placement is the whole point of the fixture: this trajectory skips steps 7, 8 and 9 together, so a guard emitted from inside the walk phase would be skipped along with the phase it guards, and the invocation would fall through to tier rows and an aggregate `pass`. Step 10 runs on every non-refused invocation. It re-reads the written file from disk and emits a `ran-evidence-walk` row at `fail` before any tier row. The evidence-quote carries the first surviving template prompt verbatim, which is what makes the row falsifiable: a delivered body either contains template prompt text or it does not.

Note that the tier-classification rows still pass. That is the trap this fixture exists to close: under the pre-divergence row set, every emitted row would be `pass` and the aggregate verdict would be `pass` per `../references/output-schema.md` §Verdict computation — indistinguishable, to a downstream consumer, from a fully authored survey. The `ran-evidence-walk` row is what makes an unwritten survey visible in the envelope. This is the same silent-pass hazard `../../source-recency-probe/references/query-strategies.md` records for uncatalogued topic tags, in a different surface.

The emitted-verdict-fail-on-placeholder-body trajectory yields the envelope below.

## Expected envelope shape

```json
{
  "version": "1.0",
  "skill": "survey-author",
  "artifact": "research-docs/content/survey/llm-based-code-review-effectiveness.md",
  "invoked_at": "<ISO-8601 UTC>",
  "verdict": "fail",
  "rows": [
    {
      "criterion-id": "ran-evidence-walk",
      "status": "fail",
      "evidence-quote": "## Landscape retains template prompt 'Author writes one subsection per pattern observed in the evidence.'; ## Method names zero query families; sources: carries 1 entry (seed) and 0 walk-discovered"
    },
    {
      "criterion-id": "applied-tier-1-rubric",
      "status": "pass",
      "evidence-quote": "arxiv.org/abs/2510.55555 confirmed via 'Abstract' + 'DOI:' sniff"
    }
  ]
}
```

The aggregate verdict is `fail` because at least one row carries `fail`, per `../references/output-schema.md` §Verdict computation (`fail` dominates `unverifiable` dominates `pass`).

## Success-criteria evidence

This fixture grounds the local DSL row: `detect emitted-verdict-fail-on-placeholder-body in ~/.claude/skills/survey-author/test-corpus/placeholder-body.md count >=1`.

The literal token `emitted-verdict-fail-on-placeholder-body` appears in this fixture body at least once, satisfying the author-time literal-token grep gate.

## Corpus-wide invariant evidence

This fixture describes a delivered body that retains template prompts, but does so in prose and inside a JSON evidence-quote — it does not itself carry the forbidden literal token, which is reserved for the corpus-wide `absent` gate in the same way the other two corpus-wide gates in `../SKILL.md` §Success criteria reserve theirs. Those two tokens are deliberately not spelled here for that reason.

No decision-statement section appears anywhere in the described body (per `../references/output-schema.md` §Forbidden section titles). The failure this fixture encodes is an absence of authored evidence, never the presence of a verdict.
