# devs-guide/openai

Community-maintained documentation, prompt artifacts, and supporting examples
for OpenAI-related projects.

> This repository is not affiliated with, endorsed by, or sponsored by OpenAI.
> OpenAI product names and trademarks belong to their respective owners.

## Products

### [DOT](dot/)

A two-lane instruction package for a configured Agent, with a compact Project
→ Internet → Data → Template workflow for pure research and controlled dataset
releases plus an optional on-demand Summary deliverable.

- Source: [`dot/`](dot/)
- Documentation: [`https://devs-guide.github.io/openai/dot/`](https://devs-guide.github.io/openai/dot/)
- Features: [`docs/features/`](docs/features/)
- History: [`docs/history/`](docs/history/)
- Releases: [`docs/releases/`](docs/releases/)

Repository releases use the reusable [`#RELEASE`](docs/release.prompt)
contract for reader-focused notes, exact review gates, immutable tags, and
verified publication across every product in this repository.

Future products should add a product directory with its own `readme.md` and
create `docs/`, `prompts/`, `examples/`, `config/`, `src/`, or `tests/` only
when accepted content exists.

## Publication model

Repository Markdown, prompt, and JSON files are the source of truth. A
validated, manifest-driven build renders extensionless documentation and exact
raw-source downloads to the orphan `www` branch for GitHub Pages. Generated
`static/` output is never tracked on `main`.

All compilation, builds, and tests run in GitHub Actions. Local work is limited
to source editing and Git operations.

## Current release

Release `0.0.1 — DOT Research Prompt System` is the published immutable
migration baseline. Release `0.0.2 — DOT Agent and Research System` consolidates
that corpus into canonical Agent and Research lanes. Release `0.0.3 — DOT
On-Demand Research Summary` adds a conditional, evidence-bound executive-brief
deliverable. Candidate `0.0.4 — Repository Release Contract` adds reusable
release style, documentation, and publication safeguards for the entire
repository. Release records use bare semantic tags and GitHub-generated source
archives; no binary assets are attached.

## Rights

This repository does not provide an open-source license. See
[`COPYRIGHT.md`](COPYRIGHT.md) before using or redistributing its contents.
