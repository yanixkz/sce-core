from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sce.scenarios.epidemic_regime_csv import (
    EpidemicRegimeCSVError,
    parse_epidemic_regime_cases,
    run_epidemic_regime_csv_cases,
)
from sce.scenarios.epidemic_regime_validation import build_epidemic_regime_validation_rows

DEFAULT_INPUT = Path("examples/data/epidemic_regime_cases.csv")


def _format_validation_table(rows: list[dict]) -> str:
    header = (
        "case_id                tx_x rec_x cap_x cost_x sce_regime              heuristic               agree  top"
        "\n---------------------------------------------------------------------------------------------------------"
    )
    body = [
        (
            f"{row['case_id']:<22} "
            f"{row['transmission_multiplier']:>4.2f} "
            f"{row['recovery_support_multiplier']:>5.2f} "
            f"{row['healthcare_capacity_multiplier']:>5.2f} "
            f"{row['intervention_cost_multiplier']:>6.2f} "
            f"{row['selected_regime']:<23} "
            f"{row['heuristic_expected_regime']:<22} "
            f"{str(row['agreement']):<5} "
            f"{row['top_score']:>7.4f}"
        )
        for row in rows
    ]
    return "\n".join([header, *body])


def _write_validation_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "transmission_multiplier",
        "recovery_support_multiplier",
        "healthcare_capacity_multiplier",
        "intervention_cost_multiplier",
        "sce_selected_regime",
        "sce_top_score",
        "heuristic_expected_regime",
        "heuristic_expected_class",
        "agreement",
        "heuristic_reason",
        "pressure_index",
        "capacity_gap",
        "recovery_balance",
        "intervention_burden",
        "sce_explanation",
    ]
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "case_id": row["case_id"],
                    "transmission_multiplier": row["transmission_multiplier"],
                    "recovery_support_multiplier": row["recovery_support_multiplier"],
                    "healthcare_capacity_multiplier": row["healthcare_capacity_multiplier"],
                    "intervention_cost_multiplier": row["intervention_cost_multiplier"],
                    "sce_selected_regime": row["selected_regime"],
                    "sce_top_score": row["top_score"],
                    "heuristic_expected_regime": row["heuristic_expected_regime"],
                    "heuristic_expected_class": row["heuristic_expected_class"],
                    "agreement": row["agreement"],
                    "heuristic_reason": row["heuristic_reason"],
                    "pressure_index": row["pressure_index"],
                    "capacity_gap": row["capacity_gap"],
                    "recovery_balance": row["recovery_balance"],
                    "intervention_burden": row["intervention_burden"],
                    "sce_explanation": row["short_explanation"],
                }
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate epidemic-regime CSV cases against a heuristic baseline.")
    parser.add_argument("input_csv", type=Path, nargs="?", default=DEFAULT_INPUT)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        cases = parse_epidemic_regime_cases(args.input_csv)
        sce_rows = run_epidemic_regime_csv_cases(cases)
    except FileNotFoundError:
        print(f"Error: input CSV not found: {args.input_csv}", file=sys.stderr)
        return 2
    except EpidemicRegimeCSVError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    rows = build_epidemic_regime_validation_rows(sce_rows)
    print("# Epidemic Regime Heuristic Validation")
    print(f"Input: {args.input_csv}")
    print(f"Cases: {len(rows)}")
    print()
    print(_format_validation_table(rows))

    if args.out is not None:
        _write_validation_csv(args.out, rows)
        print()
        print(f"CSV written to: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
