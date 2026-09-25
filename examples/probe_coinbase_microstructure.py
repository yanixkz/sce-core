from pathlib import Path
import json
from sce.data.coinbase_microstructure import fetch_snapshot

result=fetch_snapshot()
out=Path("data/bitcoin/coinbase/microstructure_probe.json")
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
