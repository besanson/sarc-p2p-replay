"""scripts/tolerance.py and the reproduce report: last-digit differences pass, real ones fail (D-F-1)."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import reproduce  # noqa: E402
import tolerance  # noqa: E402

SLOT = ROOT / "results" / "e1" / "exposure.json"


def _perturbed(tmp_path: Path, eps: float) -> Path:
    doc = json.loads(SLOT.read_text(encoding="utf-8"))
    doc["classes"]["D4"]["share_of_clearings"] += eps
    out = tmp_path / "exposure.json"
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def test_a_last_digit_difference_is_within_tolerance(tmp_path):
    r = tolerance.compare(SLOT, _perturbed(tmp_path, 1e-16))
    assert r["within_tolerance"] and r["max_abs_difference"] < 1e-15


def test_a_real_difference_is_not(tmp_path):
    r = tolerance.compare(SLOT, _perturbed(tmp_path, 1e-6))
    assert not r["byte_identical"] and not r["within_tolerance"]


def test_strings_and_structure_must_be_equal():
    assert tolerance.diff({"a": "x"}, {"a": "y"}) == (False, 0.0)
    assert tolerance.diff([1, 2], [1, 2, 3])[0] is False
    assert tolerance.diff({"a": 1.0}, {"b": 1.0})[0] is False
    assert tolerance.diff(True, 1)[0] is False


def test_text_files_are_compared_by_bytes(tmp_path):
    other = tmp_path / "paper.md"
    other.write_text((ROOT / "paper" / "paper.md").read_text(encoding="utf-8") + " ", encoding="utf-8")
    r = tolerance.compare(ROOT / "paper" / "paper.md", other)
    assert not r["parsed"] and not r["within_tolerance"] and r["max_abs_difference"] is None


def test_a_failing_pdf_step_still_writes_the_report(monkeypatch, tmp_path):
    import build_tex

    paper_dir = tmp_path / "paper"
    paper_dir.mkdir()
    shutil.copyfile(ROOT / "paper-tex" / "main.tex", paper_dir / "main.tex")
    monkeypatch.setattr(build_tex, "latex_engine", lambda: "tectonic")

    def boom(engine, out):
        raise FileNotFoundError("main.log")

    monkeypatch.setattr(build_tex, "build_pdf", boom)
    ok = reproduce.finish(tmp_path / "results", paper_dir, out=tmp_path / "out")
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert not ok and "PDF not built: FileNotFoundError" in text and "NOT REPRODUCED" in text
