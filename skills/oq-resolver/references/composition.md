# OQ-resolver — composition reference

Load at Step 4–6. The exact worktree recipe, research-skill invocations,
verdict handling, and envelope routing. The research-skill contracts referenced
here live in `~/.claude/skills/<name>/SKILL.md` + their shared locks under
`~/.claude/skills/citation-detail-verify/references/`.

## Worktree (Step 4)

`research_docs` is a submodule of `dx-prepass-meta` (this workspace's
umbrella; upstream says `research-docs` under `dx-arch-meta`). A naive worktree of a submodule
inherits `core.worktree` from the shared gitdir and shows every tracked file as
deleted — committing would commit mass deletions. Recipe:

```bash
RD="$(dxroot research_docs)"
WT="$RD/.claude/worktrees/oq-$ID"          # gitignored, external to the canonical tree
git -C "$RD" fetch origin main
git -C "$RD" worktree add "$WT" -b "auto/oq-$ID" origin/main
# heal the submodule core.worktree (idempotent) BEFORE any add/commit
git -C "$WT" config extensions.worktreeConfig true
git -C "$WT" config --worktree core.worktree "$WT"
# ASSERT identity before the first write
TOP="$(git -C "$WT" rev-parse --show-toplevel)"
[ "$(cd "$TOP" && pwd -P)" = "$(cd "$WT" && pwd -P)" ] \
  && [ "$(git -C "$WT" branch --show-current)" = "auto/oq-$ID" ] \
  || { echo "abort: worktree identity unresolved"; exit 1; }
```

Remove on EVERY exit path: `git -C "$RD" worktree remove --force "$WT"`.

## Discovery (Step 5)

Frame each `unblock-by` item as a neutral, falsifiable research question of the
shape "what does external evidence/precedent say works cleanest for
`<problem-shape>` in `<system-class>`?". The OQ's locus can be internal; the
decision is still informed by external precedent (e.g. warn-fatigue → alert-fatigue
literature; lint-vs-wrapper → static-analysis vs API-design precedent;
submodule-vs-workspace → monorepo-tooling docs).

**Fix the draft path first.** Decide the disposition artifact's repo-relative
path (e.g. `content/notes/oq-<id>-<slug>-findings.md`) before the first
search; every candidate record below anchors to it, and Step 6 writes the
draft there.

**Discovery engine — your own `WebSearch` + `WebFetch`:** run the framed
questions through `WebSearch`. For each hit you decide to fetch, FIRST record it
as proposed — this is the unfetched-stratum denominator EVAL-0002 samples:

```bash
python3 ~/.claude/skills/citation-detail-verify/scripts/candidates.py append \
  --repo "$WT" --artifact <draft-path> --stage gather \
  --title "<title as shown by the search result>" --url "<url>" --source-in-context false
```

then `WebFetch` the hit to confirm its exact title + a verbatim quote and
extract a source entry (title, URL, and where present authors/year/venue) into
the draft `sources[]`. A hit the fetch rejects (no such page, title does not
match, quote absent) gets
`candidates.py append-disposition --repo "$WT" --artifact <draft-path> --url "<url>" --disposition dropped-at-reread --stage oq-resolver --label Major|Minor`
(`Major` when nothing resolves, `Minor` when the source exists but a detail
was wrong). Sentences drafted at Step 6 are written after the fetch, so no
sentence-bearing unfetched row comes from this skill; that population is
`survey-author`'s gather / gap-find fold-in. Contract:
`~/.claude/skills/citation-detail-verify/references/candidates-contract.md` v1.0. Prefer
primary/authoritative documentation (official tool docs, language/linker specs,
RFCs, changelogs) over secondary commentary. Respect arXiv rate limits —
sequential fetches, no parallel arXiv fan-out. Do NOT reach for a multi-agent
research / fan-out harness: it is heavyweight, requires explicit user opt-in per
the Workflow-tool contract, and `WebSearch`/`WebFetch` give tighter control over
the exact citations the Step-6 verifier chain must check.

**Optional companion landscape doc — `survey-author`:**

```
/survey-author --question "<neutral falsifiable claim>" --tags <topic-tags> --target-repo "$WT"
```

`--target-repo` is REQUIRED. `--question` must be neutral (survey-author REFUSES
a caller conclusion / expected verdict). survey-author only SCAFFOLDS (its
`sources:` table is empty unless `--seed-urls` is supplied) — YOU populate
`sources[]` from discovery. The survey is descriptive; it carries NO
recommendation (corpus invariant) — the disposition rationale never lands in it.

## Verify the DRAFT (Step 6) — the chain runs on the decision artifact

The verifiers consume a *decision artifact with a `sources[]` list* (RFC / ADR /
design / findings), NOT a survey. Draft the disposition artifact first, then:

```
/source-recency-probe   --artifact <draft> --authored-against <model>,<cutoff>
/citation-detail-verify --artifact <draft>
/load-bearing-fullread  --artifact <draft> --source-ids <arXiv-venue-subset>
/adversarial-frame      --artifact <draft>
```

- `--authored-against` — the running model id + a pinned cutoff date (e.g.
  `claude-opus-4-8,2026-01`). Required by source-recency-probe.
- `--source-ids` — required by load-bearing-fullread. Its deep framing probe
  resolves arXiv IDs ONLY (derives `https://arxiv.org/html/<id>v1`); a non-arXiv
  id yields an `unverifiable` row. So pass ONLY the ids whose source `venue` is
  `arxiv`. `citation-detail-verify` (URL-liveness/title/year) and
  `source-recency-probe` work on ANY external source — they are not arXiv-limited.
- `adversarial-frame` runs LAST, on the draft (it challenges the decision's
  cited claims). The draft MUST engage each surfaced alternative before the PR.

### Verdicts (3-state — do not collapse)

Each skill emits an envelope with per-row `status: pass | fail | unverifiable`
and an aggregate `verdict` (any `fail` → `fail`; else any `unverifiable` →
`unverifiable`; else `pass`). `unverifiable` is "not a pass, not a fail" — an
escalation surface.

- any uncleared `fail` → ABORT `abort_class: evidence-unverified` (open no PR).
- `unverifiable`-dominant (no clearing `pass` rows — fetches failed, or all
  sources non-arXiv-and-unreachable) → routes to **measure**; reaches **park**
  only when `study-design` returns an infeasibility rationale. Do NOT promote on
  unverified evidence.
- `pass` → promote permitted.

### Envelope routing

Route by `skill:`/shape — the verifier skills emit 6-field rows
`(citation-id, check-name, status, cited-value, actual-value, evidence-quote)`;
`survey-author` emits 3-field rows `(criterion-id, status, evidence-quote)`; a
`{refusal}` record is a distinct top-level shape (`refusal` present, no `rows`).
A `{refusal}` → ABORT `abort_class: invocation-refused`. (A cache session-id
problem surfaces as a `notes` marker INSIDE a normal envelope, not a refusal —
Step 0 prevents it.) Reason only over `status`/`verdict`, never raw fetched
bodies.
