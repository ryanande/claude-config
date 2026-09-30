# OQ-resolver — disposition reference

Load at Step 6. The disposition decision table (5 outcomes — promote / promote
(provisional) / measure / drop / park) and the surgical frontmatter-edit
recipe. `measure` does not use the 4-state OQ status vocabulary `open | parked
| promoted | dropped` at all: it leaves `status: open` and writes `measuring:`
instead of flipping status. Every disposition is a PROPOSAL in the PR diff; the
human merge ratifies. (There is no `resolved` status — "answered by a decision
doc" IS `promoted` with a `promoted-to:`, per the OQ lifecycle.)

## Decision table

| Verdict + evidence | Disposition | OQ frontmatter | Companion artifact |
|---|---|---|---|
| every `unblock-by` item at `direct-external` or `measured-local` | **promote** | `status: promoted`, `promoted-to: RFC-<provisional>` / `<ADR\|RFC>` | draft RFC or findings note, as before |
| ≥1 item at `adjacent-domain`, transfer argument holds, reversal-cost test passes | **promote (provisional)** | `status: promoted`, `promoted-to: <ref>` | draft RFC carrying `evidence-strength: adjacent-domain`, a `falsified-by:` line, a paired measurement OQ, and a `review-by:` date |
| evidence insufficient AND a study is achievable | **measure** | `status: open` (unchanged), `measuring: EVAL-NNNN \| BENCH-NNNN` | the pre-registered study document `study-design` emitted |
| evidence shows the question evaporated | **drop** | `status: dropped` | one-paragraph rationale (cited) |
| real-but-not-now, OR `study-design` returned an infeasibility rationale | **park** | `status: parked` | rationale naming the design considered and why its envelope fails |

Rules:
- The RFC number is **PROVISIONAL** — a placeholder the human assigns at merge.
  NEVER compute `max(existing)+1` at run time: two concurrent runs would collide
  silently.
- `unverifiable`-dominant evidence still blocks **promote** and **promote
  (provisional)**. Its route changed: it now goes to **measure** first, and
  reaches **park** only when `study-design` returns an infeasibility rationale.
  Ambiguous or low-confidence evidence routes the same way.
- **A park on infeasibility grounds MUST name which design was considered and why
  its envelope fails.** A park that says only "unmeasured" is not a valid
  disposition under this table.
- `measure` leaves `status: open`. It is not a terminal state; it is a commitment
  to produce evidence, tracked by `measuring:` as a visible loose end.
- The disposition rationale lands in the OQ flip / draft RFC / PR body — NEVER in
  a `survey-author` companion (it carries no recommendation, by invariant).
- The evidence artifact is committed in ALL successful dispositions — it is the
  durable record even for park, drop, and measure.

## Surgical frontmatter edit (preserve the nested `build:` block)

OQ frontmatter carries a NESTED block a flat `key:value` rewrite would drop or
corrupt:

```yaml
status: open          # ← the only line to change (+ promoted-to)
...
build:
  render: never       # ← nested — MUST survive untouched
  list: never
```

Flip ONLY the `status` line (and add/change `promoted-to:` when promoting/
resolving). Do NOT round-trip the whole frontmatter through a flat parser.

**Preferred mechanism — the deterministic helper:**

```bash
python3 ~/.claude/skills/oq-resolver/scripts/oq_flip.py \
  --file <oq-path> --status <promoted|dropped|parked> \
  [--promoted-to <RFC-NNNN|ADR-NNNN>] --in-place
```

`oq_flip.py` rewrites ONLY the matched `status:`/`promoted-to:` lines inside the
frontmatter and leaves every other byte — including the nested `build:` block —
identical (it refuses an invalid status or a missing/duplicated key). This is the
byte-preservation guarantee, covered by `scripts/test_oq_flip.py` (run it to
verify). Fallback if the helper is unavailable: a targeted single-line `Edit` of
the `status` line (never a flat-parser round-trip; never the exocortex
`parse_simple_kv`, which handles flat key:value only).

After the flip, the self-verify step (Step 7) confirms the `build:` block is
byte-preserved in the committed diff.

### The `measure` flip

`measure` does NOT change `status`. It adds (or updates) `measuring:` — the
value is whichever provisional id `study-design` reported, `EVAL-NNNN` (D1/D3)
or `BENCH-NNNN` (D2):

```bash
python3 ~/.claude/skills/oq-resolver/scripts/oq_flip.py \
  --file <oq-path> --status open --measuring <EVAL-NNNN|BENCH-NNNN> --in-place
```

`--measuring` inserts the key immediately after `promoted-to:` when absent, and
rewrites its value when present. Insertion adds exactly one line; every other
byte — including the nested `build:` block — is preserved. Covered by
`scripts/test_oq_flip.py`.

## PR body template

```
## Proposed disposition: <promote | promote (provisional) | measure | drop | park> — OQ-<id>

<one-paragraph rationale, grounded in the verified sources>

## Evidence
- survey/findings: <path>
- sources: <n verified> / <m unverifiable>  (verified/unverifiable ratio)

## Verifier verdicts
- source-recency-probe: <verdict>
- citation-detail-verify: <verdict>
- load-bearing-fullread: <verdict>  (arXiv subset: <k> ids)
- adversarial-frame: <verdict>  (alternatives engaged: <list>)

## Human decision
This PR PROPOSES the disposition above. Merging ratifies it (assign the real RFC
number on promote). Closing rejects it. The skill never merges.
```
