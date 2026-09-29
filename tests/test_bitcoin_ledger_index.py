import json
from datetime import datetime, timedelta, timezone

from examples.run_bitcoin_continuous import cycle
from sce.research.bitcoin_ledger_index import build_index


def test_index_preserves_prospective_record_and_separate_outcome(tmp_path):
    t = datetime(2026, 9, 25, tzinfo=timezone.utc)
    rows = [(t + timedelta(minutes=15 * i), 100 + i / 10) for i in range(102)]
    issued = rows[99][0] + timedelta(minutes=15, seconds=30)
    record_id = cycle(tmp_path, rows[:100], issued, lambda: {"status": "OBSERVED"})["issued"]
    pending = build_index(tmp_path, issued)
    assert pending["entries"][0]["forecast_id"] == record_id
    assert pending["entries"][0]["outcome"] is None
    assert pending["forecasts_last_24h"] == 1
    cycle(tmp_path, rows, issued + timedelta(minutes=41), lambda: None)
    resolved = build_index(tmp_path, issued + timedelta(minutes=41))
    assert set(resolved["entries"][0]["outcome"]["outcomes"]) == {"15", "30"}
    assert json.loads((tmp_path / "forecasts" / f"{record_id}.json").read_text())["status"] == "CAUSAL"
