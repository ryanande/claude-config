# CLAUDE.md

## Passport
- **Identity:** Ryan's personal Claude Code configuration for the PrePass Chief Architect role: user-invocable skills and three weekday digest routines (PR intelligence, meeting rundown, chat surveillance).
- **Owns:** `skills/` (deployed by symlinking each into `~/.claude/skills/<name>`); `routines/` (prompt, config, runner per routine); `architectural-lens.md`; the `digests/` archive.
- **Does not own:** any notlost infrastructure or product (`home-assistant`, `notlost-k3s-containers`, `notlost-libre`, `nomadrules`). It is PrePass-role tooling that sits in this ecosystem map only because it is the same owner's config.
- **Depends on / depended on by:** external only: GitHub, Microsoft Teams, Claude Code. No notlost repo depends on it.
- **Deploys to / runs on:** the local Claude Code install (`~/.claude/skills/` symlinks); routines run on a weekday schedule, with GitHub Actions cron as stubs.
- **Entry points:** `README.md`; `architectural-lens.md`; `skills/<name>/`; `routines/<name>/` (`prompt.md`, `config.yaml`, `runner.sh`).
- **Hard rules:** each routine keeps the prompt + config + runner shape; digests are written to `digests/<routine>/YYYY-MM-DD.md`; skills are consumed via symlink, so edit them here, not under `~/.claude/skills/`.
- **Docs:** `README.md`, `docs/`.
