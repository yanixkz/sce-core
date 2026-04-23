from __future__ import annotations

import os
from datetime import timedelta
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from psycopg.types.json import Jsonb

from sce.core.episode_memory import Episode, utc_now
from sce.core.types import Link, RelationType, State
from sce.storage.postgres import (
    POSTGRES_MIGRATION_SQL,
    PostgresEpisodeRepository,
    PostgresRepository,
)


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


def test_postgres_migration_includes_episodes_table():
    assert "CREATE TABLE IF NOT EXISTS episodes" in POSTGRES_MIGRATION_SQL
    assert "episode_id           UUID PRIMARY KEY" in POSTGRES_MIGRATION_SQL
    assert "created_at           TIMESTAMPTZ NOT NULL" in POSTGRES_MIGRATION_SQL
    assert "state_snapshot       JSONB NOT NULL" in POSTGRES_MIGRATION_SQL
    assert "action_names         JSONB NOT NULL" in POSTGRES_MIGRATION_SQL
    assert "reliability          DOUBLE PRECISION" in POSTGRES_MIGRATION_SQL
    assert "source               TEXT NOT NULL DEFAULT 'unknown'" in POSTGRES_MIGRATION_SQL
    assert "scope                TEXT NOT NULL DEFAULT 'decision'" in POSTGRES_MIGRATION_SQL
    assert "CREATE INDEX IF NOT EXISTS idx_episodes_created_at ON episodes(created_at);" in POSTGRES_MIGRATION_SQL
    assert "CREATE INDEX IF NOT EXISTS idx_episodes_goal ON episodes(goal);" in POSTGRES_MIGRATION_SQL
    assert "CREATE INDEX IF NOT EXISTS idx_episodes_plan_name ON episodes(plan_name);" in POSTGRES_MIGRATION_SQL


def test_postgres_episode_repository_save_list_clear_without_db(monkeypatch):
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.__enter__.return_value = fake_cursor
    fake_cursor.__exit__.return_value = None
    fake_conn.cursor.return_value = fake_cursor
    monkeypatch.setattr("sce.storage.postgres.psycopg.connect", lambda _: fake_conn)

    repo = PostgresEpisodeRepository("postgresql://unused")
    now = utc_now()
    older = Episode(
        episode_id=uuid4(),
        created_at=now - timedelta(minutes=1),
        state_snapshot={"mode": "older"},
        goal="g",
        plan_name="p",
        action_names=["a1"],
        success=False,
        reward=0.1,
        reason="r1",
        reliability=0.25,
        source="/decide",
        scope="api_execute",
    )
    newer = Episode(
        episode_id=uuid4(),
        created_at=now,
        state_snapshot={"mode": "newer"},
        goal="g",
        plan_name="p",
        action_names=["a2"],
        success=True,
        reward=0.9,
        reason="r2",
        reliability=0.9,
        source="/decide",
        scope="api_execute",
    )

    repo.save_episode(older)
    insert_query, insert_params = fake_cursor.execute.call_args[0]
    assert "INSERT INTO episodes" in insert_query
    assert insert_params[0] == str(older.episode_id)
    assert isinstance(insert_params[2], Jsonb)
    assert isinstance(insert_params[5], Jsonb)
    assert insert_params[9] == older.reliability
    assert insert_params[10] == older.source
    assert insert_params[11] == older.scope

    fake_cursor.fetchall.return_value = [
        (
            newer.episode_id,
            newer.created_at,
            newer.state_snapshot,
            newer.goal,
            newer.plan_name,
            newer.action_names,
            newer.success,
            newer.reward,
            newer.reason,
            newer.reliability,
            newer.source,
            newer.scope,
        ),
        (
            older.episode_id,
            older.created_at,
            older.state_snapshot,
            older.goal,
            older.plan_name,
            older.action_names,
            older.success,
            older.reward,
            older.reason,
            older.reliability,
            older.source,
            older.scope,
        ),
    ]
    fake_cursor.execute.reset_mock()

    episodes = repo.list_episodes(limit=1)
    select_query, select_params = fake_cursor.execute.call_args[0]
    assert "ORDER BY created_at DESC" in select_query
    assert "LIMIT %s" in select_query
    assert select_params == (1,)
    assert episodes[0].episode_id == newer.episode_id
    assert episodes[0].reliability == newer.reliability

    fake_cursor.execute.reset_mock()
    repo.clear()
    clear_query = fake_cursor.execute.call_args[0][0]
    assert clear_query == "DELETE FROM episodes"


def test_postgres_episode_repository_integration_round_trip():
    dsn = os.getenv("SCE_DATABASE_URL")
    if not dsn:
        pytest.skip("SCE_DATABASE_URL is not set")

    repo = PostgresEpisodeRepository(dsn)
    repo.init_schema()
    repo.clear()
    now = utc_now()

    older = Episode(
        episode_id=uuid4(),
        created_at=now - timedelta(seconds=1),
        state_snapshot={"priority": "low"},
        goal="ship",
        plan_name="safe_plan",
        action_names=["check"],
        success=False,
        reward=0.2,
        reason="too_slow",
        reliability=0.3,
        source="/decide",
        scope="api_execute",
    )
    newer = Episode(
        episode_id=uuid4(),
        created_at=now,
        state_snapshot={"priority": "high"},
        goal="ship",
        plan_name="fast_plan",
        action_names=["deploy"],
        success=True,
        reward=1.0,
        reason="done",
        reliability=0.95,
        source="/decide",
        scope="api_execute",
    )

    repo.save_episode(older)
    repo.save_episode(newer)

    episodes = repo.list_episodes()
    assert len(episodes) >= 2
    assert episodes[0].episode_id == newer.episode_id
    assert episodes[1].episode_id == older.episode_id
    assert episodes[0].state_snapshot["priority"] == "high"
    assert episodes[0].reliability == pytest.approx(0.95)

    limited = repo.list_episodes(limit=1)
    assert len(limited) == 1
    assert limited[0].episode_id == newer.episode_id

    repo.clear()
    assert repo.list_episodes() == []
    repo.close()
