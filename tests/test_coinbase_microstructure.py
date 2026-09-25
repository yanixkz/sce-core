from datetime import datetime, timezone

from sce.data.coinbase_microstructure import summarize


def test_maker_side_is_inverted_for_aggressor_volume():
    book={"sequence":42,"bids":[["100","2","1"]],"asks":[["101","1","1"]]}
    trades=[{"side":"sell","size":"3"},{"side":"buy","size":"1"}]
    x=summarize(book,trades,datetime(2026,9,25,tzinfo=timezone.utc))
    assert x["top_10_size_imbalance"]==1/3
    assert x["recent_trade_imbalance"]==.5
    assert x["recent_taker_buy_btc"]==3
