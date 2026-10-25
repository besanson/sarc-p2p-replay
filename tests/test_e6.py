"""E6 timing runner and the double-run comparison on the synthetic fixture."""

from __future__ import annotations

import json

from conftest import FIXTURES
from experiments import e6, repro


def test_e6_timing_on_fixture(tmp_path):
    e0 = tmp_path / "e0-lines.txt"
    e0.write_text("", encoding="utf-8")
    report = e6.run(FIXTURES / "mini2019.xes", tmp_path / "e6", tmp_path / "work", runs=3, e0_path=e0,
                    min_month_events=1, b=50)
    written = json.loads((tmp_path / "e6" / "timing-e1.json").read_text())
    assert written == json.loads(json.dumps(report))
    assert len(report["runs"]) == 3 and report["analysed_clearings"] == 6
    assert report["median_replay_seconds"] == sorted(r["replay_seconds"] for r in report["runs"])[1]
    assert report["outputs_byte_identical_across_runs"] is True
    assert report["cost_usd_per_decision"] is None and report["hardware"]["cpu_cores"] >= 1


def test_double_run_is_byte_identical_on_fixture(tmp_path):
    e0 = tmp_path / "e0-lines.txt"
    e0.write_text("", encoding="utf-8")
    out = repro.run(FIXTURES / "mini2019.xes", tmp_path / "a", tmp_path / "b", tmp_path / "repro.json",
                    e0_path=e0, min_month_events=1, b=50)
    assert out["all_identical"] is True and out["files_compared"] == 10 + 2 + 5
    assert {f["file"].split("/")[0] for f in out["files"]} == {"e1", "e2", "e3"}
    (tmp_path / "b" / "e2" / "hypotheses.json").write_text("{}\n")
    assert not all(f["identical"] for f in repro.compare(tmp_path / "a", tmp_path / "b"))
