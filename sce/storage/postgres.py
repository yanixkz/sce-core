from __future__ import annotations

import json
from typing import Any, List
from uuid import UUID

import psycopg
from psycopg.types.json import Jsonb

from sce.core.episode_memory import Episode
from sce.core.types import Attractor, Event, Link, State, Transition

POSTGRES_MIGRATION_SQL = """
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS states (
    state_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    state_type          TEXT NOT NULL,
    data_json           JSONB NOT NULL,
    energy              DOUBLE PRECISION DEFAULT 0,
    entropy             DOUBLE PRECISION DEFAULT 0,
    coherence           DOUBLE PRECISION DEFAULT 0,
    conflict            DOUBLE PRECISION DEFAULT 0,
    stability           DOUBLE PRECISION DEFAULT 0,
    support_score       DOUBLE PRECISION DEFAULT 0,
    created_at          TIMESTAMP DEFAULT now(),
    valid_from          TIMESTAMP,
    valid_to            TIMESTAMP,
    status              TEXT DEFAULT 'active',
    signature_hash      TEXT,
    meta_json           JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS transitions (
    transition_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_state_id       UUID REFERENCES states(state_id),
    to_state_id         UUID REFERENCES states(state_id),
    rule_id             UUID,
    transition_type     TEXT,
    cost                DOUBLE PRECISION DEFAULT 0,
    probability         DOUBLE PRECISION DEFAULT 1,
    delta_time_ms       BIGINT,
    admissible          BOOLEAN DEFAULT true,
    selected            BOOLEAN DEFAULT false,
    created_at          TIMESTAMP DEFAULT now(),
    meta_json           JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS state_links (
    link_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_state_id     UUID REFERENCES states(state_id),
    target_state_id     UUID REFERENCES states(state_id),
    relation_type       TEXT NOT NULL,
    strength            DOUBLE PRECISION DEFAULT 1,
    directed            BOOLEAN DEFAULT true,
    created_at          TIMESTAMP DEFAULT now(),
    meta_json           JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS events (
    event_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type          TEXT NOT NULL,
    state_id            UUID,
    transition_id       UUID,
    event_time          TIMESTAMP DEFAULT now(),
    payload_json        JSONB DEFAULT '{}',
    meta_json           JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS attractors (
    attractor_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attractor_type      TEXT NOT NULL,
    signature_hash      TEXT,
    invariant_json      JSONB DEFAULT '{}',
    stability_score     DOUBLE PRECISION DEFAULT 0,
    discovered_at       TIMESTAMP DEFAULT now(),
    meta_json           JSONB DEFAULT '{}'
);


CREATE TABLE IF NOT EXISTS episodes (
    episode_id           UUID PRIMARY KEY,
    created_at           TIMESTAMPTZ NOT NULL,
    state_snapshot       JSONB NOT NULL,
    goal                 TEXT NOT NULL,
    plan_name            TEXT NOT NULL,
    action_names         JSONB NOT NULL,
    success              BOOLEAN NOT NULL,
    reward               DOUBLE PRECISION NOT NULL,
    reason               TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_episodes_created_at ON episodes(created_at);
CREATE INDEX IF NOT EXISTS idx_episodes_goal ON episodes(goal);
CREATE INDEX IF NOT EXISTS idx_episodes_plan_name ON episodes(plan_name);
"""


def _json_value(value: Any) -> Any:
    if isinstance(value, str):
        return json.loads(value)
    return value


class PostgresRepository:
    """Basic PostgreSQL repository for persistent states, links, transitions and events."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.conn = psycopg.connect(dsn)

    def close(self) -> None:
        self.conn.close()

    def init_schema(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(POSTGRES_MIGRATION_SQL)
        self.conn.commit()

    def add_state(self, state: State) -> UUID:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO states (
                    state_id, state_type, data_json, energy, entropy,
                    coherence, conflict, stability, support_score,
                    status, signature_hash, meta_json
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (state_id) DO UPDATE SET
                    state_type = EXCLUDED.state_type,
                    data_json = EXCLUDED.data_json,
                    energy = EXCLUDED.energy,
                    entropy = EXCLUDED.entropy,
                    coherence = EXCLUDED.coherence,
                    conflict = EXCLUDED.conflict,
                    stability = EXCLUDED.stability,
                    support_score = EXCLUDED.support_score,
                    status = EXCLUDED.status,
                    signature_hash = EXCLUDED.signature_hash,
                    meta_json = EXCLUDED.meta_json
                """,
                (
                    state.state_id,
                    state.state_type,
                    Jsonb(state.data),
                    state.energy,
                    state.entropy,
                    state.coherence,
                    state.conflict,
                    state.stability,
                    state.support,
                    state.status,
                    state.signature_hash,
                    Jsonb(state.meta),
                ),
            )
        self.conn.commit()
        return state.state_id

    def get_state(self, state_id: UUID) -> State:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT state_type, data_json, energy, entropy, coherence,
                       conflict, stability, support_score, status, signature_hash, meta_json
                FROM states
                WHERE state_id = %s
                """,
                (state_id,),
            )
            row = cur.fetchone()
        if not row:
            raise KeyError(state_id)
        return State(
            state_id=state_id,
            state_type=row[0],
            data=_json_value(row[1]),
            energy=row[2],
            entropy=row[3],
            coherence=row[4],
            conflict=row[5],
            stability=row[6],
            support=row[7],
            status=row[8],
            signature_hash=row[9],
            meta=_json_value(row[10]) or {},
        )

    def add_link(self, link: Link) -> UUID:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO state_links (link_id, source_state_id, target_state_id, relation_type, strength, directed, meta_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (link_id) DO NOTHING
                """,
                (
                    link.link_id,
                    link.source_state_id,
                    link.target_state_id,
                    link.relation_type.value,
                    link.strength,
                    link.directed,
                    Jsonb(link.meta),
                ),
            )
        self.conn.commit()
        return link.link_id

    def incoming_links(self, state_id: UUID) -> List[Link]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT link_id, source_state_id, relation_type, strength, directed, meta_json
                FROM state_links
                WHERE target_state_id = %s
                """,
                (state_id,),
            )
            rows = cur.fetchall()
        return [
            Link(
                link_id=row[0],
                source_state_id=row[1],
                target_state_id=state_id,
                relation_type=row[2],
                strength=row[3],
                directed=row[4],
                meta=_json_value(row[5]) or {},
            )
            for row in rows
        ]

    def outgoing_links(self, state_id: UUID) -> List[Link]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT link_id, target_state_id, relation_type, strength, directed, meta_json
                FROM state_links
                WHERE source_state_id = %s
                """,
                (state_id,),
            )
            rows = cur.fetchall()
        return [
            Link(
                link_id=row[0],
                source_state_id=state_id,
                target_state_id=row[1],
                relation_type=row[2],
                strength=row[3],
                directed=row[4],
                meta=_json_value(row[5]) or {},
            )
            for row in rows
        ]

    def neighborhood(self, state_id: UUID) -> List[State]:
        links = self.incoming_links(state_id) + self.outgoing_links(state_id)
        ids = {link.source_state_id for link in links} | {link.target_state_id for link in links}
        ids.discard(state_id)
        return [self.get_state(neighbor_id) for neighbor_id in ids]

    def add_transition(self, transition: Transition) -> UUID:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO transitions (
                    transition_id, from_state_id, to_state_id, rule_id,
                    transition_type, cost, probability, delta_time_ms,
                    admissible, selected, meta_json
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (transition_id) DO NOTHING
                """,
                (
                    transition.transition_id,
                    transition.from_state_id,
                    transition.to_state_id,
                    transition.rule_id,
                    transition.transition_type.value,
                    transition.cost,
                    transition.probability,
                    transition.delta_time_ms,
                    transition.admissible,
                    transition.selected,
                    Jsonb(transition.meta),
                ),
            )
        self.conn.commit()
        return transition.transition_id

    def mark_transition_selected(self, transition_id: UUID) -> None:
        with self.conn.cursor() as cur:
            cur.execute("UPDATE transitions SET selected = true WHERE transition_id = %s", (transition_id,))
        self.conn.commit()

    def add_event(self, event: Event) -> UUID:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO events (event_id, event_type, state_id, transition_id, payload_json, meta_json)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
                """,
                (
                    event.event_id,
                    event.event_type.value,
                    event.state_id,
                    event.transition_id,
                    Jsonb(event.payload),
                    Jsonb(event.meta),
                ),
            )
        self.conn.commit()
        return event.event_id

    def add_attractor(self, attractor: Attractor) -> UUID:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO attractors (attractor_id, attractor_type, signature_hash, invariant_json, stability_score, meta_json)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (attractor_id) DO NOTHING
                """,
                (
                    attractor.attractor_id,
                    attractor.attractor_type,
                    attractor.signature_hash,
                    Jsonb(attractor.invariant),
                    attractor.stability_score,
                    Jsonb(attractor.meta),
                ),
            )
        self.conn.commit()
        return attractor.attractor_id


class PostgresEpisodeRepository:
    """PostgreSQL-backed repository for episodic memory records."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.conn = psycopg.connect(dsn)

    def close(self) -> None:
        self.conn.close()

    def init_schema(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(POSTGRES_MIGRATION_SQL)
        self.conn.commit()

    def save_episode(self, episode: Episode) -> None:
        payload = episode.to_dict()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO episodes (
                    episode_id, created_at, state_snapshot, goal, plan_name,
                    action_names, success, reward, reason
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (episode_id) DO UPDATE SET
                    created_at = EXCLUDED.created_at,
                    state_snapshot = EXCLUDED.state_snapshot,
                    goal = EXCLUDED.goal,
                    plan_name = EXCLUDED.plan_name,
                    action_names = EXCLUDED.action_names,
                    success = EXCLUDED.success,
                    reward = EXCLUDED.reward,
                    reason = EXCLUDED.reason
                """,
                (
                    payload["episode_id"],
                    payload["created_at"],
                    Jsonb(payload["state_snapshot"]),
                    payload["goal"],
                    payload["plan_name"],
                    Jsonb(payload["action_names"]),
                    payload["success"],
                    payload["reward"],
                    payload["reason"],
                ),
            )
        self.conn.commit()

    def list_episodes(self, limit: int | None = None) -> List[Episode]:
        query = """
            SELECT
                episode_id,
                created_at,
                state_snapshot,
                goal,
                plan_name,
                action_names,
                success,
                reward,
                reason
            FROM episodes
            ORDER BY created_at DESC
        """
        params: tuple[int, ...] = ()
        if limit is not None:
            query += " LIMIT %s"
            params = (limit,)
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
        return [
            Episode.from_dict(
                {
                    "episode_id": str(row[0]),
                    "created_at": row[1].isoformat(),
                    "state_snapshot": _json_value(row[2]),
                    "goal": row[3],
                    "plan_name": row[4],
                    "action_names": _json_value(row[5]),
                    "success": row[6],
                    "reward": row[7],
                    "reason": row[8],
                }
            )
            for row in rows
        ]

    def clear(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM episodes")
        self.conn.commit()
