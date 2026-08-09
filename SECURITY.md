# Security policy

## Scope

QuietLoop is intentionally conservative. It evaluates structured actions, produces receipts, maintains a local retry queue, and can apply a narrowly scoped text proposal **only after explicit local approval**. It is not a sandbox, a credential manager, or a general-purpose self-modifying agent.

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |
| < 0.1 | No |

## Reporting a vulnerability

Please do **not** open a public issue for a vulnerability that could expose a local file, credential, conversation, queue, or approval bypass.

Open a private GitHub security advisory for this repository, with:

1. A minimal reproduction using synthetic data;
2. The affected version and platform;
3. The impact and expected safe behavior;
4. A suggested fix if you have one.

We will acknowledge reports within seven days and prioritize fixes for data disclosure, path traversal, symlink escape, approval bypass, unsafe writes, and queue corruption.

## Security invariants

- Core code never sends network traffic.
- Core code never discovers Hermes homes, databases, accounts, or messaging tokens automatically.
- Auto-apply is disabled by default.
- Any write must pass a relative-path allowlist, preimage digest check, size budget, explicit approval, backup, atomic replacement, and receipt write.
- Example data is synthetic. Real operational state belongs outside Git.
