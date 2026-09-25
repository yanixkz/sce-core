"""Public Coinbase Exchange spot market snapshots, collected prospectively.

REST book and latest trades are samples, not a reconstructed continuous order
flow. A trade's side is the maker side: maker sell = aggressive buy.
"""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone

ROOT = "https://api.exchange.coinbase.com/products/BTC-USD"


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "sce-core-research/1.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def summarize(book, trades, fetched_at):
    bids = [(float(p), float(s)) for p,s,*_ in book["bids"][:10]]
    asks = [(float(p), float(s)) for p,s,*_ in book["asks"][:10]]
    if not bids or not asks or bids[0][0] >= asks[0][0]:
        raise ValueError("invalid Coinbase book snapshot")
    bid_size = sum(s for _,s in bids)
    ask_size = sum(s for _,s in asks)
    taker_buy = sum(float(t["size"]) for t in trades if t.get("side") == "sell")
    taker_sell = sum(float(t["size"]) for t in trades if t.get("side") == "buy")
    return {"status": "OBSERVED", "source": "Coinbase Exchange BTC-USD REST",
            "fetched_at": fetched_at.isoformat(), "book_sequence": book.get("sequence"),
            "best_bid": bids[0][0], "best_ask": asks[0][0],
            "spread_bps": (asks[0][0]-bids[0][0])/((asks[0][0]+bids[0][0])/2)*10000,
            "top_10_bid_btc": bid_size, "top_10_ask_btc": ask_size,
            "top_10_size_imbalance": (bid_size-ask_size)/(bid_size+ask_size) if bid_size+ask_size else None,
            "recent_trade_count": len(trades), "recent_taker_buy_btc": taker_buy,
            "recent_taker_sell_btc": taker_sell,
            "recent_trade_imbalance": (taker_buy-taker_sell)/(taker_buy+taker_sell)
               if taker_buy+taker_sell else None,
            "limitation": "REST snapshots and recent trades are not a 15m order-flow history or synchronized L2 stream"}


def fetch_snapshot():
    book = _get(ROOT+"/book?level=2")
    trades = _get(ROOT+"/trades")
    return summarize(book, trades, datetime.now(timezone.utc))
