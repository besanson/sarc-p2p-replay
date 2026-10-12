"""Property tests of the replay engine (prereg/p7-v1.md section 10).

No proposition is claimed. Each property below is checked on generated lines,
not proved. Generation is derandomised, so every run checks the same cases.

P1 Determinism. Replaying the same line twice gives byte-identical evidence
sets and frame results.
PROOF-STATUS: machine-checked (tests/test_properties.py::test_p1_determinism,
400 generated lines, derandomised hypothesis).

P2 Idempotence on identical input. Canonicalising a line twice is the same as
once, and replay leaves its input unchanged.
PROOF-STATUS: machine-checked (tests/test_properties.py::test_p2_idempotence,
400 generated lines, derandomised hypothesis).

P3 Verdict invariance under reordering of events with equal timestamps. (a) A
line built from any permutation of its events replays byte-identically. (b)
Predicates, verdict, outcome and lag computed on a line whose equal-timestamp
events are in an arbitrary order equal those on the canonical line.
PROOF-STATUS: machine-checked (tests/test_properties.py::test_p3_reorder_invariance,
400 generated lines, derandomised hypothesis).

P4 No look-ahead. Adding events after the clearing time changes no predicate
and no verdict of that clearing.
PROOF-STATUS: machine-checked (tests/test_properties.py::test_p4_no_lookahead,
400 generated lines, derandomised hypothesis).

P5 min() contract. A clearing is allowed iff every applicable predicate passes,
and defective iff at least one applicable predicate fails.
PROOF-STATUS: machine-checked (tests/test_properties.py::test_p5_min_contract,
400 generated lines, derandomised hypothesis).
"""

from __future__ import annotations

import os
import random
from datetime import timedelta

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from conftest import BASE, FLAG_TRUE, P2P, THREE_WAY_AFTER, THREE_WAY_BEFORE, TWO_WAY
from p2p_replay import contract, outcome, predicates
from p2p_replay.model import Case, Event
from p2p_replay.replay import replay_case

# 400 cases per property in every ordinary run (the tagged domain). Under mutmut
# (MUTANT_UNDER_TEST set) each mutant runs 60, to keep the gate's wall time bounded.
EXAMPLES = 60 if os.environ.get("MUTANT_UNDER_TEST") else 400
SETTINGS = settings(max_examples=EXAMPLES, derandomize=True, deadline=None,
                    suppress_health_check=[HealthCheck.too_slow])

ACTIVITIES = [
    "Create Purchase Order Item", "Record Goods Receipt", "Cancel Goods Receipt", "Record Invoice Receipt",
    "Cancel Invoice Receipt", "Change Price", "Change Quantity", "Release Purchase Order",
    "Set Payment Block", "Remove Payment Block", "Delete Purchase Order Item", "Block Purchase Order Item",
    "Reactivate Purchase Order Item", "Vendor creates debit memo", "Record Subsequent Invoice", "Clear Invoice",
]
ACTORS = [None, "", "NONE", "user_1", "user_2", "batch_1"]
VALUES = [None, 0.0, 5.0, 12.5]

event_st = st.builds(
    lambda a, d, actor, v: Event(a, BASE + timedelta(days=d), actor, v),
    st.sampled_from(ACTIVITIES), st.integers(0, 40), st.sampled_from(ACTORS), st.sampled_from(VALUES),
)
attrs_st = st.sampled_from([THREE_WAY_AFTER, THREE_WAY_BEFORE, TWO_WAY])


@st.composite
def lines(draw):
    events = draw(st.lists(event_st, min_size=1, max_size=18))
    events.append(Event("Create Purchase Order Item", BASE, draw(st.sampled_from(ACTORS)), 10.0))
    events.append(Event("Clear Invoice", BASE + timedelta(days=draw(st.integers(0, 40))), draw(st.sampled_from(ACTORS)), None))
    attrs = dict(draw(attrs_st), purchase_document="P", company="c", spend_area="s", vendor="v")
    return Case.build("L", attrs, events), events


T_END = BASE + timedelta(days=200)


def outputs(case: Case) -> tuple:
    result = replay_case(case, P2P, FLAG_TRUE, T_END)
    return result.frame.status, tuple(r.to_json() for r in result.records)


def semantics(case: Case, clearing: Event, category) -> tuple:
    values = predicates.evaluate(case, clearing, P2P)
    verdict = contract.decide(values, category)
    later = outcome.first_receipt_after(case, clearing.ts, T_END, P2P)
    return (values, verdict, outcome.corrective_within(case, clearing.ts, 60, P2P), outcome.lag_band(clearing.ts, later))


def tie_shuffled(case: Case, seed: int) -> Case:
    """Same events, ordered by timestamp only, ties in a random order (bypasses canonicalisation)."""
    rng = random.Random(seed)
    keyed = [(e.ts, rng.random(), e) for e in case.events]
    return Case(case.case_id, case.attrs, tuple(e for _, _, e in sorted(keyed, key=lambda k: (k[0], k[1]))))


@SETTINGS
@given(lines())
def test_p1_determinism(drawn):
    case, events = drawn
    assert outputs(case) == outputs(case)
    assert outputs(case) == outputs(Case.build(case.case_id, case.attrs, list(events)))


@SETTINGS
@given(lines())
def test_p2_idempotence(drawn):
    case, _ = drawn
    again = Case.build(case.case_id, case.attrs, case.events)
    assert again == case
    before = (case.events, dict(case.attrs))
    outputs(case)
    assert (case.events, dict(case.attrs)) == before


@SETTINGS
@given(lines(), st.randoms(use_true_random=False), st.integers(0, 2**31))
def test_p3_reorder_invariance(drawn, rnd, seed):
    case, events = drawn
    shuffled = list(events)
    rnd.shuffle(shuffled)
    assert outputs(Case.build(case.case_id, case.attrs, shuffled)) == outputs(case)
    result = replay_case(case, P2P, FLAG_TRUE, T_END)
    if not result.frame.framed:
        return
    odd = tie_shuffled(case, seed)
    for clearing in result.frame.analysed:
        assert semantics(odd, clearing, result.frame.category) == semantics(case, clearing, result.frame.category)


@SETTINGS
@given(lines(), st.lists(event_st, min_size=1, max_size=6))
def test_p4_no_lookahead(drawn, extra):
    case, events = drawn
    result = replay_case(case, P2P, FLAG_TRUE, T_END)
    if not result.frame.framed:
        return
    for clearing in result.frame.analysed:
        later = [Event(e.activity, clearing.ts + timedelta(days=1) + (e.ts - BASE), e.actor, e.value) for e in extra]
        grown = Case.build(case.case_id, case.attrs, list(case.events) + later)
        before = predicates.evaluate(case, clearing, P2P)
        after = predicates.evaluate(grown, clearing, P2P)
        assert before == after
        assert contract.decide(before, result.frame.category) == contract.decide(after, result.frame.category)


@SETTINGS
@given(lines())
def test_p5_min_contract(drawn):
    case, _ = drawn
    result = replay_case(case, P2P, FLAG_TRUE, T_END)
    for record in result.records:
        applicable = [record.predicates[i] for i in record.applicable]
        assert (record.verdict == "allow") == all(v == "pass" for v in applicable)
        assert record.defective == any(v == "fail" for v in applicable)
        assert record.failed == [i for i in record.applicable if record.predicates[i] == "fail"]


@SETTINGS
@given(st.integers(0, 40), st.sampled_from([THREE_WAY_AFTER, THREE_WAY_BEFORE, TWO_WAY]),
       st.lists(event_st, max_size=8))
def test_p5_clean_lines_are_allowed(clear_day, attrs, noise):
    """P5, allow side: a line with every predicate passing is allowed, whatever follows the clearing."""
    t_c = BASE + timedelta(days=clear_day)
    events = [
        Event("Create Purchase Order Item", BASE, "user_1", 10.0),
        Event("Record Goods Receipt", BASE, "user_3", 10.0),
        Event("Record Invoice Receipt", BASE, "user_3", 10.0),
        Event("Clear Invoice", t_c, "user_2", 10.0),
    ] + [Event(e.activity, t_c + timedelta(seconds=1) + (e.ts - BASE), e.actor, e.value)
         for e in noise if e.activity != "Clear Invoice"]
    case = Case.build("L", dict(attrs, purchase_document="P"), events)
    records = replay_case(case, P2P, FLAG_TRUE, T_END).records
    assert len(records) == 1
    assert records[0].verdict == "allow" and not records[0].defective and records[0].failed == []
