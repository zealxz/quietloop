# QuietLoop

> **A reflection loop for personal agents that can show its work.**
>
> *Observe → decide → stage → approve → apply → verify → receipt.*

[![CI](https://github.com/zealxz/quietloop/actions/workflows/ci.yml/badge.svg)](https://github.com/zealxz/quietloop/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-0b9.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776ab.svg)](pyproject.toml)

Most personal agents can produce a reflection. Few can answer the harder questions:

- *Was there a real action, or only an eloquent summary?*
- *Did we already process this exact issue?*
- *Who authorized the change?*
- *Can we recover it?*
- *Did anything improve for the person using the agent?*

**QuietLoop** is a small, local-first toolkit and [Hermes Agent](https://hermes-agent.nousresearch.com/) skill for answering those questions with receipts instead of vibes.

It does not claim unrestricted self-improvement. It gives you a safer primitive: a private, idempotent, evidence-driven loop for turning an explicitly stated problem into a bounded and reviewable change.

## The promise

```text
   private observation
           │
           ▼
  explicit structured action ── no action / already receipted ──► sleep
           │
           ▼
  deterministic gate ──► isolated proposal (never live mutation)
                                      │
                                      ▼
                              human local approval
                                      │
                                      ▼
                     bounded apply + backup + receipt
                                      │
                                      ▼
                        independent outcome verification
```

**QuietLoop is local by default.** The core package makes no network calls, does not discover your Hermes installation, does not read chat databases, and does not scan account/token caches.

## Why this exists

It started as a real operational problem in a personal agent built collaboratively by **zealx × NOVA**: daily reflection had become costly, the “optimizer” could repeat a rejected idea forever, memory tools were adding more context than value, and a notification could disappear when a messaging provider lost reply context.

The useful parts are open-sourced here. The private operational data, account adapters, and machine-specific logic are not.

## What is included

- **Structured action parser** — extracts only explicit action items, in English or Chinese.
- **Receipt-aware gate** — avoids repeated model calls when an immutable source/action pair already has a final decision.
- **Local state primitives** — atomic JSON plus inter-process file locking.
- **Redaction layer** — removes common secrets, email addresses, home paths, long IDs, and bearer strings from short diagnostics.
- **Retry queue** — idempotent, redacted pending-delivery events with explicit acknowledgement.
- **Bounded apply primitive** — disabled unless a local reviewer approves an exact proposal. Defaults refuse code, shell, new files, path traversal, symlinks, stale preimages, and oversized writes.
- **Hermes skill** — a concise operational guide in [`SKILL.md`](SKILL.md), with integration contracts rather than private implementation details.

## What is intentionally not included

- Any real chat messages, user IDs, account IDs, tokens, databases, cron outputs, backups, or reflection archives.
- Network delivery clients, telemetry, or hidden provider calls.
- Arbitrary code execution or LLM-authorized self-modification.
- A promise that a receipt equals a successful user outcome.

## Quick start

Requirements: Python **3.11+** and a POSIX file-lock backend (Linux/macOS are the intended targets).

```bash
git clone https://github.com/zealxz/quietloop.git
cd quietloop
uv venv
uv pip install -e '.[dev]'
pytest
```

Use the included synthetic reflection:

```bash
mkdir -p /tmp/quietloop-receipts
quietloop gate \
  --reflection examples/synthetic-reflection.md \
  --receipts /tmp/quietloop-receipts
# {"wakeAgent": true, "reason": "unresolved_system_action", "action_id": "delivery-summary"}
```

A final receipt makes the same source/action pair quiet:

```bash
# Use a local JSON receipt with action_id=delivery-summary and the source_digest
# emitted/derived for the exact reflection. See tests/test_gate.py for a full,
# synthetic example.
```

### Install the Hermes skill

The skill is plain Markdown. Review it first, then install only the skill and its references:

```bash
mkdir -p ~/.hermes/skills/quietloop
rsync -a --delete \
  --include='SKILL.md' \
  --include='references/***' \
  --include='templates/***' \
  --exclude='*' \
  ./ ~/.hermes/skills/quietloop/
```

The Python package and Hermes skill are deliberately separable. The skill describes a safe process; the package implements portable, testable primitives.

## A minimal reflection format

QuietLoop executes no prose. Only a clear list item with an explicit status is eligible:

```markdown
## Action loop

1. id: delivery-summary; title: Add a compact recovery notice;
   owner: agent; status: pending-system;
   verification: a synthetic retry succeeds and emits no private content.
```

Recognized status values include `pending-system`, `pending-automation`, and `pending-auto`. All other text remains observation.

## Safe application model

The built-in apply primitive is intentionally narrow:

| Guardrail | Default behavior |
| --- | --- |
| Approval | Required for the exact proposal ID |
| Target | Existing regular file under `config/` or `docs/` |
| File types | `.md`, `.toml`, `.yaml`, `.yml` only |
| Code / shell | Refused |
| Path traversal / symlinks | Refused |
| Stale proposal | Refused via preimage SHA-256 |
| Write budget | 8 KiB replacement maximum |
| Recovery | Local backup and immutable receipt |

If your use case needs more power, extend policy cautiously and add an independent test. Do **not** turn off the checks to make a demo look autonomous.

## Hermes and notification recovery

The core package has no messaging dependency. For a Hermes deployment, use a separate adapter that follows this contract:

1. A failed delivery writes one **redacted** local event and sends nothing else by default.
2. The operator decides whether another channel may receive a summary.
3. A fresh provider context is represented as a boolean capability, never by exposing a token.
4. The adapter emits at most one compact summary.
5. The queue is acknowledged only after the scheduler records delivery success.

See [`references/hermes-integration.md`](references/hermes-integration.md) and [`docs/data-flow.md`](docs/data-flow.md).

## Threat model and privacy

Read these before connecting QuietLoop to real work:

- [Privacy promise](PRIVACY.md)
- [Security policy](SECURITY.md)
- [Threat model](docs/threat-model.md)
- [Data-flow boundaries](docs/data-flow.md)

The headline: **minimize what enters the loop; never treat redaction as permission to collect everything.**

## Development

```bash
uv pip install -e '.[dev]'
pytest
ruff check .
python -m build
```

The test suite uses only temporary directories and synthetic data. CI runs Python 3.11 and 3.12, linting, tests, build verification, and secret scanning.

## Roadmap

- [ ] Explicit Hermes adapter protocol with synthetic contract tests
- [ ] Consent-aware notification adapter examples
- [ ] Receipt signer interface for multi-operator deployments
- [ ] Benchmarks measuring reflection cost versus verified outcomes

No roadmap item will add telemetry, automatic chat-store discovery, or unrestricted code mutation.

## Star History

<a href="https://www.star-history.com/?repos=zealxz%2Fquietloop&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=zealxz/quietloop&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=zealxz/quietloop&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=zealxz/quietloop&type=date&legend=top-left" />
 </picture>
</a>

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [the code of conduct](CODE_OF_CONDUCT.md). Small tests that disprove a safety claim are especially welcome.

## Credits

QuietLoop was created collaboratively by **[zealx](https://github.com/zealxz) × NOVA**. See [AUTHORS.md](AUTHORS.md).

Released under the [MIT License](LICENSE).
