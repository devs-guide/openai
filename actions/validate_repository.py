#!/usr/bin/env python3
"""Validate public source hygiene and import provenance."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys

from release_text import normalize_bytes


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    ".github/workflows/www.pages.remote.yml",
    ".github/workflows/www.pages.yml",
    ".github/workflows/release.yml",
    ".gitignore",
    "COPYRIGHT.md",
    "actions/build_pages.py",
    "actions/audit_dot.py",
    "actions/publication.manifest.json",
    "actions/release.sh",
    "actions/release_text.py",
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
    "docs/history/two-lane-migration.json",
    "docs/history/two-lane-migration.md",
    "docs/releases/0.0.1.md",
    "docs/releases/0.0.2.md",
    "docs/releases/readme.md",
    "dot/ingest.json",
    "dot/readme.md",
    "dot/agent/master.prompt",
    "dot/agent/browser.prompt",
    "dot/agent/config.json",
    "dot/agent/config.schema.json",
    "dot/agent/media.prompt",
    "dot/agent/page.prompt",
    "dot/agent/readme.md",
    "dot/agent/runtime.json",
    "dot/research/internet.prompt",
    "dot/research/data.prompt",
    "dot/research/project.prompt",
    "dot/research/readme.md",
    "dot/research/template.prompt",
    "readme.md",
    "tools/link.prompt.sh",
    "www/assets/site.css",
}
LEGACY_SOURCES = {
    "dot/agents/browser.md",
    "dot/agents/computer.md",
    "dot/agents/doc.md",
    "dot/agents/prompt.md",
    "dot/agents/readme.md",
    "dot/prompts/core/dot.prompt",
    "dot/prompts/core/master.prompt",
    "dot/prompts/core/readme.md",
    "dot/prompts/core/reference.prompt",
    "dot/prompts/readme.md",
    "dot/prompts/research/overview.prompt",
    "dot/prompts/research/readme.md",
    "dot/prompts/research/starter-data-only.md",
    "dot/prompts/research/template.prompt",
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
BROWSER_004_SHA256 = "90b1e4af09e0454208d0b0bd4e7d74c2d031c8b87c7fdd68ffb65927a620520c"
PRESERVED_AGENT_HASHES = {
    "dot/agent/browser.prompt": "b080862884e2e8a88a5d1ff06b7119617decd1a46e85d42493f1b89f4c702ba4",
    "dot/agent/config.json": "940a1b65106af4a2f6e190f414897e55013c108243f0b59b17defd3eefbc5a71",
    "dot/agent/config.schema.json": "9c38de39ec3d2b9db5b7922788d7a8b503c3cdd9151d638c8995877a7ac60815",
    "dot/agent/runtime.json": "d00a0769b220929fea17fbb1dc17e5fa9c07cf3b7e4147a2ae2d55a39095743f",
}
DATA_CATALOG = (
    ("datasets", "dataset_id"),
    ("releases", "release_id"),
    ("sources", "source_id"),
    ("entities", "entity_id"),
    ("geographies", "geography_id"),
    ("categories", "category_id"),
    ("aliases", "alias_id"),
    ("entity_relationships", "entity_relationship_id"),
    ("category_assignments", "category_assignment_id"),
    ("documents", "document_id"),
    ("document_versions", "document_version_id"),
    ("url_occurrences", "url_occurrence_id"),
    ("access_events", "access_event_id"),
    ("source_assertions", "source_assertion_id"),
    ("observations", "observation_id"),
    ("claims", "claim_id"),
    ("evidence_links", "evidence_link_id"),
    ("review_queue", "review_item_id"),
    ("corrections", "correction_id"),
    ("release_changes", "release_change_id"),
    ("validation_results", "validation_result_id"),
    ("manifest", "manifest_file_id"),
)
DATA_SCENARIOS = {
    "blocked-source": ("blocked", "uncited", "reviewed"),
    "discovered-unreviewed-url": ("discovered", "opened", "reviewed", "cited"),
    "temporal-many-to-many": ("dated relation", "period"),
    "nullable-foreign-key": ("nullable foreign key", "controlled reason"),
    "mixed-age-allocation": ("unknown eligible share", "no invented central estimate"),
    "unresolved-interentity-payment": ("recipient id is null", "unresolved_entity"),
    "human-model-review": ("human", "model-assisted", "material gate"),
    "post-release-correction": ("successor release", "snapshot unchanged"),
}
INGEST_INSTRUCTIONS = (
    ("dot/agent/master.prompt", "AGENT_CONTRACT", "REQUIRED", None),
    ("dot/agent/config.json", "CONFIGURATION", "REQUIRED", None),
    ("dot/agent/runtime.json", "DATED_OBSERVATION", "REQUIRED", None),
    ("dot/agent/browser.prompt", "CAPABILITY_MODULE", "REQUIRED", "INTERNET_RESEARCH"),
    ("dot/agent/page.prompt", "CAPABILITY_MODULE", "CONDITIONAL", "PAGE_ACTION_OR_DESTINATION"),
    ("dot/agent/media.prompt", "CAPABILITY_MODULE", "CONDITIONAL", "AUDIOVISUAL_EVIDENCE"),
    ("dot/research/project.prompt", "RESEARCH_CONTRACT", "REQUIRED", None),
    ("dot/research/internet.prompt", "RESEARCH_CONTRACT", "REQUIRED", None),
    ("dot/research/data.prompt", "RESEARCH_CONTRACT", "REQUIRED", None),
    ("dot/research/template.prompt", "TEMPLATE", "REQUIRED", None),
)
INGEST_SUPPORTING = (
    ("dot/readme.md", "PRODUCT_ENTRYPOINT"),
    ("dot/agent/readme.md", "AGENT_NAVIGATION"),
    ("dot/agent/config.schema.json", "CONFIGURATION_SCHEMA"),
    ("dot/research/readme.md", "RESEARCH_NAVIGATION"),
)


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


def prompt_section(text: str, rule_id: str) -> str:
    marker = f"## {rule_id}"
    start = text.find(marker)
    if start < 0:
        fail(f"canonical prompt section is missing: {rule_id}")
    following = re.search(r"^## [A-Z]+-[0-9]{3}\b", text[start + len(marker) :], re.MULTILINE)
    if following is None:
        return text[start:]
    end = start + len(marker) + following.start()
    return text[start:end]


def validate_preserved_agent_sources() -> None:
    for relative, expected in PRESERVED_AGENT_HASHES.items():
        observed = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if observed != expected:
            fail(f"preserved Agent source changed: {relative}")

    browser_text = (ROOT / "dot" / "agent" / "browser.prompt").read_text(encoding="utf-8")
    browser_004 = prompt_section(browser_text, "BROWSER-004")
    observed = hashlib.sha256(browser_004.encode()).hexdigest()
    if observed != BROWSER_004_SHA256:
        fail("BROWSER-004 differs from the approved intentional behavior")

    page_text = re.sub(
        r"\s+", " ", (ROOT / "dot" / "agent" / "page.prompt").read_text(encoding="utf-8")
    )
    media_text = re.sub(
        r"\s+", " ", (ROOT / "dot" / "agent" / "media.prompt").read_text(encoding="utf-8")
    )
    for required in ("distinguish draft and complete material", "publication receipt", "readback"):
        if required not in page_text:
            fail(f"Page contract lacks required delivery distinction: {required}")
    for required in ("derived and fallible extraction layer", "source-provided transcripts distinctly"):
        if required not in media_text:
            fail(f"Media contract lacks required transcript distinction: {required}")
    ok("Agent configuration, Browser behavior, Page delivery, and media distinctions are preserved")


def validate_fact_pair_example(template_text: str) -> None:
    section = prompt_section(template_text, "TEMPLATE-006")
    json_match = re.search(r"```json\n(.*?)\n```", section, re.DOTALL)
    csv_match = re.search(r"```csv\n(.*?)\n```", section, re.DOTALL)
    if json_match is None or csv_match is None:
        fail("Template paired release-view example is incomplete")
    try:
        json_rows = json.loads(json_match.group(1))
    except json.JSONDecodeError as exc:
        fail(f"Template paired JSON example is invalid: {exc}")
    reader = csv.DictReader(io.StringIO(csv_match.group(1)))
    csv_rows = list(reader)
    if not isinstance(json_rows, list) or not json_rows or len(json_rows) != len(csv_rows):
        fail("Template paired example row counts differ")
    headers = reader.fieldnames or []
    for index, (json_row, csv_row) in enumerate(zip(json_rows, csv_rows), 1):
        if not isinstance(json_row, dict) or list(json_row) != headers:
            fail(f"Template paired example fields differ at row {index}")
        for field in headers:
            json_value = json_row[field]
            expected_csv = "" if json_value is None else str(json_value).lower() if isinstance(json_value, bool) else str(json_value)
            if csv_row[field] != expected_csv:
                fail(f"Template paired example logical value differs at row {index}, field {field}")
    if not any(row.get("value") is None and row.get("null_reason") for row in json_rows):
        fail("Template paired example does not preserve null plus reason semantics")
    ok("synthetic CSV/JSON release view preserves fields, values, ordering, and null semantics")


def validate_data_contract() -> None:
    data_path = ROOT / "dot" / "research" / "data.prompt"
    template_path = ROOT / "dot" / "research" / "template.prompt"
    data_text = data_path.read_text(encoding="utf-8")
    template_text = template_path.read_text(encoding="utf-8")

    catalog_section = prompt_section(data_text, "DATA-002")
    catalog_rows = re.findall(
        r"^\|\s*[0-9]+\s*\|\s*`([a-z_]+)`\s*\|.*?\|\s*`([a-z_]+)`\s*\|",
        catalog_section,
        re.MULTILINE,
    )
    if tuple(catalog_rows) != DATA_CATALOG:
        fail("Data paired-file catalog differs from the approved 22-basename order or key ownership")
    if len({basename for basename, _ in catalog_rows}) != len(DATA_CATALOG):
        fail("Data paired-file catalog contains a duplicate basename")

    layer_basenames = {
        "documents",
        "document_versions",
        "url_occurrences",
        "access_events",
        "source_assertions",
        "observations",
        "claims",
        "evidence_links",
    }
    if not layer_basenames.issubset({basename for basename, _ in catalog_rows}):
        fail("Data provenance layers are not represented by distinct basenames")

    scenario_section = prompt_section(data_text, "DATA-008")
    observed_scenarios = dict(
        re.findall(r"^\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|$", scenario_section, re.MULTILINE)
    )
    if set(observed_scenarios) != set(DATA_SCENARIOS):
        fail("Data acceptance scenarios are incomplete or contain undeclared cases")
    for scenario_id, required_terms in DATA_SCENARIOS.items():
        normalized = observed_scenarios[scenario_id].lower()
        if any(term not in normalized for term in required_terms):
            fail(f"Data acceptance scenario lacks required semantics: {scenario_id}")

    release_section = prompt_section(data_text, "DATA-009")
    normalized_release = re.sub(r"\s+", " ", release_section)
    for required in (
        "Never mutate or overwrite an accepted release",
        "creates a new immutable release",
        "publication receipt and readback result",
    ):
        if required not in normalized_release:
            fail(f"Data release contract lacks required behavior: {required}")

    combined = data_text + "\n" + template_text
    for required in (
        "OBSERVED",
        "DERIVED",
        "INFERRED",
        "verification_status",
        "reviewer_type",
        "unknown_historical_time",
        "precision-preserving numeric string",
    ):
        if required not in combined:
            fail(f"Data and Template contracts lack required term: {required}")

    validate_fact_pair_example(template_text)
    ok("Data owns 22 unique paired basenames, distinct provenance layers, and all acceptance scenarios")


def validate_ingest_contract() -> None:
    ingest_path = ROOT / "dot" / "ingest.json"
    try:
        ingest = json.loads(ingest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid DOT ingestion manifest: {exc}")

    expected_identity = {
        "schema": "dot-ingest/1",
        "release": "0.0.2",
        "baseline_tag": "0.0.1",
        "entrypoint": "dot/readme.md",
        "manifest_authority": "ROUTING_METADATA_ONLY",
        "rights": "OWNER_OR_SEPARATELY_AUTHORIZED_USE_ONLY",
        "activation_gate": "PROJECT_CONTROL_PACKET_READY",
        "topic_input": "OWNER_SUPPLIED_PROJECT_BRIEF",
    }
    for field, expected in expected_identity.items():
        if ingest.get(field) != expected:
            fail(f"DOT ingestion manifest has incorrect {field}")

    rows = ingest.get("instruction_files")
    if not isinstance(rows, list) or len(rows) != len(INGEST_INSTRUCTIONS):
        fail("DOT ingestion manifest has an incorrect instruction-file count")
    observed_paths: list[str] = []
    for order, (row, expected) in enumerate(zip(rows, INGEST_INSTRUCTIONS), 1):
        if not isinstance(row, dict):
            fail(f"DOT ingestion instruction row {order} is not an object")
        path, authority_class, activation, condition = expected
        expected_fields = {
            "order": order,
            "path": path,
            "authority_class": authority_class,
            "activation": activation,
            "condition": condition,
        }
        for field, value in expected_fields.items():
            if row.get(field) != value:
                fail(f"DOT ingestion instruction row {order} has incorrect {field}")
        full = ROOT / path
        if not full.is_file():
            fail(f"DOT ingestion instruction file is missing: {path}")
        digest = hashlib.sha256(full.read_bytes()).hexdigest()
        if row.get("sha256") != digest:
            fail(f"DOT ingestion hash differs for {path}")
        observed_paths.append(path)
    if len(set(observed_paths)) != len(observed_paths):
        fail("DOT ingestion manifest repeats an instruction file")

    supporting = ingest.get("supporting_files")
    if not isinstance(supporting, list):
        fail("DOT ingestion supporting files must be an array")
    observed_supporting = tuple(
        (row.get("path"), row.get("role")) for row in supporting if isinstance(row, dict)
    )
    if observed_supporting != INGEST_SUPPORTING:
        fail("DOT ingestion supporting files differ from the approved inventory")
    for path, _ in INGEST_SUPPORTING:
        if not (ROOT / path).is_file():
            fail(f"DOT ingestion supporting file is missing: {path}")

    if ingest.get("non_instruction_prefixes") != [".github/", "actions/", "docs/", "www/"]:
        fail("DOT ingestion non-instruction prefixes differ")
    if ingest.get("superseded_prefixes") != ["dot/agents/", "dot/prompts/"]:
        fail("DOT ingestion superseded prefixes differ")

    master = (ROOT / "dot" / "agent" / "master.prompt").read_text(encoding="utf-8")
    project = (ROOT / "dot" / "research" / "project.prompt").read_text(encoding="utf-8")
    template = (ROOT / "dot" / "research" / "template.prompt").read_text(encoding="utf-8")
    for term in ("connected-app context", "not project evidence"):
        if term not in master:
            fail(f"Agent contract lacks ingestion boundary: {term}")
    for term in ("ingestion receipt", "missing or truncated content", "actually verified"):
        if term not in project:
            fail(f"Project contract lacks ingestion receipt requirement: {term}")
    for term in ("Ingest a tagged release and initialize", "dot/ingest.json", "OWNER_TOPIC_BRIEF"):
        if term not in template:
            fail(f"Template lacks release-ingestion bootstrap: {term}")
    ok("DOT release ingestion order, authority classes, hashes, and activation gate are valid")


def validate_release_workflow() -> None:
    reviewed = b"## Release\n\nReviewed body.\n"
    terminal_variants = (
        b"## Release\n\nReviewed body.\n\n",
        b"## Release\r\n\r\nReviewed body.\r\n",
        b"## Release\r\rReviewed body.\r\r",
    )
    expected = normalize_bytes(reviewed)
    if any(normalize_bytes(value) != expected for value in terminal_variants):
        fail("release-body normalization does not accept line-ending or terminal-newline variants")
    if normalize_bytes(b"## Release\n\nChanged body.\n") == expected:
        fail("release-body normalization hides an internal content change")

    release_script = (ROOT / "actions" / "release.sh").read_text(encoding="utf-8")
    for required in (
        "0.0.1 is the published immutable baseline",
        "release_text.py",
        "existing release is already published",
        "existing draft target differs",
        "converged and verified draft",
    ):
        if required not in release_script:
            fail(f"release workflow lacks required safeguard: {required}")
    ok("release text comparison is newline-tolerant, content-strict, and draft-convergent")


def main() -> int:
    paths = included_paths()
    path_set = set(paths)
    missing = sorted(path for path in REQUIRED if path not in path_set or not (ROOT / path).is_file())
    if missing:
        fail("required public files are missing: " + ", ".join(missing))
    ok("required public source, workflow, and policy files exist")

    stale_candidate = "0." + "1.0"
    for path in paths:
        full = ROOT / path
        if stale_candidate in path:
            fail(f"stale candidate version remains in path: {path}")
        if not full.is_file() or full.suffix.lower() not in {".json", ".md", ".prompt", ".py", ".sh", ".yml", ".yaml"}:
            continue
        try:
            text = full.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if stale_candidate in text:
            fail(f"stale candidate version remains in source: {path}")
    ok("candidate release identity is consistently 0.0.2")

    if any(path.startswith("static/") for path in paths):
        fail("generated static output must not be included on main")
    if "dot/prompt" in path_set or any(path.startswith("dot/prompt/") for path in paths):
        fail("private singular prompt workspace is included in public source")
    if "dot/dot.master.00.prompt" in path_set:
        fail("byte-identical local master duplicate is included in public source")
    if any(path.startswith(("dot/agents/", "dot/prompts/")) for path in paths):
        fail("superseded pre-0.0.2 DOT prompt or agent tree is included in current source")
    retired_intake_prefix = "dot/" + "handoff" + "/"
    if any(path.startswith(retired_intake_prefix) for path in paths):
        fail("retired research intake artifacts are included in current source")
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
        result = subprocess.run(
            ["git", "show", f"0.0.1:{path}"],
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        if result.returncode != 0:
            fail(f"immutable 0.0.1 artifact is missing: {path}")
        observed = hashlib.sha256(result.stdout).hexdigest()
        if observed != expected:
            fail(f"immutable 0.0.1 artifact hash differs: {path}")
    ok("all original imported bodies remain recoverable with their recorded SHA-256 values")

    migration_path = ROOT / "docs" / "history" / "two-lane-migration.json"
    try:
        migration = json.loads(migration_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid two-lane migration ledger: {exc}")
    if migration.get("baseline_tag") != "0.0.1" or migration.get("release") != "0.0.2":
        fail("two-lane migration ledger has incorrect release identity")
    if migration.get("unresolved_conflicts") != []:
        fail("two-lane migration ledger contains unresolved conflicts")
    migration_sources = migration.get("sources")
    if not isinstance(migration_sources, list):
        fail("two-lane migration sources must be an array")
    listed_sources = [record.get("source") for record in migration_sources if isinstance(record, dict)]
    if set(listed_sources) != LEGACY_SOURCES or len(listed_sources) != len(LEGACY_SOURCES):
        fail("two-lane migration ledger does not map each legacy source exactly once")
    for record in migration_sources:
        dispositions = record.get("dispositions")
        targets = record.get("targets")
        if not isinstance(dispositions, list) or not dispositions:
            fail(f"migration dispositions are missing for {record.get('source')}")
        if not isinstance(targets, list) or not targets:
            fail(f"migration targets are missing for {record.get('source')}")
        allowed_dispositions = {
            "KEEP_AGENT",
            "KEEP_PROJECT",
            "KEEP_INTERNET",
            "KEEP_DATA",
            "KEEP_TEMPLATE",
            "MERGE",
            "HISTORY_ONLY",
            "DROP_REDUNDANT",
        }
        if any(disposition not in allowed_dispositions for disposition in dispositions):
            fail(f"migration disposition is invalid for {record.get('source')}")
        has_data_target = "dot/research/data.prompt" in targets
        if has_data_target != ("KEEP_DATA" in dispositions):
            fail(f"migration Data ownership is inconsistent for {record.get('source')}")
        for target in targets:
            if target not in path_set or not (ROOT / target).is_file():
                fail(f"migration target is missing: {target}")
    ok("two-lane migration ledger maps every legacy source to current owners")

    config = json.loads((ROOT / "dot" / "agent" / "config.json").read_text(encoding="utf-8"))
    if config.get("models", {}).get("policy") != "ORDERED_FALLBACK":
        fail("agent model policy must be ORDERED_FALLBACK")
    expected_fallbacks = [
        {"model": "GPT-5.6 Sol", "effort": "Extra High"},
        {"model": "GPT-5.6 Sol", "effort": "Max"},
        {"model": "GPT-5.6 Luna", "effort": "Extra High"},
        {"model": "GPT-5.6 Luna", "effort": "High"},
        {"model": "GPT-5.6 Luna", "effort": "Max"},
        {"model": "GPT-6.1 Sol", "effort": "Medium"},
        {"model": "GPT-6.1 Sol", "effort": "High"},
    ]
    if config.get("models", {}).get("primary") != {"model": "GPT-6 Astra", "effort": "assigned"}:
        fail("agent primary model differs from the approved configuration")
    if config.get("models", {}).get("collaborator") != {"model": "GPT-5.6 Sol", "effort": "High"}:
        fail("agent collaborator differs from the approved configuration")
    if config.get("models", {}).get("fallbacks") != expected_fallbacks:
        fail("agent model fallback order differs from the approved sequence")
    if config.get("execution", {}).get("default_surface") != "cloud-browser":
        fail("agent execution must default to cloud-browser")
    prohibited = set(config.get("execution", {}).get("prohibited", []))
    if not {"codex", "software-installation", "unassigned-model"}.issubset(prohibited):
        fail("agent configuration lacks required prohibitions")
    if config.get("tools", {}).get("project_allowlist_required") is not True:
        fail("cloud-computer tools must require a project allowlist")
    ok("agent configuration preserves ordered models and browser-first tool boundaries")

    validate_preserved_agent_sources()
    validate_data_contract()
    validate_ingest_contract()
    validate_release_workflow()

    canonical_paths = sorted((ROOT / "dot" / "agent").glob("*.prompt")) + sorted(
        (ROOT / "dot" / "research").glob("*.prompt")
    )
    canonical_text = "\n".join(path.read_text(encoding="utf-8") for path in canonical_paths)
    stale_authority = (
        "Use GPT-5.6 Sol High",
        "GPT-5.6-only",
        "CURRENT DATA-HANDOFF RESTRICTION",
        "chatgpt.com/space/",
    )
    for phrase in stale_authority:
        if phrase.lower() in canonical_text.lower():
            fail(f"stale prior-project authority entered a canonical contract: {phrase}")
    ok("prior-project model claims, links, and temporary authority are absent from canonical contracts")

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
        retired_reference = "handoff" + "/"
        if retired_reference in text:
            fail(f"retired research intake path is referenced by {path}")
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
