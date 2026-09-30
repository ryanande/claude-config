# Fixture: liveness reads the FULL `origin/main` history, not just the current tree

## Study document under execution

A new proposal for OQ-0002 is about to be scaffolded by `/study-design`, and
separately a caller invokes `/study-run` against it before checking liveness
manually. `recheck.py liveness --repo <research-docs-root>` walks
`git log main --diff-filter=A --name-only -- content/evals content/benchmarks`
— every path ever *added* under either directory, at any commit, not merely
what `ls` shows at HEAD today.

### The real corpus, as of this fixture

- **EVAL-0003** — `content/evals/staleness-threshold-calibration-pass.md`,
  subject OQ-0002, `pre-registration:` block frozen at commit `b090d27`. At
  HEAD: no `withdrawn:` frontmatter field; its `## Findings` section reads
  "Not yet run." (no `### Run` subsection). `live_studies` finds the wrapped
  subject line — the real body wraps it across a line break
  (`` …for\n[OQ-0002](… ``) — via `SUBJECT_RE`'s `\s+` between `for` and the
  bracket, matched against the fence-stripped text. **Live.**
- **EVAL-0002** — `content/evals/per-candidate-citation-hallucination-rate.md`,
  subject OQ-0062, six-field `pre-registration:` block frozen at `b79539b`
  (predates `MERGE_SHA`). At HEAD: no `withdrawn:` field, no `### Run`
  subsection. **Live.**
- **EVAL-0001** — subject OQ-0061, frozen and run at `f9ca43b`. At HEAD its
  `## Findings` section contains a `### Run` subsection with the computed
  precision and `verdict: deferred`. `live_studies`'s `RUN_HEAD` regex
  matches inside the `## Findings` body before the next `## ` heading, so
  `results = True`. **Not live** — a run result, once appended, retires a
  document from liveness regardless of its verdict.

### The reverted-away case

`content/evals/eval-0077-abandoned-draft.md`, subject OQ-0002, was added at
commit `c3d4e5f` with a frozen block, never run, then reverted out of the
tree entirely at a later commit (its `README` mention and file both removed).
`git log --diff-filter=A` still surfaces it as an *added* path in history;
`live_studies` detects `at_head = False` (`git cat-file -e main:<path>` fails)
and falls back to `git show <last-commit-touching-path>^:<path>` — the
content as it stood the commit before its removal. That snapshot carries no
`withdrawn:` field (reverting the file is not the same as marking it
withdrawn — the design deliberately does not treat a deletion as a
disposition) and no `### Run` subsection. `live_studies` reports it with
`"removed": true` and still counts it as **live**.

## Expected skill output

`/study-design` Step 1a and `/study-run` Step 3a both call
`recheck.py liveness --repo <research-docs-root>` and get back:

```json
[
  {"path": "content/evals/staleness-threshold-calibration-pass.md", "oq": "OQ-0002", "removed": false},
  {"path": "content/evals/per-candidate-citation-hallucination-rate.md", "oq": "OQ-0062", "removed": false},
  {"path": "content/evals/eval-0077-abandoned-draft.md", "oq": "OQ-0002", "removed": true}
]
```

EVAL-0001 is absent from this list — its `### Run` subsection retired it.
`/study-design`'s new OQ-0002 proposal refuses: two live entries already carry
OQ-0002 (EVAL-0003 at HEAD, and the reverted-but-unrun eval-0077 draft),
either of which alone is sufficient to block. `/study-run` refuses any
attempt to run a *third* OQ-0002 document at Step 3a for the same reason. A
new OQ-0062 proposal is likewise blocked by EVAL-0002; a new OQ-0061 proposal
is NOT blocked — EVAL-0001 already ran and carries results.

Token for this trajectory: `liveness-reads-full-history`.

## Invariants exercised

- Liveness is computed over `git log --diff-filter=A`'s full history, never
  `ls content/evals/`'s current directory listing — a file gone from the
  working tree can still be live.
- A document with a `### Run` subsection under `## Findings` is retired from
  liveness regardless of its verdict (`deferred`, in EVAL-0001's case) — a
  run, not a disposition, is what retires it.
- `withdrawn:` frontmatter and "has results" are two independent ways off the
  live list; neither substitutes for the other, and `eval-0077` demonstrates
  a document that is unrun, unwithdrawn, and reverted, which is still live.
- The wrapped-subject regex (`\s+` between `for` and the bracketed OQ link)
  matches EVAL-0003's real body, which line-wraps at that exact point — a
  strict single-space match would silently miss it.
