from quietloop.redaction import redact_text


def test_redactor_removes_common_sensitive_fragments() -> None:
    bearer_value = "abcd" * 7
    raw = (
        f"Bearer {bearer_value} token=super-secret email=a.person@example.com path=/home/alice/key"
    )
    clean = redact_text(raw)
    assert bearer_value not in clean
    assert "super-secret" not in clean
    assert "a.person@example.com" not in clean
    assert "/home/alice" not in clean


def test_redactor_respects_output_budget() -> None:
    assert redact_text("x" * 20, limit=8) == "xxxxxxxx…"
