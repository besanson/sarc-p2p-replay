"""E4 sample draw and views on the synthetic fixture (no model call)."""

from __future__ import annotations

import json
import re

import pytest

from conftest import FIXTURES
from experiments import common, e1, e4_sample

XES = FIXTURES / "mini2019.xes"


@pytest.fixture
def e1_dir(tmp_path):
    e0 = tmp_path / "e0-lines.txt"
    e0.write_text("", encoding="utf-8")
    e1.run(XES, tmp_path / "e1", e0, min_month_events=1, b=50)
    return tmp_path / "e1"


def test_largest_remainder():
    assert e4_sample.largest_remainder(10, {"a": 1, "b": 1, "c": 1}) == {"a": 4, "b": 3, "c": 3}
    assert e4_sample.largest_remainder(5, {"a": 3, "b": 1}) == {"a": 4, "b": 1}
    assert sum(e4_sample.largest_remainder(1000, {"x": 7, "y": 13, "z": 980}).values()) == 1000
    assert e4_sample.largest_remainder(3, {"a": 0}) == {"a": 0}


def test_draw_respects_quota_documents_and_seed():
    strata = common.Strata([{"case_id": f"l{i}", "line_value": float(i), "category": "2-way",
                             "strata": {"vendor": None, "company": None, "spend_area": None}} for i in range(40)])
    eligible = [{"case_id": f"l{i:02d}", "purchase_document": f"d{i // 2}", "line_value": float(i),
                 "category": "2-way", "strata": {"vendor": None, "company": None, "spend_area": None},
                 "status": "defective" if i % 3 else "clean"} for i in range(40)]
    a, frame = e4_sample.draw(eligible, strata, 7, {"defective": 6, "clean": 4})
    b, _ = e4_sample.draw(list(reversed(eligible)), strata, 7, {"defective": 6, "clean": 4})
    assert a == b and [l["case_id"] for l in a] == sorted(l["case_id"] for l in a)
    assert len({l["purchase_document"] for l in a}) == len(a)
    assert sum(l["status"] == "defective" for l in a) == 6 - frame["defective"]["shortfall"]
    assert frame["clean"]["drawn"] + frame["clean"]["shortfall"] == 4


def test_sample_and_views_on_fixture(e1_dir, tmp_path):
    out = tmp_path / "e4"
    e4_sample.run(XES, e1_dir, out, e0_path=e1_dir.parent / "e0-lines.txt", n_per_group={"defective": 3, "clean": 1})
    sample = json.loads((out / "sample.json").read_text())
    rows = sample["lines"]
    assert sample["drawn"] == {"clean": 1, "defective": 3} and [r["order"] for r in rows] == [1, 2, 3, 4]
    assert all(re.fullmatch(r"[0-9a-f]{16}", r["case_id"]) for r in rows)
    assert {r["human_arm"] for r in rows} <= {"hold", "release", "unclassified"}
    frame = json.loads((out / "sample-frame.json").read_text())
    assert frame["status_at_t_star_amended"]["defective"] == 5 and frame["groups"]["clean"]["eligible_lines"] == 1
    views = [json.loads(l) for l in (out / "views.jsonl").read_text().splitlines()]
    assert [v["order"] for v in views] == [1, 2, 3, 4]
    text = "\n".join(v["view"] for v in views)
    assert "ERP record as of" in text and "{" in text and "{category}" not in text
    for banned in ("user_", "vendor", "P1", "c1", "Clear Invoice"):
        assert banned not in text.replace("vendor name", "")
    timelines = [json.loads(l) for l in (out / "views-timeline.jsonl").read_text().splitlines()]
    assert all(t["label"] == "exploratory" and "Event timeline up to" in t["view"] for t in timelines)
    assert "user_" not in "\n".join(t["view"] for t in timelines)


# DECISIONS.md D-G-3: the timeline view shows the evidence before the decision, not the decision's own clearing.

def _fixture_case(case_id):
    from p2p_replay.config import load_mapping
    from p2p_replay.reader import read_log
    return next(c for c in read_log(XES, load_mapping("bpi2019")) if c.case_id == case_id)


def _rows(view):
    return view.split("\n\n", 1)[1].splitlines()[1:]


def test_timeline_view_drops_the_decisions_own_clearing():
    from p2p_replay.config import W_DAYS, load_patterns
    from p2p_replay.replay import decision_point
    p, _ = load_patterns()
    case = _fixture_case("B_stale_receipt_3way_before")  # t* is its first Clear Invoice
    t_star = decision_point(case, p, W_DAYS)
    assert [e.activity for e in case.upto(t_star)][-1] == "Clear Invoice"
    original = e4_sample.timeline_view(case, t_star, p, with_own_clearing=True)
    corrected = e4_sample.timeline_view(case, t_star, p)
    assert _rows(original)[-1] == "2018-03-10, Clear Invoice, 200.00"
    assert _rows(corrected) == _rows(original)[:-1]
    assert not any("Clear Invoice" in r for r in _rows(corrected))
    assert corrected.split("\n\n", 1)[0] == original.split("\n\n", 1)[0]
    assert "Using only the ERP record below" in corrected.split("\n\n", 1)[0]


def test_timeline_view_keeps_other_events_at_a_clearing_t_star():
    from datetime import datetime, timezone
    from p2p_replay.config import load_patterns
    from p2p_replay.model import Case, Event
    p, _ = load_patterns()
    t = lambda d: datetime(2018, 3, d, 9, tzinfo=timezone.utc)  # noqa: E731
    case = Case.build("x", {}, [Event("Create Purchase Order Item", t(1), None, 10.0),
                                Event("Record Invoice Receipt", t(2), None, 10.0),
                                Event("Clear Invoice", t(5), None, 10.0), Event("Change Price", t(5), None, 10.0)])
    rows = _rows(e4_sample.timeline_view(case, t(5), p))
    assert rows[-1] == "2018-03-05, Change Price, 10.00" and not any("Clear Invoice" in r for r in rows)
    # two indistinguishable clearing records at t*: both are the decision's clearing and both go
    twice = Case.build("z", {}, [*case.events, Event("Clear Invoice", t(5), None, 10.0)])
    rows = _rows(e4_sample.timeline_view(twice, t(5), p))
    assert len(rows) == 3 and not any("Clear Invoice" in r for r in rows)


def test_timeline_view_unchanged_at_receipt_plus_w():
    from datetime import datetime, timezone
    from p2p_replay.config import W_DAYS, load_patterns
    from p2p_replay.model import Case, Event
    from p2p_replay.replay import decision_point
    p, _ = load_patterns()
    d = lambda m, day: datetime(2018, m, day, 9, tzinfo=timezone.utc)  # noqa: E731
    case = Case.build("y", {}, [Event("Create Purchase Order Item", d(1, 1), None, 10.0),
                                Event("Record Goods Receipt", d(1, 5), None, 10.0),
                                Event("Record Invoice Receipt", d(1, 10), None, 10.0),
                                Event("Clear Invoice", d(6, 1), None, 10.0)])
    t_star = decision_point(case, p, W_DAYS)
    assert t_star < d(6, 1)  # receipt + W, before the first clearing
    corrected = e4_sample.timeline_view(case, t_star, p)
    assert corrected == e4_sample.timeline_view(case, t_star, p, with_own_clearing=True)
    assert len(_rows(corrected)) == 3
