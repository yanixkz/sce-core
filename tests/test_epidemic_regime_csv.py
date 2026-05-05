from __future__ import annotations

import csv
from pathlib import Path

import pytest

from sce.scenarios.epidemic_regime_csv import (
    EpidemicRegimeCSVError,
    parse_epidemic_regime_cases,
    run_epidemic_regime_csv_cases,
    write_epidemic_regime_csv_output,
)


def test_sample_cases_csv_can_be_parsed():
    rows = parse_epidemic_regime_cases(Path("examples/data/epidemic_regime_cases.csv"))

    assert len(rows) >= 5
    assert rows[0]["case_id"] == "baseline"


def test_parse_fails_on_missing_columns(tmp_path):
    bad_csv = tmp_path / "bad_cases.csv"
    bad_csv.write_text("case_id,transmission_multiplier\nbaseline,1.0\n", encoding="utf-8")

    with pytest.raises(EpidemicRegimeCSVError, match="Missing required columns"):
        parse_epidemic_regime_cases(bad_csv)


def test_parse_fails_on_invalid_numeric_value(tmp_path):
    bad_csv = tmp_path / "bad_numeric.csv"
    bad_csv.write_text(
        (
            "case_id,transmission_multiplier,recovery_support_multiplier,healthcare_capacity_multiplier,intervention_cost_multiplier\n"
            "bad_case,abc,1.0,1.0,1.0\n"
        ),
        encoding="utf-8",
    )

    with pytest.raises(EpidemicRegimeCSVError, match="Invalid numeric value"):
        parse_epidemic_regime_cases(bad_csv)


def test_csv_cases_produce_deterministic_rows():
    rows = [
        {
            "case_id": "baseline",
            "transmission_multiplier": 1.0,
            "recovery_support_multiplier": 1.0,
            "healthcare_capacity_multiplier": 1.0,
            "intervention_cost_multiplier": 1.0,
        },
        {
            "case_id": "high_transmission",
            "transmission_multiplier": 1.2,
            "recovery_support_multiplier": 1.0,
            "healthcare_capacity_multiplier": 1.0,
            "intervention_cost_multiplier": 1.0,
        },
    ]

    first = run_epidemic_regime_csv_cases(rows)
    second = run_epidemic_regime_csv_cases(rows)

    assert first == second
    assert {row["case_id"] for row in first} == {"baseline", "high_transmission"}
    assert all(row["selected_regime"] for row in first)
    assert all("top_score" in row and "margin" in row for row in first)


def test_csv_output_writer(tmp_path):
    out_path = tmp_path / "cases_out.csv"
    rows = run_epidemic_regime_csv_cases(
        [
            {
                "case_id": "baseline",
                "transmission_multiplier": 1.0,
                "recovery_support_multiplier": 1.0,
                "healthcare_capacity_multiplier": 1.0,
                "intervention_cost_multiplier": 1.0,
            }
        ]
    )

    write_epidemic_regime_csv_output(out_path, rows)

    with out_path.open("r", newline="", encoding="utf-8") as csv_file:
        loaded = list(csv.DictReader(csv_file))

    assert len(loaded) == 1
    assert loaded[0]["case_id"] == "baseline"
    assert loaded[0]["selected_regime"]
    assert loaded[0]["top_score"]
    assert loaded[0]["margin"]
