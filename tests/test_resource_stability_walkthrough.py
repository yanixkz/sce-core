from __future__ import annotations

import os
import subprocess
import sys

from sce.scenarios.resource_stability_demo import run_resource_stability_demo


def test_resource_stability_demo_exposes_parameter_metadata():
    result = run_resource_stability_demo()

    assert result["parameters"] == {
        "population_multiplier": 1.0,
        "consumption_rate_multiplier": 1.0,
        "regeneration_rate_multiplier": 1.0,
    }


def test_resource_stability_walkthrough_script_runs_and_includes_sensitivity_section():
    env = {**os.environ, "PYTHONPATH": "."}
    proc = subprocess.run(
        [sys.executable, "examples/resource_stability_walkthrough.py"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    report = proc.stdout

    assert "Resource Stability Walkthrough (CDS)" in report
    assert "CDS mapping" in report
    assert "One-parameter sensitivity" in report
    assert "consumption_rate_multiplier = 1.12" in report
