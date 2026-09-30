---
fixture: bad-invocations
exercises: emitted-refusal-record
expected-verdict: refused
---

# Fixture — bad-invocations

Five forbidden invocations exercising the skill's five OUT-bias / OUT-bloat surfaces per `SKILL.md` §Invocation discipline. Each emits a refusal record per `../citation-detail-verify/references/refusal-record.md` v1.1. Wire `version` field is `"1.0"` per the lock's §Shape (lock-document frontmatter `version: 1.1` is metadata only).

## Invocation 1 — bias: author's interpretation of cited evidence

Bad invocation:

```
/load-bearing-fullread --artifact content/rfc/0001.md --source-ids A18 \
    --note "I cited [A18] for the finding that ensembles overconfidently misjudge contested questions in code review"
```

The `--note` carries the author's interpretation of `[A18]`'s framing for the code-review context. Skill emits an `emitted-refusal-record`:

```json
{
  "version": "1.0",
  "skill": "load-bearing-fullread",
  "invoked_at": "2026-05-19T18:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "Author's interpretation of cited evidence.",
    "evidence": "--note \"I cited [A18] for the finding that ensembles overconfidently misjudge contested questions in code review\""
  }
}
```

## Invocation 2 — bias: pre-named framing issues to check for

Bad invocation:

```
/load-bearing-fullread --artifact content/rfc/0001.md --source-ids A8 \
    --focus framing-drift-relative-vs-absolute
```

Caller pre-names the probe to focus on; invalidates the other three probes' outputs. Skill emits an `emitted-refusal-record`:

```json
{
  "version": "1.0",
  "skill": "load-bearing-fullread",
  "invoked_at": "2026-05-19T18:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "Pre-named framing issues to check for.",
    "evidence": "--focus framing-drift-relative-vs-absolute"
  }
}
```

## Invocation 3 — bias: author's prose excerpt surrounding the citation

Bad invocation:

```
/load-bearing-fullread --artifact content/rfc/0001.md --source-ids A10 \
    --context-excerpt "Tencent's pipeline achieves 94-98% false-positive reduction, supporting LLM-as-primary-reviewer architecture."
```

Caller attaches artifact's prose framing of `[A10]`; the artifact-side framing is what the skill is independently verifying. Skill emits an `emitted-refusal-record`:

```json
{
  "version": "1.0",
  "skill": "load-bearing-fullread",
  "invoked_at": "2026-05-19T18:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "Author's prose excerpt surrounding the citation.",
    "evidence": "--context-excerpt \"Tencent's pipeline achieves 94-98% false-positive reduction, supporting LLM-as-primary-reviewer architecture.\""
  }
}
```

## Invocation 4 — bloat: attached source full-texts

Bad invocation:

```
/load-bearing-fullread --artifact content/rfc/0001.md --source-ids A8 \
    --attach-source "[A8 paper full text — 12000 words of Abstract / Introduction / Methods / Results / Discussion content pasted into the flag value]"
```

Caller attaches the full source body; duplicates the WebFetch the skill performs. Skill emits an `emitted-refusal-record`:

```json
{
  "version": "1.0",
  "skill": "load-bearing-fullread",
  "invoked_at": "2026-05-19T18:00:00Z",
  "refusal": {
    "category": "bloat",
    "rule": "Attached source full-texts.",
    "evidence": "--attach-source \"[A8 paper full text — 12000 words of Abstract / Introduction / Methods / Results / Discussion content pasted into the flag value]\""
  }
}
```

## Invocation 5 — bloat: full artifact body

Bad invocation:

```
/load-bearing-fullread --artifact content/rfc/0001.md --artifact-body "[8000-word RFC body pasted into the flag value covering background, proposal, alternatives, decisions, open questions]" --source-ids A8,A10,A18
```

Caller supplies `--artifact` AND attaches the full artifact body via `--artifact-body`. The required-arg check passes (path supplied); the bloat-check fires on the attached body. Refusal precedence: bias / bloat surfaces detected at invocation-discipline step (Workflow step 2) take precedence over the optional-flag-unknown case because the surface is the documented forbidden surface, not the unknown flag itself. Skill emits an `emitted-refusal-record`:

```json
{
  "version": "1.0",
  "skill": "load-bearing-fullread",
  "invoked_at": "2026-05-19T18:00:00Z",
  "refusal": {
    "category": "bloat",
    "rule": "Full artifact body.",
    "evidence": "--artifact-body \"[8000-word RFC body pasted into the flag value covering background, proposal, alternatives, decisions, open questions]\""
  }
}
```

## Notes

Five `emitted-refusal-record` instances — three bias + two bloat — exhaust the §Invocation discipline forbidden surface set. Each refusal-record's `refusal.rule` is the verbatim bullet from `SKILL.md` §Invocation discipline.

Wire `version: "1.0"` per the refusal-record lock §Shape; the lock's frontmatter `version: 1.1` reflects Stage 3's additive consumers-list amendment and is lock-document metadata only.
