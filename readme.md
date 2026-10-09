# devs-guide/openai

Community-maintained documentation, prompt artifacts, and supporting examples
for OpenAI-related projects.

> This repository is not affiliated with, endorsed by, or sponsored by OpenAI.
> OpenAI product names and trademarks belong to their respective owners.

## Products

### [DOT](dot/)

A reusable research-prompt system with a current consolidated protocol,
reference variants, research starters, and dated agent operating guides.

- Source: [`dot/`](dot/)
- Documentation: [`https://devs-guide.github.io/openai/dot/`](https://devs-guide.github.io/openai/dot/)
- Features: [`docs/features/`](docs/features/)
- History: [`docs/history/`](docs/history/)
- Releases: [`docs/releases/`](docs/releases/)

Future products should add a product directory with its own `readme.md` and
create `docs/`, `prompts/`, `examples/`, `config/`, `src/`, or `tests/` only
when accepted content exists.

## Publication model

Repository Markdown and prompt files are the source of truth. A validated,
manifest-driven build renders extensionless documentation and exact raw-source
downloads to the orphan `www` branch for GitHub Pages. Generated `static/`
output is never tracked on `main`.

All compilation, builds, and tests run in GitHub Actions. Local work is limited
to source editing and Git operations.

## Current release

Release `0.0.1 — DOT Research Prompt System` establishes the initial curated
source, documentation, Pages, validation, and release contracts. Release
records use bare semantic tags and GitHub-generated source archives; no binary
assets are attached.

## Rights

This repository does not provide an open-source license. See
[`COPYRIGHT.md`](COPYRIGHT.md) before using or redistributing its contents.
