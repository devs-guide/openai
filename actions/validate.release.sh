#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${RELEASE_VERSION:-0.0.4}"
NOTES="${ROOT}/docs/releases/${VERSION}.md"

fail() {
  printf '[validate.release][error] %s\n' "$*" >&2
  exit 1
}

[[ "${VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || fail "version must be a bare semantic version"
[[ -s "${NOTES}" ]] || fail "release notes are missing: docs/releases/${VERSION}.md"
grep -Fqx "## ${VERSION}" "${NOTES}" || fail "release notes must begin with ## ${VERSION}"

for heading in \
  '### Scope' \
  '### Highlights' \
  '### Added' \
  '### Changed' \
  '### Fixed' \
  '### #COMMIT' \
  '### Notable commits' \
  '### Assets'; do
  grep -Fqx "${heading}" "${NOTES}" || fail "release notes lack heading: ${heading}"
done

if grep -Eqi '(^|[^[:alnum:]])(TBD|TODO|PLACEHOLDER)([^[:alnum:]]|$)|`0000000`' "${NOTES}"; then
  fail "release notes contain an unresolved placeholder"
fi

grep -Fq 'GitHub-generated source archives' "${NOTES}" || fail "source archives are not declared"
grep -Fq 'No additional binary assets' "${NOTES}" || fail "binary asset policy is not declared"
grep -Fq "release: ${VERSION} - " "${NOTES}" || fail "chosen release commit message is missing"

cd "${ROOT}"
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  git diff --check HEAD
fi
if git ls-files | grep -Eq '^(static/|dot/prompt(?:/|$)|dot/dot\.master\.00\.prompt$)'; then
  fail "generated, private, or duplicate paths are tracked"
fi

if [[ "${VERIFY_TAG:-0}" == "1" ]]; then
  git rev-parse --verify "refs/tags/${VERSION}^{tag}" >/dev/null || fail "annotated tag is missing: ${VERSION}"
  tag_commit="$(git rev-list -n 1 "${VERSION}")"
  expected_commit="${EXPECTED_RELEASE_SHA:-$(git rev-parse HEAD)}"
  [[ "${tag_commit}" == "${expected_commit}" ]] || \
    fail "tag ${VERSION} points to ${tag_commit}, expected ${expected_commit}"
fi

printf '[validate.release] %s release contracts passed\n' "${VERSION}"
