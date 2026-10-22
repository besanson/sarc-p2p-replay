"""E2 runner on the E1 evidence set of the synthetic fixture."""

from __future__ import annotations

import json

import pytest

from conftest import FIXTURES
from experiments import e1, e2

B = 200


@pytest.fixture
def e1_dir(tmp_path):
    e0 = tmp_path / "e0-lines.txt"
    e0.write_text("", encoding="utf-8")
    e1.run(FIXTURES / "mini2019.xes", tmp_path / "e1", e0, min_month_events=1, b=B)
    return tmp_path / "e1"


def test_e2_slots_on_fixture(e1_dir, tmp_path):
    e2.run(e1_dir, tmp_path / "e2", b=B)
    text = (tmp_path / "e2" / "hypotheses.json").read_text()
    hyp = json.loads(text)
    est = hyp["estimates"]
    # H1: B (O within 60 days) and K (none) against A (none) -> 1/2 - 0/1
    assert est["H1"]["W60"]["defect_group"] == {"clearings": 2, "with_O": 1, "O_rate": 0.5}
    assert est["H1"]["W60"]["comparison_group"]["clearings"] == 1 and est["H1"]["W60"]["difference"] == 0.5
    # H2: C fails D4 (no O); A, B, F, K, L pass (B has O) -> 0 - 1/5
    assert est["H2"]["W60"]["difference"] == pytest.approx(-0.2)
    # H3: C fails D5; F is unknown and excluded; A, B, K, L pass -> 0 - 1/4
    assert est["H3"]["W60"]["difference"] == pytest.approx(-0.25) and est["H3"]["excluded"]["clearings"] == 1
    assert est["H2"]["excluded"]["clearings"] == 0
    for name in ("H1", "H2", "H3"):
        w60 = est[name]["W60"]
        assert {"bootstrap_se", "z", "p_one_sided_raw"} <= set(w60) and 0 <= w60["p_one_sided_raw"] <= 1
        assert "p_one_sided_raw" not in est[name]["W30"]
    assert "p_one_sided_raw" not in est["H1 all-category comparison"]["W60"]
    assert est["H1 all-category comparison"]["W60"]["comparison_group"]["clearings"] == 1
    assert hyp["holm"]["applied"] is False and hyp["holm"]["family"][-2:] == ["H4-Jev", "H4-Haiku"]
    assert "supported" not in text.lower()
    conf = json.loads((tmp_path / "e2" / "confounders.json").read_text())["comparisons"]
    assert set(conf) == set(e2.COMPARISONS)
    by_cat = conf["H1"]["category"]
    assert sum(v["W60"]["defect_clearings"] for v in by_cat.values()) == 2


def test_empty_group_is_reported_not_computable():
    import numpy as np
    columns = [np.zeros(3), np.zeros(3), np.ones(3), np.array([1.0, 0.0, 0.0])]
    reps = np.tile([0.0, 0.0, 3.0, 1.0], (10, 1))
    est = e2.estimate(columns, reps, ["n_d", "o_d", "n_c", "o_c"].index, with_p=True)
    assert est["difference"] is None and est["bootstrap_se"] is None and "p_one_sided_raw" not in est
    assert est["not_computable"] == "defect group has no analysed clearings"
