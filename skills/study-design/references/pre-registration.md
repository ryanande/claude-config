# study-design — the pre-registration block

Loaded at Workflow Step 6. Seven fields, frozen at the commit that introduces
them into the study document. The seventh field, `protocol:`, carries a
per-design key set — see §The protocol field.

## The block (shown for D1)

```yaml
pre-registration:
  design: D1 | D2 | D3
  metric: precision | precision-contrast | recall | F1 | <rate delta, D3>
  sample: >
    <n, source, clustering — as before>
    strata:                     # D1; the one catalog stratum
      - {name: frozen-by-construction, rule: <enumerator rule id>, n: <count>}
  stopping-rule: <as before>
  resolution: >
    <as before, PLUS: names the stratum set it is computed over>
  negative-result: >
    <as before, PLUS: precision is REAL / census; the cap counts every UNRESOLVED over the
     primary value's census (or the union where flag sets do not nest); under
     precision-contrast, the contrast conjunct against every other evaluable value>
  protocol:
    enumerator:  assets/evals/<id>/enumerate.py@sha256:<hex>
    repo-owners: [<publication owner>, <census-derived owners>, <declared owners>]
    repo-map:    assets/evals/<id>/repo-map.json@sha256:<hex>
    unresolved-identities:
      - {identity: <bare name | owner/name>, disposition: not-a-repository | owner-unknown | ambiguous-name | pair-unresolved, items-citing: <n>, item-ids: [<ids>]}
    primary-value: {value: <parameter value>, oq-record-sha: <sha>}   # parametrised flaggers only
    clause-set:
      - {type: open-questions, clause: "<the OQ REAL rule, verbatim>"}
      - {type: rfc,            clause: "<the RFC REAL rule, verbatim>"}
    evidence-scope:
      - {remote: https://github.com/<owner>/research-docs.git, ref: HEAD-at-run}
      - {remote: <url>, ref: HEAD-at-run}
      - {remote: <harness runtime url>, ref: HEAD-at-run, role: harness-runtime}
    evidence-scope-excluded: []   # only {remote, reason: remote-inaccessible, items-citing}
    labels-per-item: 2
    screen: structural-real | none
    evidence-pack: citation-neighbourhood
    disagreement: ordered-3way
    model-policy: fixed-slots
    recheck: gate+rederive
    spawn-budget: {expected: <n>, worst-case: <n>}
```

Frozen at the commit that introduces it. `study-run` refuses any document whose
block was modified after that commit.

**Emission shape is load-bearing.** Emit the block as a fenced `yaml` code
block in the document BODY, closed by a bare closing fence at column 0 —
never as document frontmatter. `study-run`'s tamper guard locates the block by
`git log -L` ranging from the `pre-registration:` line to that bare closing
fence; a block emitted as frontmatter has no such fence for the guard to
anchor on, so the run false-refuses on a 0-commit match before it ever reaches
the sample.

## Field notes

- `design` — exactly one of D1/D2/D3, matching the catalog match from Workflow
  Step 4. Never a caller-supplied design (Refusals).
- `metric` — determined by the matched design's yield, never caller-supplied.
  D1 yields precision only; D2 yields precision and recall (and, downstream,
  F1); D3's causal comparison is a rate delta between arms, named for the
  outcome the lever is expected to move (e.g. an agreement-rate delta, a
  defect-escape-rate delta) — never a bare "agreement-rate" label when the
  question and the resolution/negative-result fields are stated in a
  different rate's terms. `precision-contrast` (D1, parametrised flagger
  only) — the metric when the flagger under study takes more than one
  evaluable parameter value. Triggered by either condition: the OQ record
  names more than one evaluable value, or the flag rate at the primary value
  exceeds 0.5. When triggered, `metric` is `precision-contrast`, never a bare
  `precision`, and `protocol.primary-value` is mandatory.
- `sample` — names the source (per the catalog's "sample source" field for the
  matched design) and states its clustering structure explicitly. A sample is
  rarely i.i.d.: findings cluster by pull request, PR cluster by author,
  planted defects cluster by artifact.
- `stopping-rule` — a concrete, checkable condition (a fixed N, a calendar
  date, a fixed number of merged PRs), never "until it looks clear."
- `resolution` — see below. Mandatory, not advisory.
- `negative-result` — the specific observation that would answer the OQ "no."
  Not a restatement of uncertainty; an observation, symmetric with the
  falsifier requirement `evidence-strength.md` places on `far`-rated axes.

## The protocol field

Every key in `protocol:` is derived or pinned — never chosen. `study-run`
Step 3a re-derives the ones marked so and refuses on mismatch.

The key set is **per design**, and a block carrying a key outside its design's
set is refused rather than tolerated. The D1 keys fall into four groups, and
only one of them generalizes:

| Group | Keys | Downstream of |
|---|---|---|
| Census production | `enumerator` | a census a script can enumerate at freeze time |
| Evidence reachability | `repo-owners`, `repo-map`, `unresolved-identities`, `evidence-scope`, `evidence-scope-excluded` | census item bodies naming repositories by ambiguous identity |
| Census typing | `clause-set`, `screen` | a census whose items carry a corpus **type** with a per-type decision rule |
| Adjudication mechanics | `labels-per-item`, `evidence-pack`, `disagreement`, `model-policy`, `recheck`, `spawn-budget` | a per-item judgment made by a spawn and checked by code |

The six adjudication-mechanics keys mean the same thing in any design that
spends a spawn on a judgment, so D2 and D3 carry them. The first two groups are
unfillable outside D1's shape. The census-typing pair is not dropped but
**replaced** — D2 substitutes `match` / `match-rule`, D3 substitutes
`outcome.measure` — because both still need a frozen decision rule, just not one
keyed by a corpus type.

One principle per design follows: **D1 and D2 pin values**, because the census
exists at freeze time; **D3 pins rules**, because it does not, and the enrolment
ledger records the values as they arrive.

### D1 — retrospective adjudication

| Key | Pinned value or derivation | Re-derived by `study-run` Step 3a |
|---|---|---|
| `enumerator` | path + sha256 of the author-written, per-study census script | no — pinned at freeze |
| `repo-owners` | union of publication owner, census-derived owners, declared owners | yes |
| `repo-map` | path + sha256 of the fetched owner→repo map | yes |
| `unresolved-identities` | extractor's `not-a-repository` / `owner-unknown` / `ambiguous-name` / `pair-unresolved` rows, with item ids | yes |
| `primary-value` | the named evaluable value with the largest flag set at the pinned sample commit; ties go to the smallest parameter value; recorded with the OQ-record SHA; present only for parametrised flaggers | yes, when `metric: precision-contrast` |
| `clause-set` | one row per census type present — `screen.py`'s fixed `CLAUSES` text for a `STRUCTURAL_TYPES` member, an author-derived REAL/NOISE clause otherwise; the self-check asserts the `CLAUSES` subset | yes |
| `evidence-scope` | extractor's identity set, plus the research-docs entry, plus the harness-runtime entry when any `~/.claude` mention exists | yes |
| `evidence-scope-excluded` | remotes failing `ls-remote`, reason `remote-inaccessible`, with items-citing | yes |
| `labels-per-item` | pinned `2` | no |
| `screen` | `structural-real` when the census includes any `STRUCTURAL_TYPES` member, else `none` | yes |
| `evidence-pack` | pinned `citation-neighbourhood` | no |
| `disagreement` | pinned `ordered-3way` | no |
| `model-policy` | pinned `fixed-slots` | no |
| `recheck` | pinned `gate+rederive` | no |
| `spawn-budget` | computed per `sample-prescan.md`'s expected/worst formula | yes |

### D2 — planted-defect corpus

Twelve keys. Dropped from D1: `enumerator`, `repo-owners`, `repo-map`,
`unresolved-identities`, `clause-set`, `evidence-scope`,
`evidence-scope-excluded`, `screen`, `primary-value`.

```yaml
  protocol:
    corpus-manifest: assets/benchmarks/<id>/manifest.json@sha256:<hex>
    corpus-ref:      {remote: <corpus URL>, ref: origin/main, sha: <sha>, path: <test-corpus path>}
    blind-scope:     [{remote: <corpus URL>, ref: <sha>, path: <corpus subtree>}]
    defect-classes:  [{class: <name>, planted: <n>, clean-controls: <n>}]
    match:           region-overlap+class-equality
    match-rule:      "<verbatim MATCH_RULE text from study-run/scripts/recheck.py>"
    labels-per-item: 2
    evidence-pack:   defect-neighbourhood
    disagreement:    ordered-3way
    model-policy:    fixed-slots
    recheck:         gate+rederive
    spawn-budget:    {skill-runs: <n>, adjudication-expected: <n>, worst-case: <n>}
```

| Key | Pinned value or derivation | Re-derived by `study-run` Step 3a |
|---|---|---|
| `corpus-manifest` | path + sha256 of the frozen answer key — the `{item_id, path, region, class, planted\|clean}` rows — committed under `assets/benchmarks/<id>/` in the PUBLICATION repository | yes |
| `corpus-ref` | `{remote, ref, sha, path}` of the seeded corpus in the corpus repository; the catalog's cross-repo `origin/main:<path>` citation rule, made machine-checkable | yes |
| `blind-scope` | what the skill under test may read: PATH-SCOPED entries on the corpus remote, materialized as history-free exports | yes — publication remote absent, every entry path-scoped and ref-pinned, no export carrying `.git` |
| `defect-classes` | per-class planted and clean-control counts, so recall is reported per class | yes — counts against the manifest; a zero-`planted` class refuses |
| `match` | pinned `region-overlap+class-equality`, implemented in fixed skill code | no |
| `match-rule` | the verbatim text of `recheck.py`'s `MATCH_RULE`, carried into the frozen document so the gate has something to compare a label against — the `clause-set` analogue | yes, as a subset assertion |
| `labels-per-item` | pinned `2` | no |
| `evidence-pack` | pinned `defect-neighbourhood` | no |
| `disagreement` | pinned `ordered-3way` | no |
| `model-policy` | pinned `fixed-slots` | no |
| `recheck` | pinned `gate+rederive` | no |
| `spawn-budget` | `skill-runs` = the manifest's distinct artifact count; adjudication terms computed over the RESIDUAL, not the census | yes |

**Two repositories, and which one holds the answer key.** The corpus lives in
the corpus repository (`research-skills`, under `test-corpus/` per that repo's
convention). The manifest lives in the **publication** repository, alongside the
study document, in the same `assets/<section>/<id>/` location `run-record.md`
already fixes for D1's registration and run record. A skill that can read its own
answer key measures nothing.

**Repository granularity is NOT sufficient, and blindness takes three legs.**
Putting the manifest in another repository is necessary and nowhere near enough.
The corpus repository's own HISTORY carries the answer key — the commit that
planted the defects *is* the placement, and `git log -p` over the corpus recovers
it without ever touching the publication remote. Sibling paths in the same
repository leak too: this suite's own D2 fixture states the per-class counts
verbatim. And an entry naming a remote with no path hands over the whole tree. So:

1. the publication remote does not appear in `blind-scope`;
2. every `blind-scope` entry is PATH-SCOPED to the corpus subtree and ref-pinned;
3. what the skill under test actually reads is a HISTORY-FREE export of that path
   (`git archive` at `corpus-ref.sha`, path-scoped), never a checkout or clone —
   an export carrying `.git` or `.gitmodules` refuses.

`recheck.py manifest` runs all three and refuses rather than reporting.

**The answer-key freeze is a sha256 of the file's bytes.** Without it, an operator
who has seen the skill's output can demote the defects it missed to `clean` and
recall jumps. `recheck.py manifest --manifest-sha256` hashes the file as read; a
re-serialised parse would not detect a reordering-plus-edit.

**No `primary-value` under D2.** D1 answers a parametrised flagger inside one
block via `precision-contrast`. D2 cannot: each parameter value needs its own
blind run against the whole corpus, so folding N values into one block would
multiply `skill-runs` by N while reporting one recall figure over runs that are
not comparable item by item. A parametrised flagger under D2 emits **one study
document per evaluable value**, each with its own frozen block, each citing the
same `corpus-manifest` and `corpus-ref`.

**The UNRESOLVED cap covers the residual.** D2's adjudicated population is the
residual, not the census, so the cap is computed over the residual count and
reported alongside the manifest count. An UNRESOLVED residual item stays in the
denominator of whichever metric it bears on — recall for an unmatched planted
defect, precision for an unmatched emitted row.

### D3 — prospective A/B

Three keys, plus a seven-key adjudication group present when and only when
`outcome.adjudicated` is true. Dropped from D1 unconditionally: `enumerator`,
`repo-owners`, `repo-map`, `unresolved-identities`, `evidence-scope`,
`evidence-scope-excluded`, `clause-set`, `screen`, `primary-value`.

```yaml
  protocol:
    arm-assignment: {mode: hmac-sha256-parity, identifier: <field name>, arms: [<A-token>, <B-token>]}
    enrolment:      {eligibility: "<verbatim rule>", target-n: <n>, deadline: <ISO date>, ledger: assets/evals/<id>/enrolment.jsonl}
    outcome:        {measure: "<verbatim rule>", source: "<where it is read>", at: merge, adjudicated: true | false}
    # the next seven when and only when outcome.adjudicated is true:
    evidence-scope-rule: "<verbatim; resolved per enrolled item, recorded in the ledger>"
    labels-per-item: 2
    evidence-pack:   arm-blinded-artifact
    disagreement:    ordered-3way
    model-policy:    fixed-slots
    recheck:         gate+rederive
    spawn-budget:    {expected: <n>, worst-case: <n>}
```

| Key | Pinned value or derivation | Re-derived by `study-run` Step 3a |
|---|---|---|
| `arm-assignment` | pinned mode `hmac-sha256-parity` over a named pre-existing identifier, keyed on the study's own FREEZING COMMIT — no salt field | yes — every ledger row's arm is recomputed; an unimplemented mode refuses |
| `enrolment` | `{eligibility, target-n, deadline, ledger}`; `ledger` is a PATH to an append-only record, never a sha256 | yes — append-only against the PREVIOUS registration branch's blob, no duplicate identifier, no row carrying an outcome |
| `outcome` | `{measure, source, at, adjudicated}`; `measure` is the verbatim per-item observation rule | no — pinned at freeze |
| `evidence-scope-rule` | the verbatim rule resolved PER ENROLLED ITEM at enrol time; its resolved trees land in the ledger | yes, when adjudicated |
| `labels-per-item` | pinned `2` | no |
| `evidence-pack` | pinned `arm-blinded-artifact` | no |
| `disagreement` | pinned `ordered-3way` | no |
| `model-policy` | pinned `fixed-slots` | no |
| `recheck` | pinned `gate+rederive` | no |
| `spawn-budget` | computed from `target-n` | yes, when adjudicated |

**The block pins rules; the ledger records values.** No census exists at freeze
time, so nothing enumerated can be pinned. `enrolment.eligibility` and
`outcome.measure` are verbatim rules; the values they produce — which artifacts
enrolled, which arm each drew, what outcome each recorded, which trees the
`evidence-scope-rule` resolved to — arrive over the study's months and land in
the append-only enrolment ledger.

**Arm assignment is a mode, not prose, and it carries no author-chosen salt.**
Alternation by arrival order is steerable: an author who knows the alternation
state can hold work back to land it in the preferred arm. An author-generated
salt is no better — the block publishes it, so anyone can precompute their own
arm, and the study author can grind salts at freeze time until the assignment
they want falls out of a known identifier window. The HMAC is therefore keyed on
the study's **freezing commit SHA**: fixed by the tamper guard, not chosen
(grinding it means grinding commits whose content is the block being hashed), and
needing no field of its own. Step 3a recomputes every ledger row's arm from it —
D3's structural analogue of D1's enumerator re-run.

**Arm tokens are constrained, not free text.** The blinding-breach gate scans for
the arm token literally, so a short or common word (`A`, `optional`) fails every
label on ordinary prose and drives a whole run to UNRESOLVED — a freeze-time
lever. A token under four characters, or one on the fixed common-word denylist in
`recheck.py`, refuses at emission.

**Residual, named: a single-operator D3 cannot be made unsteerable.** When the
study author is also the enrolled artifacts' author, they can compute their own
arm once the freezing commit exists and bump an incrementable identifier (open a
throwaway issue to shift PR numbering). Nothing here forecloses that. What it does
is make the manipulation VISIBLE: `recheck.py enrolment` reports skipped
identifiers as `gaps`, and the run record carries them.

**Enrolment rows carry no outcome.** An operator holding the running per-arm delta
can stop enrolling when the interim suits them — optional stopping the phase
derivation does not detect. So an enrolment row records identifier, arm, merge
SHA, eligibility rationale, and resolved trees, and nothing else; outcomes are
read at score time from `outcome.source`. A row carrying `outcome`, `arm_split`,
or `delta` refuses.

**Enrolment and scoring are separate DERIVED phases.** A D3 study spans months,
so it cannot be one invocation. `study-run` derives its phase from the frozen
stopping rule rather than a flag: `enrol` while `target-n` is unreached and the
deadline unpassed, `score` otherwise. Deriving it from the same condition the
block froze is what stops a caller asking for an early score pass to see whether
the numbers look good — so `recheck.py phase` takes no date argument, and derives
the count from a ledger that VALIDATED, because an unvalidated ledger padded with
empty rows reaches `target-n` on its own.

**Arm blinding.** When `outcome.adjudicated` is true, a spawn that learns the arm
is no longer measuring the lever. The pack strips every arm marker, and the gate
fails a rationale that names either arm token, landing the item UNRESOLVED. The
cap is computed over the ledger's row count at score time. When
`outcome.adjudicated` is false no label exists: outcomes are read mechanically,
no cap applies, and a citation that fails to resolve is a recorded deviation
against that row.

## Strata

Strata are a D1 construct; D2 and D3 blocks carry no `sample.strata`.

D1 studies carry exactly one catalog stratum: `frozen-by-construction` — a
landed artifact whose status is asserted by design (an RFC frozen by
ADR-0018's kernel lock), not by adjudication. Informational only: it is
reported in `sample.strata` and in `protocol.cap`'s two values (at N and at N
minus the stratum count), and it is never removed from the census or from any
conjunct — a `frozen-by-construction` row still counts toward precision and
toward every contrast conjunct under `precision-contrast`.

## Version constant

`MERGE_SHA = 7624ca8135783f663ce54419f3f62bd2aebac7be` — the `research-skills` `main` commit that
landed the seventh field. `study-run` Step 4 runs a six-field block only when
its freezing commit predates this SHA in the publication repository's
history (compared by commit date, since the two repositories share no
ancestry). Filled once, in the merge commit's follow-up, never edited again.

## Effective sample size is mandatory, not advisory

`resolution:` computed from raw count understates the interval whenever
observations are clustered. Findings drawn from N pull requests written by one
author are clustered on both the PR and the author; the effective n is nearer
the PR count than the finding count. `resolution:` MUST name which comparisons
the sample forecloses, in the study's own numbers — never a generic band.

Worked example (the D1 pilot referenced in the design spec): 144 findings
clustered in 36 pull requests, single author, so the effective n is nearer the
PR count (36) than the finding count (144). That supports separating "mostly
real" from "mostly noise"; it does not support separating 60% from 70%, and
`resolution:` must say so in exactly those numbers — not "n=144" and not a
generic "small sample" caveat.
