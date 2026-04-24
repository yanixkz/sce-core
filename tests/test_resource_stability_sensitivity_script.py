from __future__ import annotations

import os
import subprocess
import sys


def test_resource_stability_sensitivity_script_runs_and_writes_optional_csv(tmp_path):
    env = {**os.environ, "PYTHONPATH": "."}
    output_csv = tmp_path / "sensitivity.csv"
    proc = subprocess.run(
        [
            sys.executable,
            "examples/resource_stability_sensitivity.py",
            "--out",
            str(output_csv),
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    report = proc.stdout

    assert "Resource Stability Sensitivity Grid" in report
    assert "Grid runs:" in report
    assert "selected_regime" in report
    assert output_csv.exists()
