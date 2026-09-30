---
title: Shared WebFetch cache contract for the research-pipeline skills
version: 1.4
status: locked
owners: [citation-detail-verify]
consumers: [citation-detail-verify, load-bearing-fullread, adversarial-frame, source-recency-probe, survey-refresh]
---

# Cache contract v1.4

Locked at Stage 1 (citation-detail-verify) of the research-pipeline skill family. The contract is REUSED unchanged by `/load-bearing-fullread`, `/adversarial-frame`, and `/source-recency-probe`. All four skills read from and write to the same absolute on-disk location so the same URL fetched by one skill within a session is served from cache to the others.

## Deployment assumption

The on-disk path below assumes user-scope APM install (`apm install ... -g --target claude,cursor`) — the dominant deployment per `~/.claude/CLAUDE.md` and the project AGENTS.md. Project-scope install (advanced; rare) places each skill copy under that repo's `.claude/skills/` and would fragment the cache because sibling skills resolve a different absolute path. Project-scope deployments SHALL pin sibling skills to the same project root before consuming this contract, or accept fragmentation.

Poppler (`pdftotext`) is an **optional** runtime dependency introduced at v1.4 for PDF bodies. It is not installed by any hook, setting, or CI step in this repo. Install with `brew install poppler` (macOS) or `apt install poppler-utils` (Debian/Ubuntu). When absent, PDF bodies are stored but not extracted, `meta.json.extracted_text.status` records `tool-missing`, and every consumer row that needed the text emits `unverifiable` with `check-detail.reason: "pdftotext-not-on-PATH"` — the pre-v1.4 behaviour with a named cause.

## On-disk location

```
~/.claude/skills/citation-detail-verify/cache/<key>/
  body              ← raw fetched bytes (HTML, JSON, PDF, plain text, etc.)
  body.txt          ← v1.4: extracted text, present only when `body` is a PDF and extraction succeeded
  meta.json         ← fetch metadata (see §meta.json shape)
```

The location is fixed by this contract. Sibling skills (`/load-bearing-fullread`, `/adversarial-frame`, `/source-recency-probe`) reference this path verbatim. citation-detail-verify owns the directory; sibling skills are read-mostly cross-readers and SHALL only write entries they fetched themselves.

The directory is created on first write. Skills MUST NOT assume it exists at startup; `mkdir -p` before write.

`body.txt` is derived from `body`, never fetched. It is written by the miss-path writer only (see §Read protocol); no reader creates it. A v1.3 reader ignores it and continues to read `body`.

## Cache key derivation

The cache key is a 64-character lowercase hex SHA-256 of the normalized URL alone:

```
key = sha256(normalized_url).hexdigest()
```

Where `normalized_url` is the fetched URL after the following normalization steps, applied in order:

1. Lowercase the scheme and host.
2. Strip default port (`:80` for http, `:443` for https).
3. Strip trailing slash from the path.
4. Remove fragment (`#...`).
5. Sort query parameters lexicographically by name.

ETag is intentionally NOT part of the key. A cold read by one skill (which has no ETag yet) and a warm rewrite by another skill (which has an ETag in `meta.json`) MUST hash to the same key so cross-skill cache hits work. ETag lives in `meta.json` and drives the conditional-revalidation invalidation trigger (see §Invalidation triggers).

Skills MUST normalize identically; divergent normalization fragments the cache and defeats cross-skill hits.

## meta.json shape

```json
{
  "version": "1.0",
  "url": "<original URL as requested>",
  "normalized_url": "<URL after normalization>",
  "etag": "<ETag header value or empty string>",
  "http_status": 200,
  "content_type": "text/html; charset=utf-8",
  "fetched_at": "<ISO-8601 UTC>",
  "fetched_by": "<skill-slug>",
  "session_id": "<Claude Code session id at fetch time>",
  "size_bytes": 87421
}
```

**Optional at v1.4** — `extracted_text`, present when a v1.4 writer stored a PDF body (absent from v1.3 entries):

```json
"extracted_text": {"tool": "pdftotext", "status": "ok", "words": 11484, "version": "norm-v1"}
```

`status` ∈ `ok | tool-missing | failed`. `words` is `0` unless `ok` (and `ok` with `words: 0` is the text-less-PDF case — see §Read protocol). The extraction subprocess is bounded by a 60 s timeout; a timeout is recorded as `failed`. Executable form: `../scripts/pdf_extract.py extract`. This field is telemetry for row `check-detail`; it is **not** the gate for reading `body.txt` (see §Read protocol).

All fields required. `session_id` is populated from the harness session-id env-var, resolved in this fixed order (v1.2 additive — earlier v1.0/v1.1 callers using only `$CLAUDE_SESSION_ID` continue unchanged):

1. `$CLAUDE_SESSION_ID` (preferred / legacy harness name).
2. `$CLAUDE_CODE_SESSION_ID` (current Claude Code harness as of 2026-05 — exposed by `CLAUDECODE=1` runs).

If neither env-var is set (and neither is empty-string), the skill SHALL refuse to write to the cache (and emit a refusal-record marker in its envelope's optional `notes` field) — empty-string `session_id` is unsafe because it would match every other empty-`session_id` entry and silently defeat per-session freshness. Readers encountering an empty-string `session_id` on disk (legacy / corrupted entry) MUST treat the entry as stale. `fetched_by` lets audit trails attribute a cache entry to the originating skill.

## Session-scope freshness policy

Cache freshness is scoped to one Claude Code session.

- An entry is fresh iff its `meta.json.session_id` equals the current session id (resolved via the §meta.json shape read order: `$CLAUDE_SESSION_ID` first, then `$CLAUDE_CODE_SESSION_ID`).
- An entry whose `session_id` does not match the current session is stale; the reader MUST treat a stale entry as a miss and re-fetch. The stale entry MAY remain on disk (used for telemetry / audit); the re-fetch overwrites atomically.
- The per-session boundary is the design pivot: safe to share across the four skills inside one pipeline run, without leaking across sessions where the source might have changed.

The 7-day garbage-collection step described in §Maintenance below is housekeeping, not a freshness rule — a 6-day-old entry from the same long-running session is still fresh.

## Maintenance (out of scope for v1.0)

Entries older than 7 days SHOULD be garbage-collected by a future maintenance step. Record only; the v1.0 contract does not specify when or how that step runs. Partial / aborted writes left as `<key>.tmp.*` files SHOULD be cleaned by the same step.

## Invalidation triggers

An entry is invalidated (treated as miss; re-fetch required) when ANY of:

1. The current session id differs from `meta.json.session_id` (see §Session-scope freshness policy).
2. A conditional re-fetch (`If-None-Match` against `meta.json.etag`) returns 200 with a different ETag. Skills SHOULD revalidate via `If-None-Match` when they have time budget; this is the proactive-revalidation flow (see §Read protocol step 4). Skills MAY skip revalidation within the same session and rely on session-scope freshness only.
3. The URL no longer normalizes to the same `normalized_url` (defensive guard against a future normalization bug).
4. `meta.json` is missing or fails to parse (corruption recovery).
5. `body` is missing while `meta.json` is present (or vice versa).

Skills SHALL NOT add invalidation triggers beyond this list. New triggers are a v1.1 (additive) change.

## Atomicity

Writes are atomic per file inside the `<key>/` directory:

1. `mkdir -p <key>/` (idempotent; safe under concurrent creation).
2. Write `body` to `<key>/body.tmp.<pid>`; `fsync`; `rename` to `<key>/body`.
   - If `body` is a PDF and `pdftotext` is present: write `body.txt` to `<key>/body.txt.tmp.<pid>`; `fsync`; `rename` to `<key>/body.txt` — only when extraction reports `words > 0`.
3. Write `meta.json` to `<key>/meta.json.tmp.<pid>`; `fsync`; `rename` to `<key>/meta.json`.

`os.rename` (POSIX `rename(2)`) is atomic at the file level; renaming over an existing file replaces it atomically. Per-file rename avoids the directory-rename pitfall (POSIX `rename` cannot replace a non-empty directory).

Readers MUST tolerate the brief window between body-rename and meta-rename: a reader observing `body` present but `meta.json` absent treats the entry as in-flight and MAY either short-spin-retry or treat as miss and re-fetch. Either is correct; the bound is one writer's two-rename window.

Concurrent writes to the same key from two skills race per file; last writer wins on each file. Acceptable — both writers fetched the same URL within the same session, so bodies are semantically equivalent.

The "bodies are semantically equivalent" rationale above does **not** extend to `body.txt`: its presence depends on the writer's machine having poppler. Two writers of differing capability can leave `meta.json.extracted_text.status` disagreeing with the presence of `body.txt`. The §Read protocol text-read rule is therefore presence-led, not status-led.

## Extracted text match key (`norm-v1`)

`body.txt` is `pdftotext` default reading-order output, stored as emitted, form feeds included (one per page). `-layout` mode is prohibited: it interleaves the two columns on each physical line. The text is **not** repaired — measured 2026-09-14 over thirteen ACL Anthology papers, every line-final hyphen is followed by a blank line and 41 of 80 are then interrupted by a page number, caption, heading, or adjacent-column text, so no in-place join is safe.

Quote presence is therefore tested on a match key rather than on the text, built in this order:

1. Unicode NFC.
2. Join line-break hyphenation: a hyphen-class code point (U+002D, U+2010, U+2011, U+00AD) followed by whitespace is removed together with that whitespace — `improve-` / blank / `ments` becomes `improvements`; `Self-` / blank / `Refine` becomes `SelfRefine`.
3. Delete any remaining hyphen-class code points — `state-of-the-art` becomes `stateoftheart`.
4. Collapse whitespace runs (including `\f`) to a single space.

Case is preserved throughout. Matching is token-boundary anchored, not raw substring containment: the candidate `evidence-quote`'s key must occur in `body.txt`'s key at a word boundary on both ends, so a short quote cannot match inside a longer word (`"a cat"` does not match `"a categorical framework"`; `"in form"` does not match `"in formal terms"`). Cross-word false positives are excluded by the boundary anchor.

A quote whose key does not match as a whole, but splits at exactly one point into a head and a tail (each at least five key characters) that occur in order in the body key with at most two quote-lengths of inserted text between them, is reported `unverifiable` with `check-detail.reason: "quote-spans-page-break"` — the shape a page-break insertion produces. Any other non-match is `fail`. A hit returns the raw offset of the match's start in `body.txt`, so `page N` anchors resolve via that offset (`pdf_extract.py page-of`) rather than from the key string. Executable form: `../scripts/pdf_extract.py quote-present`, which prints that raw offset on a hit; the underlying key→raw offset bridge is the `locate()` function inside `pdf_extract.py`.

## Read protocol

```
1. derive key from normalized_url
2. if <key>/body AND <key>/meta.json exist AND meta.json parses AND
        meta.json.session_id == current_session:
       (optional) if skill chooses to revalidate:
           HEAD or conditional GET with If-None-Match: meta.json.etag
           if 304: refresh meta.json.fetched_at, return body
           if 200 with new ETag: cache miss, fall through to fetch
       return body                                                ← cache hit
   else:
       fetch URL  (per §Liveness fetch fallback — a 403/429/503/empty body
                   escalates the ladder before the result is treated as a miss)
       atomically write <key>/body and <key>/meta.json (with response.etag)
       return body                                                ← cache miss
```

**Text-read rule (v1.4).** A consumer that needs the body *as text* reads `<key>/body.txt` whenever it is present and non-empty, else `<key>/body`. A PDF `body` with no `body.txt` is **unextracted**: the consumer proceeds as it did before v1.4 and records `check-detail.route: "pdf-extract"` plus `check-detail.reason` from `meta.json.extracted_text.status` (`pdftotext-not-on-PATH` for `tool-missing`, `pdftotext-failed` for `failed`, `not-extracted` when the field is absent). **No consumer extracts on read**; extraction happens only on the miss-path write. Consumers that compare raw bytes (`survey-refresh` SHA256) keep reading `body`.

**Byte-preserving fetch for a PDF response.** `WebFetch` cannot return binary bytes, so a response whose `content_type` starts `application/pdf` is not fetched through it. The miss-path writer instead downloads the bytes with `curl` (invoked through `Bash`, which is present in every consumer's `allowed-tools`): `curl -sSL -A "Mozilla/5.0" -o <key>/body.tmp.<pid> <url>`, then renames the temp file to `<key>/body` per §Atomicity. Only then does the writer run `pdf_extract.py extract <key>/body --out <key>/body.txt`; record its JSON as `meta.json.extracted_text`; write `meta.json`. `body.txt` is written only when `words > 0` — a text-less PDF is `status: "ok", words: 0` with no `body.txt`, and is **unextracted** under the text-read rule above.

Cold reads (no prior entry) always proceed to fetch and write. Warm reads from a sibling skill within the same session match the key by URL alone and serve immediately.

## Liveness fetch fallback

The miss-path `fetch URL` step is NOT a single bare request. A live source can be hidden behind a tool-mechanics condition — the default fetcher (Claude's WebFetch) sends no browser `User-Agent`, so authoritative hosts may bot-block it (`iso.org` → `403`), serve a client-render-only shell with an empty body (Semantic Scholar), or IP-throttle an API (`export.arxiv.org` → `429`). Treating any of those as terminal misclassifies a *live* source as unreachable and yields a false `unverifiable`. The fetch step SHALL therefore escalate through this ladder, in order, before the result is treated as a genuine miss or handed to a status check:

```
1. Default fetch.
2. If HTTP 403 / 429 / 503, OR the body is empty / a client-render-only
   shell:
     - for 429 / 503: honor any applicable rate-limit backoff first;
     - retry once with a browser User-Agent
       (e.g. "Mozilla/5.0 ... Chrome/... Safari/...").
3. If still failing: try ONE alternate authoritative route for the SAME
   artifact —
     - the publisher DOI resolver (https://doi.org/<doi>),
     - a structured bibliographic API (dblp, Semantic Scholar Graph API
       https://api.semanticscholar.org/graph/v1/...),
     - the venue's non-API host (e.g. https://arxiv.org/list/<cat>/<YYYY-MM>?show=2000
       instead of the throttled export.arxiv.org API).
4. Only if every route fails → the fetch is a genuine miss / the
   reachability check terminates at `unverifiable` (see
   output-schema.md §Status semantics).
```

Properties:

- **Failure-path only.** The ladder fires only when step 1 fails; the common `200`-first case is unchanged. Worst case adds one UA retry plus one alternate-route fetch per failing source.
- **No throttle amplification.** Step 2 honors existing rate-limit backoff for `429`/`503`; step 3 prefers a *different* host/API over re-hitting the throttled one (the arXiv listing-host route is the canonical example).
- **Not a paywall/auth bypass.** A genuinely paywalled or auth-gated body still terminates at step 4. A binary PDF is no longer "unparseable" when poppler is present — v1.4 extracts it on the miss-path write (§Read protocol); without poppler it remains an unextracted body and the consumer row says so. The ladder addresses bot-gating, throttling, and client-render gaps that an alternate read route resolves — nothing more.
- **Cache write uses the successful route.** Whichever route yields the body is what is written to `<key>/body` + `<key>/meta.json`; `meta.json.url` records the route actually fetched, and `meta.json.http_status` the status that route returned.
- **Auditability.** When step 4 is reached, the consuming skill's row `check-detail` SHALL name the routes attempted, so a terminal `unverifiable` is distinguishable from an un-attempted one.

This ladder is a property of the shared fetch primitive: all five consumer skills inherit it by REUSE, with no per-skill duplication and no new invocation flag.

## Cross-skill telemetry

The output-schema.md v1.0 envelope's `cache` field carries per-invocation telemetry: `{"hits": N, "misses": N, "writes": N}`. Skills that consume this contract MUST populate `cache` (and the envelope field is correspondingly REQUIRED for cache-consuming skills; OPTIONAL for skills that do not fetch). Aggregating across skill runs answers "did the shared cache actually deduplicate fetches?" — the test surfaced by the `detect cache-hit-on-shared-fetch` success criterion in the three sibling briefs.

## Versioning

- Major (`2.0`) — breaking change to key derivation, on-disk layout, or invalidation semantics. Pipelines fail closed: a skill running v2.0 against a v1.0 cache directory MUST refuse and refetch (key namespace divergence).
- Minor (`1.x`) — additive change only. New optional `meta.json` fields. New entries in the §Invalidation triggers list. New entries in the §meta.json shape session-id env-var fallback order (added to the tail of the read order — never reordering or removing existing entries). Refinements to *how* the miss-path fetch is performed that consumers inherit gracefully (e.g. the §Liveness fetch fallback ladder) — these change no key, layout, or invalidation semantics. Older readers MUST ignore unknown optional fields. Removals or semantic changes are major-version bumps, never minor.
- v1.0 was the locked Stage 1 contract. v1.1 added prior minor entries. v1.2 adds `$CLAUDE_CODE_SESSION_ID` as the v1.0 fallback in the §meta.json shape session-id read order; existing v1.0 callers using only `$CLAUDE_SESSION_ID` continue unchanged (the new env-var is consulted only when the legacy one is unset). v1.3 adds the §Liveness fetch fallback ladder to the miss-path fetch step (browser-`User-Agent` retry + alternate-authoritative-route escalation before a fetch is treated as a genuine miss); purely additive — no change to key derivation, on-disk layout, or invalidation semantics, so all consumers inherit it by REUSE with no pinned-reference break. v1.4 (current) adds `body.txt` and the optional `meta.json.extracted_text` field for PDF bodies, the §Extracted text match key, and the presence-led text-read rule. Minor, argued against the clauses above: a v1.3 reader finds `body` and `meta.json` unchanged, ignores the unknown file and the unknown optional field, and behaves exactly as before; no key, no existing layout element, and no invalidation trigger changes. "Layout" in the major clause is the layout existing readers depend on, which is untouched.
