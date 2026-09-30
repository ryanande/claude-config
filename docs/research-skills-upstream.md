# Research-skill suite — upstream provenance and divergence ledger

The ten research skills under `skills/` are vendored from Wyatt Rupp's
[`research-skills`](https://github.com/Wyatt-Rupp_prepass/research-skills)
repository. They are hand-copied, not a submodule or subtree: upstream is a
private repo with its own openspec corpus, deploy manifest, and CI, and this
config carries only the `skills/` half plus local divergences.

This file exists so the next sync is a three-way diff rather than an
archaeological dig. Before the 2026-09-08 sync there was no provenance marker
at all, and reconstructing which local edits were deliberate took a full pass
over four commits and their diffs.

## Sync state

| Field | Value |
|---|---|
| Upstream | `Wyatt-Rupp_prepass/research-skills` (private) |
| Last synced from | `a2ad1f3` — `chore(openspec): archive pdf-text-extraction (#12) (#13)` |
| Synced on | 2026-09-17 |
| Vendored skills | all ten: `survey-author`, `survey-refresh`, `source-recency-probe`, `citation-detail-verify`, `load-bearing-fullread`, `adversarial-frame`, `oq-resolver`, `invocation-discipline-lint`, `study-design`, `study-run` |
| Not vendored | upstream's `openspec/`, `docs/`, `CLAUDE.md`, `CODEOWNERS`, `.claude-deploy.toml` |

Deployment here is by symlink — `~/.claude/skills/<name>` points into this
repo's `skills/<name>`, so an edit is live with no deploy step. A newly
vendored skill needs its symlink created once.

## How to sync

```bash
git clone https://github.com/Wyatt-Rupp_prepass/research-skills.git /tmp/research-skills
git -C /tmp/research-skills log --oneline <last-synced-sha>..HEAD
```

Then, per skill, `rsync -a --delete --exclude 'cache/' --exclude 'candidates/'
--exclude 'clones/' /tmp/research-skills/skills/<s>/ skills/<s>/` and re-apply
every divergence below that is still marked live. Update the table above and
this ledger in the same commit.

The three excludes are runtime state, not content: the shared WebFetch cache,
the per-session candidates spool, and `study-run`'s clone root. A delete-sync
without them destroys working state.

## Runtime dependency — `pdftotext` (poppler)

Upstream `a2ad1f3` (cache-contract v1.4) added PDF text extraction:
`skills/citation-detail-verify/scripts/pdf_extract.py` shells out to
`pdftotext`, and `load-bearing-fullread` routes extracted PDF bodies through
its `full-text-unsectioned` class. The tool is optional by design — absent, the
skills take the named degradation path (`pdf-tool-missing`) rather than
failing — but without it PDF-served sources stay unreadable, which is the
whole point of the upstream change.

Installed at the 2026-09-17 sync via `brew install poppler` (poppler 26.09.0).
Without it three of seven `test_pdf_extract.py` cases (`test_locate`,
`test_extract`, `test_cli`) fail — they exercise real extraction and have no
tool-missing branch. With it the suite is 7/7. A machine that has not run that
brew install gets the degradation path, not an error.

## Live divergences

Each is deliberate and must survive a sync. Anything not listed here should be
taken from upstream unchanged.

### 1. `survey-author` runs the evidence walk in the same invocation

Upstream scaffolds shape only and leaves content to a later human pass. Here
the invoking agent *is* the author, and scaffold-only shipped an empty template
four consecutive times. This copy adds §Evidence walk (workflow steps 7–9;
upstream's steps 7–8 renumber to 10–11), the step-10 `ran-evidence-walk`
post-condition, `WebSearch` to `allowed-tools`, and the §Success criteria
§Local addendum with its two DSL rows. `references/output-schema.md` is
bumped to v1.1 to widen `criterion-id` and register the mandatory row.
`test-corpus/placeholder-body.md` is the local fixture grounding it.

Files: `skills/survey-author/SKILL.md`,
`skills/survey-author/references/output-schema.md`,
`skills/survey-author/test-corpus/placeholder-body.md`.

Also local in that SKILL.md: the §Out of scope amendment striking
"auto-generating survey content", the §Invocation discipline bloat-1 rationale
(caller-supplied body text vs skill-initiated fetching), and the
§Cross-skill compatibility consumer list (seven siblings here, five upstream).

### 2. `citation-detail-verify` recognizes `(S<n>)` citations

Additive to upstream's `[Axx]` / `[Bxx]` research-docs convention. `(S<n>)` is
the style `survey-author`'s own scaffold produces in this environment, so
without it the verify chain silently sees zero inline citations on our own
surveys. Both patterns stay live.

Files: `skills/citation-detail-verify/SKILL.md` (header note plus the two
citation-set extraction surfaces).

### 3. `survey-author --tags` no longer claims to steer the probe

Upstream's `--tags` input description still says the tag set "feeds downstream
`/source-recency-probe` venue selection". That stopped being true at
`source-recency-probe` v2.0, which derives venues from `sources[]` and never
reads `tags:`. Corrected locally; worth pushing upstream rather than carrying.

Files: `skills/survey-author/SKILL.md` §Input.

### 4. `research-docs` resolution goes through `dxroot`, not `DX_ARCH_META_ROOT`

Upstream resolves its research-docs checkout as
`$DX_ARCH_META_ROOT/repos/research-docs`. That variable is unset in this
workspace; the equivalent repo is `research_docs`, a submodule of
`dx-prepass-meta`, resolved by `dx-prepass-meta/bin/dxroot`. So `oq-resolver`
passes `--repo "$(dxroot research_docs)"` to `oq_select.py` explicitly
rather than relying on the script's env default (the script itself is
unmodified), and `study-design` / `study-run` name `dxroot` as the first
resolution rung with upstream's variable as the fallback.

Also local in `oq-resolver`: upstream's Step 0 **deploy-freshness** guard is
replaced by a note that source == runtime here. That guard exists because
upstream's source and runtime became separate trees at the 2026-09
`research-skills` decomposition; here `~/.claude/skills/oq-resolver` is a
symlink into this repo, so there is no deployed copy to drift, and the guard
would abort on an unset `DX_ARCH_META_ROOT` every run.

`study-run`'s `references/evidence-scope.md` needs no patch: its rung-2 glob
already falls through to `$DX_META_ROOT/repos/*` (set in `.zshrc`) and matches
by `origin` URL, so `research_docs` resolves under its real name.

Files: `skills/oq-resolver/SKILL.md`,
`skills/oq-resolver/references/composition.md`,
`skills/study-design/SKILL.md`, `skills/study-run/SKILL.md`.

### 5. Stale repo name corrected; upstream framework pointers marked historical

Two corrections applied during the 2026-09-08 sync, both pre-existing bugs
rather than upstream drift:

- Every reference to `ryan_research_docs` was renamed to `research_docs`.
  `dxroot --check ryan_research_docs` exits 1 — the repo is
  `Ryan-Anderson_prepass/research_docs`, cloned at
  `dx-prepass-meta/repos/research_docs` (an untracked sibling, not a registered
  submodule, so it is absent from `.gitmodules` and resolved by `dxroot` only).
  The old name resolved nowhere, which would have aborted `oq-resolver` at
  Step 0 on every run.
- `study-design` and `study-run` cite
  `~/dx-arch-meta/repos/research-docs/content/design/skill-invocation-discipline.md`
  as their invocation-discipline framework. That path does not resolve here —
  `~/dx-arch-meta` exists but its `repos/research-docs` is an uninitialized
  checkout, and the doc is not mirrored into `research_docs`. Both files now
  say so inline. The rules themselves are restated in each skill's own
  §Invocation discipline section, so nothing is lost; retargeting would need
  the doc mirrored into `research_docs` first.

`study-design/scripts/fixtures/*` also name `dx-arch-meta` repos. Those are
golden test data for `prescan_extractor.py` and MUST NOT be retargeted — the
suite asserts against them.

## Retired divergences

### `source-recency-probe` topic-tag catalog (v1.4 → v1.9) — retired 2026-09-08

This config grew upstream's 11-row topic-tag → venue catalog to roughly 90 rows
across five additions, each triggered by the same failure: a survey declared
tags no row covered, so the probe resolved zero venues and returned
`unverifiable`. The rows and their failure-mode notes are recorded in commit
`7104ee9` and its ancestors.

Upstream v2.0 removed the mechanism instead of extending it — venue derivation
moved to an OpenAlex citation-graph walk over the artifact's own `sources[]`,
on the grounds that "add rows" never converged and that an author-declared tag
selecting which venues get searched is caller-supplied focus laundered through
config. That is the root-cause fix for the failure the catalog rows were
patching, so the catalog was retired rather than merged forward.

Consequence to watch: probe recall now depends on `sources[]` being populated
and resolvable. An artifact citing nothing gets one `nothing-to-probe` row, and
recall on venues the author cited nothing from is a deliberate upstream
non-goal. If that gap bites, the fix is an additive probe strategy, not a
return of the tag table.
