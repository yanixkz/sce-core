from __future__ import annotations

import csv
import io
import json
import random
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

BASE = "https://api.exchange.coinbase.com/products/BTC-USD/candles"
NATIVE = {"15m": 900, "1h": 3600, "1d": 86400}


@dataclass(frozen=True)
class Candle:
    time: datetime
    low: float
    high: float
    open: float
    close: float
    volume: float


def fetch_candles(granularity: int, start: str, end: str):
    url = f"{BASE}?granularity={granularity}&start={start}&end={end}"
    req = urllib.request.Request(url, headers={"User-Agent": "sce-core-research/1.0"})
    raw = None
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                raw = json.load(response)
            break
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 7:
                raise
            time.sleep(min(60, 2 ** attempt) + random.random())
    time.sleep(0.35)
    if raw is None:
        raise RuntimeError("Coinbase returned no candle payload")
    out = [
        Candle(datetime.fromtimestamp(x[0], timezone.utc), *map(float, x[1:]))
        for x in raw
    ]
    return sorted(out, key=lambda x: x.time)


def resample(candles, seconds: int):
    groups = {}
    for candle in candles:
        key = int(candle.time.timestamp()) // seconds * seconds
        groups.setdefault(key, []).append(candle)
    out = []
    for key, rows in sorted(groups.items()):
        out.append(
            Candle(
                datetime.fromtimestamp(key, timezone.utc),
                min(x.low for x in rows),
                max(x.high for x in rows),
                rows[0].open,
                rows[-1].close,
                sum(x.volume for x in rows),
            )
        )
    return out


def to_csv(candles):
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["time", "open", "high", "low", "close", "volume"])
    for candle in candles:
        writer.writerow(
            [
                candle.time.isoformat(),
                candle.open,
                candle.high,
                candle.low,
                candle.close,
                candle.volume,
            ]
        )
    return stream.getvalue()
