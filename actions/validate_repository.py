#!/usr/bin/env python3
"""Validate public source hygiene and import provenance."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    ".github/workflows/www.pages.remote.yml",
    ".github/workflows/www.pages.yml",
    ".github/workflows/release.yml",
    ".gitignore",
    "COPYRIGHT.md",
    "actions/build_pages.py",
    "actions/publication.manifest.json",
    "actions/release.sh",
    "actions/validate.pages.sh",
    "actions/validate.pages.remote.sh",
    "actions/validate.release.sh",
    "actions/validate.repository.sh",
    "actions/validate_pages.py",
    "actions/validate_repository.py",
    "actions/www.pages.sh",
    "docs/features/readme.md",
    "docs/history/initial-import.md",
    "docs/history/readme.md",
    "docs/releases/0.0.1.md",
    "docs/releases/readme.md",
    "dot/readme.md",
    "readme.md",
    "tools/link.prompt.sh",
    "www/assets/site.css",
}
IMPORT_HASHES = {
    "dot/agents/browser.md": "297014149ac362021c662234105ed07af443020f41d393bbb1329e56b7893f46",
    "dot/agents/computer.md": "e99bbb77b535ce9e0facf71580e8c0b688d41b7868663e4728d068f47bc0cfce",
    "dot/agents/doc.md": "1626ba65462a5a45bbcf713014879c01e28a1cd4b029d02314e1083b7d99bc5a",
    "dot/agents/prompt.md": "33506dab7b718bbac5b3a42fcf4bcf1f7667488b1d9f7b829e814ea53dfa5763",
    "dot/prompts/core/dot.prompt": "298149b369b45ccb3fcf716a8169a3f778a9703f3a25a58394c8cca27108840d",
    "dot/prompts/core/master.prompt": "1d36de2ed42fe33e041e174a9622efcbf0a1b74c26caf2d5fe8a3a44b229ac92",
    "dot/prompts/core/reference.prompt": "92c31f665fde3b1866922ebd60d53ab744020459f5bcde61c836b785832f72fb",
    "dot/prompts/research/overview.prompt": "14e72f0bde82bd365af5356419ba162006c9fa5640392b2dcf971f8f7877ea48",
    "dot/prompts/research/starter-data-only.md": "24ef3d27e7b67998a28549a9d47ccfabcffa3923099d2b34b1398336beb0859c",
    "dot/prompts/research/template.prompt": "5ea4f8ec916d5a17a7c7b1f0a400e44320d2e4dbfe5acf40f930db2613dcfca5",
}


def fail(message: str) -> None:
    print(f"[validate.repository][error] {message}", file=sys.stderr)
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[validate.repository][ok] {message}")


def included_paths() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return sorted(path.decode() for path in result.stdout.split(b"\0") if path)


def main() -> int:
    paths = included_paths()
    path_set = set(paths)
    missing = sorted(path for path in REQUIRED if path not in path_set or not (ROOT / path).is_file())
    if missing:
        fail("required public files are missing: " + ", ".join(missing))
    ok("required public source, workflow, and policy files exist")

    if any(path.startswith("static/") for path in paths):
        fail("generated static output must not be included on main")
    if "dot/prompt" in path_set or any(path.startswith("dot/prompt/") for path in paths):
        fail("private singular prompt workspace is included in public source")
    if "dot/dot.master.00.prompt" in path_set:
        fail("byte-identical local master duplicate is included in public source")
    if any(Path(path).name.lower() in {"license", "license.md", "license.txt", "copying"} for path in paths):
        fail("a license file conflicts with the selected no-license policy")
    if any(":" in Path(path).name for path in paths):
        fail("public filenames must not contain ':'")
    ok("public/private, generated-output, filename, and no-license boundaries hold")

    for path in paths:
        full = ROOT / path
        if full.is_symlink():
            fail(f"tracked or candidate symlink is not allowed: {path}")
        if full.is_file() and full.stat().st_size == 0:
            fail(f"tracked or candidate zero-byte file: {path}")
    ok("candidate source contains no symlinks or zero-byte files")

    for path, expected in IMPORT_HASHES.items():
        full = ROOT / path
        if not full.is_file():
            fail(f"imported artifact is missing: {path}")
        observed = hashlib.sha256(full.read_bytes()).hexdigest()
        if observed != expected:
            fail(f"imported artifact changed without an import-history update: {path}")
    ok("all imported artifact bodies match their recorded SHA-256 values")

    credential_patterns = [
        re.compile(r"-----BEGIN (?:OPENSSH|RSA|DSA|EC|PGP) PRIVATE KEY-----"),
        re.compile(r"(?:^|[^A-Za-z0-9_])gh" + r"[pousr]_[A-Za-z0-9]{20,}"),
        re.compile(r"(?:^|[^A-Za-z0-9_])AK" + r"IA[0-9A-Z]{16}"),
        re.compile(r"(?:^|[^A-Za-z0-9_])sk" + r"-[A-Za-z0-9_-]{20,}"),
    ]
    for path in paths:
        full = ROOT / path
        if not full.is_file() or full.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".zip"}:
            continue
        try:
            text = full.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if path == "actions/validate_repository.py":
            continue
        for pattern in credential_patterns:
            if pattern.search(text):
                fail(f"recognized credential signature in {path}")
        if "/Users/" in text:
            fail(f"absolute macOS user path in public source: {path}")
    ok("no recognized credential signatures or macOS user paths found")

    for readme in (ROOT / "readme.md", ROOT / "dot" / "readme.md"):
        text = readme.read_text(encoding="utf-8")
        if "not affiliated with" not in text.lower() or "openai" not in text.lower():
            fail(f"unofficial-project notice is missing from {readme.relative_to(ROOT)}")
    ok("repository and product indexes carry the unofficial-project notice")

    subprocess.run([sys.executable, "actions/build_pages.py", "--validate-only"], cwd=ROOT, check=True)
    print("[validate.repository] all repository contracts passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
