from __future__ import annotations

import csv
from pathlib import Path

import pytest

from sce.scenarios.resource_stability_csv import (
    ResourceStabilityCSVError,
    parse_resource_stability_cases,
    run_resource_stability_csv_cases,
    write_resource_stability_csv_output,
)


def test_sample_cases_csv_can_be_parsed():
    rows = parse_resource_stability_cases(Path("examples/data/resource_stability_cases.csv"))

    assert len(rows) >= 5
    assert rows[0]["case_id"] == "baseline"


def test_parse_fails_on_missing_columns(tmp_path):
    bad_csv = tmp_path / "bad_cases.csv"
    bad_csv.write_text("case_id,population_multiplier\nbaseline,1.0\n", encoding="utf-8")

    with pytest.raises(ResourceStabilityCSVError, match="Missing required columns"):
        parse_resource_stability_cases(bad_csv)


def test_parse_fails_on_invalid_numeric_value(tmp_path):
    bad_csv = tmp_path / "bad_numeric.csv"
    bad_csv.write_text(
        (
            "case_id,population_multiplier,consumption_rate_multiplier,regeneration_rate_multiplier\n"
            "bad_case,abc,1.0,1.0\n"
        ),
        encoding="utf-8",
    )

    with pytest.raises(ResourceStabilityCSVError, match="Invalid numeric value"):
        parse_resource_stability_cases(bad_csv)


def test_csv_cases_produce_deterministic_rows():
    rows = [
        {
            "case_id": "baseline",
            "population_multiplier": 1.0,
            "consumption_rate_multiplier": 1.0,
            "regeneration_rate_multiplier": 1.0,
        },
        {
            "case_id": "high_consumption",
            "population_multiplier": 1.0,
            "consumption_rate_multiplier": 1.18,
            "regeneration_rate_multiplier": 1.0,
        },
    ]

    first = run_resource_stability_csv_cases(rows)
    second = run_resource_stability_csv_cases(rows)

    assert first == second
    assert {row["case_id"] for row in first} == {"baseline", "high_consumption"}


def test_csv_output_writer(tmp_path):
    out_path = tmp_path / "cases_out.csv"
    rows = run_resource_stability_csv_cases(
        [
            {
                "case_id": "baseline",
                "population_multiplier": 1.0,
                "consumption_rate_multiplier": 1.0,
                "regeneration_rate_multiplier": 1.0,
            }
        ]
    )

    write_resource_stability_csv_output(out_path, rows)

    with out_path.open("r", newline="", encoding="utf-8") as csv_file:
        loaded = list(csv.DictReader(csv_file))

    assert len(loaded) == 1
    assert loaded[0]["case_id"] == "baseline"
    assert "selected_regime" in loaded[0]
