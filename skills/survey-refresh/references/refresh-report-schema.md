---
title: Refresh-report schema for /survey-refresh
version: 1.0
status: locked
owners: [survey-refresh]
consumers: [survey-refresh]
---

# Refresh-report schema v1.0

Skill-scoped lock for `/survey-refresh`. Binds the row-population rules (check-name → row-field semantics), sidecar disposition rule, `last-refreshed:` verification rule, and SHA256-of-body-compare protocol. Sibling Stage 1 lock `../../citation-detail-verify/references/output-schema.md` frontmatter 2.0 (wire `"1.0"`) owns the envelope SHAPE; this skill-scoped lock owns the refresh-time SEMANTICS (which row gets emitted under which condition, where the sidecar lives, how the refresh-log table relates to `last-refreshed:`).

## Check-name → row-field mapping

Each row's `check-name` value is one of the four below. Field semantics follow the Stage 1 lock §Row shape; this section binds the per-check-name population rules.

### `detected-url-removed`

Fires when a URL in the survey's `sources[]` returns HTTP ≥4xx, dead link, or domain expired.

| Row field | Value |
|-----------|-------|
| `citation-id` | The `[Sxx]` source identifier from the survey's `sources[]`. |
| `check-name` | `detected-url-removed` |
| `status` | `fail` when HTTP ≥4xx with confirmed-dead semantics. `unverifiable` when network error / timeout prevented classification. |
| `cited-value` | `"live"` (the survey's implicit pre-refresh assertion). |
| `actual-value` | The HTTP status code as a string (e.g., `"404"`) or `"network-error"` / `"timeout"`. |
| `evidence-quote` | First 200 chars of the response body (truncated with `…`). Empty string on network-error / timeout per Stage 1 lock §Required row fields rule. |

### `detected-url-added`

Fires once per invocation: one advisory row per invocation. Informational row; no in-survey defect. Surface-only — the skill does NOT invoke `/source-recency-probe` directly (Decision 7).

| Row field | Value |
|-----------|-------|
| `citation-id` | `advisory:source-recency-probe` (fixed value; not per-candidate). |
| `check-name` | `detected-url-added` |
| `status` | `pass` (informational; no in-survey defect to remediate). |
| `cited-value` | Empty string `""` per Stage 1 lock §Required row fields (no prior cited value exists). |
| `actual-value` | `"run /source-recency-probe to surface post-cutoff candidates from the citation graph of sources[]"` |
| `evidence-quote` | Verbatim: `Run /source-recency-probe --artifact <survey-path> --authored-against <model>,<cutoff-date> to surface post-cutoff candidates from the citation graph of sources[].` |

### `detected-citation-stale`

Fires when a URL returns HTTP 200 AND a prior-session cache entry exists AND the SHA256 of the normalized body differs between prior-session and current.

| Row field | Value |
|-----------|-------|
| `citation-id` | The `[Sxx]` source identifier. |
| `check-name` | `detected-citation-stale` |
| `status` | `fail` when SHAs differ. `unverifiable` when HTTP 200 returned but body could not be normalized (non-UTF-8, binary content) OR when the response was reachable-but-unparseable (paywall HTML, non-HTML PDF mirror) and SHA-compare is meaningless. |
| `cited-value` | SHA256 hex (lowercase, 64 chars) of the normalized prior-session cached body. |
| `actual-value` | SHA256 hex of the normalized freshly-fetched body. |
| `evidence-quote` | First 200 chars of the freshly-fetched body showing the divergence (truncated with `…`). |

### `detected-last-refreshed-bumped`

Fires once per invocation against the survey's `## Refresh log` table.

| Row field | Value |
|-----------|-------|
| `citation-id` | The literal string `last-refreshed`. |
| `check-name` | `detected-last-refreshed-bumped` |
| `status` | `pass` when the table's most-recent row date ≥ frontmatter `last-refreshed:`. `fail` when mismatch. `unverifiable` when the `## Refresh log` table is missing entirely. |
| `cited-value` | The frontmatter `last-refreshed:` value (ISO 8601 date). |
| `actual-value` | The most-recent `## Refresh log` table row's date. Empty string on `unverifiable`. |
| `evidence-quote` | The most-recent refresh-log row's text. Empty string on `unverifiable`. |

## Sidecar disposition rule

The refresh-report is written to a sidecar file at `<survey-dir>/refresh-report-<YYYY-MM-DD>.md` where:

- `<survey-dir>` is the directory containing the input survey doc.
- `<YYYY-MM-DD>` is the invocation date in ISO 8601 (UTC).

The sidecar contains:

1. The output-schema-shaped envelope as JSON inside a fenced code block (\`\`\`json).
2. A markdown summary table with one row per envelope row (`citation-id`, `check-name`, `status`, brief evidence).
3. A footer line instructing the author to add a one-line entry to the survey's `## Refresh log` table pointing at the sidecar filename + ISO date.

The skill MUST NOT mutate the input survey doc — neither its frontmatter (no auto-bump of `last-refreshed:`) nor its body (no append to `## Refresh log` table). The author drives the body edits as the canonical authored refresh event. Brief invariant `absent rewrote-survey-body` enforces this corpus-wide.

## `last-refreshed:` verification rule

The `detected-last-refreshed-bumped` row's `status` is computed against two checks:

1. The survey body MUST contain a `## Refresh log` section with a markdown table.
2. The table's most-recent row's date (column 1 of the last data row) MUST be ≥ the frontmatter `last-refreshed:` value.

`pass` iff both checks hold. `fail` iff (1) holds but (2) fails (the bump is unevidenced). `unverifiable` iff (1) fails (no `## Refresh log` table — the skill cannot judge bump consistency).

## SHA256-of-body-compare protocol

For `detected-citation-stale` detection (Decision 8):

1. BEFORE re-fetching, check `~/.claude/skills/citation-detail-verify/cache/<key>/meta.json` for a `session_id` differing from the current. If present, snapshot the existing `<key>/body` bytes into memory (or to a temp path under `~/.claude/skills/survey-refresh/cache-snap/`). Per cache-contract §Atomicity, the next fetch will overwrite `body` + `meta.json` atomically — the snapshot is the only way to preserve the prior-session body across the re-fetch. (See §Limitations §1 below for the multi-session caveat.)
2. Fetch the URL via the shared cache per `../../citation-detail-verify/references/cache-contract.md` Read protocol. The fetch warms `body` + `meta.json` with the current `session_id`.
3. If a prior-session body snapshot was captured in step 1, compute SHA256 of the normalized body for both snapshot and current. Normalization steps, in order:
   - Decode bytes as UTF-8 with error replacement.
   - Lowercase the entire string.
   - Strip ASCII whitespace (spaces, tabs, carriage returns, newlines).
4. If the SHAs differ → emit `detected-citation-stale` row per the mapping above.
5. If no prior-session body is available → no row (cache warms for next refresh cycle).

## Limitations (v1.0)

- **Prior-session body availability.** The cache-contract v1.x atomic-write protocol replaces `body` and `meta.json` per key on the most-recent fetch; prior-session bodies are not preserved by the contract. A v1.x cache directory under active multi-session use may not retain prior-session bodies for the same key. The `detected-citation-stale` row therefore fires only when an entry written by an earlier session has NOT yet been overwritten in the current session. POSSIBLE FUTURE OPTIMIZATION: a per-session-named body sidecar (e.g., `<key>/body.<session_id>`) would preserve prior-session bodies for compare across all session boundaries; this would coordinate with a cache-contract minor bump.
- **Materiality judgment.** SHA-of-body-compare is conservative — every textual change (whitespace, footer year, template re-render) flags `detected-citation-stale`. The normalize step (lowercase, strip whitespace) cuts the most-common false-positives; the author drives the materiality call from the `evidence-quote`.
- **No LLM-driven content diff.** A deeper content-diff (abstract diff, paragraph-rewrite detection) is POSSIBLE FUTURE OPTIMIZATION, not v1.0 contract surface, per Decision 8.

## Versioning

- Major (`2.0`) — breaking change to the check-name → row-field mapping, sidecar path pattern, or verification rules. Coordinated with `../../citation-detail-verify/references/output-schema.md` major bump only if the row shape itself breaks.
- Minor (`1.1`) — additive only. New optional fields in the sidecar markdown summary, new check-name registrations (which also bump the Stage 1 output-schema lock additively per its versioning rules).
- v1.0 is the locked skill-scoped contract. Bumping requires a PR against this file; sibling skills do not depend on it.
