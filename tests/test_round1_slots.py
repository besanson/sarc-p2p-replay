"""Round-1 slots (D-D-2) on the synthetic fixture: hold composition, actors, classified-lines arms."""

from __future__ import annotations

import json

import pytest

from conftest import FIXTURES
from experiments import e1, round1_slots
from test_e4 import _root as e4_root

XES = FIXTURES / "mini2019.xes"


@pytest.fixture
def e1_dir(tmp_path):
    e0 = tmp_path / "e0-lines.txt"
    e0.write_text("", encoding="utf-8")
    e1.run(XES, tmp_path / "e1", e0, min_month_events=1, b=50)
    return tmp_path / "e1"


def test_composition_and_actors_on_fixture(e1_dir, tmp_path):
    docs = round1_slots.run(XES, e1_dir=e1_dir, e0_path=e1_dir.parent / "e0-lines.txt", out=tmp_path / "a",
                            min_month_events=1, with_arms=False)
    comp = docs["e3/human-hold-composition.json"]
    # Fixture line F has a payment block before its clearing and is the one line held by people.
    assert comp["held_by_people"] == 1 and comp["by_reason"]["payment_block_before_first_clearing"] == 1
    lit = comp["by_status"]["registered_literal_reading"]
    assert sum(v["held_by_people"] for v in lit.values()) == 1
    actors = docs["e1/actors.json"]["scopes"]
    # Line C is created and cleared by user_003: the intersection is not empty on the fixture.
    assert actors["framed"]["intersection"] == 1 and actors["all"]["distinct_clear_invoice_actors_batch"] == 0
    assert sum(actors["all"]["clear_invoice_events"].values()) == 10
    round1_slots.run(XES, e1_dir=e1_dir, e0_path=e1_dir.parent / "e0-lines.txt", out=tmp_path / "b",
                     min_month_events=1, with_arms=False)
    for name in ("e3/human-hold-composition.json", "e1/actors.json"):
        assert (tmp_path / "a" / name).read_bytes() == (tmp_path / "b" / name).read_bytes()


def test_hold_reason_rule():
    from datetime import datetime, timezone
    from conftest import P2P, ev, make_case

    t_end = datetime(2019, 1, 1, tzinfo=timezone.utc)
    block = make_case([ev("Create Purchase Order Item", 0), ev("Record Invoice Receipt", 1),
                       ev("Set Payment Block", 2), ev("Clear Invoice", 5)])
    late = make_case([ev("Create Purchase Order Item", 0), ev("Record Invoice Receipt", 1), ev("Clear Invoice", 80)])
    both = make_case([ev("Create Purchase Order Item", 0), ev("Record Invoice Receipt", 1), ev("Set Payment Block", 2)])
    released = make_case([ev("Create Purchase Order Item", 0), ev("Record Invoice Receipt", 1), ev("Clear Invoice", 5)])
    assert round1_slots.hold_reason(block, P2P, t_end) == "payment_block_before_first_clearing"
    assert round1_slots.hold_reason(late, P2P, t_end) == "no_clearing_within_W_of_first_invoice"
    assert round1_slots.hold_reason(both, P2P, t_end) == "both"
    assert round1_slots.hold_reason(released, P2P, t_end) is None


def test_arms_on_classified_lines(tmp_path):
    root = e4_root(tmp_path)
    doc = round1_slots.arms_classified(root)
    # The synthetic sample has two unclassified lines (orders 4 and 8).
    assert doc["sample_lines"] == 8 and doc["classified_lines"] == 6 and doc["unclassified_lines"] == 2
    assert doc["arms"]["jev"]["defective"]["lines"] == 3 and doc["arms"]["gate"]["clean"]["lines"] == 3
    assert json.dumps(doc)
