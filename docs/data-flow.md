# Data-flow boundaries

QuietLoop is useful only if it does not become another private-data exhaust pipe.

## Allowed default flow

```text
synthetic or minimized reflection text
  → explicit action fields
  → source digest + deterministic decision
  → local receipt / redacted queue event
  → optional human-reviewed change
```

## Explicitly forbidden default flow

```text
chat database → full transcript → prompt → cross-channel forward → public log
account token cache → queue / diagnostic
private absolute paths → README / receipt / issue
model suggestion → production file write
```

## Notification retry contract

A provider adapter may implement delivery recovery only when all conditions hold:

1. The user consented to the fallback destination.
2. It stores a stable event key and a **redacted summary**, not the full report.
3. It represents renewed send capability as `context_available: bool`; no token reaches QuietLoop's core API.
4. It sends at most the configured compact summary after capability returns.
5. It deletes an event only after its scheduler or provider reports success.
6. It rate-limits retries and exposes failures to the local operator.

This contract avoids the two common lies of notification systems: “we retried” and “we delivered.” They are different facts.
