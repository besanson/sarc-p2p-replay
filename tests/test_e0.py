"""E0 runner on the synthetic fixture (never the registered log)."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from conftest import FIXTURES
from experiments import e0
from fixtures import make_fixtures

XES = FIXTURES / "mini2019.xes"


def test_raw_inventory_on_fixture():
    inv = e0.apply_t_end(e0.raw_inventory(XES, "Create Purchase Order Item"), XES, min_month_events=1)
    assert inv["t_end_month"] == "2019-06" and inv["dropped_events"] == 0
    assert inv["latest_timestamp"] == inv["t_end"]
    assert inv["traces"] == len(make_fixtures.CASES_2019)
    assert inv["events"] == sum(len(ev) for _, ev in make_fixtures.CASES_2019.values())
    assert inv["t_end"] == datetime(2019, 6, 30, 9, 0, tzinfo=timezone.utc)
    assert inv["trace_keys"]["Item Category"] == len(make_fixtures.CASES_2019)
    assert "nested" not in inv["event_keys"]  # list children are not event attributes
    clears = sum(a == "Clear Invoice" for _, ev in make_fixtures.CASES_2019.values() for a, *_ in ev)
    assert inv["activities"]["Clear Invoice"] == clears == 10
    creates = [ts for _, ev in make_fixtures.CASES_2019.values() for a, ts, *_ in ev if a == "Create Purchase Order Item"]
    assert inv["creation_events"] == len(creates)
    assert inv["creation_events_in_window"] == sum(ts.startswith("2018") for ts in creates)


def test_stop_conditions_logic():
    inv = {"creation_events": 10, "creation_events_in_window": 5,
           "t_end": datetime(2019, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
           "trace_keys": {"concept:name": 1}, "event_keys": {"concept:name": 1}}
    mapping = {"case": {"case_id": "concept:name"}, "event": {"activity": "concept:name"}}
    out = e0.stop_conditions(inv, mapping, undefined=1, lines=100)
    assert not out["any_fires"]
    assert e0.stop_conditions(dict(inv, creation_events_in_window=4), mapping, 1, 100)["checks"]["creation_events_in_window"]["fires"]
    late = dict(inv, t_end=datetime(2020, 1, 1, tzinfo=timezone.utc))
    assert e0.stop_conditions(late, mapping, 1, 100)["checks"]["t_end"]["fires"]
    missing = dict(mapping, event={"activity": "concept:name", "value": "Cumulative net worth (EUR)"})
    check = e0.stop_conditions(inv, missing, 1, 100)["checks"]["mapped_attributes_present"]
    assert check["fires"] and check["missing_event"] == ["Cumulative net worth (EUR)"]
    assert e0.stop_conditions(inv, mapping, 2, 100)["checks"]["undefined_category"]["fires"]


def test_draw_is_seeded_uniform_and_sorted():
    ids = [f"L{i:04d}" for i in range(2000)]
    a = e0.draw_e0(list(reversed(ids)))
    assert a == e0.draw_e0(ids) and len(a) == 500 and a == sorted(a) and len(set(a)) == 500
    assert e0.draw_e0(ids, seed=1) != a
    assert e0.draw_e0(ids[:10]) == ids[:10]


def test_apply_t_end_drops_a_sparse_tail():
    inv = e0.raw_inventory(XES, "Create Purchase Order Item")
    # The fixture's busiest month count is small; with threshold 2, months with one event are a tail.
    full = sorted(m for m, n in inv["months"].items() if n >= 2)
    out = e0.apply_t_end(inv, XES, min_month_events=2)
    assert out["t_end_month"] == full[-1]
    assert out["dropped_events"] == sum(n for m, n in inv["months"].items() if m > full[-1])
    assert out["creation_events"] <= len(inv["creation_times"])
    import pytest
    with pytest.raises(ValueError):
        e0.apply_t_end(inv, XES, min_month_events=10_000)


def test_run_on_fixture(tmp_path):
    report = e0.run(XES, tmp_path, min_month_events=1)
    assert report["frame"]["framed_lines"] == 6
    assert report["frame"]["statuses"]["consignment"] == 1
    assert report["e0"]["size"] == 6 and report["e0"]["analysed_clearings"] == 6 and report["e0"]["errors"] == []
    # 3-way framed lines: A and F pass D1, B and K fail (fixture EXPECTED).
    assert report["e0"]["predicates"]["D1"] == {"fail": 2, "pass": 2}
    assert report["e0"]["predicates"]["D5"]["unknown"] == 1
    assert report["e0"]["outcome_activity_follows_clearing"]["Change Price"] == 1
    assert report["registered_activity_frequencies"]["Vendor creates debit memo"] == 0
    # The fixture omits nothing the mapping names except attributes it does not carry.
    missing = report["stop_conditions"]["checks"]["mapped_attributes_present"]
    assert set(missing["missing_case"]) == {"Item", "Source", "Purch. Doc. Category name", "Document Type",
                                            "Spend classification text", "Sub spend area text"}
    lines = (tmp_path / "e0-lines.txt").read_text().split()
    assert lines == sorted(lines) and len(lines) == 6
    assert json.loads((tmp_path / "e0-report.json").read_text())["t_end"] == "2019-06-30T09:00:00+00:00"
    assert report["registration"].startswith("p7-v1.1")
    assert report["dropped_events_after_t_end"] == 0 and report["t_end_month"] == "2019-06"
    assert e0.main(["--log", str(XES), "--out", str(tmp_path / "again"), "--min-month-events", "1"]) == 3  # fixture lacks mapped attributes
