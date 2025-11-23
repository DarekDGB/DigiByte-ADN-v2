"""
Basic sanity tests for DigiByte-ADN-v2.

Goal:
- Make sure all core modules import cleanly.
- This catches syntax errors or missing dependencies early.
"""

import importlib
import pkgutil
import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    """
    Ensure the `src` directory is on sys.path so that `adn_v2`
    can be imported when running tests without installation.
    """
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def test_import_adn_v2_package():
    """The main adn_v2 package should be importable."""
    _ensure_src_on_path()
    pkg = importlib.import_module("adn_v2")
    assert pkg is not None


def test_import_all_submodules():
    """
    Dynamically import all adn_v2.* modules.

    If any file has a syntax error or crashes on import,
    this test will fail and CI will show a red cross.
    """
    _ensure_src_on_path()
    package = importlib.import_module("adn_v2")

    for module_info in pkgutil.iter_modules(package.__path__):
        name = module_info.name
        full_name = f"adn_v2.{name}"
        imported = importlib.import_module(full_name)
        assert imported is not None, f"Failed to import {full_name}"
