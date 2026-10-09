# Initial DOT source import

The local pre-Git inventory was captured on 2026-10-09 before the first public
repository commit. The import normalizes path names while preserving document
bodies. SHA-256 values below identify the original bytes.

| Original path under `dot/` | Public path | SHA-256 | Disposition |
|---|---|---|---|
| `DOT2_Research_Starter_Template_Data_Only-3337709cc6ad4942af0f034cc222bf0c.md` | `dot/prompts/research/starter-data-only.md` | `24ef3d27e7b67998a28549a9d47ccfabcffa3923099d2b34b1398336beb0859c` | Renamed; body preserved |
| `agent:browser.md` | `dot/agents/browser.md` | `297014149ac362021c662234105ed07af443020f41d393bbb1329e56b7893f46` | Renamed; body preserved |
| `agent:computer.md` | `dot/agents/computer.md` | `e99bbb77b535ce9e0facf71580e8c0b688d41b7868663e4728d068f47bc0cfce` | Renamed; body preserved |
| `agent:doc.md` | `dot/agents/doc.md` | `1626ba65462a5a45bbcf713014879c01e28a1cd4b029d02314e1083b7d99bc5a` | Renamed; body preserved |
| `agent:prompt.md` | `dot/agents/prompt.md` | `33506dab7b718bbac5b3a42fcf4bcf1f7667488b1d9f7b829e814ea53dfa5763` | Renamed; body preserved |
| `dot.master.00.prompt` | `dot/prompts/core/master.prompt` | `1d36de2ed42fe33e041e174a9622efcbf0a1b74c26caf2d5fe8a3a44b229ac92` | Byte-identical duplicate; not published separately |
| `dot.master.01.prompt` | `dot/prompts/core/master.prompt` | `1d36de2ed42fe33e041e174a9622efcbf0a1b74c26caf2d5fe8a3a44b229ac92` | Canonical imported master; body preserved |
| `dot.prompt` | `dot/prompts/core/dot.prompt` | `298149b369b45ccb3fcf716a8169a3f778a9703f3a25a58394c8cca27108840d` | Renamed; body preserved |
| `dot.ref.prompt` | `dot/prompts/core/reference.prompt` | `92c31f665fde3b1866922ebd60d53ab744020459f5bcde61c836b785832f72fb` | Renamed; body preserved |
| `dot.research.readme.prompt` | `dot/prompts/research/overview.prompt` | `14e72f0bde82bd365af5356419ba162006c9fa5640392b2dcf971f8f7877ea48` | Renamed; body preserved |
| `dot.research.template.prompt` | `dot/prompts/research/template.prompt` | `5ea4f8ec916d5a17a7c7b1f0a400e44320d2e4dbfe5acf40f930db2613dcfca5` | Renamed; body preserved |

The local `dot.master.00.prompt` file remains ignored as a recoverable copy. It
is excluded from commits, Pages, and release archives because its bytes are
already represented by the canonical master artifact.

Credential, private-path, and repository hygiene scans run in GitHub Actions on
the exact publication candidate. Human content review remains a separate
release gate.
