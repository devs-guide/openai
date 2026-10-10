# DOT Agent

`#AGENT` is the stable operating lane for DOT. It defines the runtime,
permissions, models, browser, storage, Pages, tools, and media behavior that a
project may use. It does not define a research topic or contain research
findings.

## Read left to right

[`master.prompt`](master.prompt) → [`config.json`](config.json) →
[`runtime.json`](runtime.json) → capability module

| Capability module | Use |
|---|---|
| [`browser.prompt`](browser.prompt) | `#BROWSER`, `#CAPTCHA`, and browser-based `#TOOL` behavior |
| [`page.prompt`](page.prompt) | `#PAGE`, saving, delivery, and readback verification |
| [`media.prompt`](media.prompt) | `#VIDEO`, captions, audio, and `#TRANSCRIPTION` |

Load only the capability modules needed by the active project. A project may
narrow this lane but may not silently expand its permissions, models, tools,
accounts, or destinations.
