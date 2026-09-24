from datetime import datetime, timedelta, timezone

import pytest

from sce.research.bitcoin_forecast_lab import backtest, issue, predict, settle


def rows(n=110):
    start = datetime(2026, 9, 20, tzinfo=timezone.utc)
    return [(start+timedelta(minutes=15*i), 100+i/10) for i in range(n)]


def test_predictions_do_not_change_when_future_prices_change():
    history = [p for _,p in rows(97)]
    first = predict(history)
    assert first == predict([1000, 1]+history)
    assert first["15"]["momentum_price"] > history[-1]


def test_issue_requires_completed_fresh_contiguous_history(tmp_path):
    source = rows(100)
    last_close = source[-1][0]+timedelta(minutes=15)
    record = issue(source, last_close+timedelta(seconds=40), tmp_path)
    assert record["forecasts"]["15"]["target_bar_close"] == (last_close+timedelta(minutes=15)).isoformat()
    assert len(list((tmp_path/"forecasts").glob("*.json"))) == 1
    with pytest.raises(FileExistsError):
        issue(source, last_close+timedelta(seconds=40), tmp_path)
    with pytest.raises(ValueError, match="not fresh"):
        issue(source, last_close+timedelta(minutes=6), tmp_path)
    broken = source.copy()
    broken[-10] = (broken[-10][0]+timedelta(minutes=1), broken[-10][1])
    with pytest.raises(ValueError, match="missing 15m"):
        issue(broken, last_close+timedelta(seconds=40), tmp_path)


def test_settlement_is_separate_and_never_uses_incomplete_candle(tmp_path):
    source = rows(100)
    close = source[-1][0]+timedelta(minutes=15)
    record = issue(source, close+timedelta(seconds=40), tmp_path)
    future = rows(102)
    assert settle(record, future, close+timedelta(minutes=14), tmp_path) is None
    assert settle(record, future, close+timedelta(minutes=16), tmp_path) is None
    result = settle(record, rows(102), close+timedelta(minutes=31), tmp_path)
    assert set(result["outcomes"]) == {"15", "30"}
    assert len(list((tmp_path/"outcomes").glob("*.json"))) == 1


def test_backtest_skips_missing_future_candles():
    source = rows(120)
    source[106] = (source[106][0]+timedelta(minutes=1), source[106][1])
    report = backtest(source)
    assert report["status"] == "RETROSPECTIVE"
    assert report["eras"]["2024+"]["15"]["n"] > 0
