# Hermes integration contract

QuietLoop can complement a Hermes Agent deployment, but the core package intentionally does not import Hermes internals. Hermes schemas, gateway implementations, and platform adapters evolve independently.

## Recommended shape

```text
Hermes pre-check script
  ├─ collect only required counters / redacted summaries
  ├─ render a structured reflection action list
  ├─ call `quietloop gate`
  └─ wake an LLM only when the decision is true

Hermes optimizer
  ├─ writes a proposal to an isolated staging directory
  ├─ never modifies live files directly
  └─ attaches source digest and target preimage digest

Local safety runner
  ├─ requires a named local approver
  ├─ calls `quietloop apply --i-understand`
  ├─ runs an independent verification command
  └─ writes/retains receipts locally
```

## Privacy requirements

An adapter must not copy message content, session IDs, chat IDs, account tokens, or absolute paths into QuietLoop's default CLI output, repository, test fixtures, or public logs.

Instead of handing a provider token to the core, an adapter should pass only an opaque capability such as:

```json
{"context_available": true, "destination": "consented-alias"}
```

The alias should be local and non-identifying. The adapter owns any map to a real provider destination.

## Cron design

A no-op is the expected healthy result for most runs:

- no new action → no model call;
- final receipt for exact source → no model call;
- no pending delivery → no outbound notification;
- no fresh provider context → no retry.

Use idempotency keys. If an adapter retries a notification, retain the event until the scheduler reports a **successful delivery**, not merely a successful attempt to enqueue work.

## Versioning

Treat the integration as its own compatibility surface. Pin or contract-test the Hermes cron JSON fields, output paths, and gateway interfaces you rely on. Never make the core package guess them.
