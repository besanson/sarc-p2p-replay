"""Unit tests of the replay engine, one block per module, on hand-built cases."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from conftest import BASE, FLAG_TRUE, P2P, THREE_WAY_BEFORE, TWO_WAY, at, ev, make_case
from p2p_replay import category as cat
from p2p_replay import contract, frame, outcome, predicates
from p2p_replay.category import Category
from p2p_replay.model import Case, Event, count, parse_timestamp
from p2p_replay.predicates import Value

CREATE, GR, CGR, RIR, CLEAR = (
    "Create Purchase Order Item", "Record Goods Receipt", "Cancel Goods Receipt",
    "Record Invoice Receipt", "Clear Invoice",
)


def clearing_at(days, actor="user_2"):
    return ev(CLEAR, days, actor)


def values_for(events, clear):
    case = make_case(events + [clear])
    return predicates.evaluate(case, clear, P2P)


# ---- model ------------------------------------------------------------------

def test_parse_timestamp_normalises_to_utc():
    assert parse_timestamp("2018-01-01T01:00:00+01:00") == datetime(2018, 1, 1, tzinfo=timezone.utc)
    assert parse_timestamp("2018-01-01T00:00:00Z") == datetime(2018, 1, 1, tzinfo=timezone.utc)
    assert parse_timestamp(" 2018-01-01T00:00:00 ").tzinfo == timezone.utc


def test_case_build_sorts_canonically_and_upto_is_inclusive():
    c = make_case([ev("b", 1), ev("a", 1), ev("z", 0)])
    assert [e.activity for e in c.events] == ["z", "a", "b"]
    assert [e.activity for e in c.upto(at(0))] == ["z"]
    assert len(c.upto(at(1))) == 3
    assert [e.activity for e in c.of("a")] == ["a"]
    assert count(c.events, {"a", "b"}) == 2


def test_event_sort_key_orders_none_value_last_and_none_actor_first():
    e1 = Event("x", BASE, None, 1.0)
    e2 = Event("x", BASE, "a", 1.0)
    e3 = Event("x", BASE, "a", None)
    e4 = Event("x", BASE, "a", 2.0)
    assert sorted([e3, e4, e2, e1], key=Event.sort_key) == [e1, e2, e4, e3]
    assert e3.to_dict() == {"activity": "x", "ts": BASE.isoformat(), "actor": "a", "value": None}


# ---- category ---------------------------------------------------------------

@pytest.mark.parametrize("attrs,expected", [
    ({"gr_based_iv": "true", "goods_receipt_required": "true"}, Category.THREE_WAY_AFTER),
    ({"gr_based_iv": "false", "goods_receipt_required": "true"}, Category.THREE_WAY_BEFORE),
    ({"gr_based_iv": "false", "goods_receipt_required": "false"}, Category.TWO_WAY),
    ({"gr_based_iv": "true", "goods_receipt_required": "false"}, Category.UNDEFINED),
    ({"gr_based_iv": None, "goods_receipt_required": "true"}, Category.UNDEFINED),
    ({"gr_based_iv": "maybe", "goods_receipt_required": "false"}, Category.UNDEFINED),
    ({"gr_based_iv": "true", "goods_receipt_required": "true", "item_type": "Consignment"}, Category.CONSIGNMENT),
    ({"gr_based_iv": "false", "goods_receipt_required": "true", "item_category": "consignment"}, Category.CONSIGNMENT),
])
def test_category_from_flags(attrs, expected):
    case = Case.build("x", attrs, [])
    assert cat.category_of(case, FLAG_TRUE) is expected


def test_parse_flag_and_requires_receipt():
    assert cat.parse_flag("1", FLAG_TRUE) is True
    assert cat.parse_flag("0", FLAG_TRUE) is False
    assert cat.parse_flag(None, FLAG_TRUE) is None
    assert cat.requires_receipt(Category.THREE_WAY_AFTER) and cat.requires_receipt(Category.THREE_WAY_BEFORE)
    assert not cat.requires_receipt(Category.TWO_WAY)
    assert not cat.requires_receipt(Category.CONSIGNMENT)


# ---- predicates -------------------------------------------------------------

def base_events():
    return [ev(CREATE, 0, "user_1", 10.0), ev(GR, 1), ev(RIR, 2)]


def test_all_pass_on_a_clean_line():
    vals = values_for(base_events(), clearing_at(3))
    assert all(v is Value.PASS for v in vals.values())
    assert set(vals) == set(predicates.PREDICATES)


def test_d1_d2_receipt_counts_cancellation_and_equal_timestamp():
    assert values_for([ev(CREATE, 0), ev(RIR, 1)], clearing_at(3))["D1"] is Value.FAIL
    cancelled = [ev(CREATE, 0), ev(GR, 1), ev(CGR, 2), ev(RIR, 2)]
    vals = values_for(cancelled, clearing_at(3))
    assert vals["D1"] is Value.FAIL and vals["D2"] is Value.FAIL
    # A receipt sharing the clearing's timestamp is available evidence.
    assert values_for([ev(CREATE, 0), ev(RIR, 1), ev(GR, 3)], clearing_at(3))["D1"] is Value.PASS
    # A receipt after the clearing is not.
    assert values_for([ev(CREATE, 0), ev(RIR, 1), ev(GR, 3.5)], clearing_at(3))["D2"] is Value.FAIL
    two_one_cancel = [ev(CREATE, 0), ev(GR, 1), ev(GR, 1.5), ev(CGR, 2), ev(RIR, 2)]
    assert values_for(two_one_cancel, clearing_at(3))["D1"] is Value.PASS


def test_d3_invoice_present():
    assert values_for([ev(CREATE, 0), ev(GR, 1)], clearing_at(3))["D3"] is Value.FAIL
    assert values_for([ev(CREATE, 0), ev(GR, 1), ev(RIR, 3)], clearing_at(3))["D3"] is Value.PASS


def test_d4_change_after_last_approval_only():
    changed = base_events() + [ev("Change Price", 2.5)]
    assert values_for(changed, clearing_at(3))["D4"] is Value.FAIL
    reapproved = changed + [ev("Release Purchase Order", 2.7)]
    assert values_for(reapproved, clearing_at(3))["D4"] is Value.PASS
    same_time = base_events() + [ev("Change Quantity", 0)]
    assert values_for(same_time, clearing_at(3))["D4"] is Value.PASS
    at_clearing = base_events() + [ev("Change Quantity", 3)]
    assert values_for(at_clearing, clearing_at(3))["D4"] is Value.FAIL
    after = base_events() + [ev("Change Quantity", 4)]
    assert values_for(after, clearing_at(3))["D4"] is Value.PASS
    no_approval = [ev(GR, 1), ev(RIR, 2), ev(CREATE, 5)]
    assert values_for(no_approval, clearing_at(3))["D4"] is Value.UNKNOWN


def test_d5_actors():
    same = values_for(base_events(), clearing_at(3, "user_1"))
    assert same["D5"] is Value.FAIL
    for missing in (None, "", "NONE", " NONE "):
        assert values_for(base_events(), clearing_at(3, missing))["D5"] is Value.UNKNOWN
    unknown_creator = [ev(CREATE, 0, "NONE"), ev(GR, 1), ev(RIR, 2)]
    assert values_for(unknown_creator, clearing_at(3))["D5"] is Value.UNKNOWN
    # Only the earliest creation counts; two creators at that timestamp both count.
    later_create = base_events() + [ev(CREATE, 1, "user_2")]
    assert values_for(later_create, clearing_at(3, "user_2"))["D5"] is Value.PASS
    tied = base_events() + [ev(CREATE, 0, "user_2")]
    assert values_for(tied, clearing_at(3, "user_2"))["D5"] is Value.FAIL
    assert predicates.creation_actors((), P2P) == ()


def test_d6_payment_block_balance():
    blocked = base_events() + [ev("Set Payment Block", 2.5)]
    assert values_for(blocked, clearing_at(3))["D6"] is Value.FAIL
    removed = blocked + [ev("Remove Payment Block", 2.6)]
    assert values_for(removed, clearing_at(3))["D6"] is Value.PASS
    removed_late = blocked + [ev("Remove Payment Block", 3.1)]
    assert values_for(removed_late, clearing_at(3))["D6"] is Value.FAIL


def test_d7_deleted_or_blocked_line():
    for closing in ("Delete Purchase Order Item", "Block Purchase Order Item"):
        closed = base_events() + [ev(closing, 2.5)]
        assert values_for(closed, clearing_at(3))["D7"] is Value.FAIL
        reopened = closed + [ev("Reactivate Purchase Order Item", 2.6)]
        assert values_for(reopened, clearing_at(3))["D7"] is Value.PASS


# ---- contract ---------------------------------------------------------------

def test_contract_per_category_and_min():
    allpass = {k: Value.PASS for k in predicates.PREDICATES}
    assert contract.decide(allpass, Category.THREE_WAY_AFTER).allow
    receipt_missing = dict(allpass, D1=Value.FAIL, D2=Value.FAIL)
    v = contract.decide(receipt_missing, Category.THREE_WAY_BEFORE)
    assert (v.allow, v.defective, v.failed, v.unknown, v.held_unknown) == (False, True, ("D1", "D2"), (), False)
    # 2-way drops D1 and D2.
    assert contract.decide(receipt_missing, Category.TWO_WAY).allow
    only_unknown = dict(allpass, D5=Value.UNKNOWN)
    v = contract.decide(only_unknown, Category.TWO_WAY)
    assert (v.allow, v.defective, v.unknown, v.held_unknown) == (False, False, ("D5",), True)
    assert contract.applicable(Category.TWO_WAY) == ("D3", "D4", "D5", "D6", "D7")
    with pytest.raises(ValueError):
        contract.applicable(Category.CONSIGNMENT)
    assert contract.score(Value.PASS) == 1 and contract.score(Value.UNKNOWN) == 0 and contract.score(Value.FAIL) == 0


# ---- outcome ----------------------------------------------------------------

def test_corrective_window_is_open_closed():
    t_c = at(0)
    for days, expected in ((0, False), (0.001, True), (60, True), (60.001, False)):
        case = make_case([ev("Cancel Invoice Receipt", days)])
        assert outcome.corrective_within(case, t_c, 60, P2P) is expected, days
    not_outcome = make_case([ev("Record Goods Receipt", 1)])
    assert outcome.corrective_within(not_outcome, t_c, 60, P2P) is False


@pytest.mark.parametrize("days,band", [(0.5, "0-1"), (1, "0-1"), (1.01, "1-7"), (7, "1-7"),
                                       (7.01, "7-30"), (30, "7-30"), (30.01, "over 30"), (400, "over 30")])
def test_lag_bands(days, band):
    assert outcome.lag_band(at(0), at(days)) == band


def test_first_receipt_after_and_class():
    t_end = at(100)
    case = make_case([ev(GR, 5), ev(CGR, 5), ev(GR, 9), ev(GR, 200)])
    assert outcome.first_receipt_after(case, at(0), t_end, P2P) == at(9)
    assert outcome.first_receipt_after(make_case([ev(GR, 200)]), at(0), t_end, P2P) is None
    assert outcome.first_receipt_after(make_case([ev(GR, 100)]), at(0), t_end, P2P) == at(100)
    assert outcome.first_receipt_after(make_case([ev(GR, 0)]), at(0), t_end, P2P) is None
    assert outcome.lag_band(at(0), None) == "never"
    assert outcome.receipt_class(None) == outcome.ABSENT
    assert outcome.receipt_class(at(1)) == outcome.STALE


# ---- frame, values, human hold, decision point -------------------------------

T_END = datetime(2019, 6, 30, tzinfo=timezone.utc)


def framed_line(n_clear=1, create=BASE, attrs=None, value=10.0):
    events = [Event(CREATE, create, "user_1", value), Event(RIR, create + timedelta(days=1), "u", 5.0)]
    events += [Event(CLEAR, create + timedelta(days=2 + i), "user_2", 5.0) for i in range(n_clear)]
    return make_case(events, attrs or TWO_WAY)


def classify(case, t_end=T_END):
    return frame.classify(case, P2P, FLAG_TRUE, t_end, 60)


def test_exclusion_order_and_codes():
    assert classify(make_case([ev(RIR, 1)])).status == frame.NO_CREATION
    consign = framed_line(attrs={"item_type": "Consignment", "gr_based_iv": "true", "goods_receipt_required": "false"})
    assert classify(consign).status == frame.CONSIGNMENT
    undefined = framed_line(attrs={"gr_based_iv": "true", "goods_receipt_required": "false", "item_type": "S"})
    assert classify(undefined).status == frame.UNDEFINED_CATEGORY
    assert classify(framed_line(value=0.0)).status == frame.ZERO_OR_MISSING_VALUE
    assert classify(framed_line(value=None)).status == frame.ZERO_OR_MISSING_VALUE
    assert classify(framed_line(value=-1.0)).status == frame.ZERO_OR_MISSING_VALUE
    # Value is checked before K, K before window.
    assert classify(framed_line(n_clear=13, value=0.0)).status == frame.ZERO_OR_MISSING_VALUE
    old = framed_line(n_clear=13, create=datetime(2017, 1, 1, tzinfo=timezone.utc))
    assert classify(old).status == frame.FRAMEWORK


def test_k_boundary():
    assert classify(framed_line(n_clear=12)).status == frame.FRAMED
    assert classify(framed_line(n_clear=13)).status == frame.FRAMEWORK
    assert len(classify(framed_line(n_clear=12)).analysed) == 12


def test_window_boundaries():
    start = datetime(2018, 1, 1, tzinfo=timezone.utc)
    end = datetime(2018, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    late_end = datetime(2020, 6, 1, tzinfo=timezone.utc)
    assert classify(framed_line(create=start), late_end).status == frame.FRAMED
    assert classify(framed_line(create=start - timedelta(seconds=1)), late_end).status == frame.OUTSIDE_WINDOW
    assert classify(framed_line(create=end), late_end).status == frame.FRAMED
    assert classify(framed_line(create=end + timedelta(seconds=1)), late_end).status == frame.OUTSIDE_WINDOW


def test_horizon_and_analysed_clearings():
    line = framed_line(n_clear=3)  # clearings at day 2, 3, 4
    t_end = BASE + timedelta(days=3 + 60)
    result = classify(line, t_end)
    assert result.framed and [c.ts for c in result.analysed] == [at(2), at(3)]
    assert classify(line, BASE + timedelta(days=2 + 60)).framed
    assert classify(line, BASE + timedelta(days=2 + 60) - timedelta(seconds=1)).status == frame.INCOMPLETE_WINDOW
    uncleared = make_case([ev(CREATE, 0, value=5.0)], TWO_WAY)
    assert classify(uncleared, BASE + timedelta(days=60)).framed
    assert classify(uncleared, BASE + timedelta(days=59)).status == frame.INCOMPLETE_WINDOW
    assert classify(uncleared, BASE + timedelta(days=60)).analysed == ()
    assert classify(uncleared).category is Category.TWO_WAY


def test_line_and_cleared_values():
    case = make_case([ev(CREATE, 0, "a", 7.0), ev(CREATE, 1, "b", 9.0), ev(RIR, 2, value=0.0), ev(RIR, 3, value=4.0)])
    assert frame.line_value(case, P2P) == 7.0
    assert frame.line_value(make_case([ev(RIR, 1)]), P2P) is None
    assert frame.cleared_value(case, ev(CLEAR, 5, value=3.0), P2P) == (3.0, frame.FROM_CLEARING)
    assert frame.cleared_value(case, ev(CLEAR, 5, value=0.0), P2P) == (4.0, frame.FROM_INVOICE)
    assert frame.cleared_value(case, ev(CLEAR, 2.5), P2P) == (7.0, frame.FROM_LINE)
    assert frame.cleared_value(case, ev(CLEAR, 1.5), P2P) == (7.0, frame.FROM_LINE)
    assert frame.positive(0.01) and not frame.positive(0.0) and not frame.positive(None)


def test_human_hold():
    t_end = at(200)
    assert frame.human_hold(make_case([ev(CREATE, 0)]), P2P, t_end, 60) is None
    assert frame.human_hold(make_case([ev(RIR, 150)]), P2P, t_end, 60) is None
    assert frame.human_hold(make_case([ev(RIR, 140)]), P2P, t_end, 60) is True
    assert frame.human_hold(make_case([ev(RIR, 10), ev(CLEAR, 70)]), P2P, t_end, 60) is False
    assert frame.human_hold(make_case([ev(RIR, 10), ev(CLEAR, 70.5)]), P2P, t_end, 60) is True
    assert frame.human_hold(make_case([ev(RIR, 10), ev(CLEAR, 5)]), P2P, t_end, 60) is False
    blocked = [ev(RIR, 10), ev("Set Payment Block", 11), ev(CLEAR, 12)]
    assert frame.human_hold(make_case(blocked), P2P, t_end, 60) is True
    same_time = [ev(RIR, 10), ev("Set Payment Block", 12), ev(CLEAR, 12)]
    assert frame.human_hold(make_case(same_time), P2P, t_end, 60) is True
    after = [ev(RIR, 10), ev(CLEAR, 12), ev("Set Payment Block", 13)]
    assert frame.human_hold(make_case(after), P2P, t_end, 60) is False
    never_cleared = [ev(RIR, 10), ev("Set Payment Block", 11)]
    assert frame.human_hold(make_case(never_cleared), P2P, t_end, 60) is True


def test_decision_point():
    assert frame.decision_point(make_case([ev(CREATE, 0)]), P2P, 60) is None
    assert frame.decision_point(make_case([ev(RIR, 10), ev(CLEAR, 70)]), P2P, 60) == at(70)
    assert frame.decision_point(make_case([ev(RIR, 10), ev(CLEAR, 71)]), P2P, 60) == at(70)
    assert frame.decision_point(make_case([ev(RIR, 10)]), P2P, 60) == at(70)
    assert frame.first_invoice(make_case([ev(RIR, 10), ev(RIR, 3)]), P2P) == at(3)


def test_three_way_before_frames_with_full_contract():
    line = framed_line(attrs=THREE_WAY_BEFORE)
    result = classify(line)
    assert result.category is Category.THREE_WAY_BEFORE and result.framed


# ---- boundaries found by the mutation gate -----------------------------------

def test_inputs_at_counts_and_boundaries():
    from p2p_replay.replay import inputs_at

    events = [ev(CREATE, 0), ev("Change Price", 0), ev("Change Quantity", 1),
              ev("Set Payment Block", 1), ev("Remove Payment Block", 1.5),
              ev("Delete Purchase Order Item", 1), ev("Reactivate Purchase Order Item", 1.5)]
    clear = clearing_at(2)
    got = inputs_at(make_case(events + [clear]), clear, P2P)
    assert got == {
        "uncancelled_receipts": 0, "invoice_receipts": 0, "last_approval": at(0).isoformat(),
        "changes_since_approval": 1, "open_payment_blocks": 0, "line_closed_balance": 0,
    }
    none = inputs_at(make_case([ev(GR, 0), clearing_at(1)]), clearing_at(1), P2P)
    assert none["last_approval"] is None and none["changes_since_approval"] == 0 and none["uncancelled_receipts"] == 1


def test_decision_point_uses_an_early_clearing():
    assert frame.decision_point(make_case([ev(RIR, 10), ev(CLEAR, 30)]), P2P, 60) == at(30)


def test_lag_band_just_past_one_day():
    assert outcome.lag_band(at(0), at(0) + timedelta(days=1, seconds=1)) == "1-7"
    assert outcome.lag_band(at(0), at(0) + timedelta(days=7, seconds=1)) == "7-30"
    assert outcome.lag_band(at(0), at(0) + timedelta(days=30, seconds=1)) == "over 30"


def test_excluded_lines_keep_their_category():
    cases = {
        frame.UNDEFINED_CATEGORY: framed_line(attrs={"gr_based_iv": "true", "goods_receipt_required": "false"}),
        frame.ZERO_OR_MISSING_VALUE: framed_line(value=0.0),
        frame.FRAMEWORK: framed_line(n_clear=13),
        frame.OUTSIDE_WINDOW: framed_line(create=datetime(2017, 1, 1, tzinfo=timezone.utc)),
    }
    for status, case in cases.items():
        result = classify(case)
        assert result.status == status and result.category is not None, status
    consign = framed_line(attrs={"item_type": "Consignment"})
    assert classify(consign).category is Category.CONSIGNMENT
    late = framed_line(create=datetime(2018, 12, 1, tzinfo=timezone.utc))
    assert classify(late, datetime(2019, 1, 1, tzinfo=timezone.utc)).category is Category.TWO_WAY


def test_naive_timestamp_is_utc_whatever_the_local_zone(monkeypatch):
    import time

    monkeypatch.setenv("TZ", "America/New_York")
    time.tzset()
    try:
        assert parse_timestamp("2018-01-01T00:00:00") == datetime(2018, 1, 1, tzinfo=timezone.utc)
        assert parse_timestamp("2018-01-01T00:00:00+01:00").utcoffset() == timedelta(0)
    finally:
        monkeypatch.delenv("TZ")
        time.tzset()


def test_verdict_at_decision_point_d5_off_clearing():
    """D-C-2 B: at a t* that is not a clearing D5 is not applicable; at a clearing it stays."""
    from p2p_replay.category import Category
    from p2p_replay.replay import line_status, verdict_at_decision_point

    gr = "Record Goods Receipt"
    # No clearing within W of the invoice: t* = invoice + 60 days, no clearing actor.
    held = make_case([ev(CREATE, 0, "user_1"), ev(gr, 5), ev(RIR, 10)])
    t_star, literal = verdict_at_decision_point(held, Category.THREE_WAY_AFTER, P2P, 60, amended=False)
    assert t_star == at(70) and literal.unknown == ("D5",) and line_status(literal) == "held_unknown"
    t_star, amended = verdict_at_decision_point(held, Category.THREE_WAY_AFTER, P2P, 60)
    assert t_star == at(70) and amended.allow and amended.unknown == () and line_status(amended) == "clean"
    # A failed predicate still makes the line defective under both readings.
    no_receipt = make_case([ev(CREATE, 0, "user_1"), ev(RIR, 10)])
    for flag in (False, True):
        _, v = verdict_at_decision_point(no_receipt, Category.THREE_WAY_AFTER, P2P, 60, amended=flag)
        assert line_status(v) == "defective" and "D1" in v.failed
    # At an actual clearing D5 is evaluated under both readings: same actor fails, NONE is unknown.
    same = make_case([ev(CREATE, 0, "user_1"), ev(gr, 5), ev(RIR, 10), ev(CLEAR, 20, "user_1")])
    none = make_case([ev(CREATE, 0, "user_1"), ev(gr, 5), ev(RIR, 10), ev(CLEAR, 20, "NONE")])
    for flag in (False, True):
        t_star, v = verdict_at_decision_point(same, Category.THREE_WAY_AFTER, P2P, 60, amended=flag)
        assert t_star == at(20) and v.failed == ("D5",)
        _, v = verdict_at_decision_point(none, Category.THREE_WAY_AFTER, P2P, 60, amended=flag)
        assert v.unknown == ("D5",) and line_status(v) == "held_unknown"
    # 2-way lines carry no D1/D2; off a clearing the amended contract is D3, D4, D6, D7.
    two = make_case([ev(CREATE, 0, "user_1"), ev(RIR, 10)], attrs=TWO_WAY)
    _, v = verdict_at_decision_point(two, Category.TWO_WAY, P2P, 60)
    assert v.allow and line_status(v) == "clean"
    assert verdict_at_decision_point(make_case([ev(CREATE, 0)]), Category.THREE_WAY_AFTER, P2P, 60) == (None, None)


def test_decide_not_applicable():
    from p2p_replay.category import Category
    from p2p_replay.contract import decide
    from p2p_replay.predicates import Value

    values = {d: Value.PASS for d in ("D1", "D2", "D3", "D4", "D5", "D6", "D7")} | {"D5": Value.FAIL}
    assert decide(values, Category.TWO_WAY).failed == ("D5",)
    v = decide(values, Category.TWO_WAY, ("D5",))
    assert v.allow and not v.defective and v.failed == ()
