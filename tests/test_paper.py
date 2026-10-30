"""The paper is generated from the template and the slots: deterministic, every value recorded."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import fill_paper  # noqa: E402


def test_fill_is_deterministic_and_records_every_span(tmp_path):
    a = fill_paper.run(out_paper=tmp_path / "a.md", out_filled=tmp_path / "a.json")
    fill_paper.run(out_paper=tmp_path / "b.md", out_filled=tmp_path / "b.json")
    assert (tmp_path / "a.md").read_bytes() == (tmp_path / "b.md").read_bytes()
    assert (tmp_path / "a.json").read_bytes() == (tmp_path / "b.json").read_bytes()
    text = (tmp_path / "a.md").read_text(encoding="utf-8")
    assert "{{" not in text and "}}" not in text
    for rec in a["placeholders"]:
        assert text[rec["start"]:rec["end"]] == rec["text"]
    spans = [(s["start"], s["end"]) for s in a["spans"]]
    assert spans == sorted(spans) and all(e1 <= s2 for (_, e1), (s2, _) in zip(spans, spans[1:]))


def test_committed_paper_matches_the_template(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_bytes((ROOT / "README.md").read_bytes())
    fill_paper.run(out_paper=tmp_path / "p.md", out_filled=tmp_path / "f.json", readme=readme)
    assert (ROOT / "paper" / "paper.md").read_bytes() == (tmp_path / "p.md").read_bytes()
    assert (ROOT / "paper" / "filled-template.json").read_bytes() == (tmp_path / "f.json").read_bytes()
    assert (ROOT / "README.md").read_bytes() == readme.read_bytes()


def test_readme_headline_is_checked_by_the_lint(tmp_path):
    from lint import typed_numerals as tn

    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert fill_paper.README_START in text and fill_paper.README_END in text
    edited = tmp_path / "README.md"
    edited.write_text(text.replace("| gate |", "| gate (edited) |", 1), encoding="utf-8")
    original = tn.README
    try:
        tn.README = edited
        result = tn.run()
    finally:
        tn.README = original
    assert not result["readme"]["clean"] and "differs" in result["readme"]["violations"][0]["context"]


def test_formats_and_value_lookup():
    assert fill_paper.fmt(0.11411, "pct") == "11.41%" and fill_paper.fmt(155534, "int") == "155,534"
    assert fill_paper.fmt(1.13e-4, "p") == "1.13 × 10^-4^" and fill_paper.fmt(0.9999, "p") == "1"
    assert fill_paper.fmt([0.1, 0.2], "ivpct") == "[10.00%, 20.00%]" and fill_paper.fmt(None, "pct") == "n/a"
    assert fill_paper.walk({"a": [{"b": 3}]}, ["a", "0", "b"]) == 3
    refs = json.loads((ROOT / "verified-citations.json").read_text(encoding="utf-8"))["citations"]
    assert fill_paper.cite_text("pesic-declare-2007") == "Pesic et al. 2007" and refs
