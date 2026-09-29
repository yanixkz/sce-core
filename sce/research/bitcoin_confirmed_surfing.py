from __future__ import annotations
from statistics import median

def _confirmed_actions(preds, confirm=2, max_gap=10):
    """Require repeated same-direction causal evidence; never auto-reverse."""
    out=[]; last=None; streak=0; last_i=None
    for r in preds:
        a=r["action"]
        if a==0:
            streak=0; last=None; last_i=None
            continue
        contiguous=last==a and last_i is not None and r["index"]-last_i<=max_gap
        streak=streak+1 if contiguous else 1
        last=a; last_i=r["index"]
        if streak>=confirm:
            out.append({**r,"confirmation_count":streak})
    return out

def confirmed_surfing_backtest(preds, confirm=2, hold_days=20, fee_bps=10.0):
    """Sequential entries after confirmation. Flat first; opposite evidence does not force reversal."""
    signals=_confirmed_actions(preds,confirm)
    trades=[]; next_free=-1
    for r in signals:
        if r["index"]<next_free: continue
        gross=r["action"]*r[f"return_{hold_days}d_pct"]/100
        net=gross-2*fee_bps/10000
        trades.append({**r,"net_return":net,"gross_return":gross})
        next_free=r["index"]+hold_days
    eq=peak=1.0;dd=0.0;gp=gl=0.0;wins=0
    for t in trades:
        eq*=1+t["net_return"];peak=max(peak,eq);dd=min(dd,eq/peak-1)
        wins+=t["net_return"]>0;gp+=max(0,t["net_return"]);gl+=min(0,t["net_return"])
    return {"confirmation":confirm,"trades":len(trades),"longs":sum(t["action"]==1 for t in trades),
            "shorts":sum(t["action"]==-1 for t in trades),"total_return_pct":(eq-1)*100,
            "win_rate":wins/len(trades) if trades else None,"max_drawdown_pct":dd*100,
            "profit_factor":gp/abs(gl) if gl else None,"fee_bps_per_side":fee_bps,"trade_records":trades}

def confirmation_sweep(preds):
    # Predeclared robustness check; not a parameter optimizer.
    return {str(n):confirmed_surfing_backtest(preds,confirm=n) for n in (1,2,3)}
