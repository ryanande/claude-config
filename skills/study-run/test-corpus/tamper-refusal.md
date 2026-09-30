# Fixture: pre-registration block edited after its committing commit

This fixture renames `study-design`'s `## Open question under design` header to
`## Study document under execution` — deliberately. `study-run`'s payload is not
an open question, it is a pre-registered study document already sitting in
`research-docs`. The other two headers (`## Expected skill output`,
`## Invariants exercised`) carry over unchanged from the sibling skill's
fixture shape.

## Study document under execution

`content/evals/eval-0031-precision-of-cold-run-labeling.md` in the
`research-docs` checkout, with a `pre-registration:` block introduced at
commit `a1b2c3d`:

```yaml
pre-registration:
  design: D1
  metric: precision
  sample: 120 findings, 30 pull requests, single author
  stopping-rule: fixed N = 120
  resolution: separates mostly-real from mostly-noise; not 60% from 70%
  negative-result: precision <= 0.5 over the full 120-item denominator
```

`git -C <research-docs-root> log -L '/^pre-registration:/,/^```$/:content/evals/eval-0031-precision-of-cold-run-labeling.md' --format='%H %s'`
returns TWO commits touching that line range: `a1b2c3d` (the original) and a
later `f9e8d7c` titled `"tune negative-result threshold after seeing partial
labels"` — the metric was not touched, but `negative-result` was loosened once
early labeling results were partially visible. That is metric-shopping by
another name: the threshold that decides the answer moved after the caller
had a look.

## Expected skill output

`study-run` refuses at Workflow Step 2, before collecting any sample:

```
REFUSE: pre-registration block in 2 commits (expected exactly 1)
```

Token for this refusal:
`refusal-preregistration-edited-after-commit`

No sample is collected, no labeler is spawned, and nothing is appended to the
study document. The refusal names the commit count found (2), not a generic
"tampering suspected" message, so a human reviewing the refusal can `git log`
the same range and see exactly what changed.

## Condition (d) — already-run document

`content/evals/eval-0044-a-different-study.md`, single committing commit,
clean working tree — (a)–(c) all pass, and the freezing commit is an ancestor
of `origin/main`, so (e) passes too. Per `SKILL.md` Step 2's order,
registration runs next (`started-<date>.json` pushed on
`study-run/eval-0044-2026-09-07`, listing this attempt), and only then is (d)
checked: `assets/evals/eval-0044/run-2026-09-06.json` is present and
complete, and the document body carries a `### Run` subsection under
`## Findings` with a computed precision. `study-run` refuses at (d):

```
REFUSE: already run — run-2026-09-06.json exists, results content present
```

Registration already happened before (d) was checked, so the
`study-run/eval-0044-2026-09-07` branch and its `started-<date>.json` are not
undone by this refusal — they stay on the remote as a disclosed, orphaned
attempt, and `started-<date>.json` records the already-run refusal as the
reason the attempt went no further. The completed run stands. A caller
wanting a second measurement must go back through `/study-design` for a new
document — amending a landed result is out of scope for this skill.

## Condition (e) — freezing commit not on `main`

`content/evals/eval-0055-unmerged-freeze.md` carries a `pre-registration:`
block committed exactly once, on branch `feature/eval-0055-draft`, which has
never merged to `main` at the publication URL. `recheck.is_ancestor` against
`origin/main` returns false. `study-run` refuses at Step 2 condition (e),
before registration and before (d) is even checked:

```
REFUSE: freezing commit <sha> is not an ancestor of origin/main
```

The document may be exactly as designed and never touched again — condition
(e) does not care whether it was edited, only whether the commit that froze
it ever reached the branch the run's publication identity trusts.

## Invariants exercised

- The tamper guard runs before Step 3 (refusing caller-supplied labels) and
  before Step 5 (sample collection) — tamper detection is unconditionally
  first.
- `N -eq 1` is the only passing state; `N == 2` here is the edited case, one of
  the two failure shapes the check must catch (the other is `N == 0`, never
  committed at all).
- This fixture exercises condition (c) of the five-condition guard — the
  commit-history check — plus (d) already-run and (e) freezing-commit-not-
  on-`main` in the sections above. It deliberately does NOT re-exercise (a)
  untracked or (b) uncommitted-working-tree, which are separate conditions
  `git log` structurally cannot see at all — they are specified with their
  exact commands in `SKILL.md` Workflow Step 2 rather than re-run here with a
  third worked example.
- Registration (`started-<date>.json` pushed on `study-run/<id>-<date>`)
  happens only after (a)–(c) and (e) pass, and (d) is checked after
  registration, not before — the (c) and (e) fixtures above refuse before
  ever registering; the (d) fixture registers first (its attempt is a matter
  of record) and only then refuses on the completed prior run.
