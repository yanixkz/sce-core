from __future__ import annotations

import os

import pytest

from sce.core.types import Link, RelationType, State
from sce.storage.postgres import PostgresRepository


def test_postgres_repository_round_trip_state_and_links():
    dsn = os.getenv("SCE_DATABASE_URL")
    if not dsn:
        pytest.skip("SCE_DATABASE_URL is not set")

    repo = PostgresRepository(dsn)
    repo.init_schema()

    source = State(state_type="evidence", data={"value": 1})
    target = State(state_type="hypothesis", data={"claim": "X"})

    repo.add_state(source)
    repo.add_state(target)
    repo.add_link(Link(source.state_id, target.state_id, RelationType.SUPPORTS, 0.9))

    restored = repo.get_state(target.state_id)
    incoming = repo.incoming_links(target.state_id)
    neighborhood = repo.neighborhood(target.state_id)

    assert restored.state_id == target.state_id
    assert restored.state_type == "hypothesis"
    assert restored.data["claim"] == "X"
    assert len(incoming) == 1
    assert incoming[0].relation_type == RelationType.SUPPORTS
    assert len(neighborhood) == 1

    repo.close()
