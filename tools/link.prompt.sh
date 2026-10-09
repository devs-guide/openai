#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LINK_PATH="${ROOT}/dot/prompt"
TARGET_PATH="${ROOT}/../prompts/openai/dot"
RELATIVE_TARGET='../../prompts/openai/dot'
MODE="${1:---check}"

fail() {
  printf '[link.prompt][error] %s\n' "$*" >&2
  exit 1
}

case "${MODE}" in
  --check|--create) ;;
  *) fail "usage: $0 [--check|--create]" ;;
esac

git -C "${ROOT}" check-ignore -q dot/prompt || fail "dot/prompt is not ignored"
[[ -d "${TARGET_PATH}" ]] || fail "private prompt workspace not found: ${TARGET_PATH}"

if [[ -L "${LINK_PATH}" ]]; then
  [[ "$(readlink "${LINK_PATH}")" == "${RELATIVE_TARGET}" ]] || \
    fail "dot/prompt points somewhere unexpected"
  printf '[link.prompt][ok] dot/prompt -> %s\n' "${RELATIVE_TARGET}"
  exit 0
fi

[[ ! -e "${LINK_PATH}" ]] || fail "dot/prompt exists and is not a symlink"
if [[ "${MODE}" == "--check" ]]; then
  fail "dot/prompt is not linked; run $0 --create"
fi

ln -s "${RELATIVE_TARGET}" "${LINK_PATH}"
printf '[link.prompt][ok] created dot/prompt -> %s\n' "${RELATIVE_TARGET}"
