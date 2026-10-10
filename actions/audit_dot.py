#!/usr/bin/env python3
"""Audit the immutable DOT 0.0.1 corpus against the two-lane migration ledger.

This audit is CI-only. It reads historical sources from Git, expands the compact
migration map to clause-level records, and reports duplicate candidates without
rewriting source material.
"""

from __future__ import annotations

from collections import defaultdict
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "docs" / "history" / "two-lane-migration.json"
CANONICAL_PROMPTS = sorted((ROOT / "dot" / "agent").glob("*.prompt")) + sorted(
    (ROOT / "dot" / "research").glob("*.prompt")
)
RULE_RE = re.compile(r"^## ([A-Z]+-[0-9]{3})\b")


def fail(message: str) -> None:
    print(f"[audit.dot][error] {message}", file=sys.stderr)
    raise SystemExit(1)


def git_text(tag: str, source: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{tag}:{source}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        fail(f"cannot read {tag}:{source}")
    try:
        return result.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(f"historical source is not UTF-8: {source}: {exc}")


def normalize(value: str) -> str:
    value = re.sub(r"[`*_>#|]", " ", value.lower())
    return re.sub(r"\s+", " ", value).strip()


def clauses(source: str, value: str) -> list[dict]:
    records: list[dict] = []
    buffer: list[str] = []
    start = 0
    in_fence = False

    def emit(end: int) -> None:
        nonlocal buffer, start
        body = "\n".join(buffer).strip()
        normalized = normalize(body)
        if normalized:
            digest = hashlib.sha256(f"{source}:{start}:{end}:{normalized}".encode()).hexdigest()[:16]
            records.append(
                {
                    "clause_id": f"CLAUSE-{digest.upper()}",
                    "source": source,
                    "start_line": start,
                    "end_line": end,
                    "sha256": hashlib.sha256(body.encode()).hexdigest(),
                    "normalized_sha256": hashlib.sha256(normalized.encode()).hexdigest(),
                    "normalized": normalized,
                    "text": body,
                }
            )
        buffer = []
        start = 0

    for number, line in enumerate(value.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not buffer:
                start = number
            buffer.append(line)
            in_fence = not in_fence
            if not in_fence:
                emit(number)
            continue
        if in_fence:
            buffer.append(line)
            continue
        boundary = not stripped or stripped.startswith("#") or stripped.startswith(("- ", "* ", "> ")) or stripped.startswith("|")
        if boundary and buffer:
            emit(number - 1)
        if stripped:
            start = start or number
            buffer.append(line)
            if stripped.startswith("#") or stripped.startswith(("- ", "* ", "> ")) or stripped.startswith("|"):
                emit(number)
    if buffer:
        emit(len(value.splitlines()))
    return records


def duplicate_groups(records: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        if len(record["normalized"]) >= 120:
            grouped[record["normalized_sha256"]].append(record)
    return [
        {
            "normalized_sha256": digest,
            "members": [
                {"clause_id": item["clause_id"], "source": item["source"], "start_line": item["start_line"]}
                for item in members
            ],
        }
        for digest, members in sorted(grouped.items())
        if len(members) > 1
    ]


def near_duplicate_groups(records: list[dict]) -> list[dict]:
    buckets: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for record in records:
        words = record["normalized"].split()
        if len(words) < 30:
            continue
        key = (" ".join(words[:8]), len(words) // 20)
        buckets[key].append(record)
    matches: list[dict] = []
    for members in buckets.values():
        for left_index, left in enumerate(members):
            for right in members[left_index + 1 :]:
                if left["normalized_sha256"] == right["normalized_sha256"]:
                    continue
                ratio = difflib.SequenceMatcher(None, left["normalized"], right["normalized"]).ratio()
                if ratio >= 0.88:
                    matches.append(
                        {
                            "ratio": round(ratio, 4),
                            "left": {"clause_id": left["clause_id"], "source": left["source"], "start_line": left["start_line"]},
                            "right": {"clause_id": right["clause_id"], "source": right["source"], "start_line": right["start_line"]},
                        }
                    )
    return matches


def main() -> int:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        fail("this audit runs only in GitHub Actions")
    output_value = os.environ.get("DOT_AUDIT_DIR")
    if not output_value:
        fail("DOT_AUDIT_DIR is required")
    output_dir = Path(output_value)
    output_dir.mkdir(parents=True, exist_ok=True)

    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    if ledger.get("unresolved_conflicts"):
        fail("migration ledger has unresolved conflicts")
    mappings = {record["source"]: record for record in ledger["sources"]}
    if len(mappings) != len(ledger["sources"]):
        fail("migration ledger repeats a source")

    historical: list[dict] = []
    for source, mapping in sorted(mappings.items()):
        for record in clauses(source, git_text(ledger["baseline_tag"], source)):
            record["dispositions"] = mapping["dispositions"]
            record["targets"] = mapping["targets"]
            historical.append(record)
    if not historical or any(not record["targets"] for record in historical):
        fail("one or more historical clauses are unmapped")

    rules: dict[str, str] = {}
    canonical: list[dict] = []
    for path in CANONICAL_PROMPTS:
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            match = RULE_RE.match(line)
            if match:
                rule_id = match.group(1)
                if rule_id in rules:
                    fail(f"duplicate canonical rule ID {rule_id}: {rules[rule_id]} and {relative}")
                rules[rule_id] = relative
        canonical.extend(clauses(relative, text))

    canonical_duplicates = duplicate_groups(canonical)
    if canonical_duplicates:
        fail("canonical prompt clauses contain unapproved exact duplication")

    expected_data_rules = {f"DATA-{number:03d}" for number in range(1, 10)}
    observed_data_rules = {rule_id for rule_id in rules if rule_id.startswith("DATA-")}
    if observed_data_rules != expected_data_rules:
        fail("canonical Data contract must define DATA-001 through DATA-009 exactly once")
    if any(rules[rule_id] != "dot/research/data.prompt" for rule_id in expected_data_rules):
        fail("canonical DATA rule IDs must be owned by dot/research/data.prompt")

    expected_summary_rules = {f"SUMMARY-{number:03d}" for number in range(1, 11)}
    observed_summary_rules = {rule_id for rule_id in rules if rule_id.startswith("SUMMARY-")}
    if observed_summary_rules != expected_summary_rules:
        fail("canonical Summary contract must define SUMMARY-001 through SUMMARY-010 exactly once")
    if any(rules[rule_id] != "dot/research/summary.prompt" for rule_id in expected_summary_rules):
        fail("canonical SUMMARY rule IDs must be owned by dot/research/summary.prompt")

    expected_tabs_rules = {f"TABS-{number:03d}" for number in range(1, 8)}
    observed_tabs_rules = {rule_id for rule_id in rules if rule_id.startswith("TABS-")}
    if observed_tabs_rules != expected_tabs_rules:
        fail("canonical Browser contract must define TABS-001 through TABS-007 exactly once")
    if any(rules[rule_id] != "dot/agent/browser.prompt" for rule_id in expected_tabs_rules):
        fail("canonical TABS rule IDs must be owned by dot/agent/browser.prompt")

    canonical_text = "\n".join(path.read_text(encoding="utf-8") for path in CANONICAL_PROMPTS)
    if "#RESERACH" in canonical_text:
        fail("misspelled #RESERACH remains in canonical prompts")
    for term in ("#AGENT", "#PROJECT", "#RESEARCH", "#INTERNET", "#DATA", "#TEMPLATE", "#SUMMARY", "#PAGE", "#FACT", "#CAPTCHA", "#TOOL", "#TABS", "#VIDEO", "#TRANSCRIPTION"):
        if term not in canonical_text:
            fail(f"canonical terminology is missing {term}")

    report = {
        "schema": "dot-clause-audit/1",
        "baseline_tag": ledger["baseline_tag"],
        "release": ledger["release"],
        "historical_clause_count": len(historical),
        "mapped_clause_count": len(historical),
        "canonical_rule_count": len(rules),
        "historical_exact_duplicate_groups": duplicate_groups(historical),
        "historical_near_duplicate_candidates": near_duplicate_groups(historical),
        "canonical_exact_duplicate_groups": canonical_duplicates,
        "clauses": historical,
    }
    (output_dir / "clause-inventory.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = [
        "# DOT clause audit",
        "",
        f"- Baseline: `{ledger['baseline_tag']}`",
        f"- Release: `{ledger['release']}`",
        f"- Historical clauses: {len(historical)}",
        f"- Mapped clauses: {len(historical)}",
        f"- Canonical rule IDs: {len(rules)}",
        f"- Historical exact-duplicate groups: {len(report['historical_exact_duplicate_groups'])}",
        f"- Historical near-duplicate candidates: {len(report['historical_near_duplicate_candidates'])}",
        "- Unresolved conflicts: 0",
        "",
        "The JSON companion contains every expanded clause, source line range, hash, disposition, and canonical target.",
        "",
    ]
    (output_dir / "readme.md").write_text("\n".join(summary), encoding="utf-8")
    print(f"[audit.dot] mapped {len(historical)} historical clauses to {len(rules)} canonical rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
