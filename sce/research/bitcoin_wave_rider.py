from __future__ import annotations

def wave_rider(preds, confirm=3, fee_bps=10.0):
    """Event-driven causal rider: enter after confirmation, exit to FLAT on loss/opposite evidence.
    No automatic reversal. Uses the next causal alarm observations as state checkpoints.
    """
    trades=[]; pos=0; streak_dir=0; streak=0; entry=None
    for r in preds:
        a=r["action"]
        if a!=0 and a==streak_dir: streak+=1
        elif a!=0: streak_dir=a; streak=1
        else: streak_dir=0; streak=0

        if pos==0:
            if a!=0 and streak>=confirm:
                pos=a; entry=r
            continue

        # Exit when causal evidence no longer supports the held wave.
        if a==0 or a==-pos:
            days=r["index"]-entry["index"]
            if days>0:
                # Daily PriceUSD path is unavailable here; use the closest precomputed horizon conservatively.
                hs=(1,3,5,10,20,30)
                h=min(hs,key=lambda x:abs(x-days))
                gross=pos*entry[f"return_{h}d_pct"]/100
                net=gross-2*fee_bps/10000
                trades.append({"entry_index":entry["index"],"exit_index":r["index"],"direction":pos,
                               "observed_days":days,"proxy_horizon_days":h,"gross_return":gross,"net_return":net})
            pos=0; entry=None
            # deliberately remain FLAT; opposite signal must confirm afresh
            streak_dir=a if a!=0 else 0; streak=1 if a!=0 else 0

    eq=peak=1.0;dd=0.0;gp=gl=0.0;wins=0
    for t in trades:
        eq*=1+t["net_return"];peak=max(peak,eq);dd=min(dd,eq/peak-1)
        wins+=t["net_return"]>0;gp+=max(0,t["net_return"]);gl+=min(0,t["net_return"])
    return {"method":"causal alarm-checkpoint wave rider (proxy exits)","confirmation":confirm,
            "trades":len(trades),"longs":sum(t["direction"]==1 for t in trades),
            "shorts":sum(t["direction"]==-1 for t in trades),
            "total_return_pct":(eq-1)*100,"win_rate":wins/len(trades) if trades else None,
            "max_drawdown_pct":dd*100,"profit_factor":gp/abs(gl) if gl else None,
            "trade_records":trades,
            "limitation":"Exit PnL uses nearest available forward-return horizon, not exact daily exit price."}
