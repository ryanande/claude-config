---
fixture: abstract-only
exercises: framing-drift-domain-transfer, finding-includes-paper-evidence-quote, output-row-with-all-required-fields, parsed-source-id-list
expected-verdict: fail
---

# Fixture — abstract-only

A source whose resolved body carries a title and an abstract but no paper body sections, after
the full-text mirror hop of `../references/source-resolution.md` §Full-text mirror hop has been
attempted and failed, and after its PDF extraction route (§Full-text mirror hop step 5) has also
yielded no `body.txt` — on a machine with poppler that means the PDF had no text layer or fell
under the 1,500-word floor; see `pdf-tool-missing.md` for the no-poppler case. Demonstrates
per-probe availability: `framing-drift-domain-transfer` runs and can fail on abstract evidence,
while the three probes whose locked expected-evidence section is Methods / Results / Experimental
Setup / System Design could not run and are recorded `unverifiable`.

The aggregate verdict is `fail` per
`../../citation-detail-verify/references/output-schema.md` §Verdict computation, because one
abstract-grounded `fail` row is present and `fail` dominates `unverifiable`. The fixture
carries a `fail`, a `pass` and six floored rows in one run so that all three dispositions
reachable in the `abstract-only` class are visible together, and so the §Why this is not a
`pass`-shaped run section below can contrast the aggregate against the drift-free variant.

## Invocation

```
/load-bearing-fullread --artifact content/rfc/0019-ground-agentic-loops-in-external-verification.md --source-ids A16,A11
```

The skill emits `parsed-source-id-list`: `["A16", "A11"]` — the canonical comma-split of
`--source-ids`.

## Artifact under probe (excerpt)

> §3 — Rule 2. Separate the generator from the judge. Evidence-aware reward shaping plus
> self-correcting preference learning is the general remedy for a loop that lacks an explicit
> self-improving mechanism [A16]. Repository-grounded rubric checklists stand in for execution
> wherever running the code is too costly [A11].

## Resolution and availability

Both identifiers match `sources[]` entries declaring `aclanthology.org` landing-page URLs.
Neither is upgraded (no arXiv `/abs/` form), both landing pages fetch 200, and neither DOI
yields a live `arxiv.org/html` mirror through the full-text mirror hop. Both bodies classify
`abstract-only`; `check-detail` records the routes attempted on every floored row.

## Source A16 — domain-transfer drift, grounded in the abstract

- citation-id: `[A16]`
- source-url: `https://aclanthology.org/2026.acl-long.1718/`
- availability: `abstract-only`

The abstract names its measurement domain explicitly, and the artifact applies the finding as a
domain-general remedy without flagging the transfer. The abstract is a grounding section
`../references/probe-templates.md` §Template: framing-drift-domain-transfer lists, so the probe
runs and fails on primary-source evidence:

| Row field | Value |
|-----------|-------|
| `citation-id` | `[A16]` |
| `check-name` | `framing-drift-domain-transfer` |
| `status` | `fail` |
| `cited-value` | `"evidence-aware reward shaping plus self-correcting preference learning is the general remedy for a loop lacking an explicit self-improving mechanism"` |
| `actual-value` | `"measured on radiology report generation; the reward signal is evidence-grounded against radiology findings, and no cross-domain result is reported"` |
| `evidence-quote` | `"Enhancing Reinforcement Learning for Radiology Report Generation with Evidence-aware Rewards and Self-correcting Preference Learning"` |
| `source-url` | `https://aclanthology.org/2026.acl-long.1718/` |
| `check-detail` | `{"availability": "abstract-only", "routes-attempted": ["landing-page", "citation_pdf_url", "doi->semantic-scholar->arxiv-html"]}` |

The three remaining probes for `[A16]` could not run and are recorded `unverifiable`, each with
`cited-value` holding the artifact's framing, `actual-value` the empty string `""` (derivation
could not run, permitted on `unverifiable` rows per
`../../citation-detail-verify/references/output-schema.md` §Required row fields),
`evidence-quote` the empty string `""`, and `check-detail` naming the missing section:

| `check-name` | `status` | `check-detail` |
|--------------|----------|----------------|
| `framing-drift-relative-vs-absolute` | `unverifiable` | `{"availability": "abstract-only", "required-section": "Methods or Results", "routes-attempted": ["landing-page", "citation_pdf_url", "doi->semantic-scholar->arxiv-html"]}` |
| `framing-drift-flow-direction` | `unverifiable` | `{"availability": "abstract-only", "required-section": "Methods or System Design", "routes-attempted": ["landing-page", "citation_pdf_url", "doi->semantic-scholar->arxiv-html"]}` |
| `framing-drift-scope-mismatch` | `unverifiable` | `{"availability": "abstract-only", "required-section": "Methods or Experimental Setup", "routes-attempted": ["landing-page", "citation_pdf_url", "doi->semantic-scholar->arxiv-html"]}` |

## Source A11 — domain-transfer survives, three probes floored

- citation-id: `[A11]`
- source-url: `https://aclanthology.org/2026.acl-long.697/`
- availability: `abstract-only`

The abstract names software-engineering agents and repository-grounded rubrics, which is the
domain the artifact applies the finding to. `framing-drift-domain-transfer` runs and passes:

| Row field | Value |
|-----------|-------|
| `citation-id` | `[A11]` |
| `check-name` | `framing-drift-domain-transfer` |
| `status` | `pass` |
| `cited-value` | `"repository-grounded rubric checklists substitute for execution where running the code is too costly"` |
| `actual-value` | `"measured on SWE agents with repository-grounded rubric checklists proposed where code execution is too costly to scale — same domain as the artifact's use"` |
| `evidence-quote` | `""` |
| `source-url` | `https://aclanthology.org/2026.acl-long.697/` |
| `check-detail` | `{"availability": "abstract-only", "routes-attempted": ["landing-page", "citation_pdf_url", "doi->semantic-scholar->arxiv-html"]}` |

`evidence-quote` is empty on this `pass` row, which
`../../citation-detail-verify/references/output-schema.md` §Required row fields permits for a
`pass` ("For `pass` rows the quote MAY be empty"). The `fail` row above carries a non-empty
verbatim quote, as the same section requires of every `fail` row regardless of skill class.

`[A11]`'s three remaining probes are `unverifiable` on the same per-probe availability grounds,
with the same `check-detail` shape as `[A16]`'s.

## Emitted envelope (excerpt)

```json
{
  "version": "1.0",
  "skill": "load-bearing-fullread",
  "artifact": "/Users/wyatt.rupp/dx-arch-meta/repos/research-docs/content/rfc/0019-ground-agentic-loops-in-external-verification.md",
  "invoked_at": "2026-09-04T18:22:07Z",
  "verdict": "fail",
  "cache": { "hits": 0, "misses": 2, "writes": 2 },
  "rows": [
    {
      "citation-id": "[A16]",
      "check-name": "framing-drift-domain-transfer",
      "status": "fail",
      "cited-value": "evidence-aware reward shaping plus self-correcting preference learning is the general remedy for a loop lacking an explicit self-improving mechanism",
      "actual-value": "measured on radiology report generation; the reward signal is evidence-grounded against radiology findings, and no cross-domain result is reported",
      "evidence-quote": "Enhancing Reinforcement Learning for Radiology Report Generation with Evidence-aware Rewards and Self-correcting Preference Learning",
      "source-url": "https://aclanthology.org/2026.acl-long.1718/",
      "check-detail": { "availability": "abstract-only", "routes-attempted": ["landing-page", "citation_pdf_url", "doi->semantic-scholar->arxiv-html"] }
    },
    {
      "citation-id": "[A16]",
      "check-name": "framing-drift-relative-vs-absolute",
      "status": "unverifiable",
      "cited-value": "evidence-aware reward shaping plus self-correcting preference learning is the general remedy for a loop lacking an explicit self-improving mechanism",
      "actual-value": "",
      "evidence-quote": "",
      "source-url": "https://aclanthology.org/2026.acl-long.1718/",
      "check-detail": { "availability": "abstract-only", "required-section": "Methods or Results", "routes-attempted": ["landing-page", "citation_pdf_url", "doi->semantic-scholar->arxiv-html"] }
    },
    {
      "citation-id": "[A16]",
      "check-name": "framing-drift-flow-direction",
      "status": "unverifiable",
      "cited-value": "evidence-aware reward shaping plus self-correcting preference learning is the general remedy for a loop lacking an explicit self-improving mechanism",
      "actual-value": "",
      "evidence-quote": "",
      "source-url": "https://aclanthology.org/2026.acl-long.1718/",
      "check-detail": { "availability": "abstract-only", "required-section": "Methods or System Design", "routes-attempted": ["landing-page", "citation_pdf_url", "doi->semantic-scholar->arxiv-html"] }
    },
    {
      "citation-id": "[A16]",
      "check-name": "framing-drift-scope-mismatch",
      "status": "unverifiable",
      "cited-value": "evidence-aware reward shaping plus self-correcting preference learning is the general remedy for a loop lacking an explicit self-improving mechanism",
      "actual-value": "",
      "evidence-quote": "",
      "source-url": "https://aclanthology.org/2026.acl-long.1718/",
      "check-detail": { "availability": "abstract-only", "required-section": "Methods or Experimental Setup", "routes-attempted": ["landing-page", "citation_pdf_url", "doi->semantic-scholar->arxiv-html"] }
    },
    {
      "citation-id": "[A11]",
      "check-name": "framing-drift-domain-transfer",
      "status": "pass",
      "cited-value": "repository-grounded rubric checklists substitute for execution where running the code is too costly",
      "actual-value": "measured on SWE agents with repository-grounded rubric checklists proposed where code execution is too costly to scale — same domain as the artifact's use",
      "evidence-quote": "",
      "source-url": "https://aclanthology.org/2026.acl-long.697/",
      "check-detail": { "availability": "abstract-only", "routes-attempted": ["landing-page", "citation_pdf_url", "doi->semantic-scholar->arxiv-html"] }
    },
    {
      "citation-id": "[A11]",
      "check-name": "framing-drift-relative-vs-absolute",
      "status": "unverifiable",
      "cited-value": "repository-grounded rubric checklists substitute for execution where running the code is too costly",
      "actual-value": "",
      "evidence-quote": "",
      "source-url": "https://aclanthology.org/2026.acl-long.697/",
      "check-detail": { "availability": "abstract-only", "required-section": "Methods or Results", "routes-attempted": ["landing-page", "citation_pdf_url", "doi->semantic-scholar->arxiv-html"] }
    },
    {
      "citation-id": "[A11]",
      "check-name": "framing-drift-flow-direction",
      "status": "unverifiable",
      "cited-value": "repository-grounded rubric checklists substitute for execution where running the code is too costly",
      "actual-value": "",
      "evidence-quote": "",
      "source-url": "https://aclanthology.org/2026.acl-long.697/",
      "check-detail": { "availability": "abstract-only", "required-section": "Methods or System Design", "routes-attempted": ["landing-page", "citation_pdf_url", "doi->semantic-scholar->arxiv-html"] }
    },
    {
      "citation-id": "[A11]",
      "check-name": "framing-drift-scope-mismatch",
      "status": "unverifiable",
      "cited-value": "repository-grounded rubric checklists substitute for execution where running the code is too costly",
      "actual-value": "",
      "evidence-quote": "",
      "source-url": "https://aclanthology.org/2026.acl-long.697/",
      "check-detail": { "availability": "abstract-only", "required-section": "Methods or Experimental Setup", "routes-attempted": ["landing-page", "citation_pdf_url", "doi->semantic-scholar->arxiv-html"] }
    }
  ]
}
```

All eight rows populate the six required fields of
`../../citation-detail-verify/references/output-schema.md` §Row shape. Empty strings are the
literal `""`, never `null` or omitted, per §Required row fields.

## Why this is not a `pass`-shaped run

Eight rows: one `fail`, one `pass`, six `unverifiable`. A `fail` is present, so the aggregate is
`verdict: fail` per §Verdict computation — `fail` dominates `unverifiable`. Drop the `[A16]`
drift and the run becomes `verdict: unverifiable`, never `pass`, because six probes remain
un-run. That is the distinction the availability classes exist to preserve: an
`abstract-only` source that surfaces no drift has been *probed and floored*, not *cleared*, and
collapsing the two would let abstract-survived framing drift through the gate unremarked.
