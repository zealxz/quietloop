# Privacy promise

QuietLoop is built around a simple rule:

> Reflection should reduce private context, not create another place for it to leak.

## The core package does not

- read your chat database;
- scan your home directory or `$HERMES_HOME`;
- discover messaging accounts or context tokens;
- send telemetry, analytics, or network requests;
- upload reflections, receipts, queues, or proposals;
- forward full failed messages across channels.

## The core package may store locally

Only when a caller explicitly gives it paths and asks it to do so:

- a sanitized proposal;
- a receipt with digest, decision, and timestamp;
- an application backup under a caller-selected state directory;
- a compact retry event whose summary passes the built-in redactor.

These runtime files should remain local and are ignored by this repository.

## Integration responsibility

The optional Hermes and delivery examples are contracts, not a license to move private data around. An integrator must obtain destination consent, minimize summaries, redact before persistence, and keep account identifiers outside logs and repositories.

Before publishing an issue, example, benchmark, or screenshot: use synthetic data and search it for emails, tokens, chat IDs, absolute home paths, job IDs, and message text.
