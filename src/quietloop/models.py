from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True, slots=True)
class Action:
    """A small, testable unit extracted from a reflection."""

    id: str
    title: str
    status: str
    owner: str = ""
    verification: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Proposal:
    """A bounded local text change; it has no authority by itself."""

    id: str
    action_id: str
    source_digest: str
    target: str
    before_sha256: str
    replacement: str
    rationale: str
    created_at: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Proposal:
        fields = {name: str(data[name]) for name in cls.__dataclass_fields__}
        return cls(**fields)

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Approval:
    """A local, explicit approval for one immutable proposal ID."""

    proposal_id: str
    approved_by: str
    approved_at: str
    note: str = ""

    @classmethod
    def for_proposal(cls, proposal_id: str, approved_by: str, note: str = "") -> Approval:
        return cls(
            proposal_id=proposal_id,
            approved_by=approved_by,
            approved_at=utc_now(),
            note=note,
        )

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Receipt:
    """An immutable record of a decision or an applied proposal."""

    proposal_id: str
    action_id: str
    source_digest: str
    decision: str
    reason: str
    created_at: str
    target: str = ""
    before_sha256: str = ""
    after_sha256: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
