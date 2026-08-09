# Reflection template

Use a concise action section. Everything outside it is observation and should not be treated as an executable request.

```markdown
# Reflection — YYYY-MM-DD

## Evidence

- One or two minimized facts, links, or test references.

## Action loop

1. id: concise-stable-id; title: Plain-language action;
   owner: agent-or-operator; status: pending-system;
   verification: Observable condition that proves the result.

## Non-actions

- Risks, questions, and ideas that are not ready for a bounded change.
```

## Statuses

- `pending-system`: eligible for a deterministic gate.
- `pending-automation`: eligible for a deterministic gate.
- `done`: informational; never wakes the loop.
- `blocked`: informational; never wakes the loop.

Do not put raw messages, credentials, account identifiers, or full operational logs in this file.
