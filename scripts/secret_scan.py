#!/usr/bin/env python3
"""Tiny offline pre-commit guard for obvious real credentials."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERNS = (
    re.compile(r"\b(?:sk|rk|pk)_[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{20,}\b"),
)
SKIP = {".git", ".venv", "build", "dist"}


def main() -> int:
    hits: list[str] = []
    for path in Path(".").rglob("*"):
        if not path.is_file() or any(part in SKIP for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if any(pattern.search(text) for pattern in PATTERNS):
            hits.append(str(path))
    if hits:
        print("potential secret pattern in: " + ", ".join(hits), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
