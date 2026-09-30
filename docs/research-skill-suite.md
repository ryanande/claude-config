# The research-skill suite — usage & composition (this config's subset)

Trimmed from [Wyatt Rupp's `research-skill-suite.md`](https://github.com/Wyatt-Rupp_prepass/research-skills/blob/main/docs/research-skill-suite.md) to cover only what's vendored here. See that doc for the full suite, including `criteria-validate` (a different, unrelated dx-aicentral tool of the same name already exists in this environment — see the [port design doc](superpowers/specs/2026-07-14-research-skill-suite-port-design.md) for why it wasn't ported).

Upstream is now [`Wyatt-Rupp_prepass/research-skills`](https://github.com/Wyatt-Rupp_prepass/research-skills), not his `claude-config`. Which SHA this config last synced from, and every local divergence that must survive a sync: [`research-skills-upstream.md`](research-skills-upstream.md).

## The suite at a glance

| Skill | Role | Invoke | In → Out |
|---|---|---|---|
| [`survey-author`](../skills/survey-author/SKILL.md) | Authoring | `/survey-author --question <claim> --tags <tags> --target-repo <path>` | topic → **authored** survey doc — scaffold plus the evidence walk that fills it, in one invocation (local divergence 1) |
| [`survey-refresh`](../skills/survey-refresh/SKILL.md) | Authoring | `/survey-refresh <survey-path>` | existing survey → refresh-report **sidecar** (body never mutated) |
| [`source-recency-probe`](../skills/source-recency-probe/SKILL.md) | Verify (1) | `/source-recency-probe --artifact <path> --authored-against MODEL,DATE` | draft → recency-gap rows, derived from the artifact's own `sources[]` via the OpenAlex citation graph (v2.0 — `tags:` are never read) |
| [`citation-detail-verify`](../skills/citation-detail-verify/SKILL.md) | Verify (2) | `/citation-detail-verify --artifact <path>` | draft → citation-integrity rows |
| [`load-bearing-fullread`](../skills/load-bearing-fullread/SKILL.md) | Verify (3) | `/load-bearing-fullread --artifact <path> --source-ids <ids>` | draft → framing-drift rows |
| [`adversarial-frame`](../skills/adversarial-frame/SKILL.md) | Verify (4) | `/adversarial-frame --artifact <path>` | draft → alternative-framing rows |
| [`invocation-discipline-lint`](../skills/invocation-discipline-lint/SKILL.md) | Enforcement (optional) | `/invocation-discipline-lint --spec <path> --call <signature>` | call signature → bias/bloat violation rows |
| [`oq-resolver`](../skills/oq-resolver/SKILL.md) | Orchestrator | `/oq-resolver [--oq <id>]` | one open question → `research_docs` PR proposing a disposition, verified by the whole chain |
| [`study-design`](../skills/study-design/SKILL.md) | Measurement (1) | `/study-design --oq <path>` | one open question → ONE pre-registered study doc (frozen design/metric/sample/stopping-rule), or an infeasibility rationale |
| [`study-run`](../skills/study-run/SKILL.md) | Measurement (2) | `/study-run --study <path>` | pre-registered study → results appended to that same doc, behind a tamper guard on the frozen block |

Four roles, same as Wyatt's original:

- **Authoring** (`survey-author`, `survey-refresh`) — build and maintain a descriptive *survey* of external evidence. Carries **no recommendation**.
- **Verification chain** (the four `verify` skills) — run in order over a *decision artifact* (has `sources[]` **and** draws a conclusion — not a survey).
- **Orchestration** (`oq-resolver`) — composes discovery → optional survey → draft disposition → the full verification chain → a PR for a human to ratify.
- **Measurement** (`study-design`, `study-run`) — for an open question whose `unblock-by` items need evidence nobody has published. Design and execution are separate skills so the pre-registered metric is frozen before any result exists; `study-run` refuses a document whose pre-registration block changed after its committing commit.

`invocation-discipline-lint` sits orthogonal to all three — an optional fire-time gate on any skill's call signature, not part of the linear pipeline.

## Entry points

### 1. Verify an artifact you already drafted

Run the four verify skills **in order**: `source-recency-probe` → `citation-detail-verify` → `load-bearing-fullread` → `adversarial-frame`. Stop at the first `fail`-aggregate. Treat `unverifiable`-dominant as park-not-promote.

### 2. Author a companion survey first

```
/survey-author --question "<neutral falsifiable claim>" --tags <topic-tags> --target-repo <path>
```

`--target-repo` should point at `research_docs`. Keep it current later with `/survey-refresh <survey-path>`.

### 3. Resolve an open question end-to-end (orchestrated)

```
/oq-resolver --oq 0001      # or omit --oq to auto-pick
```

Runs the whole loop against `research_docs`: worktree off main → frame the OQ's `unblock-by` items as neutral research questions → discover evidence → draft a `promote | drop | park` disposition → run the full verify chain → open a PR carrying the evidence summary, verifier verdicts, and a `## Human decision` section. **Never auto-merges.**

### 4. Measure an open question no published evidence covers

```
/study-design --oq <path-to-oq>     # proposes; runs nothing
/study-run --study <path-to-study>  # executes exactly what was pre-registered
```

Use this when an OQ's `unblock-by` items are questions about *our* system that the literature cannot answer — `/study-design` classifies each item on the evidence-strength ladder and picks from a fixed three-design catalog (retrospective adjudication, planted-defect corpus, prospective A/B). When no design's envelope can separate the outcomes the question cares about it emits an infeasibility rationale instead, which is the only legitimate input to a park.

## The verification chain — order and why

1. **`source-recency-probe` first** — can *add* sources; running it first means the source list is final before anything downstream fetches.
2. **`citation-detail-verify` second** — cheap, mechanical, fail-fast (URL liveness, title/year, quote, anchors).
3. **`load-bearing-fullread` third** — expensive full-text framing-drift probe. `--source-ids` required; its deep probe resolves **arXiv ids only**.
4. **`adversarial-frame` last** — generates alternative interpretations over the now-verified evidence base.

## Verdict model (3-state — do not collapse)

Every verify skill emits an envelope with per-row `status: pass | fail | unverifiable` and an aggregate `verdict`:

```
any row fail          → verdict fail
else any unverifiable → verdict unverifiable
else                  → verdict pass
```

`unverifiable` is an escalation surface, not a soft pass. Reason over `status`/`verdict`, never raw fetched bodies.

## Shared contracts

- **Envelope + 3-state verdict** — one output grammar for every verify skill.
- **Shared WebFetch cache**, owned by `citation-detail-verify` at `~/.claude/skills/citation-detail-verify/cache/<key>/`, reused unchanged by `load-bearing-fullread`, `adversarial-frame`, `source-recency-probe`, `survey-refresh`. Assumes user-scope symlink deploy (this config's dominant pattern) — matches.
- **Refusal discipline** — every skill refuses caller-supplied conclusions, pre-filtered focus, or attached full bodies.

## What's different from Wyatt's original doc

- `criteria-validate` isn't in this doc's table at all — it was never a real port target (see the port design doc).
- `oq-resolver`'s repo resolution uses `dxroot research_docs` instead of `$DX_ARCH_META_ROOT/repos/research-docs` — this workspace's naming.
- `study-design` and `study-run` were vendored later than the other eight (2026-09-08); the eight-skill framing in older notes predates them.
- Full detail on failure-mode coverage, the shared cache contract's byte layout, and the envelope/verdict JSON shapes: see each skill's own `SKILL.md` + `references/`, or Wyatt's original doc for the canonical writeup.
