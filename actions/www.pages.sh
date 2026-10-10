#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

if [[ -z "${SOURCE_SHA:-}" ]]; then
  SOURCE_SHA="$(git rev-parse HEAD 2>/dev/null || printf '%040d' 0)"
fi
export SOURCE_SHA
export RELEASE_VERSION="${RELEASE_VERSION:-0.0.4}"
export PUBLISH_DIR="${PUBLISH_DIR:-static}"

printf '[www.pages] source: %s\n' "${SOURCE_SHA}"
printf '[www.pages] release: %s\n' "${RELEASE_VERSION}"
python3 actions/build_pages.py
