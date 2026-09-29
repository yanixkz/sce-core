from __future__ import annotations

import csv
import json
import math
import random
from bisect import bisect_left
from pathlib import Path

TAUS=(1,2,4,8,16,32,64,128,256,512,1024)
SEED=20260924

def load(path):
    with open(path,newline="") as f:
        return [(r["time"],float(r["close"])) for r in csv.DictReader(f)]

def ema(xs,n):
    if n<=1: return list(xs)
    a=2/(n+1); out=[]; v=xs[0]
    for x in xs:
        v=a*x+(1-a)*v; out.append(v)
    return out

def cma(xs,n):
    if n<=1: return list(xs)
    out=[]; s=0.0
    for i,x in enumerate(xs):
        s+=x
        if i>=n: s-=xs[i-n]
        out.append(s/min(n,i+1))
    return out

def extrema(xs):
    out=[]
    for i in range(1,len(xs)-1):
        if xs[i]>xs[i-1] and xs[i]>=xs[i+1]: out.append((i,"H"))
        elif xs[i]<xs[i-1] and xs[i]<=xs[i+1]: out.append((i,"L"))
    return out

def index_events(events):
    return {k:[e[0] for e in events if e[1]==k] for k in ("H","L")}

def nearest(idx,i,k,d):
    a=idx[k]; j=bisect_left(a,i); cand=[]
    if j<len(a): cand.append(a[j])
    if j: cand.append(a[j-1])
    if not cand: return None
    z=min(cand,key=lambda q:abs(q-i))
    return z if abs(z-i)<=d else None

def tolerance(tau,mode):
    if mode=="fixed": return 8
    if mode=="sqrt": return max(2,int(round(math.sqrt(tau)*2)))
    if mode=="quarter": return max(2,tau//4)
    return max(2,tau)

def analyze(prices,smoother,tol_mode):
    levels={}
    for tau in TAUS:
        ex=extrema(smoother(prices,tau))
        levels[tau]=index_events(ex)
    base=[(i,k) for k in ("H","L") for i in levels[1][k]]
    deaths=[]; survived=[0]*len(TAUS)
    for i,k in base:
        cur=i; last=0; survived[0]+=1
        for q,tau in enumerate(TAUS[1:],1):
            m=nearest(levels[tau],cur,k,tolerance(tau,tol_mode))
            if m is None: break
            cur=m; last=q; survived[q]+=1
        deaths.append(TAUS[last])
    survival=[]
    for q,tau in enumerate(TAUS):
        at_risk=survived[q-1] if q else len(base)
        conditional=survived[q]/at_risk if at_risk else None
        survival.append({"tau":tau,"hours":tau*.25,"survived":survived[q],
                         "fraction_of_births":survived[q]/len(base) if base else 0,
                         "conditional_survival":conditional})
    return {"base_extrema":len(base),"durable_6plus":survived[5],
            "durable_fraction":survived[5]/len(base) if base else 0,
            "reached_max":survived[-1],"reached_max_fraction":survived[-1]/len(base) if base else 0,
            "survival_curve":survival}

def surrogate_prices(prices,mode,rng):
    logs=[math.log(x) for x in prices]
    rets=[logs[i]-logs[i-1] for i in range(1,len(logs))]
    if mode=="shuffle":
        rng.shuffle(rets)
    elif mode=="block":
        block=96
        blocks=[rets[i:i+block] for i in range(0,len(rets),block)]
        rng.shuffle(blocks); rets=[x for b in blocks for x in b]
    out=[logs[0]]
    for r in rets: out.append(out[-1]+r)
    return [math.exp(x) for x in out]

def main():
    root=Path("data/bitcoin/coinbase")
    rows=load(root/"btc_usd_15m.csv"); prices=[p for _,p in rows]
    configs=[("ema","fixed"),("ema","sqrt"),("ema","quarter"),("ema","scale"),
             ("cma","fixed"),("cma","sqrt"),("cma","quarter")]
    smoothers={"ema":ema,"cma":cma}
    result={"method":"scale-space persistence robustness","taus":TAUS,"real":{},"null":{}}
    for sm,tol in configs:
        result["real"][f"{sm}_{tol}"]=analyze(prices,smoothers[sm],tol)
    rng=random.Random(SEED)
    for mode in ("shuffle","block"):
        sp=surrogate_prices(prices,mode,rng)
        result["null"][mode]={}
        for sm,tol in (("ema","fixed"),("ema","sqrt"),("ema","quarter")):
            result["null"][mode][f"{sm}_{tol}"]=analyze(sp,smoothers[sm],tol)
    out=root/"scale_space_robustness.json"
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    compact={"real":{k:{"durable_fraction":v["durable_fraction"],"reached_max_fraction":v["reached_max_fraction"]} for k,v in result["real"].items()},
             "null":{m:{k:{"durable_fraction":v["durable_fraction"],"reached_max_fraction":v["reached_max_fraction"]} for k,v in z.items()} for m,z in result["null"].items()}}
    print(json.dumps(compact,indent=2))

if __name__=="__main__":
    main()
