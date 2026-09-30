# Fixture: a six-field (v1.0) block runs under recorded defaults, never refused for missing `protocol:`

## Study document under execution

`content/evals/per-candidate-citation-hallucination-rate.md` (EVAL-0002),
subject OQ-0062, `pre-registration:` block frozen at commit `b79539b` — six
fields (`design`, `metric`, `sample`, `stopping-rule`, `resolution`,
`negative-result`), no `protocol:` key. `b79539b`'s commit date predates
`MERGE_SHA` (`study-design/references/pre-registration.md` §Version
constant), so Workflow Step 4 detects the v1.0 path and runs it — a missing
`protocol:` block is not itself a refusal condition.

Because `evidence-scope` defaults to research-docs only, Step 1's
`evidence-scope` URL check has no seventh-field entry to compare the checkout
against; per Step 1's six-field branch, the checkout's `origin` is recorded
as the publication identity, disclosed and unverified, never a refusal.

## Expected skill output

The run proceeds — EVAL-0002 is unrun and sole live document for OQ-0062
(`liveness-full-history.md`) — and Step 8's `run-<date>.json` lists every
default applied, per `SKILL.md` Workflow Step 4:

```
defaults applied (v1.0 block, no protocol: key):
  labels-per-item: 2 (default)
  disagreement: any-disagreement -> UNRESOLVED (default)
  evidence-scope: research-docs only (default)
  publication-identity: <checkout origin>, disclosed, unverified
  screen: off (v1.0)
  evidence-pack: off (v1.0)
  spawn-budget: off (v1.0)
  strata: off (v1.0)
  gate: off (v1.0)
  recheck: rederive-only (re-derivation applies; symmetric, monotone toward UNRESOLVED)
  model-policy: fixed-slots (assignment default; runner never chooses)
```

Three changes to EVAL-0002's own adjudication compared to a document that
predates this design entirely: fixed slots (`opus`/`sonnet`/`haiku`/`fable`)
replace runner-chosen models; re-derivation on the `fable` slot replaces a
runner self-re-check (the mechanical gate does NOT run — EVAL-0002's items
are fetched-source citations, not tracked-tree paths a `quote` can be
gated against); and labelers emit `unresolved_reason` in their JSON verdict.
EVAL-0002's block carries no unresolved cap, so the effect is a precision
number computed the same way as before, disclosed with a before/after split
against what an ungated, non-re-derived run would have shown.

### Contrast — a six-field block frozen AFTER `MERGE_SHA`

`content/evals/eval-0088-late-six-field.md`, six fields (no `protocol:` key),
frozen at a commit whose commit date is AFTER `MERGE_SHA`. Step 4's version
detection is not "does `protocol:` exist" alone — it is "protocol: absent AND
freezing commit predates `MERGE_SHA`." A six-field block frozen after the
seventh field landed is not a legitimate v1.0 survivor; it is a block that
should have carried `protocol:` and does not. `study-run` refuses:

```
REFUSE: six-field block frozen after MERGE_SHA — protocol: required, not present
```

Token for this distinction: `v10-block-defaults-recorded`.

## Invariants exercised

- `protocol:` absence alone never refuses a run — only combined with a
  freezing commit that predates `MERGE_SHA` does the v1.0 path apply at all.
- Every default the v1.0 path substitutes is individually named in the run
  record, not summarized as "ran under legacy defaults" — a human auditing
  EVAL-0002's result can see exactly which seven values were assumed.
- The mechanical gate is `v1.1`-only and does not run for EVAL-0002 — its
  legs (path-at-SHA, verbatim quote) have no referent in a fetched-source
  substrate; re-derivation still applies, because it satisfies the "symmetric
  in application, monotone toward UNRESOLVED" test Step 4 states for which
  new behaviours may extend to an old block.
- A six-field block frozen after `MERGE_SHA` is refused, not silently run
  under v1.0 defaults — the version test is commit-date-relative-to-merge,
  not merely field-count.
