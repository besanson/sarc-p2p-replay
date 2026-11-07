"""Gate G9 waits, never fails, when the PDF cannot be checked: no engine, another engine, or its exception (D-F-1)."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_tex  # noqa: E402
import gates  # noqa: E402

pytestmark = pytest.mark.skipif(shutil.which("pandoc") is None, reason="G9 regenerates main.tex with pandoc")


@pytest.mark.parametrize("engine", [None, "tectonic"])
def test_g9_waits_for_an_absent_or_other_engine(monkeypatch, engine):
    monkeypatch.setattr(build_tex, "latex_engine", lambda: engine)
    monkeypatch.setattr(build_tex, "build_pdf", lambda e, out: False)
    r = gates.g9_paper()
    assert r["status"] == "pass" and r["waiting"]  # main() turns a passing gate with waiting items into "waiting"


def test_g9_waits_when_the_engine_raises(monkeypatch):
    monkeypatch.setattr(build_tex, "latex_engine", lambda: "tectonic")

    def boom(engine, out):
        raise FileNotFoundError("main.log")

    monkeypatch.setattr(build_tex, "build_pdf", boom)
    r = gates.g9_paper()
    assert r["status"] == "pass" and "raised FileNotFoundError" in r["waiting"][0]
