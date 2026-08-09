from pathlib import Path

from quietloop.cli import main


def test_cli_gate_uses_synthetic_input(tmp_path: Path, capsys) -> None:
    reflection = tmp_path / "reflection.md"
    reflection.write_text(
        "## Action loop\n\n1. id: safe; title: Safe action; status: pending-system; verification: test.\n",
        encoding="utf-8",
    )
    receipts = tmp_path / "receipts"
    receipts.mkdir()
    assert main(["gate", "--reflection", str(reflection), "--receipts", str(receipts)]) == 0
    output = capsys.readouterr().out
    assert '"wakeAgent": true' in output
    assert "Safe action" not in output
