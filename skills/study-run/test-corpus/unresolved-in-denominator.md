# Fixture: unresolved items stay in the denominator, never silently dropped

## Study document under execution

`content/evals/eval-0031-precision-of-cold-run-labeling.md`, tamper guard
passed, `pre-registration:` block as in `payload-not-bias.md`: `metric:
precision`, `sample: 120 findings...` — this fixture uses a round 100-item
sub-sample of that population to keep the worked arithmetic legible; the same
rule applies at 120.

100 findings were adjudicated: two labelers per item (labeler A, labeler B),
cold-run and no cross-talk, except for the items `screen.py` provisionally
marked REAL, which draw one labeler per screened item per
`references/adjudication-mechanics.md` §"The screen's label never reaches a
spawn". Cap = ⌈0.10 × 100⌉ + ⌈0.05 × 100⌉ = 10 + 5 = 15, counting every
UNRESOLVED item regardless of its `unresolved_source`. Per Workflow Steps 7
and 7a, the runner performs no re-check itself: `recheck.py gate` gates every
returned label against the pinned trees, then one re-derivation spawn per
resolved item (the `fable` slot, `references/rederive-brief.md`) either
matches the gated label or forces UNRESOLVED. The runner adjudicates nothing;
every judgment traces to a spawn or to `recheck.py`:

- 60 labels gated clean and re-derivation matched — recorded **real**.
- 25 labels gated clean and re-derivation matched — recorded **noise**.
- 15 labels landed UNRESOLVED: some failed the gate (`gate-failure` — a quote
  that does not grep verbatim in the pinned tree), some passed the gate but
  the `fable` re-deriver returned a different label than the gated one
  (`rederivation-dissent`), and the rest split across
  `labeler-contradiction` / `failed-tiebreak` / `both-unresolved` per
  `recheck.unresolved_source`'s precedence order. Per Workflow Step 7a, each
  of these 15 is recorded `unresolved` with its source named, not silently
  dropped and not folded into either the real or noise count. 15 sits exactly
  at the cap (15 ≤ 15): the cap is met, not exceeded.

## Expected skill output

The precision `study-run` appends to the study document:

```
precision = 60/100 (0.60)
unresolved = 15 of 100, named individually: F-004, F-017, F-023, F-031, F-038,
  F-044, F-052, F-061, F-067, F-073, F-081, F-088, F-092, F-096, F-099
noise = 25/100
negative-result threshold (precision <= 0.5): NOT crossed (0.60 > 0.5)
```

The reported metric is `60/100`, the full denominator — NOT `60/85`, which
would silently exclude the 15 unresolved items from the denominator entirely
and report a precision 0.11 higher than what the full sample actually showed.
Excluding the unresolved 15 is exactly the failure mode this fixture exists to
rule out: it would inflate precision by treating "we couldn't tell" as if it
had never been sampled.

Token for this distinction:
`unresolved-counted-in-denominator`

## Invariants exercised

- 60 + 25 + 15 = 100. The three counts partition the full sample; none is
  dropped, none double-counted.
- The reported metric's denominator is 100 (the full sample), never 85 (the
  resolved-only subset) — `60/100`, not `60/85`.
- The 15 unresolved items are named individually in the appended result, not
  collapsed into a bare count — a human auditing the study can find exactly
  which items resisted re-derivation.
- The `negative-result` crossing check (`precision <= 0.5`) is evaluated
  against the same full-denominator metric (0.60), not against a
  resolved-only recomputation.
