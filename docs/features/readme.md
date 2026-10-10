# DOT features

This public index describes accepted or release-candidate product behavior.
Private implementation plans and operational evidence remain in the separate
`devs-guide/prompts` lifecycle workspace.

## 0.0.2

| Feature | Status | Public owners |
|---|---|---|
| Agent operating contract | Candidate | `dot/agent/` |
| Tagged-release ingestion and activation gate | Candidate | `dot/ingest.json`, Agent, Project, and Template |
| Project → Internet → Data → Template research flow | Candidate | `dot/research/` |
| Evidence-to-dataset release lifecycle | Candidate | Data contract, reusable structures, and GitHub validation |
| Ordered assigned models and project-opt-in VM tools | Candidate | Agent configuration and Project contract |
| Page, Fact, browser, CAPTCHA, video and transcription contracts | Candidate | Agent modules and Research contracts |
| Clause-level migration audit | Candidate | History ledger and GitHub Actions |
| Legacy route compatibility | Candidate | Publication manifest and Pages builder |

## 0.0.1

| Feature | Status | Public owners |
|---|---|---|
| Core DOT protocol | Accepted | `dot/prompts/core/` |
| Reusable research starters | Accepted | `dot/prompts/research/` |
| Dated agent operating guides | Accepted | `dot/agents/` |
| Tiered documentation site | Accepted | `actions/`, `www/`, and the publication manifest |
| Validated release workflow | Accepted | repository, Pages, and release validators |

A feature becomes accepted only when its source, GitHub Actions build/test
checks, live Pages routes, and applicable human review gates all pass on the
same commit. Compilation, builds, and tests do not run locally.
