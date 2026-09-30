# OQ-resolver — evidence-strength reference

Load at Step 6. The four-rung ladder, the six transfer-argument axes, and the
reversal-cost test. Cited by `study-design`; `adversarial-frame` and
`survey-author` become consumers in a follow-on change. This file is
canonical, consumers link to it.

## The ladder

Assigned per `unblock-by` item, not per open question — a question typically has
three items sitting at different strengths.

| Rung | Meaning |
|---|---|
| `measured-local` | A number from this repository's own corpus or telemetry, against a pre-registered metric. |
| `direct-external` | Published, same task shape, same artifact kind. |
| `adjacent-domain` | Published, different domain or scale. Carries only with a stated transfer argument. |
| `folklore` | Codified expert practice, no measurement behind it. |

## The transfer argument

Six axes, each rated `same`, `near`, or `far`:

| Axis | Asks |
|---|---|
| `task-shape` | What task the source measured, against what task this repository runs. |
| `artifact-kind` | Code, prose, reasoning trace, or decision document. |
| `study-n` | The source study's sample size, against what a local study could reach. |
| `deployment-scale` | The source's team size and operating context, against this one. |
| `actor` | Model family; self-review or independent review. |
| `evidence-reliability` | Replication status, source tier, and whether the reported absolute effect magnitude is large enough for the decision resting on it. |

Each axis rated `far` requires one sentence of why the result carries anyway, plus
one falsifier — a specific observation that would break the claim. Axes rated
`same` or `near` require nothing.

**Why `study-n` and `deployment-scale` are separate.** Collapsed into one `scale`
axis, every small-N study rates `same` for a single-developer repository — which
reads a study's stated limitation as a credential. A small n means the study is
cheap to replicate locally. It does not mean its result is strong.

**Why `evidence-reliability` exists.** The five distance axes cannot represent the
objection real parks are made on. The OQ-0050 park (research-docs commit `6d1bb8f`)
turned on "thin unreplicated 2026 preprints" reporting "low/unstable precision."
Without this axis every content axis rates `same` or `near`, no justification is
required, and the disposition reaches provisional promote without meeting the
objection. It differs in kind from the other five: it describes the source, not the
gap between source and question.

## The reversal-cost test

Three questions:

1. Can the decision be reversed by editing one skill or configuration file?
2. Does other already-landed work depend on this decision?
3. Does being wrong cost more than re-running the study later?

Cheap to flip, nothing depending on it, and cheap to unwind together permit
`adjacent-domain` evidence. Any failure routes to **measure**, never to park.

## Rules

- Rate every axis. An unrated axis is not the same as `same`.
- A `far` axis without both a carry-sentence and a falsifier blocks promote
  (provisional); it does not silently downgrade to `near`.
- The falsifier must be an observation, not a restatement of the risk. "This would
  fail if the effect does not transfer" is not a falsifier; "this would fail if a
  local run shows precision below the study's reported floor" is.
- Never infer a rung from prose tone. Read the source's own stated scope.
