# Contributing

Thanks for helping make personal-agent automation more useful without making it more invasive.

## Before opening a pull request

1. Use a branch with one coherent purpose.
2. Do not include real conversations, identifiers, filesystem paths, account metadata, receipts, queues, or credentials.
3. Add or update a synthetic test for behavioral changes.
4. Run:

   ```bash
   uv pip install -e '.[dev]'
   pytest
   ruff check .
   python -m build
   ```

5. Explain whether the change affects privacy, approval, write scope, or recovery behavior.

## Design principles

- Prefer explicit input over filesystem discovery.
- Prefer a refusal over a clever unsafe fallback.
- Separate proposal, approval, application, and outcome.
- Keep a receipt small, factual, and free of content that does not need to be there.
- A green unit test does not prove a user task succeeded; say which evidence you have.

## Pull request checklist

- [ ] No private or production data
- [ ] No new network behavior without explicit documentation and tests
- [ ] Default behavior remains fail-closed
- [ ] New writes have a rollback/receipt story
- [ ] Tests use only synthetic fixtures
- [ ] Documentation matches the actual behavior

Security-sensitive changes should follow [SECURITY.md](SECURITY.md), not a public issue.
