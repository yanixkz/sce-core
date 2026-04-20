from __future__ import annotations

import json
from sce.scenarios.supplier_reliability import run_demo

if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2, ensure_ascii=False))
