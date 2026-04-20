from __future__ import annotations

import json
from typing import List
from uuid import UUID

import psycopg

from sce.core.types import Link, State, Transition, Event, EventType, Attractor

from .postgres import POSTGRES_MIGRATION_SQL  # type: ignore


class PostgresRepository:
    """Basic PostgreSQL repository (Phase 1)."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.conn = psycopg.connect(dsn)

    def init_schema(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(POSTGRES_MIGRATION_SQL)
        self.conn.commit()

    def add_state(self, state: State) -> UUID:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO states (state_id, state_type, data_json, energy, entropy, coherence, conflict, stability, support_score, signature_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    state.state_id,
                    state.state_type,
                    json.dumps(state.data),
                    state.energy,
                    state.entropy,
                    state.coherence,
                    state.conflict,
                    state.stability,
                    state.support,
                    state.signature,
                ),
            )
        self.conn.commit()
        return state.state_id

    def get_state(self, state_id: UUID) -> State:
        with self.conn.cursor() as cur:
            cur.execute("SELECT state_type, data_json FROM states WHERE state_id = %s", (state_id,))
            row = cur.fetchone()
        if not row:
            raise KeyError(state_id)
        return State(state_type=row[0], data=row[1])  # partial reconstruction

    def add_link(self, link: Link) -> UUID:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO state_links (link_id, source_state_id, target_state_id, relation_type, strength, directed)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    link.link_id,
                    link.source_state_id,
                    link.target_state_id,
                    link.relation_type,
                    link.strength,
                    link.directed,
                ),
            )
        self.conn.commit()
        return link.link_id

    def incoming_links(self, state_id: UUID) -> List[Link]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT link_id, source_state_id, relation_type, strength, directed FROM state_links WHERE target_state_id = %s",
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
            )
            for row in rows
        ]

    def outgoing_links(self, state_id: UUID) -> List[Link]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT link_id, target_state_id, relation_type, strength, directed FROM state_links WHERE source_state_id = %s",
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
            )
            for row in rows
        ]

    def neighborhood(self, state_id: UUID) -> List[State]:
        links = self.incoming_links(state_id) + self.outgoing_links(state_id)
        ids = {l.source_state_id for l in links} | {l.target_state_id for l in links}
        ids.discard(state_id)
        return [self.get_state(i) for i in ids]

    def add_transition(self, transition: Transition) -> UUID:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO transitions (transition_id, from_state_id, to_state_id, cost, admissible, selected)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    transition.transition_id,
                    transition.from_state_id,
                    transition.to_state_id,
                    transition.cost,
                    transition.admissible,
                    transition.selected,
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
                INSERT INTO events (event_id, event_type, state_id, transition_id, payload_json)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    event.event_id,
                    event.event_type.value,
                    event.state_id,
                    event.transition_id,
                    json.dumps(event.payload),
                ),
            )
        self.conn.commit()
        return event.event_id

    def add_attractor(self, attractor: Attractor) -> UUID:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO attractors (attractor_id, attractor_type, signature_hash, stability_score)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    attractor.attractor_id,
                    attractor.attractor_type,
                    attractor.signature_hash,
                    attractor.stability_score,
                ),
            )
        self.conn.commit()
        return attractor.attractor_id
