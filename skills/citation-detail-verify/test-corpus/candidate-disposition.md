---
title: Fixture — candidate-disposition (a failing citation dispositions its proposal-time record)
date: 2026-09-06
fixture: citation-detail-verify
expected_check_name: year-match
expected_status: fail
sources:
  - {id: A7, title: "Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges", url: "https://arxiv.org/abs/2406.12624", year: 2023, tier: 1}
---

# Fixture — candidate-disposition

`content/rfc/0031-review-judges.md` cites [A7] with `year: 2023`; arXiv v1 was
posted 2024-06. Workflow step 3 emits `year-match: fail`; the other five checks
pass. Step 5 then finds [A7]'s proposal-time record and dispositions it.

## Sidecar before

```
{"candidate":{"id":"A7","title":"Judging the Judges: ...","url_or_identifier":"https://arxiv.org/abs/2406.12624"},"disposition":"proposed","disposition_stage":null,"label":null,"dispositioned_at":null,"record_id":"3f9a1c2b7d0e","session_id":"s-0906","stage":"gather",...}
```

## Invocation

```
python3 ~/.claude/skills/citation-detail-verify/scripts/candidates.py list --repo "$R" --artifact content/rfc/0031-review-judges.md
python3 ~/.claude/skills/citation-detail-verify/scripts/candidates.py append-disposition --repo "$R" --artifact content/rfc/0031-review-judges.md --record-id 3f9a1c2b7d0e --disposition dropped-at-citation-detail-verify --stage citation-detail-verify --label Minor
```

## Sidecar after

```
{...,"disposition":"dropped-at-citation-detail-verify","disposition_stage":"citation-detail-verify","label":"Minor","dispositioned_at":"2026-09-06T14:02:11Z",...}
```

Every other line byte-identical; the envelope is unchanged.

## Invariants exercised

- `Minor`, not `Major`: one detail check failed, the source exists. A
  `url-liveness` fail or two failing detail checks would be `Major`.
- The record was resolved through `list` and targeted by `--record-id`, so the
  same rule works when this skill runs in a later session than the proposal.
- A citation with no matching `proposed` record writes nothing — the
  denominator is what was proposed, never what was verified.
- A citation whose six rows all `pass` writes nothing here; `landed` is the
  authoring stage's landing sweep, not this skill's.
