"""Make the repository's ``src`` layout runnable with its existing interpreter.

Python imports this module automatically when launched from the repository root.
It keeps ``python -m ear_rag.demo`` usable without installing the package.
"""

from __future__ import annotations

import sys
from pathlib import Path


_SRC = Path(__file__).resolve().parent / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
