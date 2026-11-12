"""Exploratory analyses (D-G-1) on the synthetic fixture: definitions, partitions, double runs."""

from __future__ import annotations

import pytest

from conftest import FIXTURES
from experiments import e1, e2, e3
from experiments.common import read_jsonl_gz

XES = FIXTURES / "mini2019.xes"
B = 50


@pytest.fixture(scope="module")
def results(tmp_path_factory):
    root = tmp_path_factory.mktemp("results")
    e0 = root / "e0-lines.txt"
    e0.write_text("", encoding="utf-8")
    e1.run(XES, root / "e1", e0, min_month_events=1, b=B)
    e2.run(root / "e1", root / "e2", b=B)
    e3.run(root / "e1", root / "e3", b=B)
    return root


def test_x1_partitions_d4_and_runs_twice_identically(results, tmp_path):
    from experiments.exploratory import x1_d4_sensitivity as x1

    kw = dict(e0_path=results / "e0-lines.txt", min_month_events=1, b=B)
    doc = x1.run(XES, results, tmp_path / "a.json", **kw)
    records = read_jsonl_gz(results / "e1" / "evidence-set.jsonl.gz")
    d4 = sum(r["predicates"]["D4"] == "fail" for r in records)
    assert d4 >= 1 and sum(doc["d4_failures_by_anchor_kind"].values()) == d4
    a = doc["exploratory_all"]
    assert a["registered"]["clearings"] == sum(bool(r["defective"]) for r in records)
    assert a["creation_only_d4"]["clearings"] <= d4
    assert doc["exploratory"] is True
    assert "p_one_sided_raw" not in doc["exploratory_h2_explicit_only"]
    assert [t["label"] for t in doc["exploratory_materiality"]["thresholds"]] == ["0", "1%", "5%", "10%"]
    x1.run(XES, results, tmp_path / "b.json", **kw)
    assert (tmp_path / "a.json").read_bytes() == (tmp_path / "b.json").read_bytes()
