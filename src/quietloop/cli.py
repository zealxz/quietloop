"""Small CLI for local, inspectable QuietLoop workflows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .apply import ApplyRefused, apply_proposal, load_proposal
from .gate import decide_wake
from .models import Approval
from .redaction import redact_text
from .reflection import load_receipts, parse_actions, source_digest


def _gate(args: argparse.Namespace) -> int:
    reflection = Path(args.reflection).read_text(encoding="utf-8")
    digest = source_digest(reflection)
    decision = decide_wake(
        parse_actions(reflection),
        load_receipts(Path(args.receipts)),
        source_digest=digest,
    )
    # Deliberately omit reflection text, paths, and titles from default output.
    output = {
        "wakeAgent": decision.wake_agent,
        "reason": decision.reason,
        "action_id": decision.action_id,
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


def _redact(args: argparse.Namespace) -> int:
    text = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    print(redact_text(text, limit=args.limit))
    return 0


def _apply(args: argparse.Namespace) -> int:
    if not args.i_understand:
        raise ApplyRefused("pass --i-understand after reviewing the proposal and target diff")
    proposal = load_proposal(Path(args.proposal))
    approval = Approval.for_proposal(proposal.id, args.approved_by, args.note)
    receipt = apply_proposal(
        proposal,
        approval,
        root=Path(args.root),
        state_dir=Path(args.state_dir),
    )
    print(json.dumps(receipt.to_dict(), ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quietloop", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    gate = subparsers.add_parser("gate", help="make a receipt-aware wake decision")
    gate.add_argument(
        "--reflection",
        required=True,
        help="structured reflection markdown supplied by the caller",
    )
    gate.add_argument(
        "--receipts",
        required=True,
        help="local receipt directory supplied by the caller",
    )
    gate.set_defaults(handler=_gate)

    redact = subparsers.add_parser(
        "redact",
        help="redact common secrets from text or one local file",
    )
    redact.add_argument("file", nargs="?", help="input file; omit to read stdin")
    redact.add_argument("--limit", type=int, default=None, help="optional output-character ceiling")
    redact.set_defaults(handler=_redact)

    apply = subparsers.add_parser(
        "apply",
        help="apply one explicit, reviewed text proposal",
    )
    apply.add_argument("--proposal", required=True, help="local proposal JSON")
    apply.add_argument("--root", required=True, help="approved project root")
    apply.add_argument(
        "--state-dir",
        required=True,
        help="local-only directory for backups and receipts",
    )
    apply.add_argument("--approved-by", required=True, help="human approval identity")
    apply.add_argument("--note", default="", help="optional approval note")
    apply.add_argument(
        "--i-understand",
        action="store_true",
        help="confirm this is an intentional local write",
    )
    apply.set_defaults(handler=_apply)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (ApplyRefused, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"quietloop: refused: {redact_text(str(exc), limit=240)}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
