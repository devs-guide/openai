# DOT features

This public index describes accepted or release-candidate product behavior.
Private implementation plans and operational evidence remain in the separate
`devs-guide/prompts` lifecycle workspace.

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
