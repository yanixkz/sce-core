from fastapi.testclient import TestClient

from sce.api import build_app


def test_graph_endpoint():
    client = TestClient(build_app())
    resp = client.get("/graph")
    assert resp.status_code == 200
    data = resp.json()

    assert data["version"] == "v1"
    assert "graph" in data
    assert isinstance(data["graph"], dict)
    assert "meta" in data
    assert data["meta"]["source"] == "supplier-reliability"
