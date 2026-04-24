from __future__ import annotations

import os
import subprocess
import sys

from sce.scenarios.epidemic_regime_demo import run_epidemic_regime_demo


def test_epidemic_regime_demo_exposes_parameter_metadata():
    result = run_epidemic_regime_demo()

    assert result["parameters"] == {
        "transmission_multiplier": 1.0,
        "recovery_support_multiplier": 1.0,
        "healthcare_capacity_multiplier": 1.0,
        "intervention_cost_multiplier": 1.0,
    }


def test_epidemic_regime_walkthrough_script_runs_and_includes_cds_section():
    env = {**os.environ, "PYTHONPATH": "."}
    proc = subprocess.run(
        [sys.executable, "examples/epidemic_regime_walkthrough.py"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    report = proc.stdout

    assert "Epidemic Regime Walkthrough (CDS)" in report
    assert "Toy-model disclaimer" in report
    assert "CDS mapping" in report
    assert "transmission_multiplier = 1.10" in report
