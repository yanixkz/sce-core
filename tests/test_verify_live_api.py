from __future__ import annotations

import json
import sys
from pathlib import Path


EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"
if str(EXAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_DIR))

import verify_live_api as verify


def test_build_url_normalizes_slashes() -> None:
    assert verify.build_url("http://127.0.0.1:8000/", "/demo") == "http://127.0.0.1:8000/demo"
    assert verify.build_url("http://127.0.0.1:8000", "memory") == "http://127.0.0.1:8000/memory"


def test_load_payload_returns_json_object() -> None:
    payload = verify.load_payload("demo_resource_stability.json")
    assert payload == {"name": "resource-stability", "format": "json"}


def test_summarize_response_extracts_concise_fields() -> None:
    summary = verify.summarize_response(
        "/decide",
        {
            "selected_plan": "supplier_risk_plan",
            "executed": True,
            "execution_success": True,
            "scores": [{"plan": "supplier_risk_plan"}],
        },
    )
    assert "selected_plan=supplier_risk_plan" in summary
    assert "executed=True" in summary
    assert "execution_success=True" in summary


def test_payload_files_are_valid_json() -> None:
    for payload_path in (verify.PAYLOAD_DIR).glob("*.json"):
        with payload_path.open("r", encoding="utf-8") as handle:
            parsed = json.load(handle)
        assert isinstance(parsed, dict), f"Expected object payload in {payload_path.name}"
