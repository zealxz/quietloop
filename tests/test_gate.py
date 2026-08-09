from quietloop.gate import decide_wake
from quietloop.models import Receipt, utc_now
from quietloop.reflection import parse_actions, source_digest

REFLECTION = """# Synthetic\n\n## Action loop\n\n1. id: delivery-summary; title: Add recovery summary; owner: agent; status: pending-system; verification: synthetic delivery passes.\n2. id: operator-note; title: Write a note; owner: operator; status: done; verification: n/a.\n"""


def test_extracts_only_explicit_system_action() -> None:
    actions = parse_actions(REFLECTION)
    assert [(action.id, action.status) for action in actions] == [
        ("delivery-summary", "pending-system"),
        ("operator-note", "done"),
    ]


def test_extracts_one_multiline_list_item() -> None:
    reflection = """## Action loop

1. id: multiline; title: Keep the readable example;
   owner: agent; status: pending-system;
   verification: the parser keeps all fields.
"""
    [action] = parse_actions(reflection)
    assert action.id == "multiline"
    assert action.status == "pending-system"
    assert action.owner == "agent"
    assert action.verification == "the parser keeps all fields."


def test_gate_is_idempotent_for_exact_source_and_action() -> None:
    actions = parse_actions(REFLECTION)
    digest = source_digest(REFLECTION)
    first = decide_wake(actions, [], source_digest=digest)
    assert first.wake_agent is True
    assert first.action_id == "delivery-summary"

    receipt = Receipt(
        proposal_id="proposal-1",
        action_id="delivery-summary",
        source_digest=digest,
        decision="no-safe-change",
        reason="synthetic refusal",
        created_at=utc_now(),
    )
    second = decide_wake(actions, [receipt], source_digest=digest)
    assert second.wake_agent is False
    assert second.reason == "already_processed"


def test_edited_source_is_reconsidered() -> None:
    actions = parse_actions(REFLECTION)
    old_digest = source_digest(REFLECTION)
    new_digest = source_digest(REFLECTION + "\nEvidence changed.\n")
    receipt = Receipt("p", "delivery-summary", old_digest, "applied", "done", utc_now())
    assert decide_wake(actions, [receipt], source_digest=new_digest).wake_agent is True


def test_unstructured_prose_never_becomes_an_action() -> None:
    prose = "# Reflection\n\nWe should perhaps improve notifications someday.\n"
    assert parse_actions(prose) == []
    assert (
        decide_wake([], [], source_digest=source_digest(prose)).reason == "no_pending_system_action"
    )
