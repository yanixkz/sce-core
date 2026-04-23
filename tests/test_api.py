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
    assert memory_data["meta"]["scope"] == "process-local in-memory"

    reliability_resp = client.get("/reliability")
    assert reliability_resp.status_code == 200
    reliability_data = reliability_resp.json()
    assert reliability_data["version"] == "v1"
    assert reliability_data["reliability"]["recent_window_size"] == 0
    assert reliability_data["reliability"]["average_reliability"] is None
