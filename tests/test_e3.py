"""E3 runner on the E1 evidence set of the synthetic fixture."""

from __future__ import annotations

import json

import pytest

from conftest import FIXTURES
from experiments import common, e1, e3

B = 200


@pytest.fixture
def e1_dir(tmp_path):
    e0 = tmp_path / "e0-lines.txt"
    e0.write_text("", encoding="utf-8")
    e1.run(FIXTURES / "mini2019.xes", tmp_path / "e1", e0, min_month_events=1, b=B)
    return tmp_path / "e1"


def test_e3_slots_on_fixture(e1_dir, tmp_path):
    e3.run(e1_dir, tmp_path / "e3", b=B)
    out = tmp_path / "e3"
    held = json.loads((out / "gate-held.json").read_text())
    assert held["held"]["clearings"] == 5 and held["analysed_clearings"] == 6
    assert held["held"]["wilson95"] == common.wilson(5, 6) and held["held_unknown_only"] == 0
    table = json.loads((out / "verdict-by-outcome.json").read_text())["table"]
    # Only B (held: D1/D2) has a corrective, a Change Price 10 days after clearing.
    assert {k: v["clearings"] for k, v in table["W60"].items()} == {
        "hold_with_corrective": 1, "hold_without_corrective": 4,
        "allow_with_corrective": 0, "allow_without_corrective": 1}
    assert table["W60"]["hold_with_corrective"]["cleared_value_eur"] == 200.0
    assert table["W30"] == table["W60"]
    lag = json.loads((out / "lag-bands.json").read_text())
    assert lag["clearings"] == 2 and lag["bands"]["1-7"]["clearings"] == 1 and lag["bands"]["never"]["clearings"] == 1
    assert lag["receipt_class"] == {"stale receipt": 1, "absent receipt": 1}
    hh = json.loads((out / "human-hold.json").read_text())
    assert hh["framed_lines"] == 6
    assert hh["held_by_people"] + hh["released_by_people"] + hh["unclassified_no_invoice_receipt_by_t_end_minus_w"] == 6
    rates = hh["by_gate_status_at_t_star"]
    assert rates["clean"]["classified_lines"] + rates["defective"]["classified_lines"] + \
        rates["held_unknown"]["classified_lines"] == hh["held_by_people"] + hh["released_by_people"]
    conf = json.loads((out / "confounders.json").read_text())
    assert sum(v["held"] for v in conf["clearings"]["category"].values()) == 5
    assert set(conf["human_hold_lines"]) == set(common.STRATA)
