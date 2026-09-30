# Question prompts and tagging rules

Eight questions. Hard cap of 3 bullets per question per category (process / technical). If more, list "what got cut and why" — visible cuts beat invisible padding.

## Tag every bullet

- `(cited:<ref>)` — traces to a specific commit, tool call, or message — OR `(inferred)` — reasonable pattern-match without citation. Don't invent confidence.
- Strength `1`-`5` (1 = single weak cite; 5 = pattern across many cites). Grades strength among cited items.
  - 1: single weak cite
  - 2: single strong cite
  - 3: 2-3 cites or 1 strong cite + corroborating pattern
  - 4: pattern across 3+ cites
  - 5: pattern across many cites, multiple session phases
- `[process]` (collaboration, gates, prompting, tool friction, skill instructions) or `[technical]` (codebase discoveries, schema quirks, fixtures, API shapes). Process routes to skill edits/runbooks; technical routes to passports/fixtures/code comments.
- Audience override (e.g. `→skill-author`) only if different from retro's primary audience.
- If the session chained multiple skills, tag the responsible skill: `[skill:speckit-plan]`, `[skill:dev]`. "Session" framing diffuses ownership.

## Q1: What got lost or undercovered?

Things measured / discovered / decided during the session but not committed anywhere. Corpus stats, perf timings, reverse-engineered API shapes, ADF samples, implicit decisions, mysteries flagged-but-not-investigated, rejected approaches without recorded rationale. Commit messages decide what counts as "documented" — if it's in `git log`, don't list here.

## Q2: What could the session have done better?

Self-critique. See [`failure-mode-checklist.md`](failure-mode-checklist.md) — run through it before freeform critique.

## Q3: What surprised me?

Things that didn't fit your model. Tool returned unexpected shape; test passed for the wrong reason; gate fired (or didn't) when you expected the opposite; refactor turned out larger/smaller than estimated. Surprises are diagnostic gold and don't fit cleanly under wins or critiques — often the seed of the next failure-mode entry.

## Q4: Negative space — what didn't happen that should have?

The session log only shows what *did* happen. Ask: what gate / test / review didn't fire that you'd expect on this kind of work? What alternatives did you deliberately reject, and is the rationale captured anywhere? "We forgot the security review" and "we chose to skip it because X" look identical in the transcript and matter very differently for the next agent.

## Q5: Pivots and abandoned hypotheses

List mid-session pivots (test strategy switch, abandoned approach, scope change) and the trigger that caused each. Single richest source of learning, and the bullets the LLM most aggressively smooths away if not asked for explicitly. Empty list is acceptable but only if you're sure — re-scan first.

## Q6: What worked and should be preserved?

Concrete only. "Good communication" is not a bullet; "asking for the spec file path in the opening message" is. Without this question, the next agent can't learn what to keep doing — and skill edits drift toward fixing what's broken while degrading what's not.

## Q7: Context-window pressure

Score Low / Moderate / High / Critical. What consumed the most context? Did pressure force shortcuts? Earliest signal that the workflow needs to be split across sessions.

## Q8: Counterfactual — first 5 minutes

If you restarted now with everything you've learned, what would you do in the first 5 minutes? Forces structural lessons rather than tactical ones.
