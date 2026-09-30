# claude-config

Personal Claude Code configuration for the Chief Architect role at PrePass: prompts, configs, and scheduled routines that produce daily intelligence digests.

## Purpose

Three weekday-morning routines that filter org signal through an architect's lens and write a digest you can read in ~5 minutes:

| Routine | Window | What it scans | Output |
|---|---|---|---|
| PR Intelligence | 24h (72h Mon) | GitHub PRs across watched repos | `digests/pr-intelligence/YYYY-MM-DD.md` |
| Meeting Rundown | prior business day | Microsoft Teams meeting transcripts/recordings | `digests/meeting-rundown/YYYY-MM-DD.md` |
| Chat Surveillance | 24h (72h Mon) | Microsoft Teams channels and group chats | `digests/chat-surveillance/YYYY-MM-DD.md` |

Each routine is the same shape: **prompt** (the lens) + **config** (scope/exclusions) + **runner** (composes them and writes a digest).

## Layout

```
claude-config/
├── README.md
├── architectural-lens.md            # The one-pager every routine references
├── routines/
│   ├── pr-intelligence/             # prompt.md, config.yaml, runner.sh
│   ├── meeting-rundown/
│   └── chat-surveillance/
├── .github/workflows/               # Scheduled cron — stubs for now
└── digests/                         # Archive of daily outputs (committed)
```

## Skills

User-invocable skills under [`skills/`](skills/), deployed by symlinking each into `~/.claude/skills/<name>`.

| Skill | What it does |
|---|---|
| `execution-audit` | Inventory in-flight work across memory, Jira, GitHub, worktrees |
| `retro` | End-of-chunk retrospective + inbox disposition |
| `session-rundown` | Roundup of open Claude Code sessions |
| `iac-gap-analysis` | Hard, critical gap analysis of a Terraform IaC repo against the PrePass Platform Future-State Guide (Four Planes + Rules of the Road, from `arch-platform`) + the Architecture Guiding Principles (live, arch space) + Azure WAF + CIS — stack-ranked good/bad, a seven-dimension gap matrix, optional live-state drift verification, and a critical-path roadmap. Publishes branded under the arch space Research section (page 420872209). |
| `survey-author` | Scaffold an external-evidence survey doc (literature review / landscape scan) with source-tier classification and anti-recommendation discipline. **Adopted from [Wyatt Rupp's claude-config](https://github.com/Wyatt-Rupp_prepass/claude-config)** (2026-06-09); refusal-record REUSE restored 2026-07-14 now that `citation-detail-verify` is a real sibling. Pairs with [`research_docs`](https://github.com/Ryan-Anderson_prepass/research_docs) as `--target-repo`. |
| `citation-detail-verify` | Verify Stage 1 — mechanical citation-integrity gate (URL liveness, title/author/year, quote presence, anchors). Owns the shared WebFetch cache + envelope/verdict/refusal-record locks the rest of the suite reuses. **Adopted from Wyatt Rupp's claude-config** (2026-07-14), verbatim. |
| `source-recency-probe` | Verify Stage 0 — probes a draft for evidence the author should have cited but missed due to training-cutoff bias (new post-cutoff candidates, absent venues, superseded cites). Runs before `citation-detail-verify`. **Adopted from Wyatt Rupp's claude-config** (2026-07-14), verbatim. |
| `load-bearing-fullread` | Verify Stage 2 — fetches each cited source's full text and probes for abstract-survived framing drift (relative-vs-absolute, domain-transfer, flow-direction, scope-mismatch). **Adopted from Wyatt Rupp's claude-config** (2026-07-14), verbatim. |
| `adversarial-frame` | Verify Stage 3 (last) — generates alternative interpretations/weightings/compositions over an already-verified evidence base. **Adopted from Wyatt Rupp's claude-config** (2026-07-14), verbatim. |
| `survey-refresh` | Refreshes an existing survey's `sources[]` in place (URL-removed/stale probes) via a sidecar report; never mutates the survey body. **Adopted from Wyatt Rupp's claude-config** (2026-07-14), verbatim. |
| `invocation-discipline-lint` | Mechanically lints a candidate invocation call signature against a spec's declared "Invocation discipline" section (enforce or advisory mode). Fire-time enforcement layer for the whole suite's refusal discipline. **Adopted from Wyatt Rupp's claude-config** (2026-07-14), verbatim. |
| `oq-resolver` | Orchestrator — composes `survey-author` + the full verify chain to advance one `content/open-questions/` entry toward an RFC-ready disposition, opening a `research_docs` PR for human ratification (never auto-merges). **Adopted from Wyatt Rupp's claude-config** (2026-07-14); repo resolution adapted from `DX_ARCH_META_ROOT` to `dxroot research_docs` (this workspace's sibling-repo resolver) — the only non-verbatim port in the suite. |

## How it relates to the wider PrePass tooling

- **[arch-rover](https://github.com/PrePass/arch-rover)** — runs org-wide architectural reports on a schedule and commits Markdown back. This repo borrows its runner pattern (registry → script → report PR). arch-rover is **org signal**; claude-config is **personal lens**.
- **[dx-aicentral](https://github.com/PrePass/dx-aicentral)** — distributes shared skills (`/dev`, `/doc`, `/test`) via APM. If a routine here stabilizes and other architects/leads want it, the prompt graduates to a skill in dx-aicentral; personal config stays here.
- **[dx-prepass-meta](https://github.com/PrePass/dx-prepass-meta)** — the workspace root. Local runners use `bin/dxroot` to resolve sibling repos when needed.

## Running

Fill out [architectural-lens.md](architectural-lens.md) first — without it the digests will be generic.

### Primary path — slash commands inside Claude Code

Each routine is a Claude Code slash command in [.claude/commands/](.claude/commands/). Same auth and MCP servers as your interactive session — no separate API key needed.

```
cd ~/projects/pp/dx-prepass-meta/repos/claude-config
claude
> /pr-intelligence              # today's digest
> /pr-intelligence 2026-05-05   # backfill
> /meeting-rundown
> /chat-surveillance
```

The slash command reads the lens + config + prompt at runtime, generates the digest, writes to `digests/<routine>/YYYY-MM-DD.md`, and commits + pushes for you.

To make slash commands available from anywhere (not just inside this repo), symlink them into user scope:

```
ln -s ~/projects/pp/dx-prepass-meta/repos/claude-config/.claude/commands/pr-intelligence.md ~/.claude/commands/pr-intelligence.md
# (repeat for the other two)
```

### Scheduled path — cloud routines

Once a GitHub MCP connector is configured at [claude.ai/customize/connectors](https://claude.ai/customize/connectors), the routines can run as scheduled remote agents in Anthropic's cloud (weekday mornings MST). See [`docs/cloud-routines.md`](docs/cloud-routines.md) (when present) or run `/schedule list` from inside Claude Code.

### Headless / CI path — bash runners

[routines/*/runner.sh](routines/) compose the same prompt and pipe to `claude --print`. Useful in cron / CI when you have a working `ANTHROPIC_API_KEY` and need a non-interactive run. Not the primary path.

[`.github/workflows/`](.github/workflows/) contains stubs that schedule the runners — currently in dry-run mode pending CI auth setup. See TODO blocks in each workflow.

## What goes where

| Piece | Lives where | Why |
|---|---|---|
| Architectural lens (personal) | this repo | Personal opinion, evolves often |
| Repo / channel / meeting scope | this repo (`config.yaml`) | Personal scope |
| Daily digest archive | this repo (`digests/`) | Searchable history, trend over weeks |
| Generic prompt template (if reused) | promote to dx-aicentral skill | Sharing via APM |
| Org-wide architectural signals | arch-rover | Already there; don't duplicate |
