#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPECTED_SOURCE_SHA="${EXPECTED_SOURCE_SHA:-}"
BASE_URL="${PAGES_BASE_URL:-https://devs-guide.github.io/openai}"
ATTEMPTS="${REMOTE_ATTEMPTS:-12}"
DELAY_SECONDS="${REMOTE_DELAY_SECONDS:-15}"

fail() {
  printf '[validate.pages.remote][error] %s\n' "$*" >&2
  exit 1
}

[[ "${EXPECTED_SOURCE_SHA}" =~ ^[0-9a-f]{40}$ ]] || \
  fail "EXPECTED_SOURCE_SHA must be a lowercase full commit SHA"
[[ "${ATTEMPTS}" =~ ^[1-9][0-9]*$ ]] || fail "REMOTE_ATTEMPTS must be positive"
[[ "${DELAY_SECONDS}" =~ ^[0-9]+$ ]] || fail "REMOTE_DELAY_SECONDS must be numeric"

check_live() {
  local source_json=""
  source_json="$(curl -fsS "${BASE_URL}/source.json")" || return 1
  SOURCE_JSON="${source_json}" python3 - "${EXPECTED_SOURCE_SHA}" <<'PY'
import json
import os
import sys

record = json.loads(os.environ["SOURCE_JSON"])
expected = sys.argv[1]
if record.get("repository") != "devs-guide/openai":
    raise SystemExit("unexpected repository identity")
if record.get("source_sha") != expected:
    raise SystemExit(f"live source is {record.get('source_sha')}, expected {expected}")
PY

  local route=""
  for route in \
    '/' \
    '/dot/' \
    '/dot/prompts/core/master/' \
    '/dot/agents/browser/' \
    '/dot/history/initial-import/' \
    '/dot/releases/0.0.1/' \
    '/raw/dot/prompts/core/master.prompt'; do
    curl -fsS -o /dev/null "${BASE_URL}${route}" || return 1
  done

  local raw_file=""
  raw_file="$(mktemp)"
  if ! curl -fsS "${BASE_URL}/raw/dot/prompts/core/master.prompt" -o "${raw_file}"; then
    rm -f "${raw_file}"
    return 1
  fi
  if ! cmp -s "${ROOT}/dot/prompts/core/master.prompt" "${raw_file}"; then
    rm -f "${raw_file}"
    return 1
  fi
  rm -f "${raw_file}"
}

attempt=1
while (( attempt <= ATTEMPTS )); do
  printf '[validate.pages.remote] attempt %s/%s\n' "${attempt}" "${ATTEMPTS}"
  if check_live; then
    printf '[validate.pages.remote] live Pages matches %s\n' "${EXPECTED_SOURCE_SHA}"
    exit 0
  fi
  if (( attempt == ATTEMPTS )); then
    fail "live Pages did not converge to ${EXPECTED_SOURCE_SHA}"
  fi
  sleep "${DELAY_SECONDS}"
  attempt=$((attempt + 1))
done
