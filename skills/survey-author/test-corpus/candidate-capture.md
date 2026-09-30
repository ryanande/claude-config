---
title: Fixture — candidate-capture (gap-find proposals recorded before the Stage 1c WebFetch)
date: 2026-09-06
fixture: survey-author
expected_check_name: recorded-candidate-before-fetch
expected_status: pass
---

# Fixture — candidate-capture

The author has scaffolded `content/survey/llm-review-landscape.md` and spawned
the Stage 1c gap-find subagent. It returns two proposals. Under
`../SKILL.md` §Proposal-time candidate capture the author records both BEFORE
fetching either — that is the `recorded-candidate-before-fetch` trajectory.

## Subagent output (verbatim, as returned)

```json
[
  {"stage": "gap-find", "id": "A45", "title": "CodeCriticBench: A Holistic Code Critique Benchmark",
   "url": "https://arxiv.org/abs/2410.00151",
   "sentence": "CodeCriticBench establishes a holistic critique benchmark spanning both code generation and QA [A45].",
   "source_in_context": false},
  {"stage": "gap-find", "id": "A46", "title": "Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges",
   "url": "https://arxiv.org/abs/2406.12624",
   "sentence": "Thakur et al. report that judge models diverge sharply from human labels on adversarial items [A46].",
   "source_in_context": false}
]
```

## Invocation (before any WebFetch)

```
python3 ~/.claude/skills/citation-detail-verify/scripts/candidates.py append --repo "$WT" --artifact content/survey/llm-review-landscape.md --from-json proposals.json
```

Prints two `record_id`s. `content/survey/llm-review-landscape.md.candidates.jsonl`
now holds two lines, both `disposition: proposed`, `stage: gap-find`,
`source_in_context: false`, sentences verbatim.

## Re-read and commit

The Stage 1c WebFetch of `arxiv.org/abs/2410.00151` returns a paper titled
"Scheherazade" (math reasoning) — the title-to-id mapping was fabricated:

```
candidates.py append-disposition --repo "$WT" --artifact content/survey/llm-review-landscape.md --candidate-id A45 --disposition dropped-at-reread --stage survey-author --label Major
```

`A46` fetches clean and enters `sources[]`. At commit the landing sweep runs:

```
candidates.py append-disposition ... --candidate-id A46 --disposition landed --stage survey-author --label Exact
```

## Expected sidecar (committed with the survey)

```
{"artifact":"content/survey/llm-review-landscape.md","candidate":{"id":"A45",...},"disposition":"dropped-at-reread","disposition_stage":"survey-author","label":"Major",...,"sentence":"CodeCriticBench establishes ...","source_in_context":false,"stage":"gap-find",...}
{"artifact":"content/survey/llm-review-landscape.md","candidate":{"id":"A46",...},"disposition":"landed","disposition_stage":"survey-author","label":"Exact",...,"source_in_context":false,"stage":"gap-find",...}
```

## Invariants exercised

- Both records exist BEFORE the first WebFetch — the denominator cannot be
  filtered by the stage it measures. Token: `recorded-candidate-before-fetch`.
- `source_in_context: false` on both: the subagent proposed from memory. This is
  EVAL-0001's primary (unfetched) stratum and EVAL-0002's population.
- The fabricated A45 is not deleted; it is dispositioned `dropped-at-reread`
  with `Major`, so the study sees the catch and its stage.
- No record is still `proposed` after the landing sweep.
- `--seed-urls` passed to the scaffold invocation were NOT recorded.
