"""
Test package initializer for ADN v2.

Ensures that the `src/` directory is on sys.path so imports like
`import adn_v2` work in GitHub Actions and local environments.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if SRC.is_dir():
    src_str = str(SRC)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
