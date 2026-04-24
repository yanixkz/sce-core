from __future__ import annotations

import csv

from sce.scenarios.resource_stability_sensitivity import (
    DEFAULT_CONSUMPTION_MULTIPLIERS,
    DEFAULT_POPULATION_MULTIPLIERS,
    DEFAULT_REGENERATION_MULTIPLIERS,
    format_sensitivity_table,
    run_resource_stability_sensitivity_grid,
    write_sensitivity_csv,
)


def test_resource_stability_sensitivity_grid_shape_and_fields():
    rows = run_resource_stability_sensitivity_grid()

    expected_count = (
        len(DEFAULT_POPULATION_MULTIPLIERS)
        * len(DEFAULT_CONSUMPTION_MULTIPLIERS)
        * len(DEFAULT_REGENERATION_MULTIPLIERS)
    )
    assert len(rows) == expected_count

    required_fields = {
        "population_multiplier",
        "consumption_rate_multiplier",
        "regeneration_rate_multiplier",
        "selected_state",
        "selected_regime",
        "top_stability",
        "runner_up_stability",
        "stability_margin",
        "stability_explanation",
    }
    for row in rows:
        assert required_fields.issubset(row.keys())
        assert row["selected_state"] == row["selected_regime"]


def test_resource_stability_sensitivity_table_render_includes_header_and_rows():
    rows = run_resource_stability_sensitivity_grid(
        population_multipliers=(1.0,),
        consumption_rate_multipliers=(1.0,),
        regeneration_rate_multipliers=(1.0,),
    )
    rendered = format_sensitivity_table(rows)

    assert "selected_regime" in rendered
    assert rows[0]["selected_regime"] in rendered


def test_resource_stability_sensitivity_csv_writer(tmp_path):
    rows = run_resource_stability_sensitivity_grid(
        population_multipliers=(1.0,),
        consumption_rate_multipliers=(1.0,),
        regeneration_rate_multipliers=(1.0,),
    )
    output_path = tmp_path / "resource_stability_sensitivity.csv"

    write_sensitivity_csv(output_path, rows)

    assert output_path.exists()
    with output_path.open("r", encoding="utf-8") as csv_file:
        data_rows = list(csv.DictReader(csv_file))

    assert len(data_rows) == 1
    assert data_rows[0]["selected_state"] == rows[0]["selected_state"]
