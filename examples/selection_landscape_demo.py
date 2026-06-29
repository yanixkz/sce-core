from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sce.scenarios.selection_landscape import format_selection_landscape_demo, run_selection_landscape_demo


if __name__ == "__main__":
    print(format_selection_landscape_demo(run_selection_landscape_demo()))
