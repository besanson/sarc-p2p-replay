"""E7 replication runner on the synthetic BPI 2020 fixture (tests/fixtures/mini2020.xes)."""

from __future__ import annotations

import hashlib
import json
import re
import shutil

from conftest import FIXTURES
from experiments import common, e7, e7_check


def _data(tmp_path):
    data = tmp_path / "data"
    data.mkdir(exist_ok=True)
    lock = {}
    for name, key in e7_check.LOGS.items():
        f = data / f"{name}.xes"
        shutil.copyfile(FIXTURES / "mini2020.xes", f)
        lock[key] = {"file": f.name, "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
    return data, lock


def test_e7_on_fixture_and_double_run(tmp_path):
    data, lock = _data(tmp_path)
    docs = e7.run(tmp_path / "a", data=data, b=200, lock=lock)
    units = docs["units.json"]["logs"]
    # decl_late_payment pays after T_end' - W and is excluded; the other three payments are units.
    assert units["international"]["units"] == 3 and units["international"]["excluded_payments_after_t_end_prime_minus_w"] == 1
    assert units["pooled"]["units"] == 6 and units["pooled"]["cases_with_units"] == 6  # same case ids, two logs
    counts = docs["predicates.json"]["counts"]["international"]
    assert counts["D1'"] == {"pass": 2, "fail": 1, "unknown": 0}          # decl_unapproved
    assert counts["D3'"] == {"pass": 1, "fail": 1, "unknown": 1}          # resubmitted after approval; no approval
    comp = docs["comparisons.json"]["scopes"]["international"]
    # decl_wrong_role_resubmitted fails D2' and D3' and is rejected 12 days after payment; decl_ok passes all.
    assert comp["D2'"]["defect_group"]["with_O_prime"] == 1 and comp["D2'"]["all_pass_group"]["payments"] == 1
    assert comp["D3'"]["difference"] == 1.0 and comp["D3'"]["bootstrap95"] is not None
    assert docs["exposure.json"]["scopes"]["international"]["with_a_failed_predicate"] == 2
    assert "p_value" not in json.dumps(docs["comparisons.json"]) and "Holm" in docs["comparisons.json"]["status"]
    recs = common.read_jsonl_gz(tmp_path / "a" / "evidence-set.jsonl.gz")
    assert len(recs) == 6 and all(re.fullmatch(r"[0-9a-f]{16}", r["case_id"]) for r in recs)
    e7.run(tmp_path / "b", data=data, b=200, lock=lock)
    for f in sorted((tmp_path / "a").iterdir()):
        assert f.read_bytes() == (tmp_path / "b" / f.name).read_bytes(), f.name
