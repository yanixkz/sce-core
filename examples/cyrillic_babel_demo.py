from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sce.scenarios.cyrillic_babel_demo import format_cyrillic_babel_demo, run_cyrillic_babel_demo


if __name__ == "__main__":
    print(format_cyrillic_babel_demo(run_cyrillic_babel_demo()))
