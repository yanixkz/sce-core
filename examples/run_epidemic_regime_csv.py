from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sce.scenarios.epidemic_regime_csv import (
    EpidemicRegimeCSVError,
    format_epidemic_regime_csv_table,
    parse_epidemic_regime_cases,
    run_epidemic_regime_csv_cases,
    write_epidemic_regime_csv_output,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run epidemic-regime selection for a user-provided CSV of parameter cases."
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
        cases = parse_epidemic_regime_cases(args.input_csv)
        rows = run_epidemic_regime_csv_cases(cases)
    except FileNotFoundError:
        print(f"Error: input CSV not found: {args.input_csv}", file=sys.stderr)
        return 2
    except EpidemicRegimeCSVError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print("# Epidemic Regime CSV Batch")
    print(f"Input: {args.input_csv}")
    print(f"Cases: {len(rows)}")
    print()
    print(format_epidemic_regime_csv_table(rows))

    if args.out is not None:
        write_epidemic_regime_csv_output(args.out, rows)
        print()
        print(f"CSV written to: {args.out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
