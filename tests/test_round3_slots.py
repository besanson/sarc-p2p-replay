"""Round-3 slot (D-D-4): per-predicate unknown counts from the evidence set."""

from __future__ import annotations

from experiments import round3_slots
from experiments.common import write_jsonl_gz


def test_predicate_unknowns(tmp_path):
    pred = {d: "pass" for d in round3_slots.PREDICATES}
    recs = [{"applicable": list(round3_slots.PREDICATES), "predicates": {**pred, "D5": "unknown"}},
            {"applicable": ["D3", "D4", "D5", "D6", "D7"], "predicates": {**pred, "D1": "fail", "D2": "fail"}},
            {"applicable": list(round3_slots.PREDICATES), "predicates": {**pred, "D4": "fail"}}]
    write_jsonl_gz(tmp_path / "evidence-set.jsonl.gz", recs)
    a = round3_slots.run(e1_dir=tmp_path, out=tmp_path / "a")["e1/predicate-unknowns.json"]
    p = a["predicates"]
    assert a["analysed_clearings"] == 3
    assert p["D5"]["analysed_clearings"]["unknown"] == 1 and p["D5"]["applicable_clearings"]["unknown"] == 1
    # A predicate outside the contract is counted over all clearings but not over the applicable ones.
    assert p["D1"]["analysed_clearings"]["fail"] == 1 and p["D1"]["applicable_clearings"] == {
        "total": 2, "pass": 2, "fail": 0, "unknown": 0}
    round3_slots.run(e1_dir=tmp_path, out=tmp_path / "b")
    name = "e1/predicate-unknowns.json"
    assert (tmp_path / "a" / name).read_bytes() == (tmp_path / "b" / name).read_bytes()
