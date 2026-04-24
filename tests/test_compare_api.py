from fastapi.testclient import TestClient

from sce.api import API_VERSION, build_app


def test_compare_returns_baseline_sce_and_comparison_with_default_mock_provider():
    client = TestClient(build_app())

    resp = client.post(
        "/compare",
        json={
            "goal": "assess supplier risk",
            "context": {"supplier_id": "supplier A", "region": "EU"},
            "constraints": ["prefer external verification"],
            "execute": False,
        },
    )

    assert resp.status_code == 200
    data = resp.json()

    assert data["version"] == API_VERSION
    assert {"input_summary", "baseline", "sce", "comparison", "meta"}.issubset(data)

    assert data["baseline"]["provider"] == "mock"
    assert data["baseline"]["source"] == "deterministic"
    assert isinstance(data["baseline"]["answer"], str)
    assert isinstance(data["baseline"]["rationale"], str)
    assert any("no ranked alternatives" in limitation.lower() for limitation in data["baseline"]["limitations"])
    assert any("no episodic memory" in limitation.lower() for limitation in data["baseline"]["limitations"])
    assert any("no reliability" in limitation.lower() for limitation in data["baseline"]["limitations"])

    assert data["sce"]["selected_plan"]
    assert isinstance(data["sce"]["scores"], list)
    assert data["sce"]["scores"]

    assert isinstance(data["comparison"]["differences"], list)
    assert data["comparison"]["baseline_has_ranking"] is False
    assert data["comparison"]["baseline_has_memory"] is False
    assert data["comparison"]["baseline_has_reliability"] is False


def test_compare_returns_validation_error_for_missing_goal():
    client = TestClient(build_app())

    resp = client.post("/compare", json={"context": {"supplier_id": "supplier A"}})

    assert resp.status_code == 422


def test_compare_openai_provider_without_key_falls_back_to_mock(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = TestClient(build_app())

    resp = client.post(
        "/compare",
        json={
            "goal": "evaluate hypothesis",
            "context": {"dataset": "q1"},
            "baseline_provider": "openai",
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["baseline"]["provider"] == "mock"
    assert data["baseline"]["meta"]["requested_provider"] == "openai"
    assert data["baseline"]["meta"]["fallback_used"] is True
