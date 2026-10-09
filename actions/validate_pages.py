#!/usr/bin/env python3
"""Validate generated Pages routes, links, raw sources, and source identity."""

from __future__ import annotations

from html.parser import HTMLParser
import json
import os
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "actions" / "publication.manifest.json").read_text(encoding="utf-8"))
SITE_BASE = MANIFEST["site_base"]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        for name in ("href", "src"):
            if values.get(name):
                self.links.append(values[name] or "")


def fail(message: str) -> None:
    print(f"[validate.pages][error] {message}", file=sys.stderr)
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[validate.pages][ok] {message}")


def rendered_path(static_dir: Path, route: str) -> Path:
    return static_dir / route / "index.html" if route else static_dir / "index.html"


def target_for_url(static_dir: Path, page: Path, url: str) -> tuple[Path | None, str]:
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or url.startswith(("mailto:", "tel:")):
        return None, ""
    path = unquote(parsed.path)
    if not path:
        return page, parsed.fragment
    if path.startswith(f"/{SITE_BASE}/"):
        relative = path[len(SITE_BASE) + 2 :]
        target = static_dir / relative
    elif path == f"/{SITE_BASE}" or path == f"/{SITE_BASE}/":
        target = static_dir
    elif path.startswith("/"):
        fail(f"internal link escapes /{SITE_BASE}/: {url} in {page.relative_to(static_dir)}")
    else:
        target = page.parent / path
    if path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target.resolve(), parsed.fragment


def main() -> int:
    static_value = os.environ.get("STATIC_DIR", "static")
    static_dir = Path(static_value)
    if not static_dir.is_absolute():
        static_dir = ROOT / static_dir
    static_dir = static_dir.resolve()
    if not static_dir.is_dir():
        fail(f"static directory does not exist: {static_dir}")

    source_file = static_dir / "source.json"
    try:
        source_record = json.loads(source_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid source.json: {exc}")
    expected_sha = os.environ.get("EXPECTED_SOURCE_SHA")
    if expected_sha and source_record.get("source_sha") != expected_sha:
        fail(f"source SHA is {source_record.get('source_sha')}, expected {expected_sha}")
    if source_record.get("repository") != "devs-guide/openai":
        fail("source.json repository identity is incorrect")
    ok(f"source marker identifies {source_record.get('source_sha')}")

    html_parsers: dict[Path, PageParser] = {}
    for entry in MANIFEST["entries"]:
        source = ROOT / entry["source"]
        page = rendered_path(static_dir, entry["route"])
        raw = static_dir / entry["raw_route"]
        if not page.is_file():
            fail(f"rendered route is missing: {entry['route'] or '/'}")
        if not raw.is_file() or raw.read_bytes() != source.read_bytes():
            fail(f"raw route does not exactly match source: {entry['raw_route']}")
        rendered = page.read_text(encoding="utf-8")
        for required in ('<html lang="en">', '<main id="content"', 'class="skip-link"', '<article>'):
            if required not in rendered:
                fail(f"semantic HTML marker {required!r} is missing: {page.relative_to(static_dir)}")
        if f'<meta name="source-commit" content="{source_record["source_sha"]}">' not in rendered:
            fail(f"page source metadata does not match source.json: {page.relative_to(static_dir)}")
        parser = PageParser()
        parser.feed(rendered)
        html_parsers[page.resolve()] = parser
    ok("every manifest entry has matching rendered and byte-exact raw output")

    broken: list[str] = []
    for page, parser in list(html_parsers.items()):
        for url in parser.links:
            target, fragment = target_for_url(static_dir, page, url)
            if target is None:
                continue
            try:
                target.relative_to(static_dir)
            except ValueError:
                broken.append(f"{page.relative_to(static_dir)} -> {url} (escapes static tree)")
                continue
            if not target.is_file():
                broken.append(f"{page.relative_to(static_dir)} -> {url} (missing)")
                continue
            if fragment and target.suffix == ".html":
                target_parser = html_parsers.get(target)
                if target_parser is None:
                    target_parser = PageParser()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                    html_parsers[target] = target_parser
                if fragment not in target_parser.ids:
                    broken.append(f"{page.relative_to(static_dir)} -> {url} (missing fragment)")
    if broken:
        fail("broken internal links:\n  " + "\n  ".join(broken[:50]))
    ok("all generated internal links and fragments resolve within the Pages tree")

    for path in static_dir.rglob("*"):
        relative = path.relative_to(static_dir).as_posix()
        if relative == "dot/prompt" or relative.startswith("dot/prompt/"):
            fail("private singular prompt path leaked into rendered Pages output")
        if relative == "raw/dot/prompt" or relative.startswith("raw/dot/prompt/"):
            fail("private singular prompt path leaked into raw Pages output")
    required_files = [static_dir / ".nojekyll", static_dir / "assets" / "site.css", static_dir / "routes.json"]
    if any(not path.exists() for path in required_files):
        fail("Pages metadata or stylesheet output is missing")
    ok("Pages metadata, stylesheet, and public/private boundaries hold")

    print("[validate.pages] all generated Pages contracts passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
