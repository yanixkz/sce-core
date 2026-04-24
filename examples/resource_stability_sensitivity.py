from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sce.scenarios.resource_stability_sensitivity import (
    format_sensitivity_table,
    run_resource_stability_sensitivity_grid,
    write_sensitivity_csv,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a lightweight resource-stability sensitivity grid.")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional CSV output path (e.g. examples/output/resource_stability_sensitivity.csv)",
    )
    args = parser.parse_args(argv)

    rows = run_resource_stability_sensitivity_grid()
    print("# Resource Stability Sensitivity Grid")
    print(f"Grid runs: {len(rows)}")
    print()
    print(format_sensitivity_table(rows))

    if args.out is not None:
        write_sensitivity_csv(args.out, rows)
        print()
        print(f"CSV written to: {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
