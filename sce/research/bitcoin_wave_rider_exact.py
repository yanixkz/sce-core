from __future__ import annotations

def exact_wave_rider(preds, points, confirm=3, fee_bps=10.0):
    """Causal checkpoint rider with exact daily PriceUSD at entry/exit.
    Opposite evidence exits to FLAT; it never reverses automatically.
    """
    price=[float(p.price) for p in points]
    trades=[];pos=0;streak_dir=0;streak=0;entry=None
    for r in preds:
        a=r["action"]
        if a!=0 and a==streak_dir: streak+=1
        elif a!=0: streak_dir=a;streak=1
        else: streak_dir=0;streak=0
        if pos==0:
            if a!=0 and streak>=confirm:
                pos=a;entry=r
            continue
        if a==0 or a==-pos:
            ei,xi=entry["index"],r["index"]
            if xi>ei and xi<len(price):
                ep,xp=price[ei],price[xi]
                spot=xp/ep-1
                gross=spot if pos==1 else ep/xp-1
                net=(1+gross)*(1-fee_bps/10000)**2-1
                path=price[ei:xi+1]
                path_ret=[p/ep-1 if pos==1 else ep/p-1 for p in path]
                trades.append({"entry_index":ei,"exit_index":xi,"direction":pos,
                    "entry_price":ep,"exit_price":xp,"days":xi-ei,
                    "gross_return":gross,"net_return":net,
                    "mfe":max(path_ret),"mae":min(path_ret)})
            pos=0;entry=None
            streak_dir=a if a!=0 else 0;streak=1 if a!=0 else 0
    eq=peak=1.0;dd=0.0;gp=gl=0.0;wins=0
    for t in trades:
        eq*=1+t["net_return"];peak=max(peak,eq);dd=min(dd,eq/peak-1)
        wins+=t["net_return"]>0;gp+=max(0,t["net_return"]);gl+=min(0,t["net_return"])
    return {"method":"causal checkpoint wave rider; exact daily PriceUSD exits",
        "confirmation":confirm,"trades":len(trades),
        "longs":sum(t["direction"]==1 for t in trades),"shorts":sum(t["direction"]==-1 for t in trades),
        "total_return_pct":(eq-1)*100,"win_rate":wins/len(trades) if trades else None,
        "max_drawdown_pct":dd*100,"profit_factor":gp/abs(gl) if gl else None,
        "median_hold_days":sorted(t["days"] for t in trades)[len(trades)//2] if trades else None,
        "trade_records":trades}
