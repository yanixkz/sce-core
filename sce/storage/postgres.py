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

CREATE TABLE IF NOT EXISTS constraints (
    constraint_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    constraint_type     TEXT NOT NULL,
    scope_type          TEXT,
    scope_ref           TEXT,
    predicate_expr      TEXT NOT NULL,
    hard                BOOLEAN DEFAULT true,
    weight              DOUBLE PRECISION DEFAULT 1,
    priority            INTEGER DEFAULT 0,
    active_from         TIMESTAMP,
    active_to           TIMESTAMP,
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

CREATE TABLE IF NOT EXISTS attractor_members (
    attractor_id        UUID REFERENCES attractors(attractor_id),
    state_id            UUID REFERENCES states(state_id),
    membership_weight   DOUBLE PRECISION DEFAULT 1,
    PRIMARY KEY (attractor_id, state_id)
);

CREATE TABLE IF NOT EXISTS rules (
    rule_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_type           TEXT NOT NULL,
    name                TEXT NOT NULL,
    input_pattern       JSONB DEFAULT '{}',
    transform_expr      TEXT,
    cost_model          TEXT,
    active              BOOLEAN DEFAULT true,
    priority            INTEGER DEFAULT 0,
    meta_json           JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_states_type ON states(state_type);
CREATE INDEX IF NOT EXISTS idx_states_stability ON states(stability DESC);
CREATE INDEX IF NOT EXISTS idx_states_signature ON states(signature_hash);
CREATE INDEX IF NOT EXISTS idx_states_valid_from_to ON states(valid_from, valid_to);
CREATE INDEX IF NOT EXISTS idx_transitions_from ON transitions(from_state_id);
CREATE INDEX IF NOT EXISTS idx_transitions_to ON transitions(to_state_id);
CREATE INDEX IF NOT EXISTS idx_transitions_selected ON transitions(selected);
CREATE INDEX IF NOT EXISTS idx_constraints_scope ON constraints(scope_type, scope_ref);
CREATE INDEX IF NOT EXISTS idx_constraints_active ON constraints(active_from, active_to);
CREATE INDEX IF NOT EXISTS idx_links_source ON state_links(source_state_id);
CREATE INDEX IF NOT EXISTS idx_links_target ON state_links(target_state_id);
CREATE INDEX IF NOT EXISTS idx_links_relation_type ON state_links(relation_type);
CREATE INDEX IF NOT EXISTS idx_events_time ON events(event_time);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_attractors_signature ON attractors(signature_hash);
"""


class PostgresRepository:
    """Stub for Phase 2. MemoryRepository is used for MVP execution."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
