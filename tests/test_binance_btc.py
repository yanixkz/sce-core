from sce.data.binance_btc import normalized_rows, to_csv

def test_normalizes_binance_kline():
    raw=[[0,"1","2","0.5","1.5","10",59999,"0",0,"0","0","0"]]
    row=normalized_rows(raw,"1m")[0]
    assert row["scale"]=="1m"
    assert row["close"]==1.5
    assert row["volume"]==10.0

def test_multiscale_csv_schema():
    raw=[[0,"1","2","0.5","1.5","10",59999,"0",0,"0","0","0"]]
    text=to_csv(normalized_rows(raw,"4h"))
    assert "time,scale,open,high,low,close,volume,close_time_ms" in text
    assert ",4h," in text
