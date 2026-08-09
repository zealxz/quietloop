"""Deterministic, receipt-aware wake decisions."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass

from .models import Action, Receipt

_PENDING_STATUSES = frozenset({"pending-system", "pending-automation", "pending-auto"})
_FINAL_DECISIONS = frozenset({"applied", "no-safe-change", "rejected"})


@dataclass(frozen=True, slots=True)
class WakeDecision:
    wake_agent: bool
    reason: str
    action_id: str = ""

    def to_dict(self) -> dict[str, bool | str]:
        return asdict(self)


def decide_wake(
    actions: Iterable[Action],
    receipts: Iterable[Receipt],
    *,
    source_digest: str,
) -> WakeDecision:
    """Wake only for an explicit, unresolved system action.

    A completed receipt matches both the action ID and immutable source digest;
    an edited reflection is therefore reconsidered rather than silently
    inheriting a decision for different source material.
    """

    resolved = {
        (receipt.action_id, receipt.source_digest)
        for receipt in receipts
        if receipt.decision.casefold().replace("_", "-") in _FINAL_DECISIONS
    }
    pending = [action for action in actions if action.status in _PENDING_STATUSES]
    if not pending:
        return WakeDecision(False, "no_pending_system_action")
    for action in pending:
        if (action.id, source_digest) not in resolved:
            return WakeDecision(True, "unresolved_system_action", action.id)
    return WakeDecision(False, "already_processed")
