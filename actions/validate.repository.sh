#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

python3 actions/validate_repository.py

while IFS= read -r -d '' script; do
  bash -n "${script}"
done < <(find actions tools -type f -name '*.sh' -print0 | sort -z)
printf '[validate.repository][ok] shell entrypoints pass bash syntax validation\n'

if git rev-parse --verify HEAD >/dev/null 2>&1; then
  git diff --check HEAD
fi
printf '[validate.repository] source hygiene checks passed\n'
