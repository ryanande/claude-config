---
fixture: pdf-tool-missing
exercises: framing-drift-domain-transfer, output-row-with-all-required-fields, unverifiable-names-attempted-routes
expected-verdict: unverifiable
---

# Fixture — pdf-tool-missing

The same source as `full-text-unsectioned.md` on a machine without poppler. The PDF is fetched and
stored as `body`; `pdf_extract.py extract` returns `{"status": "tool-missing", "words": 0}`; no
`body.txt` is written. Per cache-contract v1.4 §Read protocol the entry is unextracted, so the
source stays `abstract-only` and is probed to the extent the landing-page abstract permits.

## Rows

`framing-drift-domain-transfer` runs against the landing-page abstract and, in this fixture, is `pass`
— the abstract names multimodal visual reasoning as the domain, which is the framing the artifact
uses. The other three probes emit `unverifiable`. Verdict per
`../../citation-detail-verify/references/output-schema.md` §Verdict computation: no `fail` row, at
least one `unverifiable` row → `unverifiable`.

```json
{"citation-id": "[A10]", "check-name": "framing-drift-domain-transfer", "status": "pass",
 "cited-value": "multimodal reasoning with self-verification grounded in bounding-box evidence",
 "actual-value": "MLLM visual reasoning; hierarchical search with self-verification",
 "evidence-quote": "", "source-url": "https://aclanthology.org/2026.acl-long.406/",
 "check-detail": {"availability": "abstract-only", "route": "landing-page"}}
```

One of the three floored rows:

```json
{"citation-id": "[A10]", "check-name": "framing-drift-relative-vs-absolute", "status": "unverifiable",
 "cited-value": "", "actual-value": "<source-body-unextracted>", "evidence-quote": "",
 "source-url": "https://aclanthology.org/2026.acl-long.406.pdf",
 "check-detail": {"availability": "abstract-only", "route": "pdf-extract", "reason": "pdftotext-not-on-PATH",
                  "routes-attempted": ["landing-page", "arxiv-html-mirror:404", "pdf-extract:tool-missing"]}}
```

## Why this is the intended outcome

This is the pre-v1.4 terminal state with a named cause. The fix is `brew install poppler`, not a
skill change; the row says so.
