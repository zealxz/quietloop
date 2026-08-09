"""Idempotent local retry queue for sanitized delivery summaries."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .models import utc_now
from .redaction import redact_text
from .state import read_json, update_json


@dataclass(frozen=True, slots=True)
class DeliveryEvent:
    key: str
    destination: str
    summary: str
    queued_at: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def enqueue(path: Path, event: DeliveryEvent, *, max_events: int = 100) -> bool:
    """Add one event once. Returns True only when a new event was stored."""

    inserted = False

    def _update(raw: Any) -> dict[str, Any]:
        nonlocal inserted
        payload = raw if isinstance(raw, dict) else {"version": 1, "events": []}
        records = payload.get("events") if isinstance(payload.get("events"), list) else []
        if any(isinstance(item, dict) and item.get("key") == event.key for item in records):
            return {"version": 1, "events": records[-max_events:]}
        inserted = True
        sanitized = DeliveryEvent(
            key=event.key,
            destination=redact_text(event.destination, limit=160),
            summary=redact_text(event.summary, limit=360),
            queued_at=event.queued_at or utc_now(),
        )
        return {"version": 1, "events": (records + [sanitized.to_dict()])[-max_events:]}

    update_json(path, {"version": 1, "events": []}, _update)
    return inserted


def pending(path: Path, destination: str | None = None) -> list[DeliveryEvent]:
    raw = read_json(path, {})
    records = raw.get("events", []) if isinstance(raw, dict) else []
    events: list[DeliveryEvent] = []
    required_fields = ("key", "destination", "summary", "queued_at")
    for item in records:
        if not isinstance(item, dict) or not all(key in item for key in required_fields):
            continue
        fields = {key: str(item[key]) for key in DeliveryEvent.__dataclass_fields__}
        event = DeliveryEvent(**fields)
        if destination is None or event.destination == destination:
            events.append(event)
    return events


def acknowledge(path: Path, keys: set[str]) -> int:
    """Remove acknowledged keys atomically and return the count removed."""

    removed = 0

    def _update(raw: Any) -> dict[str, Any]:
        nonlocal removed
        payload = raw if isinstance(raw, dict) else {"version": 1, "events": []}
        records = payload.get("events") if isinstance(payload.get("events"), list) else []
        kept = []
        for item in records:
            if isinstance(item, dict) and str(item.get("key")) in keys:
                removed += 1
            else:
                kept.append(item)
        return {"version": 1, "events": kept}

    update_json(path, {"version": 1, "events": []}, _update)
    return removed
