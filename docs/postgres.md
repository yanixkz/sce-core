# PostgreSQL backend

SCE Core includes an experimental PostgreSQL repository backend.

The default runtime backend is still `MemoryRepository`. PostgreSQL support is currently intended for persistence experiments and early integration work.

## Current status

PostgreSQL support is Phase 1 / experimental.

It currently supports persistence for:

- states
- links
- transitions
- events
- attractors
- episodes (including success/reward/reliability metadata used by `/memory` and `/reliability` when DB is configured)

Callable constraints and executable rules are still primarily handled by the in-memory runtime. This is intentional: Python callables cannot be safely or meaningfully serialized into SQL without a separate constraint/rule expression layer.

## CI integration

PostgreSQL is already integrated into GitHub Actions CI.

The test workflow spins up a PostgreSQL service and runs integration tests automatically when `SCE_DATABASE_URL` is set.

## Dependency

Install dependencies:

```bash
pip install -r requirements.txt
```

This installs:

```text
psycopg[binary]
```

## Connection string

The optional PostgreSQL test uses:

```bash
export SCE_DATABASE_URL="postgresql://postgres:pass@localhost:5432/postgres"
```

On Windows PowerShell:

```powershell
$env:SCE_DATABASE_URL="postgresql://postgres:pass@localhost:5432/postgres"
```

## Minimal usage

```python
from sce.core.types import State
from sce.storage.postgres import PostgresRepository

repo = PostgresRepository("postgresql://postgres:pass@localhost:5432/postgres")
repo.init_schema()

state = State(state_type="hypothesis", data={"claim": "supplier A is reliable"})
repo.add_state(state)

restored = repo.get_state(state.state_id)
print(restored.data)

repo.close()
```

## Optional test

The repository includes an optional PostgreSQL test:

```bash
pytest tests/test_postgres_repository.py
```

If `SCE_DATABASE_URL` is not set, the test is skipped.

If it is set, the test checks:

- schema initialization
- state persistence
- state retrieval
- link persistence
- incoming links
- neighborhood traversal

## Design notes

The PostgreSQL backend is not a replacement for the in-memory runtime yet.
The runtime remains hybrid: in-memory structures are still the fast execution view, while PostgreSQL is used as a durable backing store for episode history.

Current split:

```text
MemoryRepository:
    full runtime behavior
    callable constraints
    executable rules
    demo execution

PostgresRepository:
    persistent states
    persistent links
    persistent transitions
    persistent events
    persistent attractors
```

## Why constraints and rules are not fully persisted yet

`Constraint` and `Rule` objects currently contain Python callables:

```python
predicate: Callable[[State], bool]
transform: Callable[[State], list[State]]
```

These functions cannot be safely stored in PostgreSQL as executable logic.

A future version should introduce a constraint/rule expression layer.

## Warning

This backend is experimental and not production-ready.
