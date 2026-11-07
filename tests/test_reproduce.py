"""scripts/reproduce.py: every excluded name exists, and the report's verdict follows the rows."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import reproduce  # noqa: E402


def test_excluded_and_record_names_exist():
    for name in [*reproduce.MACHINE, *reproduce.RECORDS]:
        assert (ROOT / name).exists(), name


def test_verdict():
    row = lambda f, byte, eq, d: {"file": f, "byte_identical": byte, "within_tolerance": eq, "equal": eq,  # noqa: E731
                                  "max_abs_difference": d}
    rows = [row("a", True, True, 0.0), row("b", False, True, 1.1e-16), row("c.md", True, True, None)]
    text, ok = reproduce.report(rows, [], "PDF not built: no LaTeX engine")
    assert ok and "REPRODUCED: 3 files equal (2 byte-identical, 1 within tolerance, max difference 1.1e-16)" in text
    text, ok = reproduce.report(rows + [row("d", False, False, 1e-6)], ["e"], None)
    assert not ok and "NOT REPRODUCED: 1 of 4 compared files not equal: d; 1 committed files not regenerated: e" in text
