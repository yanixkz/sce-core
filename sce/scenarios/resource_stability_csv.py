from __future__ import annotations

import csv
from pathlib import Path

from sce.scenarios.resource_stability_demo import run_resource_stability_demo

REQUIRED_COLUMNS = (
    "case_id",
    "population_multiplier",
    "consumption_rate_multiplier",
    "regeneration_rate_multiplier",
)


class ResourceStabilityCSVError(ValueError):
    """Raised when input CSV rows are invalid for the resource-stability batch runner."""


def _require_columns(fieldnames: list[str] | None) -> None:
    available = set(fieldnames or [])
    missing = [name for name in REQUIRED_COLUMNS if name not in available]
    if missing:
        raise ResourceStabilityCSVError(
            f"Missing required columns: {', '.join(missing)}. "
            f"Expected columns: {', '.join(REQUIRED_COLUMNS)}"
        )


def _parse_float(raw_value: str, *, column: str, row_number: int) -> float:
    try:
        return float(raw_value)
    except (TypeError, ValueError) as exc:
        raise ResourceStabilityCSVError(
            f"Invalid numeric value for '{column}' on row {row_number}: {raw_value!r}"
        ) from exc


def parse_resource_stability_cases(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        _require_columns(reader.fieldnames)

        rows: list[dict] = []
        for row_number, row in enumerate(reader, start=2):
            case_id = (row.get("case_id") or "").strip()
            if not case_id:
                raise ResourceStabilityCSVError(f"Missing case_id value on row {row_number}.")

            rows.append(
                {
                    "case_id": case_id,
                    "population_multiplier": _parse_float(
                        row.get("population_multiplier", ""),
                        column="population_multiplier",
                        row_number=row_number,
                    ),
                    "consumption_rate_multiplier": _parse_float(
                        row.get("consumption_rate_multiplier", ""),
                        column="consumption_rate_multiplier",
                        row_number=row_number,
                    ),
                    "regeneration_rate_multiplier": _parse_float(
                        row.get("regeneration_rate_multiplier", ""),
                        column="regeneration_rate_multiplier",
                        row_number=row_number,
                    ),
                }
            )
    return rows


def run_resource_stability_csv_cases(rows: list[dict]) -> list[dict]:
    results: list[dict] = []
    for row in rows:
        result = run_resource_stability_demo(
            population_multiplier=row["population_multiplier"],
            consumption_rate_multiplier=row["consumption_rate_multiplier"],
            regeneration_rate_multiplier=row["regeneration_rate_multiplier"],
        )
        top = result["scores"][0]
        runner_up = result["scores"][1] if len(result["scores"]) > 1 else {"stability": top["stability"]}
        results.append(
            {
                "case_id": row["case_id"],
                "population_multiplier": row["population_multiplier"],
                "consumption_rate_multiplier": row["consumption_rate_multiplier"],
                "regeneration_rate_multiplier": row["regeneration_rate_multiplier"],
                "selected_state": result["selected_state"]["name"],
                "selected_regime": result["selected_state"]["name"],
                "top_score": top["stability"],
                "runner_up_score": runner_up["stability"],
                "margin": round(top["stability"] - runner_up["stability"], 4),
                "short_explanation": result["stability_explanation"],
            }
        )
    return results


def format_resource_stability_csv_table(rows: list[dict]) -> str:
    header = (
        "case_id                pop_x  cons_x regen_x  selected_regime        top     runner  margin"
        "\n-----------------------------------------------------------------------------------------------"
    )
    body = [
        (
            f"{row['case_id']:<22} "
            f"{row['population_multiplier']:>5.2f} "
            f"{row['consumption_rate_multiplier']:>6.2f} "
            f"{row['regeneration_rate_multiplier']:>7.2f}  "
            f"{row['selected_regime']:<22} "
            f"{row['top_score']:>7.4f} "
            f"{row['runner_up_score']:>7.4f} "
            f"{row['margin']:>7.4f}"
        )
        for row in rows
    ]
    return "\n".join([header, *body])


def write_resource_stability_csv_output(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "population_multiplier",
        "consumption_rate_multiplier",
        "regeneration_rate_multiplier",
        "selected_state",
        "selected_regime",
        "top_score",
        "runner_up_score",
        "margin",
        "short_explanation",
    ]
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
