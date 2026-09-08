"""Explicitly approved, bounded local text application with receipts."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from .models import Approval, Proposal, Receipt, utc_now
from .policy import ApplyPolicy
from .state import atomic_write_json


class ApplyRefused(ValueError):
    """A proposal failed a safety precondition and was not applied."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _safe_target(root: Path, target: str) -> Path:
    candidate = root / target
    if candidate.is_symlink():
        raise ApplyRefused("symlink targets are not allowed")
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ApplyRefused("target escapes configured root") from exc
    return candidate


def _atomic_write_text(path: Path, content: str) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def apply_proposal(
    proposal: Proposal,
    approval: Approval | None,
    *,
    root: Path,
    state_dir: Path,
    policy: ApplyPolicy | None = None,
) -> Receipt:
    """Apply one approved full-text replacement or raise without writing.

    The proposal cannot create files, touch code/shell by default, traverse a
    path, follow a symlink, bypass the exact preimage digest, or exceed the
    configured size budget. Runtime backups and receipts are local-only.
    """

    if approval is None or approval.proposal_id != proposal.id or not approval.approved_by.strip():
        raise ApplyRefused("explicit approval for this proposal is required")
    if (
        not proposal.id
        or proposal.id in {".", ".."}
        or any(character in proposal.id for character in ("/", "\\", "\0"))
    ):
        raise ApplyRefused("proposal ID must be a single non-empty filename component")
    active_policy = policy or ApplyPolicy()
    if not active_policy.allows(proposal.target, proposal.replacement):
        raise ApplyRefused("proposal violates the configured apply policy")
    if not root.is_dir():
        raise ApplyRefused("configured root does not exist")
    target = _safe_target(root, proposal.target)
    if not target.is_file():
        raise ApplyRefused("target must be an existing regular file")
    before = target.read_text(encoding="utf-8")
    if sha256_text(before) != proposal.before_sha256:
        raise ApplyRefused("target preimage changed; proposal is stale")

    backup = state_dir / "backups" / f"{proposal.id}-{target.name}.bak"
    backup.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(backup, before)
    _atomic_write_text(target, proposal.replacement)
    receipt = Receipt(
        proposal_id=proposal.id,
        action_id=proposal.action_id,
        source_digest=proposal.source_digest,
        decision="applied",
        reason=f"approved locally by {approval.approved_by.strip()}",
        created_at=utc_now(),
        target=proposal.target,
        before_sha256=proposal.before_sha256,
        after_sha256=sha256_text(proposal.replacement),
    )
    atomic_write_json(state_dir / "receipts" / f"{proposal.id}.json", receipt.to_dict())
    return receipt


def load_proposal(path: Path) -> Proposal:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ApplyRefused("proposal must be a JSON object")
    return Proposal.from_dict(data)
