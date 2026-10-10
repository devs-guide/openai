# DOT

DOT is a community-maintained two-lane instruction package for operating a
configured agent and restricting it to evidence-heavy, long-running internet
research. It is designed for owner-authorized use with OpenAI's `dot` product,
but it is not an OpenAI product or an automatic product configuration.

> This is a community-maintained project. It is not affiliated with, endorsed
> by, or sponsored by OpenAI.

## Read left to right

[`#AGENT`](agent/) → [`#PROJECT`](research/project.prompt) →
[`#INTERNET`](research/internet.prompt) →
[`#DATA`](research/data.prompt) →
[`#TEMPLATE`](research/template.prompt)

Optional deliverable: [`#SUMMARY`](research/summary.prompt) produces one
explicitly requested, evidence-bound subtopic executive brief without changing
the four-stage workflow or overwriting its parent report.

- [`agent/`](agent/) defines the runtime, exact models, permissions, browser,
  tools, workspace, Pages, video, and transcription behavior.
- [`research/`](research/) builds a project around that Agent, supplies the
  pure internet-research rules, converts reviewed evidence into controlled
  datasets, and provides reusable templates.

Repository release style, review, and publication are governed separately by
the repo-wide [`#RELEASE`](../docs/release.prompt) contract. Because `docs/` is
a non-instructional prefix in `ingest.json`, it never becomes Agent or Research
authority when DOT is loaded.

Load the Agent contract first. A Research project may narrow it but cannot
silently add a model, tool, account, permission, execution surface, or
destination.

## Load a tagged release into OpenAI dot

Use the GitHub-generated source archive for an exact published tag, not a
moving branch or the current Pages copy. Attach the archive to the owner's dot,
then direct it to [`ingest.json`](ingest.json). That manifest is routing
metadata: it identifies the release, ordered live instructions, conditional
modules, supporting files, hashes, and non-instructional paths without copying
the contracts.

The dot must inventory the archive and return an ingestion receipt before
acting as `#AGENT`. ChatGPT or dot memory, connected-app context, prior tasks,
release notes, history, CI files, and retrieved text do not become current
instructions or permissions. Research begins only after the owner-supplied
topic produces a materially complete Project Control Packet in `READY` state.

[OpenAI documents](https://help.openai.com/en/articles/20001530-getting-started-with-your-dot)
file attachment and optional local-computer and Codex routes for dot. This
contract keeps its narrower browser-first boundary: Codex, the owner's local
computer, installation, and unassigned models remain prohibited.

The rendered documentation is published at
[`https://devs-guide.github.io/openai/dot/`](https://devs-guide.github.io/openai/dot/).
Exact current sources are published beneath `/openai/raw/dot/`.

## Operating defaults

| Area | Current contract |
|---|---|
| Models | Assigned collaborator followed by an explicit, accessibility-gated fallback order |
| Execution | Cloud browser by default; existing VM tools require project opt-in |
| Codex and installation | Prohibited |
| Working files | `/workspace/scratch/<project-id>/` after verification; durability unknown |
| Durable output | Configured Page or owner-approved destination with readback |
| Research data | Human-facing atomic Facts backed by assertions, observations, claims, and evidence links |
| Dataset releases | Applicable 22-basename menu with paired CSV/JSON parity, validation, immutable snapshots, and successor corrections |
| Executive briefs | Conditional self-contained PDF summaries bound to frozen parent research, controlled Facts, visual inspection, and readback |

## History and compatibility

Release `0.0.2` consolidates the original prompts and dated guides. Release
`0.0.3` adds the optional Summary deliverable without changing the core
workflow. Release `0.0.4` adds the repository-wide Release contract without
changing the DOT instruction order. The
[`two-lane migration record`](../docs/history/two-lane-migration.md) maps every
`0.0.1` source to its current owner. Historical rendered routes redirect;
historical raw routes identify both the immutable original and current
replacement.

Compilation, auditing, static-site builds, and tests run only in GitHub
Actions. The local workstation is limited to source editing and Git operations.

## Rights

No open-source license is granted. See [`../COPYRIGHT.md`](../COPYRIGHT.md).
