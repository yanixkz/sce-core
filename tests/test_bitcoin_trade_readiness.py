from sce.research.bitcoin_trade_readiness import assess


def test_trade_gate_blocks_retrospective_loss_and_one_forward_example():
    metrics={"flat_abs_pct":.2,"volume_gated_abs_pct":.3,"flat_brier":.25,
             "volume_gated_brier":.26,"paper_mean_net_return_pct":-.1}
    result=assess({"eras":{"2024+":{"15":metrics,"30":metrics}}},[])
    assert result["status"]=="BLOCKED"
    assert result["live_trading_enabled"] is False
    assert result["paper_trading_enabled"] is False
