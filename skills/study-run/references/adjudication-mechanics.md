# study-run — adjudication mechanics

Loaded at Workflow Step 6. Why the spawn mechanics are reused rather than the
entry point they came from, why the finding batch handed to a labeler is not a
bias surface, the slot / disagreement / pack / re-check modes, and — at the end
— what each of those means under D2 and D3, whose samples are not D1's census.

## Why the mechanics are reused, not the entry point

`/review-artifact` cannot adjudicate a caller-supplied batch, and that is by
design. Its interface is `--artifact <path>` — one document. It has no input
channel for injected findings, a focus filter, or a critic brief, and that absence
IS its structural anti-anchoring guarantee. Its stated boundary also excludes
source code and PR diffs, which is D1's own ground-truth substrate. It is
generator-shaped: its critics produce the findings it then adjudicates. Labeling a
pre-existing batch is judge-shaped. Calling it would assert a capability it lacks.

What transfers is the rule set it operationalizes:

Firm mechanics:

- cold-run spawn — fresh context per labeler, no session history;
- one item per labeler, whole item;
- no cross-talk — unnamed spawns, no messaging tool, so there is no sibling roster;
- a brief generated from a fixed template with NO expected-label slot;
- the caller re-checks every returned label against ground truth. Agreement between
  labelers is not evidence. RFC-0018 calls this the **primary** lever, and says it
  "dominates the secondary, merely-correlation-reducing cross-provider preference
  (rule 4)."

Model diversity is a **secondary, hedged** lever, and must not be listed alongside
the firm mechanics. RFC-0018 rule 4 reads: "**Prefer cross-provider diversity where
stakes justify it** (secondary lever). Same-provider/same-lineage critics share
correlated errors and buy weak independence; a genuine cross-provider pairing is
stronger. Cross-model is directional, never a guarantee." `study-run` assigns a
distinct model per labeler where the roster allows, as a cheap correlation
reducer — an implementation choice, not a reused requirement — and never treats it
as a substitute for the ground-truth re-check.

## Payload is not a bias surface

`/invocation-discipline-lint` refuses "pre-filtered focus" as an OUT-bias surface.
The finding set handed to a labeler is NOT that: it is the payload — the data under
measurement, fixed by the pre-registration block before the run. The bias surfaces
are an expected label, a hint about which items are real, a caller verdict, and a
caller interpretation of any item. This split is stated explicitly in
`study-run`'s `## Invocation discipline` section in `SKILL.md` — the parsable
place `invocation-discipline-lint` reads this split from before ever reaching
this skill's payload — or `enforce` mode would refuse every invocation on its
own payload.

## The caller orchestrates and never performs

The runner spawns, collects, and runs `recheck.py`. It never labels, never
re-derives, never breaks a tie, never decides what a quote means. Every
judgment is a spawn on a fixed slot; every check is a script.

## Slots (`protocol.model-policy: fixed-slots`)

| Slot | Model | Brief |
|---|---|---|
| labeler A | `opus` | `labeler-brief.md` |
| labeler B | `sonnet` | `labeler-brief.md` |
| tiebreak | `haiku` | `labeler-brief.md` (same rendered brief as A/B) |
| re-deriver | `fable` | `rederive-brief.md` |

Assigned by roster position, never per run. A missing pinned model refuses
the run. The runner's model is read from the harness session identity where
exposed, else recorded as a disclosed self-report; equal to the re-deriver's →
refuse; equal to a labeler's or the tiebreak's → recorded correlation. Each
spawn's output carries its own `model` (source named or `unknown`);
`recheck.py ledger` refuses a mismatch with the requested model and records
`unknown` as an unverified slot.

## Disagreement (`protocol.disagreement: ordered-3way`)

`recheck.disagree(a, b)`: REAL/NOISE → UNRESOLVED, no tiebreak;
X/UNRESOLVED → one tiebreak spawn, `apply_tiebreak(X, t)` = X iff t = X else
UNRESOLVED; UNRESOLVED/UNRESOLVED stays. Rejected: "NOISE with flag" lets the
permissive labeler win by default.

## Evidence pack (D1: `protocol.evidence-pack: citation-neighbourhood`)

Per item, before any spawn: the tracked files at the pinned SHAs that cite the
item's path or id, or that the item cites (`git grep -l` over each scope tree
for the path stem and the document id; plus every path the item's body
links). Rendered into `{{PACK}}` as a list of `remote path` lines. A starting
point, not a boundary.

## The screen's label never reaches a spawn

Under `screen: structural-real`, `screen.py` assigns provisional REAL to
items its fixed rules decide. A screened item gets labeler A only; A = REAL
confirms; anything else escalates to A and B and the disagreement rule runs
over the labelers' labels only. The screen label lives in the ledger as a
covariate. A screen-contradicted item (screen REAL, final not REAL) is a
rule-defect signal, reported in Step 8.

## The re-check (`protocol.recheck: gate+rederive`)

Gate every label with `recheck.gate_label` (remote in scope, path at SHA,
quote verbatim, clause matches `clause-set`); a REAL or NOISE label with no
evidence entry fails the gate. Then one re-derivation spawn per
resolved item on the `fable` slot with `rederive-brief.md`: it sees the pinned
trees, item, clause, pack, and the labelers' cited list marked non-exhaustive
— never their labels. Match keeps the label; else UNRESOLVED. This is
RFC-0018's primary lever, moved off the runner; agreement between labelers is
still not evidence.

## D2 — mechanical first, residual only by spawn

D2's primary measurement is code, not judgment. `recheck.py match` compares
every row the skill under test emitted against the manifest rows under the
frozen `match: region-overlap+class-equality` mode: same path, overlapping line
range, equal class. A matched pair is a true positive, an unmatched planted
defect a false negative, an unmatched row over a clean control a false
positive. None of those reaches a spawn.

The residual is what the mode cannot decide: an emitted row that may describe a
planted defect under a different class name, and a planted defect some unmatched
row on ITS OWN PATH may cover without overlapping its region. A planted defect
with no such row is a decided false negative and never reaches a spawn — routing
a clean miss to judgment would let a labeler relabel it REAL and inflate recall,
and the pack (which requires the emitted row verbatim) would be unconstructible.
Only the residual is adjudicated, and it keeps the full D1 machinery — two
labels, `ordered-3way`, the fixed slots, gate and re-derivation — over a fraction
of the census.

**Evidence pack `defect-neighbourhood`.** Per residual item: the corpus region
at `corpus-ref.sha` with surrounding context, the emitted row verbatim, and the
**single** candidate manifest row the question is about. No spawn receives the
whole manifest; the pack is how blindness survives adjudication.

**The gate, re-scoped.** The same `recheck.gate_label`, with its legs pointed at
the corpus tree: the path exists at `corpus-ref.sha`, the quote greps verbatim
there, and the returned claim matches the frozen `match-rule`. A residual label
with no evidence entry fails, exactly as in D1.

**The cap covers the residual.** D2's adjudicated population is the residual,
not the census, so the UNRESOLVED cap is computed over the residual count and
reported alongside the manifest count. An UNRESOLVED residual item stays in the
denominator of whichever metric it bears on — recall for an unmatched planted
defect, precision for an unmatched emitted row.

## D3 — arm blinding, or no spawn at all

`outcome.adjudicated` decides whether D3 spawns anything.

**False.** Each outcome is read mechanically per `outcome.source`. No spawn
fires, no label exists, and no cap applies. The analogue of the gate is a
citation gate: every recorded outcome's citation must resolve at the enrolled
artifact's merge SHA. It is the same `gate_label`, over a single-entry rule set
carrying `outcome.measure` (see §The wildcard rule set). A citation that fails
to resolve is a recorded deviation against that row, never an UNRESOLVED label.

**True.** The pack is `arm-blinded-artifact`: the enrolled artifact at its merge
SHA with every arm marker stripped, over the trees `evidence-scope-rule` resolved
at enrolment and recorded in the ledger. **The pack is the blinding mechanism.**
The gate's `recheck.arm_leak` leg is a backstop: it scans the whole serialised
label, minus the frozen `clause` text, and fails any label naming either arm
token, landing the item UNRESOLVED. Two limits are stated rather than papered
over — it catches LITERAL tokens only, so a paraphrase passes; and because it is
a literal scan, the arm tokens themselves are constrained at design time (no
token under four characters, none on the common-word denylist), or ordinary
review prose would fail every label. The cap is computed over the enrolment
ledger's row count at score time.

## The wildcard rule set

`gate_label(label, trees, clause_set, item_type)` is not branched per design. D2
and D3 items carry no corpus type, so both the rule set and the item use the
literal `"*"`, and the frozen rule text — `match-rule` for D2,
`outcome.measure` for D3 — travels in the label's `clause` field. The label
vocabulary stays `REAL` / `NOISE` / `UNRESOLVED`, which is what keeps the
evidence-presence leg firing: for D2 a residual label answers "does this emitted
row describe this planted defect", for D3 it answers `outcome.measure`.
`test_recheck.py` pins the single-entry `"*"` set, so the conventions are
enforced by a test rather than by this paragraph.

## Brief slots under D2 and D3

`labeler-brief.md` renders `{{TYPE}}` and `{{STATUS}}` from a corpus item's
frontmatter, which D2 and D3 items do not have. Both are filled per design
rather than left blank: D2 renders `{{TYPE}}` as the candidate manifest row's
defect class and `{{STATUS}}` as `planted` or `clean-control`; D3 renders
`{{TYPE}}` as the enrolled artifact's kind and `{{STATUS}}` as `merged`.
Neither reveals the answer for the item under adjudication — a D2 residual spawn
is asked whether an emitted row describes the one candidate row it is shown, so
that row's class and status are the question's premise, not its answer.
