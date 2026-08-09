from pathlib import Path

import pytest

from quietloop.apply import ApplyRefused, apply_proposal, sha256_text
from quietloop.models import Approval, Proposal, utc_now


def _proposal(target: str, before: str, replacement: str) -> Proposal:
    return Proposal(
        id="proposal-1",
        action_id="action-1",
        source_digest="source-digest",
        target=target,
        before_sha256=sha256_text(before),
        replacement=replacement,
        rationale="synthetic test",
        created_at=utc_now(),
    )


def test_apply_requires_approval_and_writes_backup_and_receipt(tmp_path: Path) -> None:
    root = tmp_path / "project"
    target = root / "docs" / "note.md"
    target.parent.mkdir(parents=True)
    target.write_text("before", encoding="utf-8")
    proposal = _proposal("docs/note.md", "before", "after")

    with pytest.raises(ApplyRefused, match="approval"):
        apply_proposal(proposal, None, root=root, state_dir=tmp_path / "state")
    assert target.read_text(encoding="utf-8") == "before"

    approval = Approval.for_proposal(proposal.id, "synthetic-reviewer")
    receipt = apply_proposal(proposal, approval, root=root, state_dir=tmp_path / "state")
    assert receipt.decision == "applied"
    assert target.read_text(encoding="utf-8") == "after"
    assert (tmp_path / "state" / "backups" / "proposal-1-note.md.bak").read_text(
        encoding="utf-8"
    ) == "before"
    assert (tmp_path / "state" / "receipts" / "proposal-1.json").is_file()


def test_apply_refuses_escape_stale_content_and_code(tmp_path: Path) -> None:
    root = tmp_path / "project"
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "note.md").write_text("current", encoding="utf-8")
    approval = Approval.for_proposal("proposal-1", "synthetic-reviewer")

    escape = _proposal("../outside.md", "current", "after")
    with pytest.raises(ApplyRefused, match="policy"):
        apply_proposal(escape, approval, root=root, state_dir=tmp_path / "state")

    stale = _proposal("docs/note.md", "older", "after")
    with pytest.raises(ApplyRefused, match="preimage"):
        apply_proposal(stale, approval, root=root, state_dir=tmp_path / "state")

    code = _proposal("docs/note.py", "current", "after")
    with pytest.raises(ApplyRefused, match="policy"):
        apply_proposal(code, approval, root=root, state_dir=tmp_path / "state")
