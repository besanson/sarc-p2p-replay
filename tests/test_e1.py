"""E1 runner and the shared analysis pieces on the synthetic fixture (never the registered log)."""

from __future__ import annotations

import json
import re

import numpy as np
import pytest

from conftest import FIXTURES
from experiments import common, e1
from fixtures import make_fixtures

XES = FIXTURES / "mini2019.xes"
B = 200


def _run(tmp_path, e0=()):
    tmp_path.mkdir(parents=True, exist_ok=True)
    e0_path = tmp_path / "e0-lines.txt"
    e0_path.write_text("".join(f"{c}\n" for c in e0), encoding="utf-8")
    return e1.run(XES, tmp_path / "e1", e0_path, min_month_events=1, b=B)


def test_e1_slots_on_fixture(tmp_path):
    _run(tmp_path)
    out = tmp_path / "e1"
    exclusions = json.loads((out / "exclusions.json").read_text())
    statuses = {row["status"]: row["lines"] for row in exclusions["exclusions_in_registered_order"]}
    expected = {s: sum(1 for st, _ in make_fixtures.EXPECTED.values() if st == s) for s in e1.REGISTERED_STEP}
    assert statuses == {s: n for s, n in expected.items() if s != "framed"}
    assert [r["status"] for r in exclusions["exclusions_in_registered_order"]] == list(e1.REGISTERED_STEP)[:-1]
    assert exclusions["framed_lines"] == expected["framed"] == 6 and exclusions["analysed_clearings"] == 6
    assert exclusions["t_end"] == "2019-06-30T09:00:00+00:00" and exclusions["events_after_t_end_excluded"] == 0

    exposure = json.loads((out / "exposure.json").read_text())
    counts = {k: v["clearings"] for k, v in exposure["classes"].items()}
    # B stale, K absent, C D4 and D5, F D6 (D5 unknown), L D7; A clean (fixture EXPECTED)
    assert counts == {"D1 class (absent receipt)": 1, "D2 class (stale receipt)": 1, "D3": 0, "D4": 1,
                      "D5": 1, "D6": 1, "D7": 1, "at least one defect": 5}
    assert exposure["held unknown"]["clearings"] == 0
    assert exposure["applicable_clearings"]["D1 class (absent receipt)"] == 4
    anyd = exposure["classes"]["at least one defect"]
    assert anyd["share_of_clearings"] == 5 / 6 and anyd["wilson95"] == common.wilson(5, 6)
    assert anyd["share_of_value"] == pytest.approx((200 + 55 + 10 + 30 + 80) / (100 + 200 + 55 + 10 + 30 + 80), abs=0.2)
    lo, hi = anyd["bootstrap95"]
    assert 0 <= lo <= hi <= 1 and exposure["bootstrap"]["B"] == B and exposure["bootstrap"]["clusters"] == 6

    strata = json.loads((out / "exposure-by-stratum.json").read_text())["strata"]
    assert set(strata) == set(common.STRATA)
    assert sum(c["analysed_clearings"] for c in strata["category"].values()) == 6
    assert strata["category"]["2-way"]["analysed_clearings"] == 2

    assert json.loads((out / "value-fallback.json").read_text())["analysed_clearings"] == 6
    cross = json.loads((out / "category-crosscheck.json").read_text())
    assert cross["framed_lines"] == 6 and cross["framed_lines_disagreeing"] == 0
    coverage = json.loads((out / "coverage-check.json").read_text())
    fired = {r["predicate"]: r["fired"] for r in coverage["rows"]}
    assert fired == {"D1": True, "D2": True, "D3": False, "D4": True, "D5": True, "D6": True, "D7": True}
    assert coverage["every_detected_row_fired"] is False

    records = common.read_jsonl_gz(out / "evidence-set.jsonl.gz")
    assert len(records) == 6 and all(re.fullmatch(r"[0-9a-f]{16}", r["case_id"]) for r in records)
    assert all(r["strata"]["vendor"] is None or re.fullmatch(r"[0-9a-f]{16}", r["strata"]["vendor"]) for r in records)
    sample = (out / "evidence-sample.jsonl").read_text().splitlines()
    assert len(sample) == 6
    lines = common.read_jsonl_gz(out / "lines.jsonl.gz")
    assert len(lines) == 6 and {l["t_star_status"] for l in lines} == {"clean", "defective"}


def test_e1_is_byte_identical_and_removes_e0_lines(tmp_path):
    _run(tmp_path / "a")
    _run(tmp_path / "b")
    for f in sorted((tmp_path / "a" / "e1").iterdir()):
        assert f.read_bytes() == (tmp_path / "b" / "e1" / f.name).read_bytes(), f.name
    _run(tmp_path / "c", e0=["A_clean_3way_after"])
    ex = json.loads((tmp_path / "c" / "e1" / "exclusions.json").read_text())
    assert ex["e0_lines_removed"] == 1 and ex["framed_lines_after_e0_removal"] == 5 and ex["analysed_clearings"] == 5
    with pytest.raises(RuntimeError):
        _run(tmp_path / "d", e0=["D_consignment"])  # an E0 line must be a framed line


def test_wilson_cents_and_quartiles():
    assert common.wilson(0, 10)[0] == 0.0 and common.wilson(10, 10)[1] == 1.0 and common.wilson(0, 0) is None
    lo, hi = common.wilson(5, 6)
    assert lo < 5 / 6 < hi
    assert common.cents(298.0) == 29800 and common.cents(2.6787987e7) == 2678798700
    with pytest.raises(ValueError):
        common.cents(1.005)
    cut = common.quartile_cutpoints([1, 2, 3, 4, 5, 6, 7, 8])
    assert [common.quartile_of(v, cut) for v in (1, 2.75, 3, 5, 8)] == ["Q1", "Q1", "Q2", "Q3", "Q4"]
    assert common.quartile_of(None, cut) == common.MISSING
    assert common.one_sided_p(0.0) == 0.5 and common.one_sided_p(1.959963984540054) == pytest.approx(0.025)


def test_cluster_bootstrap_is_seeded_exact_and_clustered():
    clusters = ["d2", "d1", "d1", "d3"]
    boot = common.ClusterBootstrap(clusters, b=50)
    assert boot.clusters == ["d1", "d2", "d3"]
    cols = [np.ones(4), np.array([1.0, 0.0, 1.0, 0.0])]
    a, b = boot.totals(cols), boot.totals(cols)
    assert (a == b).all() and a.shape == (50, 2)
    # every resample draws three clusters; d1 carries two records
    assert set(a[:, 0]) <= {3.0, 4.0, 5.0, 6.0} and (a[:, 1] <= a[:, 0]).all()
    rng = np.random.Generator(np.random.PCG64(20261201))
    first = np.bincount(rng.integers(0, 3, size=3), minlength=3)
    assert a[0, 0] == first @ np.array([2.0, 1.0, 1.0])
    assert common.percentile95(np.zeros(3), np.zeros(3)) == {"interval": None, "resamples_used": 0}
