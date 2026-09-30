#!/usr/bin/env bash
# PR Intelligence — local runner
#
# Composes prompt + config + lens, invokes Claude Code, writes the digest to
# digests/pr-intelligence/YYYY-MM-DD.md.
#
# Usage:
#   ./routines/pr-intelligence/runner.sh
#   ./routines/pr-intelligence/runner.sh --date 2026-05-06     # backfill
#   ./routines/pr-intelligence/runner.sh --dry-run             # print prompt, don't run

set -euo pipefail

ROUTINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${ROUTINE_DIR}/../.." && pwd)"

DATE="$(date +%Y-%m-%d)"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --date)    DATE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
done

OUT_DIR="${REPO_ROOT}/digests/pr-intelligence"
OUT_FILE="${OUT_DIR}/${DATE}.md"
mkdir -p "${OUT_DIR}"

PROMPT="${ROUTINE_DIR}/prompt.md"
CONFIG="${ROUTINE_DIR}/config.yaml"
LENS="${REPO_ROOT}/architectural-lens.md"

for f in "${PROMPT}" "${CONFIG}" "${LENS}"; do
  [[ -f "${f}" ]] || { echo "missing: ${f}" >&2; exit 1; }
done

# Monday: extend window to cover the weekend.
WEEKDAY="$(date -u +%u)"   # 1=Mon … 7=Sun
WINDOW_HOURS="$(awk '/^window_hours:/ {print $2}' "${CONFIG}")"
[[ "${WEEKDAY}" == "1" ]] && WINDOW_HOURS=72

COMPOSED="$(mktemp)"
trap 'rm -f "${COMPOSED}"' EXIT

{
  echo "# Run context"
  echo
  echo "- Date: ${DATE}"
  echo "- Window hours: ${WINDOW_HOURS}"
  echo
  echo "---"
  echo
  cat "${LENS}"
  echo
  echo "---"
  echo
  echo "# Config"
  echo
  echo '```yaml'
  cat "${CONFIG}"
  echo '```'
  echo
  echo "---"
  echo
  cat "${PROMPT}"
} > "${COMPOSED}"

if [[ "${DRY_RUN}" == "1" ]]; then
  cat "${COMPOSED}"
  exit 0
fi

# Invoke Claude Code in headless / print mode.
# Requires `claude` CLI on PATH. The agent uses MCP servers configured in
# ~/.claude.json (GitHub, Atlassian, etc.) — no per-routine MCP wiring needed.
claude --print < "${COMPOSED}" > "${OUT_FILE}"

echo "Wrote ${OUT_FILE}"
