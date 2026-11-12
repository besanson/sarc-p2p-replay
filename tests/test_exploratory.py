"""Exploratory analyses (D-G-1) on the synthetic fixture: definitions, partitions, double runs."""

from __future__ import annotations

import json

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


def test_x2_standardisation(results, tmp_path):
    from experiments.exploratory import x2_adjusted_h1_h2 as x2

    # Two strata: the standardised difference weights stratum differences by the comparison distribution.
    rates = {"s1": (2, 1, 8, 2), "s2": (1, 0, 2, 1), "s3": (0, 0, 10, 1)}
    diff, kept, weights = x2.standardise(rates)
    assert kept == ["s1", "s2"] and weights["s3"] == 0.5
    assert diff == pytest.approx(0.8 * (0.5 - 0.25) + 0.2 * (0.0 - 0.5))
    doc = x2.run(results, tmp_path / "a.json", b=B)
    assert set(doc["exploratory_estimates"]) == {"H1", "H2"} and doc["exploratory"] is True
    assert "p_one_sided_raw" not in json.dumps(doc)
    x2.run(results, tmp_path / "b.json", b=B)
    assert (tmp_path / "a.json").read_bytes() == (tmp_path / "b.json").read_bytes()


def test_x3_hold_friction(results, tmp_path):
    from experiments.exploratory import x3_hold_friction as x3

    doc = x3.run(results, tmp_path / "a.json", b=B)
    for w, e in doc["exploratory_overall"].items():
        assert e["with_corrective"] + e["without_corrective"] == e["holds"]
    assert "cost" not in json.dumps(doc["exploratory_overall"])
    x3.run(results, tmp_path / "b.json", b=B)
    assert (tmp_path / "a.json").read_bytes() == (tmp_path / "b.json").read_bytes()


def test_x4_renders_both_views_of_a_synthetic_line(tmp_path):
    from experiments.exploratory import x4_prompt_examples as x4

    doc = x4.run(tmp_path / "a.json", tmp_path / "a.md")
    assert doc["renders"] == {"erp_view": True, "timeline_view": True}
    assert doc["synthetic_line"]["source"] == "tests/fixtures/mini2019.xes"
    erp = doc["views"]["erp_view"]
    assert "ERP record as of" in erp and "{" + "category}" not in erp
    assert doc["requests"]["haiku"]["messages"][0]["content"] == erp
    assert "Reply with only a JSON object" not in doc["requests"]["jev"]["state"]["context"]  # the Jev deviation
    x4.run(tmp_path / "b.json", tmp_path / "b.md")
    assert (tmp_path / "a.json").read_bytes() == (tmp_path / "b.json").read_bytes()
    assert (tmp_path / "a.md").read_bytes() == (tmp_path / "b.md").read_bytes()


def test_x5_audit_counts_the_clearing_at_t_star():
    from experiments.exploratory import x5_timeline_leakage as x5

    head = "Task.\n\nEvent timeline up to 2018-03-10 (date, activity, value in EUR)\n"
    sample = [{"order": 1, "status": "defective", "t_star": "2018-03-10T09:00:00+00:00", "t_star_is_clearing": True},
              {"order": 2, "status": "clean", "t_star": "2018-03-10T09:00:00+00:00", "t_star_is_clearing": False}]
    timeline = {1: {"view": head + "2018-03-01, Create Purchase Order Item, 1.00\n2018-03-10, Clear Invoice, 1.00"},
                2: {"view": head + "2018-03-01, Create Purchase Order Item, 1.00"}}
    corrected = {1: {"view": head + "2018-03-01, Create Purchase Order Item, 1.00"}, 2: timeline[2]}
    erp = {1: {"view": "ERP record"}, 2: {"view": "ERP record"}}
    calls = {f: {1: {"status": "ok", "decision": "hold"}, 2: {"status": "ok", "decision": "clear"}} for f in ("jev", "haiku")}
    doc = x5.analyse(sample, timeline, corrected, erp, calls, {"lines_rerendered": 1, "identical_to_committed": 1})
    assert doc["views_with_the_clearing"] == 1 and doc["views_with_the_clearing_as_last_row"] == 1
    assert doc["erp_view_check"]["unaffected"] and doc["corrected_views_check"]["views_containing_a_clearing"] == 0
    assert doc["committed_exploratory_hold_rates"]["jev"]["views_with_the_clearing"]["defective"]["hold_rate"] == 1.0
    bad = {1: timeline[1], 2: timeline[2]}  # a corrected view that still shows the clearing is refused
    with pytest.raises(RuntimeError):
        x5.analyse(sample, timeline, bad, erp, calls, {"lines_rerendered": 1, "identical_to_committed": 1})
