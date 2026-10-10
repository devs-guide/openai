#!/usr/bin/env python3
"""Normalize reviewed and GitHub-returned release text for comparison."""

from __future__ import annotations

from pathlib import Path
import sys


def normalize_bytes(value: bytes) -> bytes:
    text = value.decode("utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"
    return normalized.encode("utf-8")


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: release_text.py SOURCE DESTINATION")
    source = Path(sys.argv[1])
    destination = Path(sys.argv[2])
    destination.write_bytes(normalize_bytes(source.read_bytes()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
