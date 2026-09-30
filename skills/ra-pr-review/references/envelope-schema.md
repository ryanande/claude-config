# Envelope schema — /ra-pr-review (self-contained)

The findings envelope and refusal record `/ra-pr-review` emits internally during adjudication.
Self-contained: this skill owns its output contract; it does not depend on any external locked
schema. The shape is the same fixed 6-field-row / 3-status-vocabulary / aggregate-verdict-
computation contract `review-artifact` uses, scoped to this skill's check-names and PR-review
semantics. Wire `version` is `"1.0"`. **The envelope never leaves the skill as a posted artifact —
it is the adjudication scratchpad behind the rendered PR comment (SKILL.md §Output).**

## Envelope

Top-level JSON object held internally per invocation:

```json
{
  "version": "1.0",
  "skill": "ra-pr-review",
  "artifact": "<PR URL>",
  "invoked_at": "<ISO-8601 UTC, second precision>",
  "verdict": "pass | fail | unverifiable",
  "rows": [ /* one row object per adjudicated finding, see below */ ],
  "notes": "<optional free-text; suppressed when empty; never load-bearing>"
}
```

### Envelope required fields

| Field | Type | Notes |
|-------|------|-------|
| `version` | string | MUST equal `"1.0"`. |
| `skill` | string | Always `"ra-pr-review"`. |
| `artifact` | string | The reviewed PR's URL. |
| `invoked_at` | string | ISO-8601 UTC timestamp, second precision. |
| `verdict` | string | Aggregate verdict over all rows — see §Verdict computation. |
| `rows` | array | One element per adjudicated finding. Empty array when the diff holds up under every lens AND the run was clean. |

### Envelope optional fields

| Field | Type | Notes |
|-------|------|-------|
| `notes` | string | Free-text (e.g. an escalation note for an `unverifiable` lens). Suppressed when empty. Never load-bearing. |

## Row shape

```json
{
  "citation-id": "<lens-id>",
  "check-name": "lens-finding-blocking | lens-finding-should-fix | lens-finding-minor",
  "status": "pass | fail | unverifiable",
  "cited-value": "<string>",
  "actual-value": "<string>",
  "evidence-quote": "<string>"
}
```

### Required row fields

| Field | Type | Semantics for /ra-pr-review | Empty-string rule |
|-------|------|-------------------------------|-------------------|
| `citation-id` | string | The **lens-id** — which lens surfaced the finding. MUST NOT be empty. |
| `check-name` | string | Closed enum of finding severity-category — see §Check-name vocabulary. MUST NOT be empty. |
| `status` | string | Enum `pass` \| `fail` \| `unverifiable`. MUST NOT be empty. See §Status semantics. |
| `cited-value` | string | The diff span / claim the finding is about ("the value as it appears in the diff"). Literal `""` permitted only where no diff span applies (e.g. a dead-critic synthetic row). |
| `actual-value` | string | The critic's asserted correction / what the orchestrator's read of the real file says instead. Literal `""` permitted on `unverifiable` rows where no correction was derived. |
| `evidence-quote` | string | Verbatim code the orchestrator verified against during adjudication — the real (post-diff) file, not just the diff hunk. On a `fail` row it MUST be non-empty. On `pass` / `unverifiable` rows it MAY be empty. |

No row field beyond these six. The skill adds NO top-level severity field — severity lives only in
`check-name`.

## Check-name vocabulary

Closed enum of the finding's severity-category, assigned by the surfacing critic lens and preserved
through the orchestrator's ground-truth adjudication:

- `lens-finding-blocking` — a finding the surfacing lens marked **blocking** severity that survived
  ground-truth adjudication.
- `lens-finding-should-fix` — as above, **should-fix** severity.
- `lens-finding-minor` — as above, **minor** severity. (Also the fixed default `check-name` for a
  dead/null-critic synthetic `unverifiable` row, which has no critic-assigned severity.)

## Status semantics

Load-bearing; MUST NOT collapse. Row polarity (fail = surviving real finding; pass = refuted noise;
unverifiable = un-adjudicated):

- **`fail`** — the finding **survived** the orchestrator's direct read of the actual code → a real
  issue the author must resolve. `evidence-quote` MUST be non-empty (`cited-value` = the diff span
  it targets; `actual-value` = the asserted correction).
- **`pass`** — the finding was **refuted** by the orchestrator's read of the actual code → critic
  noise; not published to the comment. `actual-value` holds the asserted-but-refuted correction;
  `cited-value` the diff span it targeted; `evidence-quote` MAY be empty.
- **`unverifiable`** — could not be adjudicated from the diff / the reachable code → escalation
  surface, surfaced to the user, never to the PR comment. Not a pass; not a fail. `evidence-quote`
  MAY be empty.

## Verdict computation

Aggregate `verdict` over `rows` (applied verbatim):

- `fail` iff at least one row is `fail`. **Dominates** `unverifiable`.
- else `unverifiable` iff no `fail` row exists AND at least one row is `unverifiable`.
- else `pass` (zero `fail` rows AND zero `unverifiable` rows).

Empty `rows` → `verdict: pass` only when the skill ran successfully and every lens holds up.
`verdict: fail` is not a flat "don't post" — severity is per-row (`check-name`), which the verdict
does not read; you decide comment content by reading per-row severities directly (only surviving
`fail` rows render into the comment).

## Refusal record

The distinct abort shape, emitted when the skill refuses an invocation that violates its §Refusal
surface. A message is an envelope (has `rows`) XOR a refusal record (has `refusal`) — both-present
or neither is malformed.

```json
{
  "version": "1.0",
  "skill": "ra-pr-review",
  "invoked_at": "<ISO-8601 UTC, second precision>",
  "refusal": {
    "category": "bias | bloat",
    "rule": "<the Violation cell, verbatim, of the SKILL.md §Refusal surface table row the invocation violated>",
    "evidence": "<the offending input slice — flag + value; ≤500 chars, `…`-truncated>"
  }
}
```

| Field | Type | Notes |
|-------|------|-------|
| `version` | string | MUST equal `"1.0"`. |
| `skill` | string | Always `"ra-pr-review"`. |
| `invoked_at` | string | ISO-8601 UTC timestamp, second precision. |
| `refusal.category` | string | Enum `bias` \| `bloat`. |
| `refusal.rule` | string | The violated row's Violation cell from the SKILL.md §Refusal surface table, character for character (backticks and `≠` included), so the caller can locate and fix the invocation. |
| `refusal.evidence` | string | The offending input slice; ≤500 chars, `…`-truncated. |

Optional: `notes` (free-text, suppressed when empty); `multi` (array of additional
`{category, rule, evidence}` when more than one rule was violated).
