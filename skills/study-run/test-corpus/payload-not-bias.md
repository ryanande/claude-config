# Fixture: the finding batch handed to a labeler is payload, not a bias surface

## Study document under execution

`content/evals/eval-0031-precision-of-cold-run-labeling.md`, tamper guard
already passed (one committing commit, clean working tree). The frozen
`pre-registration:` block:

```yaml
pre-registration:
  design: D1
  metric: precision
  sample: 120 findings, 30 pull requests, single author
  stopping-rule: fixed N = 120
  resolution: separates mostly-real from mostly-noise; not 60% from 70%
  negative-result: precision <= 0.5 over the full 120-item denominator
```

Before `study-run` fires, the caller separately runs
`/invocation-discipline-lint --spec ~/.claude/skills/study-run/SKILL.md --call
"/study-run --study content/evals/eval-0031-...md" --mode enforce` — an
external lint invocation, not a `study-run` flag. The candidate invocation the
lint inspects is `study-run`'s own spawn call to each labeler, which hands that
labeler exactly one of the 120 findings from the `sample:` field — a
pre-filtered set, by construction, since it is one item out of the 120 the
design fixed.

## Expected skill output

`/invocation-discipline-lint` in `enforce` mode does NOT refuse this call,
because `study-run`'s `## Invocation discipline` section in `SKILL.md` states
the payload carve-out explicitly — the parsable place the lint reads before
ever reaching this call's payload. The 120-item sample is the payload the
pre-registration block fixed before the run started — the data under
measurement — not the kind of surface the lint's "pre-filtered focus" rule
targets. That rule targets a caller narrowing which findings a critic even
sees in order to steer the outcome; here the set was frozen by `/study-design`
before any run existed to steer.

What the lint DOES still refuse in the same call, because these are the actual
bias surfaces:
- an `--expected-label real` flag on any one labeler spawn;
- a `--hint "items 40-60 are the planted noise"` argument;
- a caller-supplied verdict passed alongside the spawn ("this one's precision
  looks low, mark it noise");
- a caller interpretation of any individual item's finding text.

Token for this distinction:
`payload-distinct-from-bias-surface`

The same carve-out covers three more surfaces `study-run`'s own spawns touch,
none of which the lint treats as caller-added bias either:
- the evidence pack `{{PACK}}` handed to each labeler — derived by
  `adjudication-mechanics.md`'s citation-neighbourhood rule from the pinned
  trees, not chosen by the caller;
- the screen's provisional REAL label — held in the ledger only, per
  `references/adjudication-mechanics.md` §"The screen's label never reaches
  a spawn", and never shown to any labeler or the re-deriver;
- the cited list `{{CITED}}` handed to the re-deriver — the labelers' cited
  file paths, non-exhaustive and with their conclusions withheld, per
  `references/rederive-brief.md`.

## Invariants exercised

- Adjudication proceeds unmodified: each of the 120 labelers receives its one
  finding with no expected-label slot, per
  `references/adjudication-mechanics.md`.
- The lint's refusal surfaces are limited to caller-added surfaces layered on
  top of the payload — never the payload itself, which was fixed by the frozen
  block, not the caller, at design time.
- Had the lint refused the payload itself, `enforce` mode would refuse every
  `study-run` invocation on its own sample, which is the exact reference note
  this fixture exists to keep true.
