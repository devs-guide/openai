#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${RELEASE_VERSION:-}"
SOURCE_SHA="${SOURCE_SHA:-}"
MODE="${RELEASE_MODE:-}"
CONFIRMATION="${RELEASE_CONFIRMATION:-}"
REPOSITORY="${GITHUB_REPOSITORY:-devs-guide/openai}"
NOTES="${ROOT}/docs/releases/${VERSION}.md"
TITLE="${VERSION} — DOT Research Prompt System"

fail() {
  printf '[release][error] %s\n' "$*" >&2
  exit 1
}

[[ "${VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || fail "invalid bare semantic version"
[[ "${SOURCE_SHA}" =~ ^[0-9a-f]{40}$ ]] || fail "SOURCE_SHA must be a lowercase full commit SHA"
[[ "${MODE}" == "draft" || "${MODE}" == "publish" ]] || fail "RELEASE_MODE must be draft or publish"
[[ "${CONFIRMATION}" == "release ${VERSION}@${SOURCE_SHA} ${MODE}" ]] || fail "release confirmation does not match"
[[ -s "${NOTES}" ]] || fail "reviewed release notes are missing"

cd "${ROOT}"
[[ "$(git rev-parse HEAD)" == "${SOURCE_SHA}" ]] || fail "checkout does not match SOURCE_SHA"
remote_main="$(git ls-remote --exit-code --heads origin refs/heads/main | awk 'NR == 1 {print $1}')"
[[ "${remote_main}" == "${SOURCE_SHA}" ]] || fail "main is ${remote_main:-missing}, expected ${SOURCE_SHA}"

EXPECTED_SOURCE_SHA="${SOURCE_SHA}" bash actions/validate.pages.remote.sh

ensure_tag() {
  if git rev-parse --verify --quiet "refs/tags/${VERSION}" >/dev/null; then
    [[ "$(git cat-file -t "refs/tags/${VERSION}")" == "tag" ]] || fail "${VERSION} is not an annotated tag"
    [[ "$(git rev-list -n 1 "${VERSION}")" == "${SOURCE_SHA}" ]] || fail "${VERSION} points to another commit"
    return
  fi
  git config user.name 'github-actions[bot]'
  git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
  git tag -a "${VERSION}" -m "${TITLE}" "${SOURCE_SHA}"
  git push origin "refs/tags/${VERSION}"
}

verify_release() {
  local expected_draft="$1"
  local metadata=""
  local body_file=""
  metadata="$(gh release view "${VERSION}" --repo "${REPOSITORY}" --json assets,isDraft,name,tagName,targetCommitish)"
  [[ "$(jq -r '.tagName' <<<"${metadata}")" == "${VERSION}" ]] || fail "release tag differs"
  [[ "$(jq -r '.name' <<<"${metadata}")" == "${TITLE}" ]] || fail "release title differs"
  [[ "$(jq -r '.isDraft' <<<"${metadata}")" == "${expected_draft}" ]] || fail "release draft state differs"
  [[ "$(jq -r '.assets | length' <<<"${metadata}")" == "0" ]] || fail "unexpected uploaded assets"
  [[ "$(git rev-list -n 1 "${VERSION}")" == "${SOURCE_SHA}" ]] || fail "release tag moved"
  body_file="$(mktemp)"
  gh release view "${VERSION}" --repo "${REPOSITORY}" --json body --jq '.body' >"${body_file}"
  if ! diff -u "${NOTES}" "${body_file}"; then
    rm -f "${body_file}"
    fail "live release body differs from reviewed notes"
  fi
  rm -f "${body_file}"
}

ensure_tag

if [[ "${MODE}" == "draft" ]]; then
  if gh release view "${VERSION}" --repo "${REPOSITORY}" >/dev/null 2>&1; then
    verify_release true
    printf '[release] reviewed draft already exists for %s\n' "${VERSION}"
    exit 0
  fi
  gh release create "${VERSION}" \
    --repo "${REPOSITORY}" \
    --verify-tag \
    --target "${SOURCE_SHA}" \
    --title "${TITLE}" \
    --notes-file "${NOTES}" \
    --draft
  verify_release true
  printf '[release] created and verified draft %s\n' "${VERSION}"
  exit 0
fi

verify_release true
gh release edit "${VERSION}" --repo "${REPOSITORY}" --draft=false --latest
verify_release false
printf '[release] published and verified %s\n' "${VERSION}"
