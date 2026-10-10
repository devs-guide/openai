#!/usr/bin/env python3
"""Build the manifest-defined static documentation tree."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
from urllib.parse import quote, unquote, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "actions" / "publication.manifest.json"
REQUIRED_FIELDS = {
    "aliases",
    "content_type",
    "source",
    "route",
    "raw_route",
    "title",
    "kind",
    "status",
    "reviewed_on",
}
ALLOWED_STATUS = {"current", "reference", "dated-evidence", "candidate", "archived"}
ALLOWED_CONTENT_TYPES = {"json", "markdown", "prompt"}
SOURCE_SUFFIXES = {".json", ".md", ".prompt"}
ATTR_RE = re.compile(r'(?P<prefix>\b(?:href|src)=")(?P<url>[^"]*)(?P<suffix>")')


class BuildError(RuntimeError):
    """A publication contract failure."""


def fail(message: str) -> None:
    raise BuildError(message)


def normalize_relative(value: str, *, allow_empty: bool, directory: bool) -> str:
    if not isinstance(value, str):
        fail("manifest paths must be strings")
    if value == "" and allow_empty:
        return value
    if not value or value.startswith("/") or "\\" in value:
        fail(f"path must be a non-empty relative POSIX path: {value!r}")
    pure = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in pure.parts):
        fail(f"path contains an unsafe segment: {value!r}")
    if directory and not value.endswith("/"):
        fail(f"rendered route must end in '/': {value!r}")
    if not directory and value.endswith("/"):
        fail(f"file route must not end in '/': {value!r}")
    return value


def discover_publishable_sources() -> set[str]:
    discovered = {"readme.md", "COPYRIGHT.md"}
    for root_name in ("dot", "docs"):
        base = ROOT / root_name
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel == "dot/dot.master.00.prompt" or rel.startswith("dot/prompt/"):
                continue
            discovered.add(rel)
    return discovered


def load_manifest() -> tuple[dict, list[dict]]:
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read publication manifest: {exc}")

    if manifest.get("schema_version") != 2:
        fail("publication manifest schema_version must be 2")
    site_base = manifest.get("site_base")
    if not isinstance(site_base, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", site_base):
        fail("site_base must be one lowercase URL segment")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        fail("publication manifest entries must be a non-empty list")

    sources: set[str] = set()
    routes: set[str] = set()
    raw_routes: set[str] = set()
    aliases: set[str] = set()
    normalized: list[dict] = []
    for index, raw_entry in enumerate(entries):
        if not isinstance(raw_entry, dict):
            fail(f"manifest entry {index} must be an object")
        missing = REQUIRED_FIELDS - raw_entry.keys()
        if missing:
            fail(f"manifest entry {index} lacks: {', '.join(sorted(missing))}")
        entry = dict(raw_entry)
        source = normalize_relative(entry["source"], allow_empty=False, directory=False)
        route = normalize_relative(entry["route"], allow_empty=True, directory=True)
        raw_route = normalize_relative(entry["raw_route"], allow_empty=False, directory=False)
        if source in sources:
            fail(f"duplicate source in manifest: {source}")
        if route in routes or route in aliases:
            fail(f"duplicate rendered route in manifest: {route or '/'}")
        if raw_route in raw_routes:
            fail(f"duplicate raw route in manifest: {raw_route}")
        content_type = entry["content_type"]
        if content_type not in ALLOWED_CONTENT_TYPES:
            fail(f"unsupported content type for {source}: {content_type}")
        expected_suffix = {"json": ".json", "markdown": ".md", "prompt": ".prompt"}[content_type]
        if not source.endswith(expected_suffix):
            fail(f"content type and suffix disagree for {source}")
        entry_aliases = entry["aliases"]
        if not isinstance(entry_aliases, list):
            fail(f"aliases must be an array for {source}")
        normalized_aliases: list[str] = []
        for raw_alias in entry_aliases:
            alias = normalize_relative(raw_alias, allow_empty=False, directory=True)
            if alias == route or alias in routes or alias in aliases:
                fail(f"duplicate or canonical alias route: {alias}")
            aliases.add(alias)
            normalized_aliases.append(alias)
        entry["aliases"] = normalized_aliases
        source_path = ROOT / source
        if not source_path.is_file() or source_path.is_symlink() or source_path.stat().st_size == 0:
            fail(f"manifest source is missing, empty, or a symlink: {source}")
        if content_type == "json":
            try:
                json.loads(source_path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                fail(f"manifest JSON source is invalid: {source}: {exc}")
        if not isinstance(entry["title"], str) or not entry["title"].strip():
            fail(f"manifest title is empty: {source}")
        if entry["status"] not in ALLOWED_STATUS:
            fail(f"unsupported status for {source}: {entry['status']}")
        try:
            dt.date.fromisoformat(entry["reviewed_on"])
        except (TypeError, ValueError):
            fail(f"reviewed_on must be YYYY-MM-DD for {source}")
        sources.add(source)
        routes.add(route)
        raw_routes.add(raw_route)
        normalized.append(entry)

    raw_migrations = manifest.get("raw_migrations")
    if not isinstance(raw_migrations, list):
        fail("raw_migrations must be an array")
    migration_routes: set[str] = set()
    for index, migration in enumerate(raw_migrations):
        if not isinstance(migration, dict) or set(migration) != {"route", "historical_url", "replacement"}:
            fail(f"raw migration {index} has invalid fields")
        migration_route = normalize_relative(migration["route"], allow_empty=False, directory=False)
        replacement = normalize_relative(migration["replacement"], allow_empty=False, directory=False)
        if migration_route in raw_routes or migration_route in migration_routes:
            fail(f"duplicate raw migration route: {migration_route}")
        if replacement not in raw_routes:
            fail(f"raw migration replacement is not a canonical raw route: {replacement}")
        if not migration["historical_url"].startswith("https://github.com/devs-guide/openai/blob/0.0.1/"):
            fail(f"raw migration does not use immutable 0.0.1 source: {migration_route}")
        migration_routes.add(migration_route)

    discovered = discover_publishable_sources()
    unlisted = sorted(discovered - sources)
    missing = sorted(sources - discovered)
    if unlisted:
        fail("publishable sources missing from manifest: " + ", ".join(unlisted))
    if missing:
        fail("manifest lists undiscovered sources: " + ", ".join(missing))

    return manifest, normalized


def resolve_internal_target(source: str, url: str, entries_by_source: dict[str, dict], site_base: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or url.startswith(("/", "#")) or not parsed.path:
        return url

    decoded = unquote(parsed.path)
    source_parent = PurePosixPath(source).parent
    candidate = source_parent / decoded
    parts: list[str] = []
    for part in candidate.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if not parts:
                return url
            parts.pop()
        else:
            parts.append(part)
    target = PurePosixPath(*parts).as_posix()
    if decoded.endswith("/") or (ROOT / target).is_dir():
        target = f"{target.rstrip('/')}/readme.md"
    entry = entries_by_source.get(target)
    if entry is None:
        return url
    rendered = f"/{site_base}/{entry['route']}"
    return urlunsplit(("", "", rendered, parsed.query, parsed.fragment))


def rewrite_internal_links(fragment: str, source: str, entries_by_source: dict[str, dict], site_base: str) -> str:
    def replace(match: re.Match[str]) -> str:
        original = html.unescape(match.group("url"))
        rewritten = resolve_internal_target(source, original, entries_by_source, site_base)
        return f"{match.group('prefix')}{html.escape(rewritten, quote=True)}{match.group('suffix')}"

    return ATTR_RE.sub(replace, fragment)


def breadcrumb_html(route: str, site_base: str) -> str:
    if not route:
        return ""
    pieces = [piece for piece in route.split("/") if piece]
    links = [f'<a href="/{site_base}/">Home</a>']
    accumulated: list[str] = []
    for piece in pieces[:-1]:
        accumulated.append(piece)
        label = piece.replace("-", " ").title()
        links.append(f'<a href="/{site_base}/{"/".join(accumulated)}/">{html.escape(label)}</a>')
    links.append(html.escape(pieces[-1].replace("-", " ").title()))
    return '<nav class="breadcrumbs" aria-label="Breadcrumb">' + "<span aria-hidden=\"true\">/</span>".join(links) + "</nav>"


def render_page(entry: dict, body: str, source_sha: str, site_base: str) -> str:
    title = html.escape(entry["title"])
    source = entry["source"]
    ref = source_sha if re.fullmatch(r"[0-9a-f]{40}", source_sha) and set(source_sha) != {"0"} else "main"
    source_url = f"https://github.com/devs-guide/openai/blob/{ref}/{quote(source)}"
    raw_url = f"/{site_base}/{entry['raw_route']}"
    breadcrumbs = breadcrumb_html(entry["route"], site_base)
    workflow_nav = ""
    if entry["route"].startswith("dot/research/"):
        workflow_nav = f'''<nav class="workflow-nav" aria-label="Research workflow">
      <a href="/{site_base}/dot/research/project/">Project</a>
      <span aria-hidden="true">→</span>
      <a href="/{site_base}/dot/research/internet/">Internet</a>
      <span aria-hidden="true">→</span>
      <a href="/{site_base}/dot/research/data/">Data</a>
      <span aria-hidden="true">→</span>
      <a href="/{site_base}/dot/research/template/">Template</a>
    </nav>
    <nav class="deliverable-nav" aria-label="Optional Research deliverable">
      <span>Optional deliverable:</span>
      <a href="/{site_base}/dot/research/summary/">Summary</a>
    </nav>'''
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{title} · community-maintained devs-guide/openai documentation">
  <meta name="source-commit" content="{html.escape(source_sha)}">
  <title>{title} · devs-guide/openai</title>
  <link rel="stylesheet" href="/{site_base}/assets/site.css">
</head>
<body>
  <a class="skip-link" href="#content">Skip to content</a>
  <header class="site-header">
    <div class="site-header__inner">
      <a class="site-brand" href="/{site_base}/">devs-guide/openai</a>
      <nav aria-label="Primary">
        <a href="/{site_base}/release/">Release</a>
        <a href="/{site_base}/dot/">DOT</a>
        <a href="/{site_base}/dot/agent/">Agent</a>
        <a href="/{site_base}/dot/research/">Research</a>
        <a href="/{site_base}/dot/features/">Features</a>
        <a href="/{site_base}/dot/history/">History</a>
        <a href="/{site_base}/dot/releases/">Releases</a>
      </nav>
    </div>
  </header>
  <main id="content" class="page-shell">
    {breadcrumbs}
    {workflow_nav}
    <div class="document-meta" aria-label="Document status">
      <span>{html.escape(entry['kind'])}</span>
      <span>{html.escape(entry['status'])}</span>
      <span>reviewed {html.escape(entry['reviewed_on'])}</span>
    </div>
    <article>
{body}
    </article>
  </main>
  <footer class="site-footer">
    <p>Community maintained; not affiliated with or endorsed by OpenAI.</p>
    <p><a href="{html.escape(source_url, quote=True)}">Repository source</a> · <a href="{html.escape(raw_url, quote=True)}">Raw source</a></p>
  </footer>
</body>
</html>
"""


def render_redirect(route: str, target: str, title: str, source_sha: str, site_base: str) -> str:
    destination = f"/{site_base}/{target}"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="source-commit" content="{html.escape(source_sha)}">
  <meta http-equiv="refresh" content="0; url={html.escape(destination, quote=True)}">
  <link rel="canonical" href="{html.escape(destination, quote=True)}">
  <title>Moved · {html.escape(title)}</title>
</head>
<body>
  <main id="content">
    <h1>Document moved</h1>
    <p>This route moved to <a href="{html.escape(destination, quote=True)}">{html.escape(title)}</a>.</p>
  </main>
</body>
</html>
"""


def run_pandoc(source: Path) -> str:
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        fail("pandoc is required to build Pages")
    result = subprocess.run(
        [pandoc, "--from=gfm-raw_html", "--to=html5", "--wrap=none", "--section-divs"],
        input=source.read_text(encoding="utf-8"),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail(f"pandoc failed for {source.relative_to(ROOT)}: {result.stderr.strip()}")
    return result.stdout


def render_source(source: Path, content_type: str) -> str:
    if content_type in {"markdown", "prompt"}:
        return run_pandoc(source)
    if content_type == "json":
        try:
            value = json.loads(source.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"invalid JSON in {source.relative_to(ROOT)}: {exc}")
        rendered = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True)
        return f'<pre class="source-json"><code>{html.escape(rendered)}</code></pre>'
    fail(f"unsupported content type: {content_type}")


def output_index_path(publish_dir: Path, route: str) -> Path:
    return publish_dir / route / "index.html" if route else publish_dir / "index.html"


def build(manifest: dict, entries: list[dict], publish_dir: Path, source_sha: str, release_version: str) -> None:
    if publish_dir != (ROOT / "static").resolve():
        fail("publish directory must resolve to the repository's static/ directory")
    if publish_dir.is_symlink():
        fail("publish directory must not be a symlink")
    if publish_dir.exists():
        shutil.rmtree(publish_dir)
    publish_dir.mkdir(parents=True)

    site_base = manifest["site_base"]
    entries_by_source = {entry["source"]: entry for entry in entries}
    route_records: list[dict] = []
    for entry in entries:
        source_path = ROOT / entry["source"]
        body = render_source(source_path, entry["content_type"])
        body = rewrite_internal_links(body, entry["source"], entries_by_source, site_base)
        output_path = output_index_path(publish_dir, entry["route"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_page(entry, body, source_sha, site_base), encoding="utf-8")

        raw_path = publish_dir / entry["raw_route"]
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, raw_path)
        route_records.append(
            {
                "kind": entry["kind"],
                "raw_route": entry["raw_route"],
                "route": entry["route"],
                "source": entry["source"],
                "status": entry["status"],
            }
        )

        for alias in entry["aliases"]:
            alias_path = output_index_path(publish_dir, alias)
            alias_path.parent.mkdir(parents=True, exist_ok=True)
            alias_path.write_text(
                render_redirect(alias, entry["route"], entry["title"], source_sha, site_base),
                encoding="utf-8",
            )
            route_records.append(
                {
                    "kind": "redirect",
                    "redirect_to": entry["route"],
                    "route": alias,
                    "source": entry["source"],
                    "status": "archived",
                }
            )

    for migration in manifest["raw_migrations"]:
        migration_path = publish_dir / migration["route"]
        migration_path.parent.mkdir(parents=True, exist_ok=True)
        replacement_url = f"/{site_base}/{migration['replacement']}"
        migration_path.write_text(
            "This 0.0.1 source moved during the DOT two-lane migration.\n"
            f"Historical source: {migration['historical_url']}\n"
            f"Current replacement: {replacement_url}\n",
            encoding="utf-8",
        )
        route_records.append(
            {
                "kind": "raw-migration",
                "raw_route": migration["route"],
                "redirect_to": migration["replacement"],
                "status": "archived",
            }
        )

    assets = ROOT / "www" / "assets"
    shutil.copytree(assets, publish_dir / "assets")
    (publish_dir / ".nojekyll").write_text("", encoding="utf-8")
    source_record = {
        "repository": "devs-guide/openai",
        "release": release_version,
        "schema_version": 1,
        "source_sha": source_sha,
    }
    (publish_dir / "source.json").write_text(
        json.dumps(source_record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (publish_dir / "routes.json").write_text(
        json.dumps({"routes": route_records, "schema_version": 2}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    digest = hashlib.sha256()
    for path in sorted(publish_dir.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(publish_dir).as_posix().encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    print(f"[www.pages] built {len(entries)} documents into {publish_dir}")
    print(f"[www.pages] tree sha256: {digest.hexdigest()}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    manifest, entries = load_manifest()
    print(f"[publication.manifest][ok] {len(entries)} sources and routes validated")
    if args.validate_only:
        return 0

    publish_value = os.environ.get("PUBLISH_DIR", "static")
    publish_dir = Path(publish_value)
    if not publish_dir.is_absolute():
        publish_dir = ROOT / publish_dir
    source_sha = os.environ.get("SOURCE_SHA", "0" * 40)
    if not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        fail("SOURCE_SHA must be a lowercase 40-character commit SHA")
    release_version = os.environ.get("RELEASE_VERSION", "0.0.6")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", release_version):
        fail("RELEASE_VERSION must be a bare semantic version")
    build(manifest, entries, publish_dir.resolve(), source_sha, release_version)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BuildError as exc:
        print(f"[www.pages][error] {exc}", file=sys.stderr)
        raise SystemExit(1)
