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
    assert data["version"] == "v1"
    assert data["name"] == "hypothesis"
    assert data["format"] == "json"
    assert isinstance(data["result"], dict)
    assert "selected_hypothesis" in data["result"]
    assert data["explanation"] is None
    assert data["meta"]["type"] == "raw"


def test_run_demo_pretty():
    client = TestClient(build_app())
    resp = client.post("/demo", json={"name": "supplier-risk", "format": "pretty"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == "v1"
    assert data["name"] == "supplier-risk"
    assert data["format"] == "pretty"
    assert isinstance(data["result"], dict)
    assert isinstance(data["explanation"], str)
    assert "SCE Supplier Risk Demo" in data["explanation"]
    assert data["meta"]["type"] == "formatted"


def test_explain_endpoint():
    client = TestClient(build_app())
    resp = client.post("/demo/explain", json={"name": "hypothesis"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == "v1"
    assert data["name"] == "hypothesis"
    assert isinstance(data["explanation"], str)
    assert data["meta"]["type"] == "explanation"
