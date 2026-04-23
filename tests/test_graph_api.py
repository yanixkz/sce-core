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
    assert isinstance(data["meta"]["node_count"], int)
    assert isinstance(data["meta"]["edge_count"], int)
    assert "node_fields" in data["meta"]["schema"]
    assert "edge_fields" in data["meta"]["schema"]
    assert data["meta"]["ui"]["default_layout"] == "force-directed"
