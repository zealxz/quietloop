"""Small, locked, atomic JSON stores for local QuietLoop state."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, TypeVar

try:  # QuietLoop targets POSIX-first personal-agent deployments.
    import fcntl
except ImportError:  # pragma: no cover - documented unsupported lock backend
    fcntl = None  # type: ignore[assignment]

T = TypeVar("T")


@contextmanager
def file_lock(path: Path) -> Iterator[None]:
    """Acquire an advisory sidecar lock; fail closed where fcntl is absent."""

    if fcntl is None:
        raise RuntimeError("QuietLoop requires a POSIX file-lock backend")
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f".{path.name}.lock")
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def read_json(path: Path, default: T) -> T:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return default


def atomic_write_json(path: Path, payload: Any) -> None:
    """Durably replace one JSON file without exposing a partial document."""

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def update_json(path: Path, default: T, updater: Callable[[T], T]) -> T:
    """Read-modify-write under one inter-process lock."""

    with file_lock(path):
        value = read_json(path, default)
        updated = updater(value)
        atomic_write_json(path, updated)
        return updated
