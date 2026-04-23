from __future__ import annotations

import json
import subprocess
import sys


def run_cli(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "sce.cli", *command.split()],
        check=False,
        capture_output=True,
        text=True,
    )


def test_cli_default_demo_runs():
    result = run_cli("demo")

    assert result.returncode == 0, result.stderr
    assert "SCE Supplier Risk Demo" in result.stdout
    assert "Decide. Explain. Improve." in result.stdout


def test_cli_supplier_risk_json_runs():
    result = run_cli("run-supplier-risk-demo")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["changed_choice"] is True
    assert payload["final_choice"] == "escalation_plan"


def test_cli_demo_json_mode():
    result = run_cli("demo supplier-risk --json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert isinstance(payload, dict)


def test_cli_hypothesis_research_demo_runs():
    result = run_cli("run-hypothesis-research-demo-pretty")

    assert result.returncode == 0, result.stderr
    assert "Hypothesis" in result.stdout


def test_cli_visualize_graph_runs():
    result = run_cli("visualize-graph")

    assert result.returncode == 0, result.stderr
    assert "State Graph" in result.stdout
