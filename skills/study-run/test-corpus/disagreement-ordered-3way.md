# Fixture: `ordered-3way` disagreement — noise-vs-unresolved is not symmetric with tiebreaks

## Study document under execution

`content/evals/eval-0031-precision-of-cold-run-labeling.md`, tamper guard
passed, `protocol.disagreement: ordered-3way` (`references/pre-registration.md`
§The protocol field). Four items, one A/B pair each, worked through
`recheck.disagree(a, b)` and, where it fires, `apply_tiebreak(x, t)`:

| Item | Labeler A | Labeler B | `disagree` result | Tiebreak (`haiku`) | Final |
|---|---|---|---|---|---|
| F-101 | REAL | NOISE | `UNRESOLVED`, no tiebreak | — | UNRESOLVED |
| F-102 | NOISE | UNRESOLVED | `NOISE`, tiebreak fires | NOISE | NOISE (tiebreak keeps NOISE) |
| F-103 | NOISE | UNRESOLVED | `NOISE`, tiebreak fires | REAL | UNRESOLVED (failed-tiebreak) |
| F-104 | UNRESOLVED | UNRESOLVED | `UNRESOLVED`, no tiebreak | — | UNRESOLVED |

## Expected skill output

- **F-101 (REAL/NOISE).** `disagree("REAL", "NOISE")` returns `("UNRESOLVED",
  False)` — a straight contradiction between the two labelers never gets a
  tiebreak spawn. This is the case the design rejects the permissive
  alternative for: a "NOISE with flag" convention would let the more
  permissive labeler win by default; `ordered-3way` refuses to pick a winner
  at all and lands UNRESOLVED with `unresolved_source: labeler-contradiction`.
- **F-102 (NOISE/UNRESOLVED, tiebreak NOISE).** `disagree("NOISE",
  "UNRESOLVED")` returns `("NOISE", True)` — a tiebreak spawn fires because
  one side is UNRESOLVED, not a contradiction. `apply_tiebreak("NOISE",
  "NOISE")` = `"NOISE"` since the tiebreak matches: the pre-tiebreak
  provisional value keeps. Final label: NOISE.
- **F-103 (NOISE/UNRESOLVED, tiebreak REAL).** Same `disagree` call as F-102,
  same provisional `"NOISE"`. But `apply_tiebreak("NOISE", "REAL")` =
  `"UNRESOLVED"` because the tiebreak does not match the provisional value —
  a *failed* tiebreak, distinct from F-101's no-tiebreak contradiction.
  `unresolved_source: failed-tiebreak`, not `labeler-contradiction`: the two
  reasons a two-item disagreement lands UNRESOLVED are structurally
  different (one never got a tiebreak spawn at all; the other got one and it
  disagreed too), and `recheck.unresolved_source`'s precedence keeps them
  distinguishable in the run record.
- **F-104 (UNRESOLVED/UNRESOLVED).** `disagree("UNRESOLVED", "UNRESOLVED")`
  returns `("UNRESOLVED", False)` per the pure function's first branch
  (`a == b`) — stays UNRESOLVED, no tiebreak spawn, `unresolved_source:
  both-unresolved`.

Token for this distinction: `noise-vs-unresolved-tiebreaks`.

## Invariants exercised

- A straight REAL/NOISE contradiction (F-101) and a failed tiebreak after a
  NOISE/UNRESOLVED disagreement (F-103) both end at UNRESOLVED, but carry
  different `unresolved_source` values — the run record does not collapse
  them into one bucket.
- A tiebreak spawn fires only when exactly one side is UNRESOLVED
  (`{a, b} != {"REAL", "NOISE"}` and `"UNRESOLVED" in {a, b}`), never on a
  straight contradiction and never when both sides already agree.
- `apply_tiebreak` is not "majority wins" — it is "the tiebreak must match
  the non-UNRESOLVED provisional value, else UNRESOLVED," so a tiebreak can
  make an item *less* resolved than before it ran (F-103), never more
  resolved than the non-UNRESOLVED side already was.
- Two labelers already agreeing (neither F-101 through F-104 shows this case)
  never reaches `disagree` at all — the function is called only when A != B.
