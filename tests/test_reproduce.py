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
    rows = [{"file": "a", "committed": "x" * 64, "regenerated": "x" * 64, "match": True}]
    text, ok = reproduce.report(rows, [], None)
    assert ok and "REPRODUCED: all 1 compared files match." in text
    rows.append({"file": "b", "committed": "x" * 64, "regenerated": "y" * 64, "match": False})
    text, ok = reproduce.report(rows, ["c"], None)
    assert not ok and "NOT REPRODUCED: 1 of 2 compared files differ; 1 committed files were not regenerated." in text
