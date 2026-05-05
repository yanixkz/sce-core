from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sce.scenarios.resource_stability_csv import (
    ResourceStabilityCSVError,
    format_resource_stability_csv_table,
    parse_resource_stability_cases,
    run_resource_stability_csv_cases,
    write_resource_stability_csv_output,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run resource-stability selection for a user-provided CSV of parameter cases."
    )
    parser.add_argument("input_csv", type=Path, help="Path to input CSV with case multipliers.")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional output CSV path for result rows.",
    )
    args = parser.parse_args(argv)

    try:
        cases = parse_resource_stability_cases(args.input_csv)
        rows = run_resource_stability_csv_cases(cases)
    except FileNotFoundError:
        print(f"Error: input CSV not found: {args.input_csv}", file=sys.stderr)
        return 2
    except ResourceStabilityCSVError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print("# Resource Stability CSV Batch")
    print(f"Input: {args.input_csv}")
    print(f"Cases: {len(rows)}")
    print()
    print(format_resource_stability_csv_table(rows))

    if args.out is not None:
        write_resource_stability_csv_output(args.out, rows)
        print()
        print(f"CSV written to: {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
