from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sce.scenarios.resource_stability_csv import (
    ResourceStabilityCSVError,
    parse_resource_stability_cases,
    run_resource_stability_csv_cases,
)
from sce.scenarios.resource_stability_validation import build_resource_stability_validation_rows

DEFAULT_INPUT = Path("examples/data/resource_stability_cases.csv")


def _format_validation_table(rows: list[dict]) -> str:
    header = (
        "case_id                sce_regime              heuristic               agree  top_score"
        "\n----------------------------------------------------------------------------------"
    )
    body = [
        (
            f"{row['case_id']:<22} "
            f"{row['selected_regime']:<23} "
            f"{row['heuristic_expected_regime']:<22} "
            f"{str(row['agreement']):<5} "
            f"{row['top_score']:>8.4f}"
        )
        for row in rows
    ]
    return "\n".join([header, *body])


def _write_validation_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "population_multiplier",
        "consumption_rate_multiplier",
        "regeneration_rate_multiplier",
        "sce_selected_regime",
        "sce_top_score",
        "heuristic_expected_regime",
        "heuristic_expected_class",
        "agreement",
        "heuristic_reason",
        "sce_explanation",
    ]
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "case_id": row["case_id"],
                    "population_multiplier": row["population_multiplier"],
                    "consumption_rate_multiplier": row["consumption_rate_multiplier"],
                    "regeneration_rate_multiplier": row["regeneration_rate_multiplier"],
                    "sce_selected_regime": row["selected_regime"],
                    "sce_top_score": row["top_score"],
                    "heuristic_expected_regime": row["heuristic_expected_regime"],
                    "heuristic_expected_class": row["heuristic_expected_class"],
                    "agreement": row["agreement"],
                    "heuristic_reason": row["heuristic_reason"],
                    "sce_explanation": row["short_explanation"],
                }
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate resource-stability CSV cases against a heuristic baseline.")
    parser.add_argument("input_csv", type=Path, nargs="?", default=DEFAULT_INPUT)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        cases = parse_resource_stability_cases(args.input_csv)
        sce_rows = run_resource_stability_csv_cases(cases)
    except FileNotFoundError:
        print(f"Error: input CSV not found: {args.input_csv}", file=sys.stderr)
        return 2
    except ResourceStabilityCSVError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    rows = build_resource_stability_validation_rows(sce_rows)
    print("# Resource Stability Heuristic Validation")
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
