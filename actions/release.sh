#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${RELEASE_VERSION:-}"
SOURCE_SHA="${SOURCE_SHA:-}"
MODE="${RELEASE_MODE:-}"
CONFIRMATION="${RELEASE_CONFIRMATION:-}"
REPOSITORY="${GITHUB_REPOSITORY:-devs-guide/openai}"
NOTES="${ROOT}/docs/releases/${VERSION}.md"
case "${VERSION}" in
  0.0.1) TITLE="${VERSION} — DOT Research Prompt System" ;;
  0.0.2) TITLE="${VERSION} — DOT Agent and Research System" ;;
  0.0.3) TITLE="${VERSION} — DOT On-Demand Research Summary" ;;
  *) TITLE="${VERSION} — DOT" ;;
esac

fail() {
  printf '[release][error] %s\n' "$*" >&2
  exit 1
}

[[ "${VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || fail "invalid bare semantic version"
[[ "${VERSION}" != "0.0.1" ]] || fail "0.0.1 is the published immutable baseline and cannot be recreated"
[[ "${SOURCE_SHA}" =~ ^[0-9a-f]{40}$ ]] || fail "SOURCE_SHA must be a lowercase full commit SHA"
[[ "${MODE}" == "draft" || "${MODE}" == "publish" ]] || fail "RELEASE_MODE must be draft or publish"
[[ "${CONFIRMATION}" == "release ${VERSION}@${SOURCE_SHA} ${MODE}" ]] || fail "release confirmation does not match"
[[ -s "${NOTES}" ]] || fail "reviewed release notes are missing"

cd "${ROOT}"
[[ "$(git rev-parse HEAD)" == "${SOURCE_SHA}" ]] || fail "checkout does not match SOURCE_SHA"
remote_main="$(git ls-remote --exit-code --heads origin refs/heads/main | awk 'NR == 1 {print $1}')"
[[ "${remote_main}" == "${SOURCE_SHA}" ]] || fail "main is ${remote_main:-missing}, expected ${SOURCE_SHA}"

if [[ "${VERSION}" == "0.0.3" ]]; then
  git rev-parse --verify "refs/tags/0.0.2^{tag}" >/dev/null || \
    fail "0.0.2 must be published before 0.0.3: annotated tag is missing"
  prior_metadata="$(gh release view 0.0.2 --repo "${REPOSITORY}" --json isDraft,tagName)" || \
    fail "0.0.2 must be published before 0.0.3: GitHub release is missing"
  [[ "$(jq -r '.tagName' <<<"${prior_metadata}")" == "0.0.2" ]] || \
    fail "0.0.2 must be published before 0.0.3: release tag differs"
  [[ "$(jq -r '.isDraft' <<<"${prior_metadata}")" == "false" ]] || \
    fail "0.0.2 must be published before 0.0.3: release remains a draft"
fi

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

normalize_text_file() {
  local source_file="$1"
  local normalized_file="$2"
  python3 "${ROOT}/actions/release_text.py" "${source_file}" "${normalized_file}"
}

verify_release() {
  local expected_draft="$1"
  local metadata=""
  local body_file=""
  local expected_file=""
  local observed_file=""
  metadata="$(gh release view "${VERSION}" --repo "${REPOSITORY}" --json assets,isDraft,name,tagName,targetCommitish)"
  [[ "$(jq -r '.tagName' <<<"${metadata}")" == "${VERSION}" ]] || fail "release tag differs"
  [[ "$(jq -r '.name' <<<"${metadata}")" == "${TITLE}" ]] || fail "release title differs"
  [[ "$(jq -r '.isDraft' <<<"${metadata}")" == "${expected_draft}" ]] || fail "release draft state differs"
  [[ "$(jq -r '.assets | length' <<<"${metadata}")" == "0" ]] || fail "unexpected uploaded assets"
  [[ "$(git rev-list -n 1 "${VERSION}")" == "${SOURCE_SHA}" ]] || fail "release tag moved"
  body_file="$(mktemp)"
  expected_file="$(mktemp)"
  observed_file="$(mktemp)"
  gh release view "${VERSION}" --repo "${REPOSITORY}" --json body --jq '.body' >"${body_file}"
  normalize_text_file "${NOTES}" "${expected_file}"
  normalize_text_file "${body_file}" "${observed_file}"
  if ! diff -u "${expected_file}" "${observed_file}"; then
    rm -f "${body_file}" "${expected_file}" "${observed_file}"
    fail "live release body differs from reviewed notes"
  fi
  rm -f "${body_file}" "${expected_file}" "${observed_file}"
}

ensure_tag

if [[ "${MODE}" == "draft" ]]; then
  if gh release view "${VERSION}" --repo "${REPOSITORY}" >/dev/null 2>&1; then
    existing_metadata="$(gh release view "${VERSION}" --repo "${REPOSITORY}" --json isDraft,tagName,targetCommitish)"
    [[ "$(jq -r '.isDraft' <<<"${existing_metadata}")" == "true" ]] || fail "existing release is already published"
    [[ "$(jq -r '.tagName' <<<"${existing_metadata}")" == "${VERSION}" ]] || fail "existing draft tag differs"
    [[ "$(jq -r '.targetCommitish' <<<"${existing_metadata}")" == "${SOURCE_SHA}" ]] || fail "existing draft target differs"
    gh release edit "${VERSION}" \
      --repo "${REPOSITORY}" \
      --target "${SOURCE_SHA}" \
      --title "${TITLE}" \
      --notes-file "${NOTES}" \
      --draft
    verify_release true
    printf '[release] converged and verified draft %s\n' "${VERSION}"
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
