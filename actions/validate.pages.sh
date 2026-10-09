#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
export STATIC_DIR="${STATIC_DIR:-static}"

python3 actions/validate_pages.py
