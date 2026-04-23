from __future__ import annotations

from fastapi.testclient import TestClient

from sce.api import API_VERSION, build_app


client = TestClient(build_app())


def test_demo_json_contract_includes_version_and_expected_shape():
    resp = client.post("/demo", json={"name": "hypothesis", "format": "json"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == API_VERSION
    assert data["name"] == "hypothesis"
    assert data["format"] == "json"
    assert isinstance(data["result"], dict)
    assert {"selected_hypothesis", "scores", "backbone_nodes", "next_actions"}.issubset(data["result"])
    assert data["explanation"] is None


def test_demo_pretty_contract_includes_explanation_string():
    resp = client.post("/demo", json={"name": "supplier-risk", "format": "pretty"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == API_VERSION
    assert data["name"] == "supplier-risk"
    assert data["format"] == "pretty"
    assert isinstance(data["result"], dict)
    assert isinstance(data["explanation"], str)
    assert data["explanation"].strip()


def test_demo_explain_contract_returns_name_explanation_and_version():
    resp = client.post("/demo/explain", json={"name": "hypothesis"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == API_VERSION
    assert data["name"] == "hypothesis"
    assert isinstance(data["explanation"], str)
    assert data["explanation"].strip()


def test_graph_contract_returns_version_graph_and_basic_graph_fields():
    resp = client.get("/graph")

    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == API_VERSION
    assert isinstance(data["graph"], dict)
    assert {"nodes", "edges"}.issubset(data["graph"])
    assert isinstance(data["graph"]["nodes"], list)
    assert isinstance(data["graph"]["edges"], list)
    assert data["graph"]["nodes"]
    assert {"state_id", "state_type", "stability", "constraints_satisfied", "data"}.issubset(data["graph"]["nodes"][0])
    assert data["meta"]["source"] == "supplier-reliability"
