from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from sce.scenarios.epidemic_regime_csv import parse_epidemic_regime_cases, run_epidemic_regime_csv_cases
from sce.scenarios.epidemic_regime_validation import (
    build_epidemic_regime_validation_rows,
    evaluate_epidemic_regime_heuristic,
)


def test_heuristic_is_deterministic_for_known_case():
    first = evaluate_epidemic_regime_heuristic(
        transmission_multiplier=1.2,
        recovery_support_multiplier=0.9,
        healthcare_capacity_multiplier=0.85,
        intervention_cost_multiplier=1.0,
    )
    second = evaluate_epidemic_regime_heuristic(
        transmission_multiplier=1.2,
        recovery_support_multiplier=0.9,
        healthcare_capacity_multiplier=0.85,
        intervention_cost_multiplier=1.0,
    )

    assert first == second
    assert first["expected_regime"] in {
        "uncontrolled_spread",
        "managed_containment",
        "overload_risk",
        "recovery_dominant",
        "suppressed_low_activity",
    }


def test_validation_rows_include_agreement_boolean():
    cases = parse_epidemic_regime_cases(Path("examples/data/epidemic_regime_cases.csv"))
    sce_rows = run_epidemic_regime_csv_cases(cases[:2])
    rows = build_epidemic_regime_validation_rows(sce_rows)

    assert len(rows) == 2
    assert isinstance(rows[0]["agreement"], bool)


def test_validation_runner_writes_csv(tmp_path):
    out_path = tmp_path / "validation.csv"
    completed = subprocess.run(
        [
            sys.executable,
            "examples/validate_epidemic_regime_csv.py",
            "examples/data/epidemic_regime_cases.csv",
            "--out",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert out_path.exists()

    with out_path.open("r", newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))
    assert rows
    assert rows[0]["agreement"] in {"True", "False"}


def test_validation_runner_fails_for_invalid_csv(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("case_id,transmission_multiplier\ncase,1.0\n", encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "examples/validate_epidemic_regime_csv.py", str(bad_csv)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "Missing required columns" in completed.stderr
