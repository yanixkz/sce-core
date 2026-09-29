"""Build the public read model after prospective forecast issuance/settlement."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from sce.research.bitcoin_ledger_index import write_index


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args()
    result = write_index(args.ledger, datetime.now(timezone.utc))
    print(json.dumps({key: result[key] for key in ("generated_at", "total_forecasts", "forecasts_last_24h")}))


if __name__ == "__main__":
    main()
