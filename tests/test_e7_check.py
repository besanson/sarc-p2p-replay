"""E7 vocabulary check on the synthetic BPI 2020 fixture (never the registered logs)."""

from __future__ import annotations

import hashlib
import json
import shutil

from conftest import FIXTURES
from experiments import e7_check
from fixtures import make_fixtures


def _data(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    lock = {}
    for name, key in e7_check.LOGS.items():
        f = data / f"{name}.xes"
        shutil.copyfile(FIXTURES / "mini2020.xes", f)
        lock[key] = {"file": f.name, "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
    return data, lock


def test_vocabulary_on_fixture(tmp_path):
    data, lock = _data(tmp_path)
    doc = e7_check.run(tmp_path / "out", data=data, lock=lock)
    assert doc["stop"] is False
    log = doc["logs"]["international"]
    assert log["traces"] == len(make_fixtures.CASES_2020)
    pays = sum(a == "Payment Handled" for ev in make_fixtures.CASES_2020.values() for a, _ in ev)
    assert doc["registered_lists"]["payment"]["Payment Handled"]["international"] == pays
    # A registered name the fixture never uses is reported with zero counts, not dropped.
    assert doc["registered_lists"]["outcome_prime"]["Declaration REJECTED by MISSING"] == {"international": 0, "domestic": 0}
    assert "Declaration REJECTED by MISSING" in doc["registered_names_absent_from_both_logs"]
    assert json.loads((tmp_path / "out" / "vocabulary.json").read_text())["stop"] is False


def test_bad_hash_stops(tmp_path):
    data, lock = _data(tmp_path)
    lock["bpi2020_domestic"]["sha256"] = "0" * 64
    try:
        e7_check.run(tmp_path / "out", data=data, lock=lock)
    except RuntimeError as exc:
        assert "SHA-256" in str(exc)
    else:
        raise AssertionError("a hash mismatch must stop")
