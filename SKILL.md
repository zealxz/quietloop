---
name: quietloop
description: "Use when designing or operating evidence-driven reflection, receipt-gated low-risk automation, privacy-preserving memory hygiene, or reliable notification recovery for Hermes-based personal agents. Do not use for generic journaling, unrestricted self-modification, or any workflow that cannot provide explicit approval and rollback."
---

# QuietLoop

QuietLoop turns reflection into a bounded control loop:

```text
observe → extract explicit action → gate → stage → approve → apply → verify → receipt
```

It is deliberately **not** a general self-modifying agent. Silence is not success; a written reflection is not an outcome; and a model suggestion is never approval.

## Use this skill when

- A personal agent's daily/weekly/monthly reflection is expensive, repetitive, or unable to prove it improved anything.
- You need an idempotent `wakeAgent` decision based on explicit system actions and immutable receipts.
- You want to reduce memory/context bloat without silently discarding useful facts.
- A notification must survive provider context expiry or rate limiting through a consented, compact retry summary.
- A low-risk local configuration/documentation change should be proposed and applied only after explicit approval.

## Never use it to

- Read or upload a chat database, account token cache, or private reflection automatically.
- Forward full private reports between channels by default.
- Let a model write arbitrary code, shell scripts, credentials, or production configuration.
- Treat an LLM self-assessment as proof of user-task success.
- Apply a proposal without a human reviewer, a preimage digest, a narrow path policy, a backup, and a receipt.

## Operating procedure

1. **Minimize first.** Pass the smallest structured reflection or synthetic summary needed. Redact identifiers before persistence.
2. **Extract only explicit actions.** Supported list format is in `templates/reflection-template.md`. Prose is observation, not an executable task.
3. **Gate deterministically.** Run `quietloop gate --reflection ... --receipts ...`. `wakeAgent=false` means no model call.
4. **Stage, don't patch.** A model may produce a proposal outside the live root. Review its target, rationale, digest, and full replacement before considering it.
5. **Approve locally.** The core package is manual-approval-first. It allows only caller-configured, existing text files under a relative allowlist; code and shell are refused by default.
6. **Verify outcome separately.** A receipt proves a decision or write, not that a user task succeeded. Link a real test, delivery record, or user-confirmed outcome.
7. **Recover notifications minimally.** Keep failure queues local. At most send a redacted, consented summary after a fresh delivery context; acknowledge only after the scheduler records success.

## Hermes integration

Read `references/hermes-integration.md` before wiring QuietLoop to Hermes cron or platform adapters. The core package does not discover `~/.hermes`, call gateway APIs, or inspect message stores.

## Safety checks

Before any deployment, read `SECURITY.md`, `PRIVACY.md`, and `docs/threat-model.md`. Run the full test suite and use synthetic fixtures only.
