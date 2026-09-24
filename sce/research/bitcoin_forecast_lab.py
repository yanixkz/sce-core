"""Frozen, causal 15m/30m forecast baselines over Coinbase 15m close prices.

Exploratory research only. These fixed rules are not fitted to future labels.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

BAR_SECONDS = 900
HORIZONS = (1, 2)
LOOKBACK = 96


def read_close_csv(path):
    with open(path, newline="") as handle:
        return [(datetime.fromisoformat(r["time"].replace("Z", "+00:00")), float(r["close"]))
                for r in csv.DictReader(handle)]


def predict(closes):
    """Only consumes closes already known at the forecast's observation time."""
    if len(closes) < LOOKBACK + 1 or any(not math.isfinite(p) or p <= 0 for p in closes):
        raise ValueError("need at least 97 positive finite closes")
    p = closes[-1]
    log_returns = [math.log(b/a) for a, b in zip(closes[-LOOKBACK-1:-1], closes[-LOOKBACK:])]
    drift = math.log(p/closes[-5]) / 4
    vol = math.sqrt(sum((r - sum(log_returns)/LOOKBACK)**2 for r in log_returns)/LOOKBACK)
    return {str(h*15): {
        "flat_price": p,
        "momentum_price": p*math.exp(h*drift),
        "flat_p_up": 0.5,
        "momentum_p_up": 0.55 if drift > 0 else (0.45 if drift < 0 else 0.5),
        "momentum_80_interval": [p*math.exp(h*drift-1.2815515655*vol*math.sqrt(h)),
                                 p*math.exp(h*drift+1.2815515655*vol*math.sqrt(h))],
    } for h in HORIZONS}


def backtest(rows):
    """Hourly nonoverlapping origins; labels are read only after each prediction."""
    sums = {era: {str(h*15): {"n": 0, "flat_abs_pct": 0., "momentum_abs_pct": 0.,
                            "flat_brier": 0., "momentum_brier": 0., "interval_hits": 0}
                  for h in HORIZONS}
            for era in ("2017-2020", "2021-2023", "2024+")}
    streak = 1
    for i in range(1, len(rows)-max(HORIZONS), 1):
        streak = streak+1 if (rows[i][0]-rows[i-1][0]).total_seconds() == BAR_SECONDS else 1
        if streak < LOOKBACK+1 or i % 4 != 0:
            continue
        forecast = predict([p for _, p in rows[i-LOOKBACK:i+1]])
        year = rows[i][0].year
        era = "2017-2020" if year <= 2020 else ("2021-2023" if year <= 2023 else "2024+")
        for h in HORIZONS:
            if (rows[i+h][0]-rows[i][0]).total_seconds() != h*BAR_SECONDS:
                continue
            target, observed = rows[i+h][1], rows[i][1]
            f = forecast[str(h*15)]
            result = sums[era][str(h*15)]
            y = float(target > observed)
            result["n"] += 1
            result["flat_abs_pct"] += abs(f["flat_price"]-target)/observed*100
            result["momentum_abs_pct"] += abs(f["momentum_price"]-target)/observed*100
            result["flat_brier"] += (f["flat_p_up"]-y)**2
            result["momentum_brier"] += (f["momentum_p_up"]-y)**2
            result["interval_hits"] += f["momentum_80_interval"][0] <= target <= f["momentum_80_interval"][1]
    for horizon_rows in sums.values():
        for result in horizon_rows.values():
            n = result["n"]
            for key in ("flat_abs_pct", "momentum_abs_pct", "flat_brier", "momentum_brier", "interval_hits"):
                result[key] = result[key]/n if n else None
    return {"status": "RETROSPECTIVE", "sampling": "hourly origins, no overlapping 30m outcomes",
            "horizons_minutes": [15, 30], "baseline": "unchanged last close; p(up)=0.5",
            "candidate": "fixed 4-bar momentum; p(up)=0.55/0.45, uncalibrated",
            "note": "Price evaluated at future bar close; no fees, spread or trading claim."
                    " Interval uses trailing volatility; empirical coverage is reported, not calibrated.",
            "eras": sums}


def immutable_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, sort_keys=True, indent=2)
        handle.write("\n")


def issue(rows, issued_at, output_dir, run_id=None):
    """Write a prospective forecast only while the last fully closed bar is fresh."""
    issued_at = issued_at.astimezone(timezone.utc)
    eligible = [(t, p) for t, p in rows if t+timedelta(seconds=BAR_SECONDS) <= issued_at]
    if len(eligible) < LOOKBACK+1:
        raise ValueError("insufficient completed candles")
    t, p = eligible[-1]
    known_at = t+timedelta(seconds=BAR_SECONDS)
    lag = (issued_at-known_at).total_seconds()
    if not 0 <= lag < 300:
        raise ValueError("latest completed 15m bar is not fresh enough for +15m forecast")
    history = eligible[-LOOKBACK-1:]
    if any((b[0]-a[0]).total_seconds() != BAR_SECONDS for a, b in zip(history, history[1:])):
        raise ValueError("missing 15m bars in observation window")
    f = predict([v for _, v in history])
    payload = {"status": "CAUSAL", "source": "Coinbase Exchange BTC-USD 15m",
               "issued_at": issued_at.isoformat(), "observed_bar_open": t.isoformat(),
               "observed_bar_close": known_at.isoformat(), "observed_price": p,
               "source_snapshot_sha256": hashlib.sha256(json.dumps([(x.isoformat(), v) for x,v in history]).encode()).hexdigest(),
               "run_id": run_id, "forecasts": {k: {**v,
                   "target_bar_close": (known_at+timedelta(minutes=int(k))).isoformat(),
                   "effective_lead_minutes": int(k)-lag/60} for k,v in f.items()}}
    forecast_id = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    payload["forecast_id"] = forecast_id
    immutable_json(output_dir/"forecasts"/f"{forecast_id}.json", payload)
    return payload


def settle(record, rows, resolved_at, output_dir):
    if record["status"] != "CAUSAL":
        raise ValueError("only causal forecasts can be settled")
    by_close = {t+timedelta(seconds=BAR_SECONDS): p for t,p in rows
                if t+timedelta(seconds=BAR_SECONDS) <= resolved_at}
    outcomes = {}
    for horizon, f in record["forecasts"].items():
        target = datetime.fromisoformat(f["target_bar_close"])
        if target not in by_close:
            continue
        y = by_close[target]
        outcomes[horizon] = {"actual_price": y,
            "flat_abs_pct": abs(y-f["flat_price"])/record["observed_price"]*100,
            "momentum_abs_pct": abs(y-f["momentum_price"])/record["observed_price"]*100,
            "momentum_direction_correct": (f["momentum_p_up"] > 0.5) == (y > record["observed_price"]),
            "momentum_brier": (f["momentum_p_up"]-float(y > record["observed_price"]))**2}
    if not outcomes:
        return None
    outcome = {"status": "RESOLVED", "forecast_id": record["forecast_id"],
               "resolved_at": resolved_at.isoformat(), "outcomes": outcomes}
    immutable_json(output_dir/"outcomes"/f"{record['forecast_id']}.json", outcome)
    return outcome
