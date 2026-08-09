from pathlib import Path

from quietloop.models import utc_now
from quietloop.queue import DeliveryEvent, acknowledge, enqueue, pending


def test_queue_is_idempotent_redacted_and_acknowledged(tmp_path: Path) -> None:
    path = tmp_path / "runtime" / "queue.json"
    synthetic_key = "sk_" + "example" + "-not-a-real-key" * 2
    event = DeliveryEvent(
        key="same-event",
        destination="consented-alias-123456789012",
        summary=f"token={synthetic_key} user@example.com /home/alice/private.txt",
        queued_at=utc_now(),
    )
    assert enqueue(path, event) is True
    assert enqueue(path, event) is False

    stored = pending(path)
    assert len(stored) == 1
    assert "sk_" not in stored[0].summary
    assert "@example.com" not in stored[0].summary
    assert "/home/alice" not in stored[0].summary
    assert acknowledge(path, {"same-event"}) == 1
    assert pending(path) == []


def test_acknowledging_unknown_event_is_a_noop(tmp_path: Path) -> None:
    assert acknowledge(tmp_path / "missing.json", {"not-there"}) == 0
