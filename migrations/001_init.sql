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

CREATE INDEX IF NOT EXISTS idx_states_type ON states(state_type);
CREATE INDEX IF NOT EXISTS idx_states_stability ON states(stability DESC);
CREATE INDEX IF NOT EXISTS idx_states_signature ON states(signature_hash);
CREATE INDEX IF NOT EXISTS idx_states_valid_from_to ON states(valid_from, valid_to);
CREATE INDEX IF NOT EXISTS idx_transitions_from ON transitions(from_state_id);
CREATE INDEX IF NOT EXISTS idx_transitions_to ON transitions(to_state_id);
CREATE INDEX IF NOT EXISTS idx_transitions_selected ON transitions(selected);
CREATE INDEX IF NOT EXISTS idx_links_source ON state_links(source_state_id);
CREATE INDEX IF NOT EXISTS idx_links_target ON state_links(target_state_id);
CREATE INDEX IF NOT EXISTS idx_links_relation_type ON state_links(relation_type);
CREATE INDEX IF NOT EXISTS idx_events_time ON events(event_time);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_attractors_signature ON attractors(signature_hash);
CREATE INDEX IF NOT EXISTS idx_episodes_created_at ON episodes(created_at);
CREATE INDEX IF NOT EXISTS idx_episodes_goal ON episodes(goal);
CREATE INDEX IF NOT EXISTS idx_episodes_plan_name ON episodes(plan_name);
