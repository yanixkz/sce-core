from __future__ import annotations

import csv
from itertools import product
from pathlib import Path

from sce.scenarios.resource_stability_demo import run_resource_stability_demo


DEFAULT_POPULATION_MULTIPLIERS = (0.95, 1.0, 1.05)
DEFAULT_CONSUMPTION_MULTIPLIERS = (0.95, 1.0, 1.1)
DEFAULT_REGENERATION_MULTIPLIERS = (0.95, 1.0)


def run_resource_stability_sensitivity_grid(
    *,
    population_multipliers: tuple[float, ...] = DEFAULT_POPULATION_MULTIPLIERS,
    consumption_rate_multipliers: tuple[float, ...] = DEFAULT_CONSUMPTION_MULTIPLIERS,
    regeneration_rate_multipliers: tuple[float, ...] = DEFAULT_REGENERATION_MULTIPLIERS,
) -> list[dict]:
    rows: list[dict] = []
    for population, consumption, regeneration in product(
        population_multipliers,
        consumption_rate_multipliers,
        regeneration_rate_multipliers,
    ):
        result = run_resource_stability_demo(
            population_multiplier=population,
            consumption_rate_multiplier=consumption,
            regeneration_rate_multiplier=regeneration,
        )
        top = result["scores"][0]
        runner_up = result["scores"][1] if len(result["scores"]) > 1 else {"stability": top["stability"]}
        rows.append(
            {
                "population_multiplier": population,
                "consumption_rate_multiplier": consumption,
                "regeneration_rate_multiplier": regeneration,
                "selected_state": result["selected_state"]["name"],
                "selected_regime": result["selected_state"]["name"],
                "top_stability": top["stability"],
                "runner_up_stability": runner_up["stability"],
                "stability_margin": round(top["stability"] - runner_up["stability"], 4),
                "stability_explanation": result["stability_explanation"],
            }
        )
    return rows


def format_sensitivity_table(rows: list[dict]) -> str:
    header = (
        "pop_x  cons_x regen_x  selected_regime        top_stab runner_up   margin"
        "\n--------------------------------------------------------------------------"
    )
    body = [
        (
            f"{row['population_multiplier']:>5.2f}  "
            f"{row['consumption_rate_multiplier']:>6.2f} "
            f"{row['regeneration_rate_multiplier']:>7.2f}  "
            f"{row['selected_regime']:<22} "
            f"{row['top_stability']:>8.4f} "
            f"{row['runner_up_stability']:>8.4f} "
            f"{row['stability_margin']:>8.4f}"
        )
        for row in rows
    ]
    return "\n".join([header, *body])


def write_sensitivity_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "population_multiplier",
        "consumption_rate_multiplier",
        "regeneration_rate_multiplier",
        "selected_state",
        "selected_regime",
        "top_stability",
        "runner_up_stability",
        "stability_margin",
        "stability_explanation",
    ]
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
