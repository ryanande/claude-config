---
fixture: full-text-unsectioned
exercises: framing-drift-relative-vs-absolute, framing-drift-domain-transfer, framing-drift-flow-direction, framing-drift-scope-mismatch, output-row-with-all-required-fields
expected-verdict: pass
---

# Fixture — full-text-unsectioned

A source whose landing page is `abstract-only`, whose §Full-text mirror hop finds no arXiv HTML
(`2026.acl-long.406` → `2510.18619` returns 404), and whose PDF extracts under cache-contract
v1.4 to a `body.txt` of 7,614 words. Per `../references/source-resolution.md` §Full-text
availability classification the body is read via `body.txt`, so it classifies
`full-text-unsectioned` regardless of the heading words it contains, and all four probes run
over the whole body.

## Invocation

```
/load-bearing-fullread --artifact content/survey/iterative-self-correction-conditions-in-agent-loops.md --source-ids A10
```

## Resolution and fetch

1. `A10` matches the frontmatter `sources:` entry with `url: https://aclanthology.org/2026.acl-long.406/`.
2. Landing page fetch → `200`, title + abstract, no body sections → `abstract-only` pending the hop.
3. Mirror hop: DOI `10.18653/v1/2026.acl-long.406` → Semantic Scholar `externalIds.ArXiv: 2510.18619` → `https://arxiv.org/html/2510.18619` → `404`.
4. PDF route: `https://aclanthology.org/2026.acl-long.406.pdf` → `200 application/pdf` → miss-path write runs `pdf_extract.py extract` → `body.txt`, `meta.json.extracted_text: {"tool":"pdftotext","status":"ok","words":7614,"version":"norm-v1"}`.
5. `body.txt` present, 7,614 > 1,500 → `full-text-unsectioned`.

## Rows

Four rows, one per template, each with `source-url: https://aclanthology.org/2026.acl-long.406.pdf` and
`check-detail: {"section": "unsectioned", "route": "pdf-extract"}`. In this fixture all four are `pass`:
the artifact frames [A10] as a tree-search policy that backtracks on explicit bounding-box evidence,
and the body's Method and Experiments text supports that framing on all four axes.

```json
{"citation-id": "[A10]", "check-name": "framing-drift-domain-transfer", "status": "pass",
 "cited-value": "multimodal reasoning with self-verification grounded in bounding-box evidence",
 "actual-value": "MLLM visual reasoning; hierarchical search with self-verification",
 "evidence-quote": "", "source-url": "https://aclanthology.org/2026.acl-long.406.pdf",
 "check-detail": {"section": "unsectioned", "route": "pdf-extract"}}
```

## Why this is not an `abstract-only` run

Under v1.3 the same source floored three rows `unverifiable`. The only difference is which file of
the cache entry is read. A `fail` row here would carry a verbatim `evidence-quote` from `body.txt`,
matched under the `norm-v1` key, so a hyphen-split span in the PDF still grounds it.
