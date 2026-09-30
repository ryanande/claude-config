#!/usr/bin/env bash
# Chat Surveillance — local runner
#
# Composes prompt + config + lens, invokes Claude Code, writes the digest to
# digests/chat-surveillance/YYYY-MM-DD.md.
#
# Usage:
#   ./routines/chat-surveillance/runner.sh
#   ./routines/chat-surveillance/runner.sh --date 2026-05-06
#   ./routines/chat-surveillance/runner.sh --dry-run

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

OUT_DIR="${REPO_ROOT}/digests/chat-surveillance"
OUT_FILE="${OUT_DIR}/${DATE}.md"
mkdir -p "${OUT_DIR}"

PROMPT="${ROUTINE_DIR}/prompt.md"
CONFIG="${ROUTINE_DIR}/config.yaml"
LENS="${REPO_ROOT}/architectural-lens.md"

for f in "${PROMPT}" "${CONFIG}" "${LENS}"; do
  [[ -f "${f}" ]] || { echo "missing: ${f}" >&2; exit 1; }
done

WEEKDAY="$(date -u +%u)"
WINDOW_HOURS=24
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

claude --print < "${COMPOSED}" > "${OUT_FILE}"

echo "Wrote ${OUT_FILE}"
