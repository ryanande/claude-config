# Failure-mode checklist

Use during Q2 ("what could the session have done better?"). Faster and more honest than freeform critique — ask "did any of these happen?" and cite the moment if yes.

- **Flailing on the same problem** — same file re-read, same approach retried with no new information.
- **Scope creep** — work expanded beyond the stated task without an explicit decision.
- **Context loss mid-session** — repeated questions or assumptions that contradicted earlier decisions.
- **Hallucinated API or file path** — referenced something that didn't exist; cost time before discovery.
- **Premature optimization** — abstraction or generalization before the second concrete use case.
- **Rubber-stamped gate** — a checkpoint passed without genuine evaluation (e.g., "looks good" without reading).
- **Premature "looks good"** — declared done before verification.
- **Abandoned approach without recorded alternatives** — tried X, dropped it, didn't write down what was tried or why.
- **Missing CI / pre-commit / quality gate** — a regression-catching mechanism that should have existed and didn't.
- **Mid-session document drift** — a runbook, plan file, or README that should have been updated as the work happened, but wasn't.
- **Wiring without integration test** — a CLI command, orchestration step, or hook landed without a test that exercises it end-to-end.
- **Single-giant-commit cadence** — work that should have been logical checkpoints landed as one opaque commit.
