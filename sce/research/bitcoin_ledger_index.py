"""Publish a small, cacheable read model of the immutable prospective ledger."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def build_index(ledger: Path, now: datetime, limit: int = 300) -> dict:
    now = now.astimezone(timezone.utc)
    forecasts = []
    for path in (ledger / "forecasts").glob("*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("status") != "CAUSAL" or record.get("forecast_id") != path.stem:
            raise ValueError(f"invalid forecast record: {path}")
        forecasts.append(record)
    forecasts.sort(key=lambda r: r["observed_bar_close"])
    selected = forecasts[-limit:]
    entries = []
    for record in selected:
        outcome_path = ledger / "outcomes" / f"{record['forecast_id']}.json"
        outcome = json.loads(outcome_path.read_text(encoding="utf-8")) if outcome_path.exists() else None
        if outcome and (outcome.get("forecast_id") != record["forecast_id"] or outcome.get("status") != "RESOLVED"):
            raise ValueError(f"invalid outcome: {outcome_path}")
        entries.append({
            "forecast_id": record["forecast_id"], "issued_at": record["issued_at"],
            "observed_bar_close": record["observed_bar_close"],
            "observed_price": record["observed_price"],
            "source": record["source"], "source_snapshot_sha256": record["source_snapshot_sha256"],
            "forecasts": record["forecasts"], "outcome": outcome,
        })
    recent = [r for r in forecasts if datetime.fromisoformat(r["observed_bar_close"]) >= now - timedelta(hours=24)]
    return {"schema_version": 1, "generated_at": now.isoformat(),
            "last_forecast_at": forecasts[-1]["issued_at"] if forecasts else None,
            "total_forecasts": len(forecasts), "forecasts_last_24h": len(recent),
            "expected_15m_bars_last_24h": 96, "entries": entries}


def write_index(ledger: Path, now: datetime) -> dict:
    result = build_index(ledger, now)
    (ledger / "index.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result
