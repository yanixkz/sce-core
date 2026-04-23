# Contributing

SCE Core is an early product/research system. Keep contributions focused, observable, and easy to review.

## Pick a workstream

Use one primary workstream framing per issue/PR:

- `product`
- `research`
- `api`
- `core`
- `docs`
- `tests`
- `governance`

Reference: [`docs/governance.md`](docs/governance.md).

## Typical contribution areas

- candidate generation and ranking quality
- constraint DSL and validation ergonomics
- coherence/conflict/entropy and reliability formulas
- decision backbone and graph inspectability
- memory and PostgreSQL persistence behavior
- API/UI contract clarity and documentation
- scenario coverage for flagship demos

## Minimal flow

1. Start from a focused issue (or open one with clear acceptance criteria).
2. Keep PRs small and scoped to one dominant workstream.
3. Run tests before opening a PR.
4. State backward-compatibility impact explicitly.

Run tests:

```bash
pytest
```
