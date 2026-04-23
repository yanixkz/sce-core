from fastapi.testclient import TestClient

from sce.api import build_app


def test_list_demos_endpoint():
    client = TestClient(build_app())
    resp = client.get("/demo")
    assert resp.status_code == 200
    data = resp.json()
    names = {item["name"] for item in data}
    assert "supplier-risk" in names
    assert "hypothesis" in names


def test_run_demo_json():
    client = TestClient(build_app())
    resp = client.post("/demo", json={"name": "hypothesis", "format": "json"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "hypothesis"
    assert isinstance(data["output"], dict)
    assert "selected_hypothesis" in data["output"]


def test_run_demo_pretty():
    client = TestClient(build_app())
    resp = client.post("/demo", json={"name": "supplier-risk", "format": "pretty"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "supplier-risk"
    assert isinstance(data["output"], str)
    assert "SCE Supplier Risk Demo" in data["output"]
