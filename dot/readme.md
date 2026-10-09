# DOT

DOT is a reusable research-prompt system for planning, executing, validating,
and resuming evidence-heavy work. This directory contains the public prompt
artifacts and dated agent operating guides for the first `devs-guide/openai`
product.

> This is a community-maintained project. It is not affiliated with, endorsed
> by, or sponsored by OpenAI.

## Start here

- [`prompts/core/master.prompt`](prompts/core/master.prompt) is the current
  consolidated DOT prompt.
- [`prompts/core/dot.prompt`](prompts/core/dot.prompt) is the earlier baseline.
- [`prompts/core/reference.prompt`](prompts/core/reference.prompt) is retained
  as reference material.
- [`prompts/research/`](prompts/research/) contains reusable research starters.
- [`agents/`](agents/) contains dated browser, computer, document, and prompt
  operating guides.

The rendered documentation is published at
[`https://devs-guide.github.io/openai/dot/`](https://devs-guide.github.io/openai/dot/).
Exact source downloads are published beneath `/openai/raw/dot/`.

Compilation, static-site builds, and tests run only in GitHub Actions. The local
workstation is used for source editing and Git operations, not runtime
validation.

## Artifact status

| Area | Status | Intended use |
|---|---|---|
| Core master prompt | Current | Primary reusable DOT protocol |
| Baseline and reference prompts | Reference | Historical comparison and recovery |
| Research starters | Reusable templates | New research-project initialization |
| Agent guides | Dated evidence | Bounded operating and capability records |

Dates and capability observations inside an artifact remain scoped to the
environment and test window stated by that artifact. They are not permanent
product guarantees. Owner policies are instructions, not verified platform
facts.

## Project layout

Public product artifacts use plural `prompts/`. The optional singular
`prompt` path is an ignored local symlink to private lifecycle material in the
separate `devs-guide/prompts` repository; it is never included in source
releases or Pages output.

The original flat-file import, source hashes, normalized paths, and duplicate
disposition are recorded in [`../docs/history/initial-import.md`](../docs/history/initial-import.md).

## Rights

No open-source license is granted. See [`../COPYRIGHT.md`](../COPYRIGHT.md).
