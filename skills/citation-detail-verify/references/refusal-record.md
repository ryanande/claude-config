---
title: Refusal-record contract for the research-pipeline skills
version: 1.4
status: locked
owners: [citation-detail-verify]
consumers: [citation-detail-verify, load-bearing-fullread, adversarial-frame, source-recency-probe, survey-author, criteria-validate, survey-refresh, invocation-discipline-lint]
---

# Refusal record v1.0

Locked at Stage 1 of the research-pipeline skill family. The consumer skills listed in `consumers:` above SHALL emit refusal records conforming to this shape when they refuse an invocation that violates their `SKILL.md` §Invocation discipline. Independently versioned from `references/output-schema.md`; major-version bumps coordinate with the envelope's major, minor-version bumps are independent.

## Shape

```json
{
  "version": "1.0",
  "skill": "<skill-slug>",
  "invoked_at": "<ISO-8601 UTC>",
  "refusal": {
    "category": "bias | bloat",
    "rule": "<verbatim bullet from the refusing skill's SKILL.md §Invocation discipline>",
    "evidence": "<offending input slice — the flag, value, or attachment that triggered the refusal>"
  }
}
```

## Required fields

| Field | Type | Notes |
|-------|------|-------|
| `version` | string | MUST equal `"1.0"`. Major-version namespace is shared with `references/output-schema.md` (bumps coordinate); minor-version is independent. |
| `skill` | string | The refusing skill's slug. |
| `invoked_at` | string | ISO-8601 UTC timestamp, second precision. |
| `refusal` | object | The three sub-fields below are all required. |
| `refusal.category` | string | Enum: `bias` or `bloat`. Maps to the OUT-bias / OUT-bloat dimensions of the skill-invocation-discipline framework. |
| `refusal.rule` | string | The verbatim bullet from the refusing skill's `SKILL.md` §Invocation discipline (or its equivalent in the founding brief) that the invocation violated. Verbatim so the caller can locate the rule and fix the invocation. |
| `refusal.evidence` | string | The specific offending input — the flag name + value (`"--focus [A18]"`), the attached body bytes preview (first 200 chars + `…`), or the equivalent slice. Long evidence MUST be truncated to ≤500 chars with `…` suffix. |

## Optional fields

| Field | Type | Notes |
|-------|------|-------|
| `notes` | string | Free-text. Suppressed when empty. |
| `multi` | array | When the invocation violated multiple rules, MAY hold an array of `{category, rule, evidence}` objects in addition to the primary `refusal` field (which always holds the first or dominant violation). Absent when only one rule was violated. |

## Distinguishing refusal records from envelopes

A consumer parser SHALL determine the message kind by the top-level shape:

- Presence of `rows` (array) → envelope per `references/output-schema.md` §Envelope.
- Presence of `refusal` (object) → refusal record per this file.
- Both present OR neither present → malformed; consumers MUST reject.

## Versioning

- Major (`2.0`) — breaking change to `refusal.*` required fields. Coordinated with `references/output-schema.md` major bump (envelopes and refusal records share a major namespace so consumer parsers fail closed together).
- Minor (`1.1`) — additive only. New optional fields. New `refusal.category` enum values bump the minor (consumers ignore unknown enum values gracefully by treating as `bias`). Independent of `references/output-schema.md` minor bumps.
- v1.0 is the locked Stage 1 contract. Downstream skills SHALL reference this file verbatim and SHALL NOT shadow the required fields.
