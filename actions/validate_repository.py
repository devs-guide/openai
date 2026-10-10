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
    "docs/release.prompt",
    "docs/releases/0.0.1.md",
    "docs/releases/0.0.2.md",
    "docs/releases/0.0.3.md",
    "docs/releases/0.0.4.md",
    "docs/releases/0.0.5.md",
    "docs/releases/0.0.6.md",
    "docs/releases/0.0.7.md",
    "docs/releases/readme.md",
    "dot/ingest.json",
    "dot/readme.md",
    "dot/agent/master.prompt",
    "dot/agent/browser.prompt",
    "dot/agent/config.json",
    "dot/agent/config.schema.json",
    "dot/agent/media.prompt",
    "dot/agent/page.prompt",
    "dot/agent/progress.prompt",
    "dot/agent/readme.md",
    "dot/agent/runtime.json",
    "dot/agent/storage.prompt",
    "dot/research/internet.prompt",
    "dot/research/data.prompt",
    "dot/research/project.prompt",
    "dot/research/readme.md",
    "dot/research/summary.prompt",
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
SUMMARY_SCENARIOS = {
    "missing-contact-resource": (
        "names, physical or mailing addresses",
        "public email addresses",
        "outbound links",
        "externally hosted resources",
    ),
    "blank-or-blocked-route": ("blank javascript search shell", "blocked route"),
    "explicit-source-limit": ("explicitly_source_limited", "complete_with_gaps"),
    "shared-resource-attribution": ("shared resource as exclusive to one entity",),
    "immutable-successor": ("keep those inputs immutable", "successor dataset release"),
    "three-format-export": ("csv, json, or markdown activates all three release views",),
    "review-independence": ("distinct self-review pass", "not independent"),
    "all-entity-coverage": (
        "reconcile the eligible entity or subject universe",
        "sampling cannot support a claim that every requested entity was checked",
    ),
}
TABS_SCENARIOS = {
    "default-four": ("four counted tabs open", "a fifth request"),
    "override-two": ("a project limit of two", "a third request remains queued"),
    "override-six": ("a project limit of six", "not six per worker"),
    "contended-slot": ("two workers requesting the final slot", "one reservation and one queued request"),
    "unknown-inventory": ("an `unknown` global count", "prevents another tab from opening"),
    "protected-tab": ("an authentication, unsaved-form, active-download, takeover, or leased tab", "not closed for capacity"),
    "scheduled-check": ("15-minute receipt, timezone, project id, and next run are verified", "active only after"),
    "event-fallback": ("disclosed event-driven checks", "no automation claim"),
    "pause-or-end": ("schedule is paused or removed", "resumable state is retained"),
    "observed-cause": ("does not invent a memory, cpu, browser, or website cause",),
    "sensitive-state": ("exported records omit credentials", "sensitive authentication routes"),
    "captcha": ("actual captcha encounter follows unchanged `browser-004`",),
}
STORAGE_SCENARIOS = {
    "probe-failure": ("failed save or readback", "blocks substantive dependent work"),
    "ordinary-file-integrity": ("byte length and sha-256",),
    "native-document-integrity": ("without an invented checksum",),
    "output-before-review": ("persistently saved and verified as unreviewed",),
    "manifest-recovery": ("latest verified checkpoint",),
    "existing-purpose-location": ("reused without creating a duplicate",),
    "new-purpose-location": ("creates, probes, registers, and verifies",),
    "purpose-name-conflict": ("more precise functional term",),
    "cross-project-separation": ("distinct project ids", "recovery manifests"),
    "full-capacity": ("new work is `local only`",),
    "wip-not-delivery": ("not delivered or recipient-access confirmed",),
    "archive-integrity": ("missing member, bad hash, or extraction failure",),
    "post-upload-mismatch": ("does not replace its predecessor",),
    "self-hash-prevention": ("completed zip digest is recorded externally",),
    "cleanup-permission": ("compression alone never removes",),
}
PROGRESS_SCENARIOS = {
    "scheduled-project-check": ("id, timezone, project id, enabled state, and next run",),
    "scheduler-unavailable": ("event-driven monitoring", "no recurring-automation claim"),
    "disabled-schedule": ("remains disabled until explicitly authorized",),
    "overlap-attempt": ("no duplicate research run starts",),
    "healthy-long-task": ("`healthy_running` rather than `#lazy`",),
    "unknown-task-state": ("`progress_unknown`", "inspected before intervention"),
    "confirmed-lazy": ("`lazy_confirmed` and triggers recovery",),
    "unchanged-blocker": ("not progress", "permitted alternative"),
    "external-dependency": ("`blocked_external`", "independent useful work continues"),
    "unsaved-output": ("cannot establish progress or completion",),
    "pause-or-complete": ("applicable project schedule is disabled",),
}
INGEST_INSTRUCTIONS = (
    ("dot/agent/master.prompt", "AGENT_CONTRACT", "REQUIRED", None),
    ("dot/agent/config.json", "CONFIGURATION", "REQUIRED", None),
    ("dot/agent/runtime.json", "DATED_OBSERVATION", "REQUIRED", None),
    ("dot/agent/storage.prompt", "CAPABILITY_MODULE", "REQUIRED", None),
    ("dot/agent/progress.prompt", "CAPABILITY_MODULE", "REQUIRED", None),
    ("dot/agent/browser.prompt", "CAPABILITY_MODULE", "REQUIRED", "INTERNET_RESEARCH"),
    ("dot/agent/page.prompt", "CAPABILITY_MODULE", "CONDITIONAL", "PAGE_ACTION_OR_DESTINATION"),
    ("dot/agent/media.prompt", "CAPABILITY_MODULE", "CONDITIONAL", "AUDIOVISUAL_EVIDENCE"),
    ("dot/research/project.prompt", "RESEARCH_CONTRACT", "REQUIRED", None),
    ("dot/research/internet.prompt", "RESEARCH_CONTRACT", "REQUIRED", None),
    ("dot/research/data.prompt", "RESEARCH_CONTRACT", "REQUIRED", None),
    ("dot/research/template.prompt", "TEMPLATE", "REQUIRED", None),
    ("dot/research/summary.prompt", "RESEARCH_CONTRACT", "CONDITIONAL", "ON_DEMAND_SUBTOPIC_EXECUTIVE_BRIEF"),
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
    ok("Agent runtime, intentional BROWSER-004 behavior, Page delivery, and media distinctions are preserved")


def validate_storage_progress_contract() -> None:
    master = (ROOT / "dot" / "agent" / "master.prompt").read_text(encoding="utf-8")
    storage = (ROOT / "dot" / "agent" / "storage.prompt").read_text(encoding="utf-8")
    progress = (ROOT / "dot" / "agent" / "progress.prompt").read_text(encoding="utf-8")
    project = (ROOT / "dot" / "research" / "project.prompt").read_text(encoding="utf-8")
    internet = (ROOT / "dot" / "research" / "internet.prompt").read_text(encoding="utf-8")
    template = (ROOT / "dot" / "research" / "template.prompt").read_text(encoding="utf-8")
    summary = (ROOT / "dot" / "research" / "summary.prompt").read_text(encoding="utf-8")
    config = json.loads((ROOT / "dot" / "agent" / "config.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "dot" / "agent" / "config.schema.json").read_text(encoding="utf-8"))

    if "**Contract:** `dot-agent/2`" not in master:
        fail("Agent contract version is not dot-agent/2")
    if "**Contract:** `dot-research-project/2`" not in project:
        fail("Project contract version is not dot-research-project/2")
    storage_rules = re.findall(r"^## (STORAGE-[0-9]{3})\b", storage, re.MULTILINE)
    if storage_rules != [f"STORAGE-{number:03d}" for number in range(1, 13)]:
        fail("Storage contract must define STORAGE-001 through STORAGE-012 in order")
    progress_rules = re.findall(r"^## (PROGRESS-[0-9]{3})\b", progress, re.MULTILINE)
    if progress_rules != [f"PROGRESS-{number:03d}" for number in range(1, 9)]:
        fail("Progress contract must define PROGRESS-001 through PROGRESS-008 in order")

    required_storage = {
        "STORAGE-001": ("`#storage` owns persistence", "`agent:storage` default"),
        "STORAGE-002": ("`ephemeral_untrusted`", "save a small nonsensitive probe", "reopen or download"),
        "STORAGE-003": ("save every completed source capture", "periodic health check audits"),
        "STORAGE-004": ("byte length and sha-256", "revision/content readback", "delivery accepted"),
        "STORAGE-005": ("save evidence before analysis", "stable artifact ids"),
        "STORAGE-006": ("safe canonical url", "never replace a missing value with zero"),
        "STORAGE-007": ("persistently saved, versioned project recovery manifest", "avoid self-hash cycles"),
        "STORAGE-008": ("never overwrite or delete the only verified copy", "common logical source version"),
        "STORAGE-009": ("immutable zip successor", "submitted research prompts and captured visible replies"),
        "STORAGE-010": ("after upload, retrieve the saved zip", "retain two free slots"),
        "STORAGE-011": ("`agent:<term>`", "reuse a suitable verified location first", "wip file in `agent:pdf` remains undelivered"),
        "STORAGE-012": ("latest verified persistent checkpoint", "compression authorizes packaging, not deletion"),
    }
    for rule_id, phrases in required_storage.items():
        section = re.sub(r"\s+", " ", prompt_section(storage, rule_id)).lower()
        for phrase in phrases:
            if phrase not in section:
                fail(f"Storage contract lacks required {rule_id} behavior: {phrase}")

    required_progress = {
        "PROGRESS-001": ("own the task through delivery", "one agent is expected per account"),
        "PROGRESS-002": ("every 15 minutes", "*/15 * * * *", "one project-specific health check", "project lease"),
        "PROGRESS-003": ("generated-but-unsaved file", "progress_unknown"),
        "PROGRESS-004": ("`#lazy` is an operational recovery state", "lazy_confirmed", "elapsed time"),
        "PROGRESS-005": ("denied file must not be retrieved", "changed condition"),
        "PROGRESS-006": ("`prepared`, `submitted`, `answered`, and `tested`", "never treat an advisory answer as factual evidence"),
        "PROGRESS-007": ("routine all-clear checks in the log", "cumulative captcha totals"),
        "PROGRESS-008": ("disable or remove only its authorized health check", "recoverability from verified checkpoints"),
    }
    for rule_id, phrases in required_progress.items():
        section = re.sub(r"\s+", " ", prompt_section(progress, rule_id)).lower()
        for phrase in phrases:
            if phrase not in section:
                fail(f"Progress contract lacks required {rule_id} behavior: {phrase}")

    for contract_name, contract_text, scenarios in (
        ("Storage", storage, STORAGE_SCENARIOS),
        ("Progress", progress, PROGRESS_SCENARIOS),
    ):
        rows = dict(re.findall(r"^\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|$", contract_text, re.MULTILINE))
        if set(rows) != set(scenarios):
            fail(f"{contract_name} acceptance scenarios are incomplete or contain undeclared cases")
        for scenario_id, phrases in scenarios.items():
            normalized = rows[scenario_id].lower()
            for phrase in phrases:
                if phrase not in normalized:
                    fail(f"{contract_name} acceptance scenario lacks required behavior: {scenario_id}: {phrase}")

    if config.get("schema") != "dot-agent-config/3":
        fail("Agent configuration is not dot-agent-config/3")
    expected_health = {
        "scheduled_interval_minutes": 15,
        "suggested_cron": "*/15 * * * *",
        "timezone_required": True,
        "scheduler_policy": "WHEN_AVAILABLE_AND_AUTHORIZED",
        "fallback": "EVENT_DRIVEN",
        "scope": "ACTIVE_PROJECT",
        "project_schedule_limit": 1,
        "overlap_policy": "INSPECT_HEALTHY_RUN",
        "event_triggers": [
            "TASK_START_OR_RESUME",
            "WORKER_HANDOFF",
            "BEFORE_RISKY_OPERATION",
            "AFTER_CRASH_OR_TOOL_FAILURE",
        ],
    }
    if config.get("progress", {}).get("health_checks") != expected_health:
        fail("Agent health-check configuration differs from the approved cron-style branch")
    if config.get("progress", {}).get("lazy") != {
        "owner": "#PROGRESS",
        "requires_observed_inactivity": True,
        "requires_executable_authorized_action": True,
        "elapsed_time_alone_is_sufficient": False,
    }:
        fail("Agent #LAZY configuration differs from the approved evidence gate")

    storage_config = config.get("storage", {})
    required_storage_config = {
        "working_storage_class": "EPHEMERAL_UNTRUSTED",
        "durable_destination": "agent:storage",
        "project_override_allowed": True,
        "verify_before_use": True,
        "readback_required": True,
        "native_document_integrity": "REVISION_AND_CONTENT_READBACK",
        "recovery_manifest_required": True,
        "version_policy": "IMMUTABLE_SUCCESSORS",
    }
    if any(storage_config.get(field) != value for field, value in required_storage_config.items()):
        fail("Agent Storage defaults differ from the approved configuration")
    if storage_config.get("file_integrity") != {"byte_count_required": True, "checksum": "SHA-256"}:
        fail("Agent file-integrity configuration is incomplete")
    if storage_config.get("research_archives") != {
        "required": True,
        "format": "ZIP",
        "pre_upload_extraction_required": True,
        "post_upload_download_required": True,
        "planning_reserve_slots": 2,
    }:
        fail("Agent Research archive configuration is incomplete")
    purpose = storage_config.get("purpose_locations", {})
    if purpose != {
        "creation_policy": "NEED_BASED_AUTOMATIC",
        "reuse_policy": "REUSE_VERIFIED_MATCH_FIRST",
        "destination_kinds": ["LOCATION", "PROJECT"],
        "title_pattern": "^agent:[a-z][a-z0-9-]*$",
        "scope": "SHARED_BY_FUNCTION_ACROSS_PROJECTS",
        "registry_required": True,
        "sharing_or_deletion_authorized": False,
    }:
        fail("Agent purpose-location configuration differs from the approved policy")
    if storage_config.get("preservation_states") != [
        "LOCAL ONLY", "SAVED BUT UNVERIFIED", "PERSISTENTLY SAVED AND VERIFIED", "VALIDATED"
    ]:
        fail("Agent preservation-state sequence is incorrect")
    if storage_config.get("delivery_states") != ["NOT DELIVERED", "DELIVERED", "DELIVERY ACCEPTED"]:
        fail("Agent delivery-state sequence is incorrect")

    if schema.get("properties", {}).get("schema", {}).get("const") != "dot-agent-config/3":
        fail("Agent configuration schema does not require dot-agent-config/3")
    if not {"storage", "progress", "browser"}.issubset(schema.get("required", [])):
        fail("Agent configuration schema does not require Storage, Progress, and Browser")
    normalized_schema = json.dumps(schema, sort_keys=True)
    for required in (
        "agent:storage", "EPHEMERAL_UNTRUSTED", "*/15 * * * *",
        "INSPECT_HEALTHY_RUN", "NEED_BASED_AUTOMATIC", "IMMUTABLE_SUCCESSORS",
    ):
        if required not in normalized_schema:
            fail(f"Agent configuration schema lacks required Storage/Progress constant: {required}")

    combined = re.sub(r"\s+", " ", "\n".join((master, project, internet, template, summary))).lower()
    for required in (
        "`#storage`", "`#files`", "`#progress`", "`#lazy`",
        "recovery manifest", "health-check", "immutable research zip",
    ):
        if required not in combined:
            fail(f"Agent and Research integration lacks required term: {required}")

    prohibited = (
        "agent:" + "edu",
        "agent:" + "prompts",
        "bjc:" + "health",
        "agent:" + "bjc-heath",
        "bcj:" + "employees",
    )
    canonical = (master + storage + progress + project + internet + template + summary).lower()
    if any(value in canonical for value in prohibited):
        fail("project-specific destination or scope entered the reusable contracts")
    ok("Storage and Progress own verified persistence, purpose locations, cron-style checks, and #LAZY recovery")


def validate_tabs_contract() -> None:
    master = (ROOT / "dot" / "agent" / "master.prompt").read_text(encoding="utf-8")
    browser = (ROOT / "dot" / "agent" / "browser.prompt").read_text(encoding="utf-8")
    config = json.loads((ROOT / "dot" / "agent" / "config.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "dot" / "agent" / "config.schema.json").read_text(encoding="utf-8"))

    if config.get("schema") != "dot-agent-config/3":
        fail("Agent configuration is not dot-agent-config/3")
    expected_tabs = {
        "default_max_open": 4,
        "limit_scope": "ALL_WINDOWS_AND_WORKERS",
        "project_override_allowed": True,
        "blocker_checks": {"inherit_from": "progress.health_checks"},
    }
    if config.get("browser", {}).get("tabs") != expected_tabs:
        fail("Agent Browser/Tabs defaults differ from the approved configuration")

    if schema.get("properties", {}).get("schema", {}).get("const") != "dot-agent-config/3":
        fail("Agent configuration schema does not require dot-agent-config/3")
    if "browser" not in schema.get("required", []):
        fail("Agent configuration schema does not require Browser configuration")
    browser_schema = schema.get("properties", {}).get("browser", {})
    tabs_schema = browser_schema.get("properties", {}).get("tabs", {})
    if browser_schema.get("required") != ["tabs"]:
        fail("Agent configuration schema does not require exactly one Browser/Tabs domain")
    expected_tab_fields = [
        "default_max_open", "limit_scope", "project_override_allowed", "blocker_checks"
    ]
    if tabs_schema.get("required") != expected_tab_fields:
        fail("Agent configuration schema does not require every Browser/Tabs field")
    max_schema = tabs_schema.get("properties", {}).get("default_max_open", {})
    if max_schema.get("type") != "integer" or max_schema.get("minimum") != 1:
        fail("Agent configuration schema does not constrain tab limits to positive integers")
    blocker_schema = tabs_schema.get("properties", {}).get("blocker_checks", {})
    if blocker_schema.get("required") != ["inherit_from"]:
        fail("Agent configuration schema does not link Browser checks to Progress")
    schema_constants = {
        "limit_scope": tabs_schema.get("properties", {}).get("limit_scope", {}).get("const"),
        "project_override_allowed": tabs_schema.get("properties", {}).get("project_override_allowed", {}).get("const"),
        "inherit_from": blocker_schema.get("properties", {}).get("inherit_from", {}).get("const"),
    }
    if schema_constants != {
        "limit_scope": "ALL_WINDOWS_AND_WORKERS",
        "project_override_allowed": True,
        "inherit_from": "progress.health_checks",
    }:
        fail("Agent configuration schema does not enforce the approved Tabs branch")

    master_terms = re.sub(r"\s+", " ", master).lower()
    for required in (
        "`#tabs` | the configured shared capacity",
        "effective `#tabs` settings",
        "observable open-tab inventory",
        "`#tabs` ownership and queued-work state",
    ):
        if required not in master_terms:
            fail(f"Agent contract lacks required Tabs integration: {required}")

    observed_rules = re.findall(r"^## (TABS-[0-9]{3})\b", browser, re.MULTILINE)
    expected_rules = [f"TABS-{number:03d}" for number in range(1, 8)]
    if observed_rules != expected_rules:
        fail("Browser contract must define TABS-001 through TABS-007 in order")

    required_by_rule = {
        "TABS-001": ("config.browser.tabs", "another positive integer", "all agent-controlled"),
        "TABS-002": ("one shared inventory", "only one worker may hold a tab lease", "open no additional tab"),
        "TABS-003": ("reserve capacity", "place the task in a resumable queue", "closing protected state"),
        "TABS-004": ("before reuse, handoff, or closure", "sensitive authentication routes"),
        "TABS-005": ("single `#progress` health-check branch", "apply exactly one monitoring branch", "15-minute", "event-driven checks"),
        "TABS-006": ("require new evidence", "do not attribute a failure", "apply `browser-004`"),
        "TABS-007": ("pause or remove", "release worker leases", "final monitoring branch"),
    }
    for rule_id, phrases in required_by_rule.items():
        section = re.sub(r"\s+", " ", prompt_section(browser, rule_id)).lower()
        for phrase in phrases:
            if phrase not in section:
                fail(f"Browser contract lacks required {rule_id} behavior: {phrase}")

    normalized_browser = re.sub(r"\s+", " ", browser).lower()
    for scenario_id, phrases in TABS_SCENARIOS.items():
        for phrase in phrases:
            if phrase not in normalized_browser:
                fail(f"Tabs acceptance scenario {scenario_id} lacks required behavior: {phrase}")

    prohibited = ("agent:" + "prompts", "gpt-5.6 sol high", "8 gb of ram", "eight cpu cores")
    if any(term in browser.lower() for term in prohibited):
        fail("stale route, model, or hardware advice entered the Browser/Tabs contract")
    ok("Tabs configuration v3 and TABS-001 through TABS-007 define shared capacity and consume the Progress monitor")


def validate_fact_pair_example(template_text: str) -> None:
    section = prompt_section(template_text, "TEMPLATE-006")
    json_match = re.search(r"```json\n(.*?)\n```", section, re.DOTALL)
    csv_match = re.search(r"```csv\n(.*?)\n```", section, re.DOTALL)
    markdown_match = re.search(r"```markdown\n(.*?)\n```", section, re.DOTALL)
    if json_match is None or csv_match is None or markdown_match is None:
        fail("Template three-format release-view example is incomplete")
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

    markdown_lines = [line for line in markdown_match.group(1).splitlines() if line.strip()]
    if len(markdown_lines) != len(json_rows) + 2:
        fail("Template Markdown example row count differs")
    markdown_headers = [value.strip() for value in markdown_lines[0].strip("|").split("|")]
    if markdown_headers != headers:
        fail("Template Markdown example fields or order differ")
    for index, (json_row, line) in enumerate(zip(json_rows, markdown_lines[2:]), 1):
        values = [value.strip() for value in line.strip("|").split("|")]
        if len(values) != len(headers):
            fail(f"Template Markdown example field count differs at row {index}")
        for field, markdown_value in zip(headers, values):
            json_value = json_row[field]
            expected = "null" if json_value is None else str(json_value).lower() if isinstance(json_value, bool) else str(json_value)
            if markdown_value != expected:
                fail(f"Template Markdown logical value differs at row {index}, field {field}")
    ok("synthetic CSV/JSON/Markdown release view preserves fields, values, ordering, and null semantics")


def validate_data_contract() -> None:
    data_path = ROOT / "dot" / "research" / "data.prompt"
    template_path = ROOT / "dot" / "research" / "template.prompt"
    data_text = data_path.read_text(encoding="utf-8")
    template_text = template_path.read_text(encoding="utf-8")

    if "**Contract:** `dot-research-data/2`" not in data_text:
        fail("Data contract version is not dot-research-data/2")

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
    normalized_data = re.sub(r"\s+", " ", data_text).lower()
    for required in (
        "`<basename>.csv`, `<basename>.json`, and `<basename>.md`",
        "csv and json remain the canonical machine pair",
        "markdown contains every row and field",
        "persist and verify corrections before regenerating downstream views",
    ):
        if required not in normalized_data:
            fail(f"Data three-format contract lacks required behavior: {required}")
    ok("Data owns 22 unique basenames, three-format parity, distinct provenance layers, and all acceptance scenarios")


def validate_summary_contract() -> None:
    summary_path = ROOT / "dot" / "research" / "summary.prompt"
    project_path = ROOT / "dot" / "research" / "project.prompt"
    internet_path = ROOT / "dot" / "research" / "internet.prompt"
    template_path = ROOT / "dot" / "research" / "template.prompt"
    summary = summary_path.read_text(encoding="utf-8")
    project = project_path.read_text(encoding="utf-8")
    internet = internet_path.read_text(encoding="utf-8")
    template = template_path.read_text(encoding="utf-8")

    if "**Contract:** `dot-research-summary/3`" not in summary:
        fail("Summary contract version is not dot-research-summary/3")
    observed_rules = re.findall(r"^## (SUMMARY-[0-9]{3})\b", summary, re.MULTILINE)
    expected_rules = [f"SUMMARY-{number:03d}" for number in range(1, 11)]
    if observed_rules != expected_rules:
        fail("Summary contract must define SUMMARY-001 through SUMMARY-010 in order")

    required_by_rule = {
        "SUMMARY-001": (
            "only when the owner requests",
            "never rewrite, replace, rename, or overwrite the main research report",
            "verify the persistent parent inputs",
            "keep those inputs immutable",
            "successor dataset release or proposed correction set",
        ),
        "SUMMARY-002": (
            "8–16 core pages",
            "ask only about omissions whose answers would materially alter",
            "approved destination",
            "public_source_gap_filling",
            "explicitly_source_limited",
            "unless the owner explicitly sets",
        ),
        "SUMMARY-003": (
            "one row for every in-scope subject and every required fact",
            "reconcile the eligible entity or subject universe",
            "bind each material statement and comparison to controlled `#fact` records",
            "inaccessible, missing, suppressed, conflicting, and noncomparable",
            "not_started",
            "bounded_negative",
            "authorization_required",
        ),
        "SUMMARY-004": (
            "missing material fact as unfinished research",
            "actual navigation trail",
            "blank javascript search shell",
            "continue while an accessible, material route remains unperformed",
            "explicitly_source_limited",
            "inside the pdf",
            "links provide traceability but never substitute",
            "privacy, suppression, and audience controls",
        ),
        "SUMMARY-005": (
            "education or subject-matter consultant, research editor, and information designer",
            "three to five strongest findings",
            "edutainment means strong narrative pacing",
            "must not imply affiliation with ted",
            "what remains uncertain",
        ),
        "SUMMARY-006": (
            "embedded data appendix",
            "do not add filler",
            "one main idea per page or spread",
        ),
        "SUMMARY-007": (
            "values behind every material chart",
            "bar chart's numeric axis at zero",
            "never rely on color alone",
        ),
        "SUMMARY-008": (
            "derivation_class: observed",
            "derivation_class: derived",
            "derivation_class: inferred",
            "null plus a controlled missing reason",
            "never reconstruct protected small groups",
        ),
        "SUMMARY-009": (
            "official identity, official linkage, successful retrieval",
            "shared resource as exclusive to one entity",
            "historical condition as current",
            "k–6 as a working assumption",
            "k–12 or pk–8",
            "does not establish quality",
        ),
        "SUMMARY-010": (
            "build the fact matrix",
            "distinct self-review pass",
            "sampling cannot support a claim that every requested entity was checked",
            "csv/json/markdown companions",
            "immediately persist and read back the unreviewed draft",
            "visually inspect every page",
            "mark delivery `blocked`",
            "versioned native pdf attachment",
            "do not build an application, database, website, or code product",
            "codex is not required or authorized",
        ),
    }
    for rule_id, phrases in required_by_rule.items():
        section = re.sub(r"\s+", " ", prompt_section(summary, rule_id)).lower()
        for phrase in phrases:
            if phrase not in section:
                fail(f"Summary contract lacks required {rule_id} behavior: {phrase}")

    project_section = re.sub(r"\s+", " ", prompt_section(project, "PROJECT-009")).lower()
    for phrase in (
        "owner requests its named output",
        "use `#summary`",
        "route missing facts back through `#internet` and applicable `#data`",
        "never mutates the parent report or an accepted release",
    ):
        if phrase not in project_section:
            fail(f"Project lacks conditional Summary control: {phrase}")

    normalized_internet = re.sub(r"\s+", " ", internet).lower()
    for phrase in (
        "follow the relevant navigation rather than stopping at a search result or homepage",
        "record the actual navigation trail",
        "blank javascript search shell",
        "a sample cannot support an all-entities claim",
    ):
        if phrase not in normalized_internet:
            fail(f"Internet lacks evidence-completion behavior: {phrase}")

    prohibited_advice = ("agent:" + "prompts", "gpt-5.6" + "-sol-high")
    if any(term in (summary + project + internet).lower() for term in prohibited_advice):
        fail("stale model or prompt-workspace advice entered the active research contracts")

    summary_contracts = re.sub(r"\s+", " ", summary + project + internet + template).lower()
    for scenario_id, phrases in SUMMARY_SCENARIOS.items():
        for phrase in phrases:
            if phrase not in summary_contracts:
                fail(f"Summary acceptance scenario {scenario_id} lacks required behavior: {phrase}")

    template_section = prompt_section(template, "TEMPLATE-016")
    json_blocks = re.findall(r"```json\n(.*?)\n```", template_section, re.DOTALL)
    if len(json_blocks) != 3:
        fail("Template must define one Executive Brief Request, Fact Matrix row, and Completion Receipt")
    try:
        request, matrix, completion = (json.loads(block) for block in json_blocks)
    except json.JSONDecodeError as exc:
        fail(f"Template Executive Brief record is invalid JSON: {exc}")
    if request.get("schema") != "dot-executive-brief-request/2":
        fail("Executive Brief Request schema is not version 2")
    if matrix.get("schema") != "dot-summary-fact-matrix-row/1":
        fail("Summary Fact Matrix row schema is incorrect")
    if completion.get("schema") != "dot-executive-brief-completion/2":
        fail("Executive Brief Completion schema is not version 2")

    required_request_fields = {
        "summary_request_id", "parent_project_id", "parent_project_version",
        "requested_subtopic", "audience", "supported_decision_or_discussion",
        "geographic_population_and_entity_scope", "relevant_dates_and_research_cutoff",
        "input_files_pages_datasets_and_urls", "research_mode", "required_fact_fields",
        "required_questions_or_comparisons", "requested_entity_chapters_and_order",
        "excluded_topics", "requested_data_companions", "desired_length", "output_title",
        "output_version", "output_filename", "approved_destination", "recorded_assumptions",
        "acceptance_test_ids",
    }
    if not required_request_fields.issubset(request):
        fail("Executive Brief Request lacks required input fields")
    if request.get("research_mode") != "PUBLIC_SOURCE_GAP_FILLING":
        fail("Executive Brief Request does not default to public-source gap filling")

    required_matrix_fields = {
        "summary_request_id", "matrix_row_id", "subject_id", "subject_id_null_reason",
        "inclusion_disposition", "required_fact_key", "required_grain",
        "required_population", "required_period", "fact_id", "fact_id_null_reason",
        "evidence_link_ids", "research_state", "coverage_disposition", "missing_reason",
        "reviewer_type", "next_action",
    }
    if not required_matrix_fields.issubset(matrix):
        fail("Summary Fact Matrix row lacks required control fields")
    matrix_text = json.dumps(matrix, sort_keys=True)
    for required in (
        "NOT_STARTED", "IN_PROGRESS", "AWAITING_REVIEW", "BLOCKED", "TERMINAL",
        "SUPPORTED", "DISPUTED", "BOUNDED_NEGATIVE", "ACCESS_BLOCKED",
        "AUTHORIZATION_REQUIRED", "NOT_APPLICABLE", "UNRESOLVED",
    ):
        if required not in matrix_text:
            fail(f"Summary Fact Matrix lacks required state or disposition: {required}")

    required_completion_fields = {
        "summary_request_id", "output_filename", "output_version",
        "initial_dataset_release_ids", "dataset_release_ids", "fact_and_evidence_versions",
        "fact_matrix_version", "fact_matrix_sha256", "entity_denominator",
        "matrix_expected_row_count", "matrix_terminal_row_count",
        "matrix_blocked_row_count", "matrix_unresolved_row_count", "page_count", "sha256",
        "gap_completion_check", "official_site_path_check", "material_claim_check",
        "calculation_and_measurement_check", "citation_and_link_check",
        "appendix_and_supporting_value_check",
        "privacy_and_suppression_check", "fact_check_reviewer_type",
        "fact_check_independence", "requested_export_parity_check", "visual_page_inspection",
        "native_attachment_state", "delivery_reference", "readback_at",
        "unreviewed_draft_persistence_state", "recovery_manifest_id_and_version",
        "archive_id_and_version", "final_progress_classification", "health_check_disposition",
        "material_limitations", "completion_status",
    }
    if not required_completion_fields.issubset(completion):
        fail("Executive Brief Completion Receipt lacks required validation or delivery fields")
    ok("Summary owns one conditional, evidence-completing, Fact-bound executive-brief lifecycle")


def validate_release_contract() -> None:
    release_path = ROOT / "docs" / "release.prompt"
    release = release_path.read_text(encoding="utf-8")
    observed_rules = re.findall(r"^## (RELEASE-[0-9]{3})\b", release, re.MULTILINE)
    expected_rules = [f"RELEASE-{number:03d}" for number in range(1, 11)]
    if observed_rules != expected_rules:
        fail("Release contract must define RELEASE-001 through RELEASE-010 in order")

    required_by_rule = {
        "RELEASE-001": (
            "repository releases, not the immutable dataset releases owned by `#data`",
            "does not authorize a tag, merge, upload, publication, or external announcement",
        ),
        "RELEASE-002": (
            "complete previous-tag-to-candidate commit range",
            "at least one prior well-structured release",
            "never infer completion from a branch name",
        ),
        "RELEASE-003": (
            "bare numeric tags",
            "published tag and its target commit as immutable",
            "behavioral correction creates a new version",
        ),
        "RELEASE-004": (
            "practical outcome and why it matters",
            "reusable behavior",
            "do not pad notes",
        ),
        "RELEASE-005": (
            "compact core",
            "operator workflow and safety",
            "interfaces and compatibility",
            "migration and recovery",
            "validation evidence",
            "known boundaries",
        ),
        "RELEASE-006": (
            "hashes verified from the actual release range",
            "github-generated source archives",
            "never claim that source-only documentation is an executable or binary asset",
        ),
        "RELEASE-007": (
            "publication-manifest entry",
            "byte-exact raw sources",
            "live route represents another commit",
        ),
        "RELEASE-008": (
            "stacked releases",
            "publish each predecessor before retargeting",
            "failed check",
            "one tracked acceptance ledger",
            "do not create an intermediate tag, prerelease, or partial public release",
        ),
        "RELEASE-009": (
            "complete proposed body in a normal tracked markdown file",
            "create or converge a draft first",
            "read the public release back through the github api",
            "github draft only after every canonical prompt",
            "prohibited before that freeze",
        ),
        "RELEASE-010": (
            "supported source archives",
            "separate manual acceptance test",
            "do not claim the downstream test passed",
        ),
    }
    for rule_id, phrases in required_by_rule.items():
        section = re.sub(r"\s+", " ", prompt_section(release, rule_id)).lower()
        for phrase in phrases:
            if phrase not in section:
                fail(f"Release contract lacks required {rule_id} behavior: {phrase}")

    rule_ids = re.findall(r"^## ([A-Z]+-[0-9]{3})\b", release, re.MULTILINE)
    if len(rule_ids) != len(set(rule_ids)):
        fail("Release contract contains duplicate canonical rule IDs")
    ok("Release owns one adaptive repository-wide review and publication contract")


def validate_ingest_contract() -> None:
    ingest_path = ROOT / "dot" / "ingest.json"
    try:
        ingest = json.loads(ingest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid DOT ingestion manifest: {exc}")

    expected_identity = {
        "schema": "dot-ingest/1",
        "release": "0.0.7",
        "baseline_tag": "0.0.1",
        "prior_release_tag": "0.0.6",
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
    normalized_project = re.sub(r"\s+", " ", project)
    for term in ("ingestion receipt", "missing or truncated content", "actually verified"):
        if term not in normalized_project:
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
        "must be published before",
        "is not an ancestor of",
        "Repository Release Contract",
        "Evidence-Completing Research Summaries",
        "Coordinated Browser Tabs",
        "Continuous Progress and Recoverable Agent Storage",
        "release_text.py",
        "existing release is already published",
        "existing draft target differs",
        "converged and verified draft",
        "release prerelease state differs",
        "release target differs",
    ):
        if required not in release_script:
            fail(f"release workflow lacks required safeguard: {required}")

    candidate = (ROOT / "docs" / "releases" / "0.0.7.md").read_text(encoding="utf-8")
    normalized_candidate = re.sub(r"\s+", " ", candidate).lower()
    for required in (
        "### edge-case acceptance ledger",
        "every row is a release gate",
        "progress | verified or missing scheduler",
        "storage | failed probe/readback",
        "provisioning | existing match",
        "delivery | wip versus delivered",
        "browser | four-tab capacity",
        "research | one failed query",
        "data | three-format parity",
        "archives | missing member",
        "security | credentials",
        "lifecycle | pause, resume",
        "repository and pages workflow `pass`",
    ):
        if required not in normalized_candidate:
            fail(f"0.0.7 edge-case release ledger lacks required gate: {required}")
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
    ok("candidate release identity is consistently 0.0.7 and contains no stale candidate-version reference")

    if any(path.startswith("static/") for path in paths):
        fail("generated static output must not be included on main")
    if "dot/prompt" in path_set or any(path.startswith("dot/prompt/") for path in paths):
        fail("private singular prompt workspace is included in public source")
    if "dot/dot.master.00.prompt" in path_set:
        fail("byte-identical local master duplicate is included in public source")
    if any(path.startswith(("dot/agents/", "dot/prompts/")) for path in paths):
        fail("superseded pre-0.0.2 DOT prompt or agent tree is included in current source")
    if any(Path(path).suffix.lower() == ".pdf" for path in paths):
        fail("generated Summary PDFs must not be tracked as repository or release assets")
    retired_intake_prefix = "dot/" + "handoff" + "/"
    if any(path.startswith(retired_intake_prefix) for path in paths):
        fail("retired research intake artifacts are included in current source")
    retired_summary_draft = "dot/research/" + "brief.prompt"
    if retired_summary_draft in path_set:
        fail("retired Summary draft remains in current source")
    for path in paths:
        full = ROOT / path
        if path == "actions/validate_repository.py" or not full.is_file():
            continue
        if full.suffix.lower() not in {".json", ".md", ".prompt", ".py", ".sh", ".yml", ".yaml"}:
            continue
        try:
            content = full.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if retired_summary_draft in content:
            fail(f"retired Summary draft is referenced by current source: {path}")
    retired_tabs_draft = "dot/agent/" + "tabs.prompt"
    if retired_tabs_draft in path_set:
        fail("standalone Tabs draft remains in current source")
    for path in paths:
        full = ROOT / path
        if path == "actions/validate_repository.py" or not full.is_file():
            continue
        if full.suffix.lower() not in {".json", ".md", ".prompt", ".py", ".sh", ".yml", ".yaml"}:
            continue
        try:
            content = full.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if retired_tabs_draft in content:
            fail(f"standalone Tabs draft is referenced by current source: {path}")
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
    validate_storage_progress_contract()
    validate_tabs_contract()
    validate_data_contract()
    validate_summary_contract()
    validate_release_contract()
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
