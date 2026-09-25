from __future__ import annotations
import csv, io

FIELDS=("time","from_regime","to_regime","detection","signal_time","lead_days","price_usd","pre_5d_return_pct",
"return_1d_pct","return_2d_pct","return_3d_pct","return_5d_pct","return_10d_pct","return_20d_pct","return_30d_pct",
"mfe_30d_pct","mae_30d_pct","up_1pct_day","down_1pct_day","up_2pct_day","down_2pct_day",
"up_3pct_day","down_3pct_day","up_5pct_day","down_5pct_day","up_10pct_day","down_10pct_day")

def event_table_csv(rows):
    buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=FIELDS,extrasaction="ignore"); w.writeheader()
    for r in rows:w.writerow({k:r.get(k) for k in FIELDS})
    return buf.getvalue()
