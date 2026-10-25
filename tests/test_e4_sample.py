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
