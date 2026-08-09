"""Parse a deliberately small, portable reflection action format."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from pathlib import Path

from .models import Action, Receipt

_FIELD_ALIASES = {
    "id": ("id", "action", "行动"),
    "title": ("title", "标题"),
    "owner": ("owner", "负责人"),
    "status": ("status", "状态"),
    "verification": ("verification", "verify", "验收", "验证条件"),
}
_ACTION_HEADING = re.compile(r"^#{1,3}\s+(?:action(?:s)?|action loop|行动闭环|行动项)\b", re.I)
_LIST_ITEM = re.compile(r"^\s*(?:[-*]|\d+[.)])\s*(?:\[[ xX]\]\s*)?(?P<body>.+?)\s*$")


def source_digest(markdown: str) -> str:
    """Return a stable digest of the caller-provided reflection text."""

    normalized = markdown.replace("\r\n", "\n").strip() + "\n"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _section_lines(markdown: str) -> Iterable[str]:
    lines = markdown.splitlines()
    start = next((index for index, line in enumerate(lines) if _ACTION_HEADING.match(line)), None)
    if start is None:
        return ()
    selected: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("#"):
            break
        selected.append(line)
    return selected


def _field(body: str, aliases: tuple[str, ...]) -> str:
    names = "|".join(re.escape(alias) for alias in aliases)
    match = re.search(rf"(?:^|[;；])\s*(?:{names})\s*[:：]\s*([^;；]+)", body, re.I)
    return match.group(1).strip() if match else ""


def _title(body: str, explicit: str) -> str:
    if explicit:
        return explicit
    stripped = re.sub(
        r"(?:^|[;；])\s*(?:id|action|行动|owner|负责人|status|状态|verification|verify|验收|验证条件)\s*[:：]\s*[^;；]+",
        "",
        body,
        flags=re.I,
    )
    return stripped.strip(" ;；") or "Untitled action"


def _list_bodies(lines: Iterable[str]) -> Iterable[str]:
    """Join one indented continuation block to its preceding list item."""

    current: list[str] = []
    for line in lines:
        matched = _LIST_ITEM.match(line)
        if matched:
            if current:
                yield " ".join(current)
            current = [matched.group("body")]
            continue
        if current and line.strip() and line[:1].isspace():
            previous = current[-1].rstrip()
            separator = " " if previous.endswith((";", "；")) else "; "
            current.append(separator + line.strip())
            continue
        if current and line.strip():
            yield " ".join(current)
            current = []
    if current:
        yield " ".join(current)


def parse_actions(markdown: str) -> list[Action]:
    """Extract action list items that explicitly state a status.

    The parser accepts English and Chinese field labels but intentionally does
    not guess hidden actions from prose. If a reflection is unstructured, it
    produces no executable candidates.
    """

    actions: list[Action] = []
    for body in _list_bodies(_section_lines(markdown)):
        status = _field(body, _FIELD_ALIASES["status"]).casefold().replace("_", "-")
        if not status:
            continue
        action_id = _field(body, _FIELD_ALIASES["id"])
        title = _title(body, _field(body, _FIELD_ALIASES["title"]))
        if not action_id:
            action_id = hashlib.sha256(title.encode("utf-8")).hexdigest()[:12]
        actions.append(
            Action(
                id=action_id,
                title=title,
                status=status,
                owner=_field(body, _FIELD_ALIASES["owner"]),
                verification=_field(body, _FIELD_ALIASES["verification"]),
            )
        )
    return actions


def load_receipts(directory: Path) -> list[Receipt]:
    """Load well-formed local receipts; malformed files are ignored safely."""

    if not directory.is_dir():
        return []
    receipts: list[Receipt] = []
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            fields = {field: str(data.get(field, "")) for field in Receipt.__dataclass_fields__}
            receipts.append(Receipt(**fields))
        except (OSError, json.JSONDecodeError, TypeError):
            continue
    return receipts
