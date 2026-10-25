"""E4 analysis: TOST, kappa, Holm, and the arm summaries on a synthetic sample and responses."""

from __future__ import annotations

import json
import math

import pytest

from experiments import e4, e4_run


def test_tost_kappa_holm():
    t = e4.tost(50, 100, 50, 100)
    assert t["d"] == 0 and t["p_lower"] == t["p_upper"] == pytest.approx(0.5 * math.erfc((0.05 / math.sqrt(0.005)) / math.sqrt(2)))
    assert t["p_tost"] == max(t["p_lower"], t["p_upper"])
    far = e4.tost(90, 100, 10, 100)
    assert far["d"] == pytest.approx(0.8) and far["p_tost"] > 0.99
    assert e4.tost(0, 0, 1, 2)["p_tost"] is None
    assert e4.tost(0, 10, 0, 10)["p_tost"] == 0.0 and e4.tost(10, 10, 0, 10)["p_tost"] == 1.0
    assert e4.kappa(["hold", "clear"], ["hold", "clear"]) == 1.0
    assert e4.kappa(["hold", "clear"], ["clear", "hold"]) == -1.0
    assert e4.kappa(["hold", "hold"], ["hold", "hold"]) is None and e4.kappa([], []) is None
    rows = {r["test"]: r for r in e4.holm({"a": 0.01, "b": 0.04, "c": 0.03, "d": 1.0, "e": 0.001})}
    assert rows["e"]["p_holm"] == pytest.approx(0.005) and rows["a"]["p_holm"] == pytest.approx(0.04)
    assert rows["c"]["p_holm"] == pytest.approx(0.09) and rows["b"]["p_holm"] == pytest.approx(0.09)
    assert [rows[k]["below_alpha"] for k in "eacbd"] == [True, True, False, False, False]
    assert e4.defect_rate_group(["D1", "D2", "D4"]) == "H1" and e4.defect_rate_group(["D4"]) == "H2"
    assert e4.defect_rate_group(["D6"]) is None


def _root(tmp_path):
    lines = []
    for i in range(8):
        status = "defective" if i < 4 else "clean"
        lines.append({"order": i + 1, "case_id": f"{i:016x}", "status": status,
                      "failed": (["D1", "D2"] if i == 0 else ["D4"] if i < 3 else ["D6"]) if status == "defective" else [],
                      "value_eur": 100.0 * (i + 1), "human_arm": ["hold", "release", "release", "unclassified"][i % 4]})
    (tmp_path / "results" / "e4").mkdir(parents=True)
    (tmp_path / "results" / "e4" / "sample.json").write_text(json.dumps({"lines": lines}))
    (tmp_path / "results" / "e2").mkdir(parents=True)
    hyp = {"estimates": {"H1": {"W60": {"defect_group": {"O_rate": 0.5}, "p_one_sided_raw": 0.001}},
                         "H2": {"W60": {"defect_group": {"O_rate": 0.1}, "p_one_sided_raw": 0.02}}},
           "holm": {"applied": False}}
    (tmp_path / "results" / "e2" / "hypotheses.json").write_text(json.dumps(hyp))
    decisions = {"jev": ["hold", "clear", "clear", "hold", "clear", "clear", "hold", "clear"],
                 "haiku": ["hold", "hold", "hold", None, "clear", "clear", "clear", "clear"]}
    for family, decs in decisions.items():
        log = e4_run.Log(tmp_path / "responses" / "e4" / family / "responses.jsonl")
        for i, d in enumerate(decs):
            log.append({"kind": "attempt", "order": i + 1, "charged_usd": 0.001})
            log.append({"kind": "call", "order": i + 1, "status": "ok" if d else "invalid", "decision": d,
                        "p_hold": 0.5 if d else None, "returned_model": "m"})
        log.append({"kind": "run_event", "status": "COMPLETE"})
    return tmp_path


def test_analysis_and_holm_written(tmp_path):
    root = _root(tmp_path)
    result = e4.run("e4", root)
    arms = json.loads((root / "results" / "e4" / "arms.json").read_text())["arms"]
    assert arms["gate"]["hold_rate_defective"] == 1.0 and arms["gate"]["hold_rate_clean"] == 0.0
    assert arms["jev"]["defective"] == {"lines": 4, "held": 2} and arms["jev"]["clean"] == {"lines": 4, "held": 1}
    # jev releases defective lines 2 and 3 (D4): value 200 + 300, expected 2 x 0.1
    assert arms["jev"]["value_released_on_defective_lines_eur"] == 500.0
    assert arms["jev"]["expected_correctives"] == pytest.approx(0.2)
    assert arms["haiku"]["invalid"] == 1 and arms["haiku"]["defective"] == {"lines": 3, "held": 3}
    assert arms["haiku"]["kappa_with_gate"] == 1.0 and arms["haiku"]["cost_usd_per_decision"] == pytest.approx(0.001)
    # people: line 1 held, lines 2 and 3 released, line 4 unclassified
    assert arms["people"]["defective"] == {"lines": 3, "held": 1} and arms["people"]["unclassified"] == 2
    assert arms["people"]["value_released_on_defective_lines_eur"] == 500.0
    h4 = json.loads((root / "results" / "e4" / "h4.json").read_text())
    assert h4["families"]["H4-Jev"]["d"] == pytest.approx(0.25)
    hyp = json.loads((root / "results" / "e2" / "hypotheses.json").read_text())
    assert hyp["holm"]["applied"] is True and {r["test"] for r in hyp["holm"]["table"]} == {"H1", "H2", "H3", "H4-Jev", "H4-Haiku"}
    assert next(r for r in hyp["holm"]["table"] if r["test"] == "H3")["p_raw"] == 1.0
    assert "supported" not in json.dumps(hyp).lower()
    before = {p.name: p.read_bytes() for p in (root / "results" / "e4").iterdir()}
    e4.run("e4", root)
    assert before == {p.name: p.read_bytes() for p in (root / "results" / "e4").iterdir()}
    assert result["holm"]["table"][0]["test"] == "H1"
