---
title: Fixture — candidate-capture (each new-candidate-found row is also a recorded proposal)
date: 2026-09-06
fixture: source-recency-probe
expected_check_name: new-candidate-found
expected_status: fail
authored_against: claude-opus-4-7,2025-09-01
sources:
  - id: A1
    title: "Constitutional AI"
    url: "https://arxiv.org/abs/2212.08073"
    year: 2022
---

# Fixture — candidate-capture

Same probe as `new-candidate.md`; this fixture pins the side effect Workflow
step 6 adds: every `new-candidate-found` (and `source-superseded-by-newer`) row
is a proposed candidate and is written to the artifact's `candidates.jsonl`
per `../../citation-detail-verify/references/candidates-contract.md`.

## Emitted row

```json
{"citation-id": "arXiv:2510.12345", "check-name": "new-candidate-found", "status": "fail",
 "cited-value": "[A1]", "actual-value": "Programmatic Quality Gates for LLM-Authored Code · 2025-10-04 · 7",
 "evidence-quote": "Programmatic Quality Gates for LLM-Authored Code"}
```

## Recorded candidate row

```
python3 ~/.claude/skills/citation-detail-verify/scripts/candidates.py append --repo <artifact-checkout> --artifact content/survey/llm-review-landscape.md --stage recency-probe-candidate --url "arXiv:2510.12345" --title "Programmatic Quality Gates for LLM-Authored Code" --source-in-context false --published-year 2025 --cited-by-count 7 --reference-class arxiv-preprint
```

yielding one sidecar line with `stage: recency-probe-candidate`, `sentence: ""`,
`source_in_context: false`, `source_meta: {"published_year": 2025, "openalex_cited_by_count": 7, "reference_class": "arxiv-preprint"}`,
`disposition: proposed`. Token for this side effect: `recorded-candidate-row`.

## Invariants exercised

- One recorded candidate row per `new-candidate-found` /
  `source-superseded-by-newer` row; `probed-no-candidates`, `source-unresolved`,
  `venue-absent-from-sources`, and `nothing-to-probe` rows record nothing.
- `sentence` is empty — the probe proposes metadata, not prose — so the row is
  in EVAL-0002's population and outside EVAL-0001's.
- `source_meta` is populated from the OpenAlex work at capture time, which is
  what EVAL-0001's arm proxy asks for.
- The envelope is unchanged: the record is a side effect, not a row field, so
  the shared output-schema lock is not touched.
