from __future__ import annotations

from fastapi.testclient import TestClient

from sce.api import API_VERSION, build_app


client = TestClient(build_app())


def _assert_memory_scope_matches_persistence(meta: dict) -> None:
    if meta["persistence"] == "postgres":
        assert meta["scope"] == "durable postgres + process-local in-memory runtime"
    else:
        assert meta["scope"] == "process-local in-memory"


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
    assert data["meta"]["type"] == "raw"
    assert data["meta"]["ui"]["view"] == "hypothesis"
    assert "ranked_hypotheses" in data["meta"]["ui"]["panel_order"]


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
    assert data["meta"]["type"] == "formatted"
    assert data["meta"]["ui"]["view"] == "supplier-risk"


def test_demo_explain_contract_returns_name_explanation_and_version():
    resp = client.post("/demo/explain", json={"name": "hypothesis"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == API_VERSION
    assert data["name"] == "hypothesis"
    assert isinstance(data["explanation"], str)
    assert data["explanation"].strip()
    assert data["meta"]["type"] == "explanation"
    assert isinstance(data["meta"]["sections"], list)


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
    assert isinstance(data["meta"]["node_count"], int)
    assert isinstance(data["meta"]["edge_count"], int)
    assert {"node_fields", "edge_fields"}.issubset(data["meta"]["schema"])


def test_decide_contract_returns_structured_decision_response():
    resp = client.post(
        "/decide",
        json={
            "goal": "assess supplier risk",
            "context": {"supplier_id": "supplier A", "claim": "supplier may be unreliable"},
            "constraints": ["prefer external verification"],
            "execute": True,
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == API_VERSION
    assert data["goal"] == "assess supplier risk"
    assert data["selected_plan"] == "supplier_risk_plan"
    assert data["executed"] is True
    assert data["execution_success"] is True
    assert isinstance(data["action_names"], list)
    assert isinstance(data["execution_trace"], list)
    assert isinstance(data["scores"], list)
    assert {"plan", "reason", "base_score", "memory_bias", "reliability", "reliability_bonus", "total_score"}.issubset(
        data["scores"][0]
    )
    assert data["meta"]["constraints"] == ["prefer external verification"]
    assert data["meta"]["constraints_supported"] is False


def test_decide_validation_error_for_missing_goal():
    resp = client.post("/decide", json={"context": {"supplier_id": "supplier A"}})
    assert resp.status_code == 422


def test_memory_contract_reports_process_local_episodes_after_decide_execute():
    decide = client.post(
        "/decide",
        json={
            "goal": "assess supplier risk",
            "context": {"supplier_id": "supplier A"},
            "execute": True,
        },
    )
    assert decide.status_code == 200

    resp = client.get("/memory")
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == API_VERSION
    assert isinstance(data["episodes"], list)
    assert data["episodes"]
    assert {"episode_id", "created_at", "goal", "selected_plan", "success", "reward", "reliability"}.issubset(
        data["episodes"][0]
    )
    _assert_memory_scope_matches_persistence(data["meta"])
    assert data["meta"]["source"] == "/decide with execute=true"
    assert data["meta"]["persistence"] in {"none", "postgres"}


def test_reliability_contract_reports_summary_over_recent_window():
    decide = client.post(
        "/decide",
        json={
            "goal": "assess supplier risk",
            "context": {"supplier_id": "supplier B"},
            "execute": True,
        },
    )
    assert decide.status_code == 200

    resp = client.get("/reliability")
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == API_VERSION
    assert {"recent_window_size", "reliability_episode_count", "average_reliability", "success_rate", "latest"}.issubset(
        data["reliability"]
    )
    assert isinstance(data["reliability"]["latest"], list)
    _assert_memory_scope_matches_persistence(data["meta"])
    assert data["meta"]["source"] == "/decide with execute=true"
