# Architecture

QuietLoop has one job: make an agent's reflective behavior **inspectable and bounded**.

## Layers

```text
┌───────────────────────────────────────────────────────────┐
│ Integration boundary (optional)                            │
│ Hermes cron, message providers, local observability        │
│ Must supply explicit/sanitized inputs; not in core         │
└─────────────────────────┬─────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│ QuietLoop core                                             │
│ reflection parser │ gate │ receipts │ queue │ redaction    │
│ policy │ approved text apply │ atomic local state          │
└─────────────────────────┬─────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│ Operator boundary                                          │
│ reviews proposal │ gives local approval │ verifies outcome │
└───────────────────────────────────────────────────────────┘
```

## Trust boundaries

| Boundary | What crosses it | Required control |
| --- | --- | --- |
| Observation → reflection | minimized, purpose-specific facts | data minimization and redaction |
| Reflection → gate | explicit action fields only | deterministic parser and source digest |
| Gate → proposal | a candidate change, never authority | isolated staging and path policy |
| Proposal → application | immutable proposal plus local approval | digest, allowlist, backup, atomic write |
| Application → outcome | independent test or user-visible result | receipt is necessary but not sufficient |
| Delivery failure → retry | compact redacted summary | consent, idempotency, scheduler-confirmed acknowledgement |

## Receipt semantics

A receipt tells you that a decision was made for a specific `action_id + source_digest` pair. It can record `applied`, `no-safe-change`, or `rejected`.

It does **not** prove the real world improved. Store outcome evidence separately: a test result, a delivery acknowledgement, a completed artifact, or user confirmation.

## Portability

The core only needs Python 3.11+ and POSIX file locks. It deliberately knows nothing about Hermes's internal SQLite schema, a platform's context-token format, or a specific filesystem layout. Those are adapter concerns and should be versioned/tested independently.
