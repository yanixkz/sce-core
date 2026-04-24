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


def test_cli_demo_help_highlights_canonical_demos():
    result = run_cli("demo --help")

    assert result.returncode == 0, result.stderr
    assert "supplier-risk" in result.stdout
    assert "hypothesis" in result.stdout
    assert "resource-stability" in result.stdout
    assert "list" in result.stdout


def test_cli_top_level_help_highlights_product_surface():
    result = run_cli("--help")

    assert result.returncode == 0, result.stderr
    assert "Primary surface:" in result.stdout
    assert "sce demo hypothesis" in result.stdout
    assert "Graph inspection:" in result.stdout
    assert "sce export-graph" in result.stdout
    assert "Compatibility:" in result.stdout


def test_cli_top_level_help_marks_legacy_aliases():
    result = run_cli("--help")

    assert result.returncode == 0, result.stderr
    assert "run-supplier-risk-demo" in result.stdout
    assert "Legacy alias (backward compatibility)." in result.stdout


def test_cli_demo_list_promotes_hypothesis_entrypoint():
    result = run_cli("demo list")

    assert result.returncode == 0, result.stderr
    assert "supplier-risk\tSupplier Risk Agent" in result.stdout
    assert "hypothesis\tHypothesis Research (Flagship)" in result.stdout
    assert "resource-stability\tResource Stability (Scientific)" in result.stdout
