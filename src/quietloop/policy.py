"""Fail-closed policy for an explicitly approved local text replacement."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True, slots=True)
class ApplyPolicy:
    """Narrow defaults: documentation/configuration text, never code or shell."""

    allowed_prefixes: tuple[str, ...] = ("config", "docs")
    allowed_suffixes: tuple[str, ...] = (".md", ".toml", ".yaml", ".yml")
    max_replacement_bytes: int = 8_192

    def allows(self, target: str, replacement: str) -> bool:
        path = PurePosixPath(target)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            return False
        has_allowed_prefix = any(
            target == prefix or target.startswith(f"{prefix}/") for prefix in self.allowed_prefixes
        )
        if not has_allowed_prefix:
            return False
        if path.suffix.lower() not in self.allowed_suffixes:
            return False
        return len(replacement.encode("utf-8")) <= self.max_replacement_bytes
