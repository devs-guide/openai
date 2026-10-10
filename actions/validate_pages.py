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
    if MANIFEST.get("schema_version") != 2:
        fail("publication manifest schema_version must be 2")
    data_entries = [entry for entry in MANIFEST["entries"] if entry.get("source") == "dot/research/data.prompt"]
    if len(data_entries) != 1:
        fail("publication manifest must contain exactly one Data contract source")
    data_entry = data_entries[0]
    if data_entry.get("route") != "dot/research/data/" or data_entry.get("raw_route") != "raw/dot/research/data.prompt":
        fail("Data contract rendered or raw route is incorrect")
    summary_entries = [entry for entry in MANIFEST["entries"] if entry.get("source") == "dot/research/summary.prompt"]
    if len(summary_entries) != 1:
        fail("publication manifest must contain exactly one Summary contract source")
    summary_entry = summary_entries[0]
    if summary_entry.get("route") != "dot/research/summary/" or summary_entry.get("raw_route") != "raw/dot/research/summary.prompt":
        fail("Summary contract rendered or raw route is incorrect")
    if summary_entry.get("title") != "Evidence-Completing Research Summary" or summary_entry.get("status") != "current":
        fail("Summary publication identity is incorrect")
    browser_entries = [entry for entry in MANIFEST["entries"] if entry.get("source") == "dot/agent/browser.prompt"]
    if len(browser_entries) != 1:
        fail("publication manifest must contain exactly one Browser/Tabs contract source")
    browser_entry = browser_entries[0]
    if (
        browser_entry.get("route") != "dot/agent/browser/"
        or browser_entry.get("raw_route") != "raw/dot/agent/browser.prompt"
        or browser_entry.get("title") != "Browser, Tabs, and tool contract"
    ):
        fail("Browser/Tabs contract publication identity is incorrect")
    ingest_entries = [entry for entry in MANIFEST["entries"] if entry.get("source") == "dot/ingest.json"]
    if len(ingest_entries) != 1:
        fail("publication manifest must contain exactly one DOT ingestion manifest")
    ingest_entry = ingest_entries[0]
    if ingest_entry.get("route") != "dot/ingest/" or ingest_entry.get("raw_route") != "raw/dot/ingest.json":
        fail("DOT ingestion manifest rendered or raw route is incorrect")
    release_entries = [entry for entry in MANIFEST["entries"] if entry.get("source") == "docs/release.prompt"]
    if len(release_entries) != 1:
        fail("publication manifest must contain exactly one repository Release contract")
    release_entry = release_entries[0]
    if release_entry.get("route") != "release/" or release_entry.get("raw_route") != "raw/docs/release.prompt":
        fail("Release contract rendered or raw route is incorrect")
    candidate_entries = [entry for entry in MANIFEST["entries"] if entry.get("source") == "docs/releases/0.0.6.md"]
    if len(candidate_entries) != 1:
        fail("publication manifest must contain exactly one 0.0.6 release record")
    candidate_entry = candidate_entries[0]
    if (
        candidate_entry.get("route") != "dot/releases/0.0.6/"
        or candidate_entry.get("raw_route") != "raw/docs/releases/0.0.6.md"
        or candidate_entry.get("status") != "candidate"
    ):
        fail("0.0.6 release record publication identity is incorrect")
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
    if source_record.get("release") != "0.0.6":
        fail("source.json release identity is not 0.0.6")
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
        if f'href="/{SITE_BASE}/release/"' not in rendered:
            fail(f"repository Release navigation is missing: {page.relative_to(static_dir)}")
        parser = PageParser()
        parser.feed(rendered)
        html_parsers[page.resolve()] = parser
        if entry["source"] == "dot/agent/browser.prompt":
            for anchor_prefix in (
                "tabs-001",
                "tabs-005",
                "tabs-007",
                "browser-004",
            ):
                if not any(anchor.startswith(anchor_prefix) for anchor in parser.ids):
                    fail(f"Browser/Tabs rendered anchor is missing: {anchor_prefix}")
        if entry["route"].startswith("dot/research/"):
            if '<nav class="workflow-nav" aria-label="Research workflow">' not in rendered:
                fail(f"Research workflow navigation is missing: {page.relative_to(static_dir)}")
            workflow_links = [
                f'/{SITE_BASE}/dot/research/project/',
                f'/{SITE_BASE}/dot/research/internet/',
                f'/{SITE_BASE}/dot/research/data/',
                f'/{SITE_BASE}/dot/research/template/',
            ]
            positions = [rendered.find(f'href="{link}"') for link in workflow_links]
            if any(position < 0 for position in positions) or positions != sorted(positions):
                fail(f"four-stage Research navigation is missing or out of order: {page.relative_to(static_dir)}")
            if '<nav class="deliverable-nav" aria-label="Optional Research deliverable">' not in rendered:
                fail(f"optional Research deliverable navigation is missing: {page.relative_to(static_dir)}")
            if f'href="/{SITE_BASE}/dot/research/summary/"' not in rendered:
                fail(f"Summary navigation link is missing: {page.relative_to(static_dir)}")
    ok("every manifest entry has matching rendered and byte-exact raw output")

    for entry in MANIFEST["entries"]:
        for alias in entry["aliases"]:
            page = rendered_path(static_dir, alias)
            if not page.is_file():
                fail(f"redirect route is missing: {alias}")
            rendered = page.read_text(encoding="utf-8")
            destination = f'/{SITE_BASE}/{entry["route"]}'
            if f'<link rel="canonical" href="{destination}">' not in rendered:
                fail(f"redirect canonical target is incorrect: {alias}")
            if f'<meta name="source-commit" content="{source_record["source_sha"]}">' not in rendered:
                fail(f"redirect source metadata is incorrect: {alias}")
            parser = PageParser()
            parser.feed(rendered)
            html_parsers[page.resolve()] = parser
    ok("every legacy rendered route redirects to its canonical replacement")

    for migration in MANIFEST["raw_migrations"]:
        pointer = static_dir / migration["route"]
        if not pointer.is_file():
            fail(f"raw migration pointer is missing: {migration['route']}")
        text = pointer.read_text(encoding="utf-8")
        expected_replacement = f"/{SITE_BASE}/{migration['replacement']}"
        if migration["historical_url"] not in text or expected_replacement not in text:
            fail(f"raw migration pointer has incorrect targets: {migration['route']}")
    ok("every legacy raw route identifies its historical source and replacement")

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
        retired_route = "dot/" + "handoff"
        retired_raw_route = "raw/" + retired_route
        standalone_tabs_raw = "raw/dot/agent/" + "tabs.prompt"
        if relative == "dot/prompt" or relative.startswith("dot/prompt/"):
            fail("private singular prompt path leaked into rendered Pages output")
        if relative == "raw/dot/prompt" or relative.startswith("raw/dot/prompt/"):
            fail("private singular prompt path leaked into raw Pages output")
        if relative == retired_route or relative.startswith(retired_route + "/"):
            fail("retired handoff path leaked into rendered Pages output")
        if relative == retired_raw_route or relative.startswith(retired_raw_route + "/"):
            fail("retired handoff path leaked into raw Pages output")
        if relative == "dot/agent/tabs" or relative.startswith("dot/agent/tabs/"):
            fail("standalone Tabs route leaked into rendered Pages output")
        if relative == standalone_tabs_raw:
            fail("standalone Tabs source leaked into raw Pages output")
    routes_file = static_dir / "routes.json"
    try:
        routes_record = json.loads(routes_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid routes.json: {exc}")
    if routes_record.get("schema_version") != 2:
        fail("routes.json schema_version must be 2")
    route_rows = routes_record.get("routes")
    expected_rows = len(MANIFEST["entries"]) + sum(len(entry["aliases"]) for entry in MANIFEST["entries"]) + len(MANIFEST["raw_migrations"])
    if not isinstance(route_rows, list) or len(route_rows) != expected_rows:
        fail("routes.json does not enumerate every canonical, redirect, and raw migration route")
    required_files = [static_dir / ".nojekyll", static_dir / "assets" / "site.css", routes_file]
    if any(not path.exists() for path in required_files):
        fail("Pages metadata or stylesheet output is missing")
    ok("Pages metadata, stylesheet, and public/private boundaries hold")

    print("[validate.pages] all generated Pages contracts passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
