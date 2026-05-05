from __future__ import annotations

import csv
from pathlib import Path

from sce.scenarios.epidemic_regime_demo import run_epidemic_regime_demo

REQUIRED_COLUMNS = (
    "case_id",
    "transmission_multiplier",
    "recovery_support_multiplier",
    "healthcare_capacity_multiplier",
    "intervention_cost_multiplier",
)


class EpidemicRegimeCSVError(ValueError):
    """Raised when input CSV rows are invalid for the epidemic-regime batch runner."""


def _require_columns(fieldnames: list[str] | None) -> None:
    available = set(fieldnames or [])
    missing = [name for name in REQUIRED_COLUMNS if name not in available]
    if missing:
        raise EpidemicRegimeCSVError(
            f"Missing required columns: {', '.join(missing)}. "
            f"Expected columns: {', '.join(REQUIRED_COLUMNS)}"
        )


def _parse_float(raw_value: str, *, column: str, row_number: int) -> float:
    try:
        return float(raw_value)
    except (TypeError, ValueError) as exc:
        raise EpidemicRegimeCSVError(
            f"Invalid numeric value for '{column}' on row {row_number}: {raw_value!r}"
        ) from exc


def parse_epidemic_regime_cases(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        _require_columns(reader.fieldnames)

        rows: list[dict] = []
        for row_number, row in enumerate(reader, start=2):
            case_id = (row.get("case_id") or "").strip()
            if not case_id:
                raise EpidemicRegimeCSVError(f"Missing case_id value on row {row_number}.")

            rows.append(
                {
                    "case_id": case_id,
                    "transmission_multiplier": _parse_float(
                        row.get("transmission_multiplier", ""),
                        column="transmission_multiplier",
                        row_number=row_number,
                    ),
                    "recovery_support_multiplier": _parse_float(
                        row.get("recovery_support_multiplier", ""),
                        column="recovery_support_multiplier",
                        row_number=row_number,
                    ),
                    "healthcare_capacity_multiplier": _parse_float(
                        row.get("healthcare_capacity_multiplier", ""),
                        column="healthcare_capacity_multiplier",
                        row_number=row_number,
                    ),
                    "intervention_cost_multiplier": _parse_float(
                        row.get("intervention_cost_multiplier", ""),
                        column="intervention_cost_multiplier",
                        row_number=row_number,
                    ),
                }
            )
    return rows


def run_epidemic_regime_csv_cases(rows: list[dict]) -> list[dict]:
    results: list[dict] = []
    for row in rows:
        result = run_epidemic_regime_demo(
            transmission_multiplier=row["transmission_multiplier"],
            recovery_support_multiplier=row["recovery_support_multiplier"],
            healthcare_capacity_multiplier=row["healthcare_capacity_multiplier"],
            intervention_cost_multiplier=row["intervention_cost_multiplier"],
        )
        top = result["scores"][0]
        runner_up = result["scores"][1] if len(result["scores"]) > 1 else {"stability": top["stability"]}
        results.append(
            {
                "case_id": row["case_id"],
                "transmission_multiplier": row["transmission_multiplier"],
                "recovery_support_multiplier": row["recovery_support_multiplier"],
                "healthcare_capacity_multiplier": row["healthcare_capacity_multiplier"],
                "intervention_cost_multiplier": row["intervention_cost_multiplier"],
                "selected_regime": result["selected_regime"]["name"],
                "top_score": top["stability"],
                "runner_up_score": runner_up["stability"],
                "margin": round(top["stability"] - runner_up["stability"], 4),
                "short_explanation": result["stability_explanation"],
            }
        )
    return results


def format_epidemic_regime_csv_table(rows: list[dict]) -> str:
    header = (
        "case_id                tx_x rec_x cap_x cost_x selected_regime        top     runner  margin"
        "\n-----------------------------------------------------------------------------------------------"
    )
    body = [
        (
            f"{row['case_id']:<22} "
            f"{row['transmission_multiplier']:>4.2f} "
            f"{row['recovery_support_multiplier']:>5.2f} "
            f"{row['healthcare_capacity_multiplier']:>5.2f} "
            f"{row['intervention_cost_multiplier']:>6.2f} "
            f"{row['selected_regime']:<22} "
            f"{row['top_score']:>7.4f} "
            f"{row['runner_up_score']:>7.4f} "
            f"{row['margin']:>7.4f}"
        )
        for row in rows
    ]
    return "\n".join([header, *body])


def write_epidemic_regime_csv_output(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "transmission_multiplier",
        "recovery_support_multiplier",
        "healthcare_capacity_multiplier",
        "intervention_cost_multiplier",
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
