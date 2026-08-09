# Threat model

QuietLoop protects against accidental over-automation in a personal-agent environment. It does not claim to defend against a fully compromised operating system or a malicious operator with filesystem access.

## Assets

- Conversation content and titles
- Account identifiers and delivery contexts
- Credentials and bearer tokens
- Local configuration and production documents
- Proposal/receipt integrity
- Notification delivery state

## Threats and mitigations

| Threat | Example | Mitigation | Residual risk |
| --- | --- | --- | --- |
| Reflection leaks private data | A transcript is pasted into a proposal or receipt | Core never discovers data; caller minimization; redaction; synthetic examples | A caller can still provide sensitive input |
| Repeated autonomous churn | Same rejected action wakes a model every day | `action_id + source_digest` receipt gate | Edited source is intentionally reconsidered |
| Unauthorized mutation | Model writes a config after self-evaluation | Explicit approval, allowed prefixes/suffixes, preimage digest, backup, receipt | Operator can widen policy; review remains necessary |
| Path escape | `../../config` or symlink target | Relative-path checks, resolved-root containment, symlink refusal | Filesystem TOCTOU is out of scope for untrusted local users |
| Stale overwrite | File changes after proposal was made | SHA-256 preimage check | Concurrent writers should coordinate outside the tool |
| Queue replay or loss | Retry sends an event twice or an ack drops it | Stable event key, lock, atomic JSON, explicit acknowledgement | Provider delivery acknowledgement is adapter-specific |
| Cross-channel disclosure | Full failed report silently forwarded | Core has no transport; compact redacted/consented summaries only | Integrator can violate contract |
| “Receipt equals outcome” theater | Applied edit treated as task success | Separate decision/application receipts from independent outcome evidence | Requires operational discipline |

## Non-goals

- Sandboxing arbitrary Python or shell changes
- Vetting third-party model output as safe code
- Managing provider authentication or refresh tokens
- Telemetry, remote logging, or cloud synchronization
- Replacing a change-review process for high-impact systems

## Deployment checklist

1. Keep QuietLoop state outside version control.
2. Run it with least filesystem privilege.
3. Start with `docs/` only; do not expand the apply allowlist casually.
4. Keep adapters separate from core and test them using fake provider state.
5. Record a real outcome before calling a loop successful.
6. Rotate any credential accidentally placed in a prompt, issue, terminal output, or commit.
