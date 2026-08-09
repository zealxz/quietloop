"""Conservative redaction for summaries and operator-visible diagnostics."""

from __future__ import annotations

import re

_REDACTIONS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)\b(?:sk|rk|pk)_[A-Za-z0-9_-]{16,}\b"), "<API_KEY>"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"), "<GITHUB_TOKEN>"),
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{12,}\b"), "Bearer <REDACTED>"),
    (
        re.compile(r"(?i)\b(api[_-]?key|token|secret|password|credential)\b\s*[:=]\s*[^\s,;]+"),
        r"\1=<REDACTED>",
    ),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "<EMAIL>"),
    (re.compile(r"(?:/home/[^/\s]+|/Users/[^/\s]+)(?:/[^\s]*)?"), "<HOME_PATH>"),
    (re.compile(r"\b\d{12,}\b"), "<LONG_ID>"),
)


def redact_text(value: str, *, limit: int | None = None) -> str:
    """Remove common secrets and machine identifiers from a short text value.

    This is defense in depth, not a substitute for data minimization. Callers
    should avoid collecting private content in the first place.
    """

    redacted = str(value)
    for pattern, replacement in _REDACTIONS:
        redacted = pattern.sub(replacement, redacted)
    if limit is not None and limit >= 0 and len(redacted) > limit:
        return redacted[:limit].rstrip() + "…"
    return redacted
