from fastapi.testclient import TestClient

from sce.api import build_app


def test_health():
    client = TestClient(build_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ask_simple():
    client = TestClient(build_app())
    resp = client.post("/ask", json={"text": "check supplier risk"})
    assert resp.status_code == 200
    data = resp.json()
    assert "intent" in data
    assert "selected_plan" in data


def test_decide_minimal_request():
    client = TestClient(build_app())
    resp = client.post("/decide", json={"goal": "assess supplier risk", "context": {"supplier_id": "supplier A"}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == "v1"
    assert data["goal"] == "assess supplier risk"
    assert data["selected_plan"]
    assert isinstance(data["scores"], list)


def test_memory_and_reliability_empty_state():
    client = TestClient(build_app())

    memory_resp = client.get("/memory")
    assert memory_resp.status_code == 200
    memory_data = memory_resp.json()
    assert memory_data["version"] == "v1"
    assert memory_data["episodes"] == []
    if memory_data["meta"]["persistence"] == "postgres":
        assert memory_data["meta"]["scope"] == "durable postgres + process-local in-memory runtime"
    else:
        assert memory_data["meta"]["scope"] == "process-local in-memory"

    reliability_resp = client.get("/reliability")
    assert reliability_resp.status_code == 200
    reliability_data = reliability_resp.json()
    assert reliability_data["version"] == "v1"
    assert reliability_data["reliability"]["recent_window_size"] == 0
    assert reliability_data["reliability"]["average_reliability"] is None
    if reliability_data["meta"]["persistence"] == "postgres":
        assert reliability_data["meta"]["scope"] == "durable postgres + process-local in-memory runtime"
    else:
        assert reliability_data["meta"]["scope"] == "process-local in-memory"


def test_durable_memory_and_reliability_when_database_configured(monkeypatch):
    class FakePostgresEpisodeRepository:
        def __init__(self, dsn: str) -> None:
            self.dsn = dsn
            self._episodes = []

        def init_schema(self) -> None:
            return None

        def save_episode(self, episode) -> None:
            self._episodes.append(episode)

        def list_episodes(self, limit=None):
            ordered = list(reversed(self._episodes))
            return ordered if limit is None else ordered[:limit]

        def clear(self) -> None:
            self._episodes.clear()

    monkeypatch.setenv("SCE_DATABASE_URL", "postgresql://unused")
    monkeypatch.setattr("sce.api.PostgresEpisodeRepository", FakePostgresEpisodeRepository)

    client = TestClient(build_app())
    decide = client.post("/decide", json={"goal": "assess supplier risk", "context": {"supplier_id": "supplier A"}, "execute": True})
    assert decide.status_code == 200
    decide_data = decide.json()
    assert decide_data["meta"]["memory_persistence"] == "postgres+memory"
    assert decide_data["meta"]["memory_durable_status"] == "enabled"

    memory_resp = client.get("/memory")
    assert memory_resp.status_code == 200
    memory_data = memory_resp.json()
    assert memory_data["episodes"]
    assert memory_data["meta"]["persistence"] == "postgres"
    assert memory_data["meta"]["scope"] == "durable postgres + process-local in-memory runtime"

    reliability_resp = client.get("/reliability")
    assert reliability_resp.status_code == 200
    reliability_data = reliability_resp.json()
    assert reliability_data["reliability"]["reliability_episode_count"] >= 1
    assert reliability_data["meta"]["persistence"] == "postgres"
