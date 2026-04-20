from __future__ import annotations

import argparse
import json

from sce.scenarios.supplier_reliability import run_demo
from sce.storage.postgres import POSTGRES_MIGRATION_SQL


def main() -> None:
    parser = argparse.ArgumentParser(prog="sce")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("run-demo")
    sub.add_parser("explain-demo")
    sub.add_parser("print-migration")
    args = parser.parse_args()

    if args.command == "run-demo":
        print(json.dumps(run_demo(), indent=2, ensure_ascii=False))
    elif args.command == "explain-demo":
        print(json.dumps(run_demo()["explanation"], indent=2, ensure_ascii=False))
    elif args.command == "print-migration":
        print(POSTGRES_MIGRATION_SQL)


if __name__ == "__main__":
    main()
