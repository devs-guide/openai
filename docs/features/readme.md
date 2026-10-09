# DOT features

This public index describes accepted or release-candidate product behavior.
Private implementation plans and operational evidence remain in the separate
`devs-guide/prompts` lifecycle workspace.

## 0.0.1 candidate

| Feature | Status | Public owners |
|---|---|---|
| Core DOT protocol | Candidate | `dot/prompts/core/` |
| Reusable research starters | Candidate | `dot/prompts/research/` |
| Dated agent operating guides | Candidate | `dot/agents/` |
| Tiered documentation site | Candidate | `actions/`, `www/`, and the publication manifest |
| Validated release workflow | Candidate | repository, Pages, and release validators |

A feature becomes accepted only when its source, GitHub Actions build/test
checks, live Pages routes, and applicable human review gates all pass on the
same commit. Compilation, builds, and tests do not run locally.
