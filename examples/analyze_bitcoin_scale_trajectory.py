from __future__ import annotations
import csv,json,math,random
from bisect import bisect_left
from pathlib import Path

TAUS=(1,2,4,8,16,32,64,128,256,512,1024)
SEED=20260924

def load(p):
    with open(p,newline="") as f:return [(r["time"],float(r["close"])) for r in csv.DictReader(f)]

def ema(x,n):
    if n<=1:return list(x)
    a=2/(n+1);v=x[0];o=[]
    for z in x:v=a*z+(1-a)*v;o.append(v)
    return o

def extrema(x):
    o=[]
    for i in range(1,len(x)-1):
        if x[i]>x[i-1] and x[i]>=x[i+1]:o.append((i,"H",x[i]))
        elif x[i]<x[i-1] and x[i]<=x[i+1]:o.append((i,"L",x[i]))
    return o

def idx(ex):
    return {k:([e[0] for e in ex if e[1]==k],[e for e in ex if e[1]==k]) for k in ("H","L")}

def near(ix,i,k,d):
    a,e=ix[k];j=bisect_left(a,i);c=[]
    if j<len(e):c.append(e[j])
    if j:c.append(e[j-1])
    if not c:return None
    q=min(c,key=lambda z:abs(z[0]-i))
    return q if abs(q[0]-i)<=d else None

def tol(t):return max(2,int(round(math.sqrt(t)*2)))

def tracks(prices):
    lv={}
    for t in TAUS:
        ex=extrema(ema(prices,t));lv[t]=idx(ex)
    base=lv[1]["H"][1]+lv[1]["L"][1];out=[]
    for e in base:
        tr=[(1,e[0],e[1],e[2])];cur=e
        for t in TAUS[1:]:
            m=near(lv[t],cur[0],cur[1],tol(t))
            if m is None:break
            tr.append((t,m[0],m[1],m[2]));cur=m
        if len(tr)>=2:out.append(tr)
    return out

def features(tr):
    shifts=[abs(tr[i][1]-tr[i-1][1]) for i in range(1,len(tr))]
    norm=[shifts[i]/TAUS[i+1] for i in range(len(shifts))]
    signs=[0 if tr[i][1]==tr[i-1][1] else (1 if tr[i][1]>tr[i-1][1] else -1) for i in range(1,len(tr))]
    reversals=sum(1 for a,b in zip(signs,signs[1:]) if a and b and a!=b)
    return {"levels":len(tr),"death_tau":tr[-1][0],
      "mean_norm_drift":sum(norm)/len(norm) if norm else 0,
      "max_norm_drift":max(norm) if norm else 0,
      "drift_reversals":reversals,
      "net_index_drift":tr[-1][1]-tr[0][1],
      "kind":tr[0][2]}

def summarize(fs):
    def med(a):
        if not a:return None
        a=sorted(a);n=len(a);return a[n//2] if n%2 else (a[n//2-1]+a[n//2])/2
    return {"n":len(fs),
      "median_levels":med([x["levels"] for x in fs]),
      "median_mean_norm_drift":med([x["mean_norm_drift"] for x in fs]),
      "median_max_norm_drift":med([x["max_norm_drift"] for x in fs]),
      "median_drift_reversals":med([x["drift_reversals"] for x in fs]),
      "fraction_reversal_free":sum(x["drift_reversals"]==0 for x in fs)/len(fs) if fs else 0}

def block_null(prices,rng,block=96):
    lp=[math.log(x) for x in prices];r=[lp[i]-lp[i-1] for i in range(1,len(lp))]
    b=[r[i:i+block] for i in range(0,len(r),block)];rng.shuffle(b);r=[z for q in b for z in q]
    o=[lp[0]]
    for z in r:o.append(o[-1]+z)
    return [math.exp(z) for z in o]

def main():
    root=Path("data/bitcoin/coinbase");rows=load(root/"btc_usd_15m.csv");p=[x[1] for x in rows]
    real=[features(t) for t in tracks(p)]
    rng=random.Random(SEED);nullp=block_null(p,rng);null=[features(t) for t in tracks(nullp)]
    result={"method":"scale-space trajectory geometry","matching":"EMA + 2*sqrt(tau) tolerance",
      "features":["levels","death_tau","mean_norm_drift","max_norm_drift","drift_reversals","net_index_drift"],
      "real":summarize(real),"block_null":summarize(null),
      "warning":"descriptive structure test; no future returns or trading labels"}
    (root/"scale_space_trajectory.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
