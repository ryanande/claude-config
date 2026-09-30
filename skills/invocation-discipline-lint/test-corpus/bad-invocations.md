# Fixture: bad-invocations

At least 5 forbidden invocations of `/invocation-discipline-lint` itself — 3 bias + 2 bloat surfaces per the recursion-strictest §Invocation discipline. Each MUST produce one refusal record per `../citation-detail-verify/references/refusal-record.md`.

## 1 (bias) — caller's belief about whether the call signature passes

```
/invocation-discipline-lint --spec notes/x.md --call '...' "I'm confident this call signature passes — confirm it."
```
→ `emitted-refusal-record` (category `bias`): pre-determined verdict.

## 2 (bias) — pre-filtered violation category to check

```
/invocation-discipline-lint --spec notes/x.md --call '...' --only-check bloat
```
→ `emitted-refusal-record` (category `bias`): caller-directed focus invalidates the universal-pass guarantee.

## 3 (bias) — caller's interpretation of the call signature's intent

```
/invocation-discipline-lint --spec notes/x.md --call '...' "the caller really just means to refresh the cache, so be lenient."
```
→ `emitted-refusal-record` (category `bias`): intent is the spec's to declare, not the caller's.

## 4 (bloat) — attached spec body

```
/invocation-discipline-lint --spec-body "<<< 6000 chars of pasted SKILL.md >>>" --call '...'
```
→ `emitted-refusal-record` (category `bloat`): the lint reads §Invocation discipline from disk by spec path; a pasted body bypasses the content-key.

## 5 (bloat) — full call signature when only one knob is in question

```
/invocation-discipline-lint --spec notes/x.md --call '<<< entire 40-line worker payload >>>' --knob-in-question mode
```
→ `emitted-refusal-record` (category `bloat`): v0 lints whole-signature only; per-knob mode is a follow-on, so a single-knob question with a full-signature attachment is bloat.

## Refusal-record shape (each of the 5 above conforms)

```json
{
  "version": "1.0",
  "skill": "invocation-discipline-lint",
  "invoked_at": "2026-05-26T00:00:00Z",
  "refusal": {
    "category": "bias",
    "rule": "Caller's belief about whether the call signature passes.",
    "evidence": "\"I'm confident this call signature passes — confirm it.\""
  }
}
```

All five invocations are refused before any spec parse runs — the skill emits the refusal record (wire `"version": "1.0"`) and does not proceed. Total: 5 refusal records (`emitted-refusal-record` ×5).
