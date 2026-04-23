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
