from __future__ import annotations
import argparse,json
from pathlib import Path
from sce.research.bitcoin_temporal_field import build_temporal_field,parse_price_csv
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,default=Path("data/bitcoin/btc_priceusd_1d.csv"));p.add_argument("--out",type=Path,default=Path("data/bitcoin/bitcoin_temporal_field.json"));a=p.parse_args()
    field=build_temporal_field(parse_price_csv(a.input.read_text(encoding="utf-8")));a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(field,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");print(f"Wrote {len(field['cells'])} cells to {a.out}")
if __name__=="__main__":main()
