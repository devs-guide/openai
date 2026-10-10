# DOT two-lane migration

Release `0.0.2` replaces the overlapping `dot/agents/` and `dot/prompts/`
documents with one canonical `#AGENT` lane and a compact research sequence:

`#PROJECT` → `#INTERNET` → `#DATA` → `#TEMPLATE`

Exact `0.0.1` bodies remain available from the immutable tag. The current tree
does not republish those bodies as an archive.

## Disposition rules

| Disposition | Meaning |
|---|---|
| `KEEP_AGENT` | Consolidated into the Agent contract, configuration, runtime observations, or a capability module. |
| `KEEP_PROJECT` | Consolidated into project setup, state, recovery, or completion. |
| `KEEP_INTERNET` | Consolidated into internet-research method and evidence controls. |
| `KEEP_DATA` | Consolidated into evidence-to-dataset selection, structure, parity, validation, or release controls. |
| `KEEP_TEMPLATE` | Consolidated into reusable records, examples, prompts, or delivery structures. |
| `MERGE` | Repeated rules were combined under one canonical rule ID. |
| `HISTORY_ONLY` | Dated test procedure or result remains available through `0.0.1` but is not an active rule. |
| `DROP_REDUNDANT` | A byte-identical or substantively duplicated live copy was removed after its canonical target was recorded. |

## Source disposition

| `0.0.1` source | Disposition | Current owner |
|---|---|---|
| `dot/agents/browser.md` | `KEEP_AGENT`, `HISTORY_ONLY` | Agent browser, runtime, and history |
| `dot/agents/computer.md` | `KEEP_AGENT`, `HISTORY_ONLY` | Agent runtime and history |
| `dot/agents/doc.md` | `KEEP_AGENT`, `KEEP_DATA`, `KEEP_TEMPLATE` | Agent contract, Data controls, and Research templates |
| `dot/agents/prompt.md` | `HISTORY_ONLY`, `KEEP_AGENT` | Agent browser rules and history |
| `dot/agents/readme.md` | `DROP_REDUNDANT` | Agent index |
| `dot/prompts/core/master.prompt` | `MERGE`, `KEEP_DATA` | Agent, Project, Internet, Data, and Template |
| `dot/prompts/core/dot.prompt` | `MERGE`, `DROP_REDUNDANT` | Project and Internet |
| `dot/prompts/core/reference.prompt` | `MERGE`, `DROP_REDUNDANT` | Project and Internet |
| `dot/prompts/core/readme.md` | `DROP_REDUNDANT` | DOT and migration indexes |
| `dot/prompts/research/overview.prompt` | `MERGE`, `KEEP_DATA`, `DROP_REDUNDANT` | Project, Internet, Data, and Template |
| `dot/prompts/research/template.prompt` | `MERGE`, `KEEP_DATA`, `DROP_REDUNDANT` | Project, Internet, Data, and Template |
| `dot/prompts/research/starter-data-only.md` | `MERGE`, `KEEP_DATA` | Agent restrictions, Data controls, and Research templates |
| `dot/prompts/research/readme.md` | `DROP_REDUNDANT` | Research index |
| `dot/prompts/readme.md` | `DROP_REDUNDANT` | DOT and Research indexes |

The machine-readable companion supplies the targets used by the CI audit. The
audit extracts clauses from tag `0.0.1`, assigns the declared source
disposition to every clause, and emits the expanded clause inventory for human
review as a workflow artifact.

## Policy resolutions

- The browser is the default execution surface. Existing cloud-computer tools
  require an exact project allowlist; installation remains prohibited.
- Model selection is `ORDERED_FALLBACK`: GPT-6 Astra remains the assigned
  primary and GPT-5.6 Sol/High the initial collaborator. When that exact
  configuration is no longer accessible, use only the ordered configurations
  in `config.json`; exhausting the list blocks the dependent branch.
- `/workspace/scratch/<project-id>/` is the working default after verification;
  its retention remains unknown. Durable delivery requires a configured Page
  or owner-approved destination and readback.
- `#PAGE` is an Agent-owned human-readable workspace. `#FACT` is a
  Research-owned human-facing atomic concept backed by linked assertions,
  observations, claims, and evidence records.
- `#DATA` owns applicable-file selection, grains, paired CSV/JSON semantics,
  validation, immutable releases, corrections, and refreshes. `#TEMPLATE`
  owns the fillable record shapes.
- CAPTCHA, browser tools, video acquisition, and transcription are Agent
  mechanics. Research references those rules and owns evidence evaluation.

## Compatibility

Old rendered routes redirect to a current replacement or this record. Old raw
routes return a migration pointer containing the immutable `0.0.1` source URL
and the replacement raw URL.
