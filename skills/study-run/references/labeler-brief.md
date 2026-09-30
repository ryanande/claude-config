# study-run — labeler brief (template)

Slot list: `{{PAYLOAD}}`, `{{REPOPATH}}`, `{{TYPE}}`, `{{STATUS}}`, `{{RULE}}`,
`{{SCOPE}}`, `{{PACK}}`, plus `{{STUDYPATH}}` (the study document's own path,
generalising the EVAL-0003 template's hard-coded document name). Rendered
copies land under `assets/evals/<id>/briefs/`.
Used for the labeler A / labeler B / tiebreak slots (`adjudication-mechanics.md`
§Slots) — the tiebreak spawn receives the same rendered brief as A and B.

Schema note: the design's evidence entry `{path, quote, what}` gains a fourth
field, `remote`, required because the gate resolves the path in the
repository the entry names (multi-repo scope) — a plan-introduced extension
of the design's schema, not a founding-design field.

Per-design slot substitution: `{{TYPE}}` and `{{STATUS}}` come from a corpus
item's frontmatter under D1, which D2 and D3 items do not have. D2 renders
`{{TYPE}}` as the candidate manifest row's defect class and `{{STATUS}}` as
`planted` or `clean-control`; D3 renders `{{TYPE}}` as the enrolled artifact's
kind and `{{STATUS}}` as `merged`. `{{RULE}}` carries `match-rule` under D2 and
`outcome.measure` under D3, and `{{TYPE}}`'s value in the rule-set lookup is the
literal `"*"` — see `adjudication-mechanics.md` §The wildcard rule set.

---

You are a cold-run labeler for one item in a pre-registered study. You label
exactly ONE item and return a JSON verdict. You have no knowledge of other
items and must not look for them.

## Rules of engagement
- READ-ONLY. Do not edit, create, or delete any file. Do not run any git
  command that changes state (no checkout, stash, commit, reset, branch).
  Allowed: `git ls-files`, `git show <sha>:<path>`, `git grep`, `cat`, `grep`,
  `find`, `ls`, Read, Grep, Glob.
- Confine ALL evidence to the pinned trees listed under `{{SCOPE}}` (one
  `remote path sha` per line). Cite evidence as `{remote, path, quote, what}`
  where `quote` is a verbatim span from that file at that SHA — a citation
  whose quote does not grep fails mechanically and lands UNRESOLVED.
- Do NOT look up the item's history, authoring date, or age (`git log`,
  `git blame`, frontmatter dates). Age is irrelevant to the label by rule and
  is deliberately withheld.
- Do NOT read the study document itself or any `*.candidates.jsonl`.

## The item

The item under review is a snapshot taken at an earlier commit, stored at:
`{{PAYLOAD}}`

Its repo-relative path is `{{REPOPATH}}`. Its type is `{{TYPE}}` and its
frontmatter status is `{{STATUS}}`. This is one item from the study document
at `{{STUDYPATH}}`.

Read the snapshot in full first. Then check the pinned trees under `{{SCOPE}}`
for the evidence the rule below asks about.

## Label rule

Apply the ONE clause matching the type:

`{{RULE}}`

Return UNRESOLVED when you cannot tell from the pinned trees alone. UNRESOLVED
is a legitimate answer; do not guess.

## Where to start (not where to stop)

`{{PACK}}`

## Output — return ONLY this JSON, nothing else

```json
{
  "label": "REAL | NOISE | UNRESOLVED",
  "clause": "<the clause text you applied, verbatim>",
  "evidence": [{"remote": "<url>", "path": "<repo-relative>", "quote": "<verbatim span>", "what": "<why it bears on the label>"}],
  "unresolved_reason": "out-of-scope | insufficient-evidence | contradiction | null",
  "out_of_scope_identities": ["<repo or location you would have needed>"],
  "rationale": "<3-8 sentences>",
  "checked_but_absent": ["<what you looked for and did not find>"],
  "model": "<your model id as you know it, or unknown>"
}
```

No expected-label slot anywhere in this brief.
