"""E5 with paper 5's compiler (sibling at its pin) on the E1 evidence set of the synthetic fixture."""

from __future__ import annotations

import json

import pytest

from conftest import FIXTURES
from experiments import e1, e5


def _compiler_unavailable() -> str | None:
    """Why paper 5's compiler cannot run here, or None. A fresh clone without siblings skips."""
    try:
        e5.sibling_path()
    except Exception as exc:  # noqa: BLE001 - absent checkout, off its pin, or no git
        return f"{e5.SIBLING} not available at its engines.lock pin ({type(exc).__name__})"
    try:
        import pysat  # noqa: F401
    except ImportError:
        return "python-sat (paper 5's dependency) not installed"
    return None


needs_compiler = pytest.mark.skipif(_compiler_unavailable() is not None, reason=str(_compiler_unavailable()))


@pytest.fixture
def e1_dir(tmp_path):
    e0 = tmp_path / "e0-lines.txt"
    e0.write_text("", encoding="utf-8")
    e1.run(FIXTURES / "mini2019.xes", tmp_path / "e1", e0, min_month_events=1, b=50)
    return tmp_path / "e1"


def test_losses_and_states():
    s = e5.State(0, 1, 2, "pass", 0, 0, 2)
    three, two = e5.loss_model("3-way, invoice after receipt"), e5.loss_model("2-way")
    assert three["L1"](s) and not two["L1"](s)          # no receipt: a loss only where receipt is required
    assert three["L2"](s) and three["L3"](s)            # second clearing on one invoice; changed after approval
    assert not three["L2"](e5.State(1, 2, 0, "pass", 0, 0, 2))
    assert e5.predicates_of(["receipts", "clearing_ordinal"]) == ["D1", "D2"]


@needs_compiler
def test_e5_on_fixture_and_double_run(e1_dir, tmp_path):
    doc = e5.run(e1_dir, tmp_path / "a")
    cats = doc["categories"]
    assert set(cats) == {"2-way", "3-way, invoice after receipt", "3-way, invoice before receipt"}
    assert doc["compiler"]["modified"] is False and len(doc["compiler"]["commit"]) == 40
    for name, s in cats.items():
        assert s["registered_contract"] == list(e5.REGISTERED_CONTRACT[name])
        assert s["result"] in ("reproduces", "does not reproduce")
        assert s["equal"] == (s["derived_contract"] == s["registered_contract"])
        trace = json.loads((tmp_path / "a" / f"trace-{e5.slug(name)}.json").read_text())
        assert trace["minimum_cardinality_reduct"] == s["minimum_cardinality_field_set"]
        assert sum(st["clearings"] for st in trace["states"]) == s["analysed_clearings"]
    # Fixture: C (2-way, L3) differs from L (no loss) on changes, D5 and the closed balance, so
    # with two states each of the three alone separates them: three single-field reducts.
    assert cats["2-way"]["clearings_per_loss"]["L3"] == 1
    assert cats["2-way"]["minimal_reducts"] == [["changes"], ["closed"], ["distinct_actors"]]
    assert cats["2-way"]["contracts_of_minimal_reducts"] == [["D4"], ["D7"], ["D5"]]
    # K (3-way after receipt) has no receipt at clearing -> L1 -> receipts in the field set.
    assert "receipts" in cats["3-way, invoice after receipt"]["minimum_cardinality_field_set"]
    assert all(s["result"] == "does not reproduce" for s in cats.values())  # no loss reads D5, D6 or D7
    e5.run(e1_dir, tmp_path / "b")
    for f in sorted((tmp_path / "a").iterdir()):
        assert f.read_bytes() == (tmp_path / "b" / f.name).read_bytes(), f.name
