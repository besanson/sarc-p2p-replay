"""Round-2 slots (D-D-3): the registered contract through paper 5's sufficiency function, the E4 call
timeline, and the analysed-clearing actors, on the synthetic fixture and on hand-built states."""

from __future__ import annotations

import json
import subprocess
from collections import Counter

import pytest

from conftest import FIXTURES
from experiments import e1, e5, round2_slots
from test_e5 import needs_compiler

XES = FIXTURES / "mini2019.xes"
THREE = "3-way, invoice before receipt"


@pytest.fixture
def e1_dir(tmp_path):
    e0 = tmp_path / "e0-lines.txt"
    e0.write_text("", encoding="utf-8")
    e1.run(XES, tmp_path / "e1", e0, min_month_events=1, b=50)
    return tmp_path / "e1"


def test_registered_fields():
    assert round2_slots.registered_fields("2-way") == ["invoices", "changes", "distinct_actors", "blocks", "closed"]
    assert round2_slots.registered_fields(THREE)[0] == "receipts"
    assert "clearing_ordinal" not in round2_slots.registered_fields(THREE)


@needs_compiler
def test_l2_is_not_sufficient_without_the_clearing_ordinal():
    path, _ = e5.sibling_path()
    e5.import_compiler(path)
    from reduct import sufficiency

    once, twice = e5.State(1, 1, 0, "pass", 0, 0, 1), e5.State(1, 1, 0, "pass", 0, 0, 2)
    changed = e5.State(1, 1, 1, "pass", 0, 0, 1)
    s = round2_slots.sufficiency_category(THREE, Counter({once: 3, twice: 1, changed: 2}), ["D3", "D4"], sufficiency)
    assert s["per_loss"]["L2"]["sufficient"] is False and s["per_loss"]["L2"]["analysed_clearings_with_loss"] == 1
    assert s["per_loss"]["L2"]["counterexample"]["differing_fields"] == ["clearing_ordinal"]
    assert s["sufficient_for"] == ["L1", "L3"] and s["not_sufficient_for"] == ["L2"]
    assert s["all_three_losses"]["sufficient"] is False
    # Only changes separates the L3 state; every other registered field can go: not minimal.
    assert "changes" not in s["fields_droppable_keeping_sufficiency"]
    assert s["minimal_for_the_losses_it_is_sufficient_for"] is False
    assert s["derived_subset_of_registered"] and s["derived_proper_subset_of_registered"]


@needs_compiler
def test_sufficiency_and_actors_on_fixture_double_run(e1_dir, tmp_path):
    e5.run(e1_dir, tmp_path / "e5")
    kw = dict(e1_dir=e1_dir, e5_dir=tmp_path / "e5", e0_path=e1_dir.parent / "e0-lines.txt", min_month_events=1,
              parts=("sufficiency", "actors"))
    docs = round2_slots.run(XES, out=tmp_path / "a", **kw)
    cats = docs["e5/sufficiency.json"]["categories"]
    assert set(cats) == {"2-way", "3-way, invoice after receipt", "3-way, invoice before receipt"}
    for s in cats.values():
        assert s["derived_subset_of_registered"]
        assert sorted(s["sufficient_for"] + s["not_sufficient_for"]) == ["L1", "L2", "L3"]
    a = docs["e1/analysed-clearing-actors.json"]
    assert a["analysed_clearings"] == a["analysed_clearings_in_evidence_set"] == 6
    # One analysed fixture clearing has no earliest-creation actor: D5 is unknown there, and only there.
    assert a["analysed_clearings_earliest_creation_actor_missing"] == a["analysed_clearings_D5_unknown"] == 1
    assert a["analysed_clearings_clearing_actor_missing"] == 0
    round2_slots.run(XES, out=tmp_path / "b", **kw)
    for name in ("e5/sufficiency.json", "e1/analysed-clearing-actors.json"):
        assert (tmp_path / "a" / name).read_bytes() == (tmp_path / "b" / name).read_bytes()


def test_timeline_from_the_committed_logs(tmp_path):
    try:
        round2_slots._commit(round2_slots.ROOT, round2_slots.DECISION_COMMIT)
    except subprocess.CalledProcessError:
        pytest.skip("git history not available")
    doc = round2_slots.timeline_doc(round2_slots.ROOT)
    assert set(doc["calls"]) == {"e4/jev", "e4/haiku", "e4-exploratory/jev", "e4-exploratory/haiku"}
    assert doc["earliest_sent_utc_any_call"] == min(a["earliest_sent_utc"] for a in doc["calls"].values())
    assert all(doc["order"].values())
    committed = round2_slots.ROOT / "results" / "e4" / "timeline.json"
    if committed.exists():
        assert json.loads(committed.read_text(encoding="utf-8")) == doc


def test_unknown_overlap(tmp_path):
    from experiments.common import write_jsonl_gz

    recs = [{"log": "domestic", "predicates": {"D1'": "fail", "D2'": "fail", "D3'": "unknown"}},
            {"log": "domestic", "predicates": {"D1'": "pass", "D2'": "pass", "D3'": "unknown"}},
            {"log": "domestic", "predicates": {"D1'": "pass", "D2'": "pass", "D3'": "pass"}}]
    write_jsonl_gz(tmp_path / "evidence-set.jsonl.gz", recs)
    d = round2_slots.unknown_overlap_doc(tmp_path)["logs"]["domestic"]
    assert d["with_a_predicate_unknown"] == 2 and d["with_a_predicate_unknown_and_another_failing"] == 1
    assert d["every_predicate_passing"] == 1 and d["unknown_per_predicate"]["D3'"] == 2
