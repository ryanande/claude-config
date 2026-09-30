# study-design — the D1 sample pre-scan

Loaded at Workflow Step 4a (D1 only), before the Step 5 infeasibility
judgment. The pre-scan is mechanical. Its enumerator is author-written per
study — the census rule *is* the study's question — committed under
`assets/evals/<id>/enumerate.py` and sha256-pinned in `protocol.enumerator`.
Its extractor is fixed skill code: `~/.claude/skills/study-design/scripts/prescan_extractor.py`.

## What the report carries

| Field | Source | Direction stated |
|---|---|---|
| population | the slice the OQ record names (a corpus section, a status class, or both), resolved from the frozen OQ record | — |
| census N | enumerator output at the pinned commit | padding with expected-NOISE items lowers precision and raises the cap |
| flagged per parameter value | enumerator, one column per evaluable value the OQ record names | — |
| stratum count | `frozen-by-construction` rows | informational only |
| cap | ⌈0.10 N⌉ + ⌈0.05 N⌉, at N and at N minus the stratum count | — |
| identity report | extractor: owners, identities, unresolved with disposition, excluded mentions | omission narrows reach and consumes cap |
| screen-decidable fraction per type | `screen.py` over the census at the pinned SHA | REAL-favouring, bounded by fixed code |
| spawn budget | expected = screened × 1 + unscreened × 2 + escalation allowance (= screened count, each may escalate to two) + tiebreak allowance ⌈0.10 N⌉ (a plan convention; the design names the allowance without a value) + one re-derivation per expected resolved item (N minus the tiebreak allowance); worst = N × 4 | not a stopping rule |

## Running the extractor

```bash
S=~/.claude/skills/study-design/scripts
OWNERS=$(python3 $S/prescan_extractor.py derive-owners --bodies <bodies.json> --publication-url <research-docs URL> | python3 -c 'import json,sys; print(",".join(json.load(sys.stdin)))')
python3 $S/prescan_extractor.py repo-map --owners "$OWNERS" --out assets/evals/<id>/repo-map.json
python3 $S/prescan_extractor.py extract --bodies <bodies.json> \
  --repo-map assets/evals/<id>/repo-map.json \
  --publication-url <research-docs URL> --harness-url <claude-config URL> \
  --out assets/evals/<id>/prescan-identities.json
```

Three stages, all code: derive owners, fetch the map for exactly those owners, extract. `extract` refuses (`MissingOwnerMap`) when any owner lacks a map entry, so an owner can never be dropped by hand. `<bodies.json>` is `[{item_id, path, type, body}]` with frontmatter stripped,
each body read via `git show <sample-sha>:<path>`. The repo map is every
repository the authenticated `gh` identity can see under each owner (`gh repo
list`, never the public-only `gh api users/<o>/repos`); record `gh_login` and
per-owner counts in the block's provenance and re-fetch at emission to confirm
the sha256 still matches.

## Identity forms and dispositions (behaviour, pinned by tests)

Fixed in `test_prescan_extractor.py`. Summary for the reader:

- self-contained: a `https://github.com/<owner>/<name>` URL, or an
  `<owner>/<name>` pair whose owner is in `repo-owners`;
- bare name: a map name appearing case-exactly as a whole token (not joined by
  `-`, `_` or `/` to a longer token — `exocortex-data` never yields `exocortex`),
  and either hyphenated/underscored itself or wrapped in backticks; a plain word
  in prose (`ADRs`, `exocortex`) is not a mention;
- `~/.claude` → the block's `role: harness-runtime` entry;
- `@owner/team` → excluded (`team-mention`), logged with item ids;
- dispositions for the unresolvable: `not-a-repository` (non-GitHub URL),
  `owner-unknown` (`~/.claude` with no harness URL), `ambiguous-name` (bare
  name under two owners), `pair-unresolved` (owner known, name not in its
  map). None enters C — none has a URL an `ls-remote` could lift.

Rejected forms: a bare name consulting the author's disk (`repos/*`); any
per-item decision.

## Measured on EVAL-0003 (2026-09-07, 283 map names)

Self-contained and bare-name forms together yield **35 of 53** bodies (the
design's pre-implementation hand count was 37; the tested extractor gives
35 — two bodies whose only mention was a path-adjacent near-miss such as
`dx-arch-meta/repos/…`). Fifteen identities; fourteen scope entries plus
`harness-runtime`. `dx-knowledge-mirror` is `ambiguous-name` (under both
`Wyatt-Rupp_prepass` and `PrePass`). `research-skills` appears in no body
(item-37's labeler rationale only). Unrestricted bare matching would give 43
with an `ADRs` collision; the earlier seven-name hand list gave 41. `gh repo
list` counts are 18 (`Wyatt-Rupp_prepass`) and 265 (`PrePass`), 283 names.
These are the golden fixture in `scripts/fixtures/eval-0003-expected.json`.

## The infeasibility test (Step 5 reads this)

C = census items whose body names a repository in `evidence-scope-excluded`
(reason `remote-inaccessible`). If C > cap, emit an infeasibility rationale
recording C, the cap, the mention-vs-unreachability rate, and per remote the
`git ls-remote` failure output plus the last reachability the design-time
checkout's refs show (state "no fetch history" when empty). Re-attempt
`ls-remote` immediately before emitting; refuse a STOP whose exclusions no
longer hold. On EVAL-0003 at the derived-maximal scope every identity answers
`ls-remote`: C = 0.
