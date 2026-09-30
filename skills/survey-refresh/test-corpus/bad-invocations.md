---
title: Fixture — bad-invocations (5 forbidden invocations, refusal-record each)
date: 2026-05-20
fixture: survey-refresh
expected_check_name: refusal-record
expected_status: refusal
---

# Fixture — bad-invocations

Five forbidden invocations covering the 3 bias surfaces + 2 bloat surfaces declared in `../SKILL.md` §Invocation discipline. Each one MUST trigger a refusal-record per `../../citation-detail-verify/references/refusal-record.md` v1.3 (REUSED unchanged in wire shape). Wire `version` per refusal-record §Shape is `"1.0"`.

## Invocation 1 — Bias: caller's preferred refresh outcome

```
/survey-refresh content/survey/llm-review-landscape.md --expect-pass "everything should be fine, just confirm no urls broke"
```

The flag encodes a preferred refresh outcome (confirmation-search) before the skill walks the URLs.

### Expected refusal record (emitted-refusal-record)

```json
{
  "version": "1.0",
  "skill": "survey-refresh",
  "invoked_at": "2026-05-20T00:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "Bias — Caller's preferred refresh outcome.",
    "evidence": "--expect-pass \"everything should be fine, just confirm no urls broke\""
  }
}
```

## Invocation 2 — Bias: per-URL pre-classification

```
/survey-refresh content/survey/llm-review-landscape.md --i-think-source-S3-is-stale
```

The flag frames the URL-check before the skill walks `[S3]`.

### Expected refusal record (emitted-refusal-record)

```json
{
  "version": "1.0",
  "skill": "survey-refresh",
  "invoked_at": "2026-05-20T00:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "Bias — Per-URL pre-classification.",
    "evidence": "--i-think-source-S3-is-stale"
  }
}
```

## Invocation 3 — Bias: expected refresh-report verdict

```
/survey-refresh content/survey/llm-review-landscape.md --expected-verdict fail
```

The flag short-circuits the surface the refresh is supposed to discover.

### Expected refusal record (emitted-refusal-record)

```json
{
  "version": "1.0",
  "skill": "survey-refresh",
  "invoked_at": "2026-05-20T00:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "Bias — Expected refresh-report verdict.",
    "evidence": "--expected-verdict fail"
  }
}
```

## Invocation 4 — Bloat: full survey body attachment

```
/survey-refresh content/survey/llm-review-landscape.md --attach-body "<full markdown text of the survey body, 12kb …>"
```

The skill reads frontmatter + `## Refresh log` table only; body re-walking belongs in `/load-bearing-fullread`.

### Expected refusal record (emitted-refusal-record)

```json
{
  "version": "1.0",
  "skill": "survey-refresh",
  "invoked_at": "2026-05-20T00:00:00Z",
  "refusal": {
    "category": "bloat",
    "rule": "Bloat — Full survey body attachment.",
    "evidence": "--attach-body \"<full markdown text of the survey body, 12kb …>\""
  }
}
```

## Invocation 5 — Bloat: full text of currently-cited sources

```
/survey-refresh content/survey/llm-review-landscape.md --attach-source-bodies "S1: <full text of arxiv paper> | S2: <full text of acme blog>"
```

The skill re-fetches each URL itself; pre-attached source bodies bias the staleness sniff.

### Expected refusal record (emitted-refusal-record)

```json
{
  "version": "1.0",
  "skill": "survey-refresh",
  "invoked_at": "2026-05-20T00:00:00Z",
  "refusal": {
    "category": "bloat",
    "rule": "Bloat — Full text of currently-cited sources.",
    "evidence": "--attach-source-bodies \"S1: <full text of arxiv paper> | S2: <full text of acme blog>\""
  }
}
```

## Success-criteria evidence

This fixture grounds one brief DSL row:

- `detect emitted-refusal-record in ~/.claude/skills/survey-refresh/test-corpus/bad-invocations.md count >=5`

Literal token `emitted-refusal-record` appears in this fixture body at least 5 times (one per invocation section heading).

## Wire-version evidence

Every refusal-record example above carries wire `"version": "1.0"` per refusal-record lock §Shape. The lock's frontmatter `version: 1.3` is lock-document metadata, not wire payload — per inbox lesson on lock-frontmatter-vs-wire-version. The `skill` field equals `"survey-refresh"` in every record.
