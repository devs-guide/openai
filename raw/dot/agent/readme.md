# DOT Agent

`#AGENT` is the stable operating lane for DOT. It defines the runtime,
permissions, models, browser, storage, Pages, tools, and media behavior that a
project may use. It does not define a research topic or contain research
findings.

## Read left to right

[`master.prompt`](master.prompt) → [`config.json`](config.json) →
[`runtime.json`](runtime.json) → [`storage.prompt`](storage.prompt) →
[`progress.prompt`](progress.prompt) → capability module

| Capability module | Use |
|---|---|
| [`storage.prompt`](storage.prompt) | Required `#STORAGE`, `#FILES`, verified persistence, recovery manifests, archives, capacity, and `agent:<term>` locations |
| [`progress.prompt`](progress.prompt) | Required `#PROGRESS`, 15-minute or event-driven checks, `#LAZY`, recovery, consultations, logs, and notifications |
| [`browser.prompt`](browser.prompt) | `#BROWSER`, configured `#TABS`, `#CAPTCHA`, and browser-based `#TOOL` behavior |
| [`page.prompt`](page.prompt) | `#PAGE`, saving, delivery, and readback verification |
| [`media.prompt`](media.prompt) | `#VIDEO`, captions, audio, and `#TRANSCRIPTION` |

Storage and Progress are required for every active project. Load the other
capability modules only when needed. A project may
narrow this lane but may not silently expand its permissions, models, tools,
accounts, or destinations.

`#TABS` is not a separate capability module. It is the Browser-owned shared
capacity and recovery configuration in `config.json`; its canonical rules live
inside `browser.prompt` and apply whenever that module is loaded. Its monitoring
branch consumes the single project-wide `#PROGRESS` health check rather than
creating another schedule.
