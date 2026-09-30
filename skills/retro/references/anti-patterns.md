# LLM retro anti-patterns

LLMs writing retros default to three failure modes. The retro workflow must resist all three.

## 1. Sycophantic narrative

"Everything went great." If your draft has fewer than two honest critiques of the session's own approach, you haven't tried hard enough. Re-read the session looking for: things discovered late that you should have known earlier, code paths committed without tests, docs not updated, patterns you'd object to in code review.

## 2. Hallucinated coherence

LLMs smooth a session into a tidy arc. Force yourself to list 1-2 contradictions, dead ends, or abandoned hypotheses verbatim — the messiness holds the most learning. Q5 (pivots) enforces this explicitly.

## 3. Recency bias

Findings cluster in the last 20% of the transcript because that's freshest. **Require at least one finding (across Q1-Q5) sourced from the first third of the session.** Early-decision drag — a wrong tool chosen at minute 5 that costs 40 minutes at minute 50 — is usually the highest-leverage lesson.

## Honesty over politeness

A retro that says "all good" wasted everyone's time. If the session was actually clean (small fix, tests added, one commit), say so explicitly and stop early — don't manufacture critiques.
