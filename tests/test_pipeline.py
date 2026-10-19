"""Reader, end-to-end replay on the fixtures, evidence set, E7, ERP view, CLI and config."""

from __future__ import annotations

import gzip
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from conftest import BASE, DECL, FIXTURES, FLAG_TRUE, MAPPING, P2P, TWO_WAY, at, ev, make_case
from fixtures import make_fixtures
from p2p_replay import cli, config, declarations, evidence, view
from p2p_replay.config import load_mapping
from p2p_replay.model import Case, Event
from p2p_replay.reader import make_event, read_csv, read_log, read_xes
from p2p_replay.replay import log_end, replay_case, replay_log

XES = FIXTURES / "mini2019.xes"
CSV = FIXTURES / "mini2019.csv"
XES2020 = FIXTURES / "mini2020.xes"
CSV_MAPPING = {
    "case": dict(MAPPING["case"], case_id="case:concept:name"),
    "event": dict(MAPPING["event"], actor_fallback=None),
    "flag_true": FLAG_TRUE,
}
ROOT = Path(__file__).resolve().parent.parent


# ---- fixtures ---------------------------------------------------------------

def test_committed_fixtures_regenerate_byte_identically():
    for name, make in make_fixtures.OUTPUTS.items():
        assert (FIXTURES / name).read_text(encoding="utf-8") == make(), name


# ---- reader -----------------------------------------------------------------

def test_xes_reader_keeps_mapped_fields_only():
    cases = {c.case_id: c for c in read_xes(XES, MAPPING)}
    assert set(cases) == set(make_fixtures.CASES_2019)
    a = cases["A_clean_3way_after"]
    assert a.attr("gr_based_iv") == "true" and a.attr("purchase_document") == "P1"
    assert "vendor name 1" not in json.dumps(a.attrs) or a.attr("vendor_name") == "vendor name 1"
    assert [e.activity for e in a.events][0] == "Create Purchase Order Item"
    assert a.events[0].ts == datetime(2018, 2, 1, 8, 0, tzinfo=timezone.utc)
    assert a.events[0].actor == "user_001" and a.events[0].value == 100.0
    assert len(a.events) == 4  # nested <list> attributes ignored, no phantom events


def test_xes_and_csv_readers_agree():
    from_xes = {c.case_id: c.events for c in read_xes(XES, MAPPING)}
    from_csv = {c.case_id: c.events for c in read_csv(CSV, CSV_MAPPING)}
    assert from_xes == from_csv


def test_gzip_and_dispatch(tmp_path: Path):
    gz = tmp_path / "mini2019.xes.gz"
    gz.write_bytes(gzip.compress(XES.read_bytes()))
    assert [c.case_id for c in read_log(gz, MAPPING)] == [c.case_id for c in read_log(XES, MAPPING)]
    csv_gz = tmp_path / "mini2019.csv.gz"
    csv_gz.write_bytes(gzip.compress(CSV.read_bytes()))
    assert len(list(read_log(csv_gz, CSV_MAPPING))) == len(make_fixtures.CASES_2019)
    with pytest.raises(ValueError):
        read_log(tmp_path / "log.parquet", MAPPING)


def test_reader_errors(tmp_path: Path):
    with pytest.raises(ValueError):
        make_event({"concept:name": "x"}, MAPPING)
    bad = tmp_path / "bad.csv"
    bad.write_text("other\n1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        list(read_csv(bad, CSV_MAPPING))
    no_id = tmp_path / "noid.xes"
    no_id.write_text('<log><trace><string key="Item" value="1"/></trace></log>', encoding="utf-8")
    with pytest.raises(ValueError):
        list(read_xes(no_id, MAPPING))


def test_reader_value_parsing_and_actor_fallback():
    m = {"event": {"activity": "a", "timestamp": "t", "actor": "r", "actor_fallback": "u", "value_eur": "v"}}
    e = make_event({"a": "x", "t": "2018-01-01T00:00:00", "u": "fallback", "v": "abc"}, m)
    assert e.actor == "fallback" and e.value is None
    e = make_event({"a": "x", "t": "2018-01-01T00:00:00", "r": "primary", "u": "fb", "v": " "}, m)
    assert e.actor == "primary" and e.value is None
    e = make_event({"a": "x", "t": "2018-01-01T00:00:00", "v": "2.5"}, m)
    assert e.actor is None and e.value == 2.5
    e = make_event({"a": "x", "t": "2018-01-01T00:00:00", "v": "2.5"}, {"event": {"activity": "a", "timestamp": "t"}})
    assert e.value is None


# ---- end-to-end replay on the fixture ---------------------------------------

def replay_fixture():
    return {r.case_id: r for r in replay_log(lambda: read_log(XES, MAPPING), P2P, FLAG_TRUE, min_month_events=1)}


def test_fixture_cases_replay_to_expected():
    results = replay_fixture()
    for cid, (status, records) in make_fixtures.EXPECTED.items():
        got = results[cid]
        assert got.frame.status == status, cid
        observed = [(r.verdict, r.failed, r.unknown, r.receipt_class, r.lag_band, r.outcome_w) for r in got.records]
        assert observed == [(v, f, u, rc, lb, o) for v, f, u, rc, lb, o in records], cid


def test_fixture_evidence_fields():
    rec = replay_fixture()["K_absent_receipt"].records[0]
    assert rec.cleared_value == 10.0 and rec.cleared_value_source == "invoice_receipt"
    assert rec.line_value == 10.0 and rec.purchase_document == "P10"
    assert rec.category == "3-way, invoice after receipt"
    assert rec.applicable == ["D1", "D2", "D3", "D4", "D5", "D6", "D7"]
    assert rec.inputs["uncancelled_receipts"] == 0 and rec.inputs["invoice_receipts"] == 1
    assert rec.strata == {"company": "c2", "spend_area": "s1", "vendor": "v3"}
    assert rec.outcome_w_sensitivity is False
    b = replay_fixture()["B_stale_receipt_3way_before"].records[0]
    assert b.outcome_w is True and b.outcome_w_sensitivity is True
    c = replay_fixture()["C_same_actor_changed_2way"].records[0]
    assert c.inputs["changes_since_approval"] == 1 and c.receipt_class is None
    f = replay_fixture()["F_open_block_unknown_creator"].records[0]
    assert f.inputs["open_payment_blocks"] == 1 and f.verdict == "hold" and f.defective
    l = replay_fixture()["L_deleted_2way"].records[0]
    assert l.inputs["line_closed_balance"] == 1


def test_log_end_and_empty_log():
    assert log_end(read_log(XES, MAPPING)) == datetime(2019, 6, 30, 9, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        log_end([Case.build("x", {}, [])])


def test_replay_case_of_excluded_line_has_no_records():
    result = replay_case(make_case([ev("Record Invoice Receipt", 1)]), P2P, FLAG_TRUE, at(500))
    assert result.records == [] and result.frame.status == "no_creation"


# ---- evidence set -----------------------------------------------------------

def test_source_hash_covers_events_up_to_t_c_only():
    case = make_case([ev("A", 0), ev("B", 1), ev("C", 2)])
    h1 = evidence.source_hash(case, at(1))
    assert h1 == evidence.source_hash(make_case([ev("A", 0), ev("B", 1), ev("Z", 5)]), at(1))
    assert h1 != evidence.source_hash(case, at(2))
    assert h1 != evidence.source_hash(make_case([ev("A", 0), ev("B", 1)], case_id="L2"), at(1))
    assert len(h1) == 64


def test_export_record_hashes_identifiers():
    rec = replay_fixture()["A_clean_3way_after"].records[0]
    out = evidence.export_record(rec)
    assert out["case_id"] == evidence.sha256_text("A_clean_3way_after")[:16]
    assert out["purchase_document"] == evidence.sha256_text("P1")[:16]
    assert out["clearing_actor"] == evidence.sha256_text("user_002")[:16]
    assert out["strata"]["vendor"] == evidence.sha256_text("v1")[:16]
    assert out["strata"]["company"] == evidence.sha256_text("c1")[:16]
    assert out["strata"]["spend_area"] == "s1"
    assert "A_clean" not in json.dumps(out)
    rec_none = evidence.EvidenceSet(**dict(rec.to_dict(), purchase_document=None, clearing_actor=None,
                                           strata={"company": None, "spend_area": None, "vendor": None}))
    out = evidence.export_record(rec_none)
    assert out["purchase_document"] is None and out["strata"]["vendor"] is None


def test_evidence_json_is_canonical():
    rec = replay_fixture()["A_clean_3way_after"].records[0]
    text = rec.to_json()
    assert text == json.dumps(json.loads(text), sort_keys=True, separators=(",", ":"))
    with pytest.raises(ValueError):
        evidence.canonical_json({"x": float("nan")})


# ---- E7 declarations ---------------------------------------------------------

def test_declarations_fixture():
    mapping = load_mapping("bpi2020")
    records = {r.case_id: r for r in declarations.replay_declarations(lambda: read_log(XES2020, mapping), DECL)}
    ok = records["decl_ok"]
    assert (ok.verdict, ok.defective, ok.outcome_prime) == ("allow", False, False)
    wrong = records["decl_wrong_role_resubmitted"]
    assert wrong.predicates == {"D1'": "pass", "D2'": "fail", "D3'": "fail"} and wrong.outcome_prime
    unapproved = records["decl_unapproved"]
    assert unapproved.predicates == {"D1'": "fail", "D2'": "fail", "D3'": "unknown"} and unapproved.verdict == "hold"
    assert "decl_late_payment" not in records  # payment after T_end' - W
    assert json.loads(ok.to_json())["case_id"] == "decl_ok"


def test_outcome_prime_window():
    case = Case.build("d", {}, [ev("Payment Handled", 0), ev("Declaration REJECTED by SUPERVISOR", 60)])
    assert declarations.outcome_prime(case, at(0), DECL)
    late = Case.build("d", {}, [ev("Payment Handled", 0), ev("Declaration REJECTED by SUPERVISOR", 60.01)])
    assert not declarations.outcome_prime(late, at(0), DECL)
    same = Case.build("d", {}, [ev("Payment Handled", 0), ev("Declaration REJECTED by SUPERVISOR", 0)])
    assert not declarations.outcome_prime(same, at(0), DECL)
    reapproved = Case.build("d", {}, [ev("Declaration SUBMITTED by EMPLOYEE", 0),
                                      ev("Declaration FINAL_APPROVED by DIRECTOR", 1), ev("Payment Handled", 2)])
    assert declarations.evaluate_payment(reapproved, ev("Payment Handled", 2), DECL) == {
        "D1'": declarations.Value.PASS, "D2'": declarations.Value.PASS, "D3'": declarations.Value.PASS}


# ---- ERP view ---------------------------------------------------------------

def test_view_renders_registered_template_without_timeline_or_ids():
    case = make_case([
        ev("Create Purchase Order Item", 0, "user_9", 100.0),
        ev("Record Invoice Receipt", 2, value=99.5),
        ev("Change Price", 3), ev("Change Quantity", 4),
        ev("Record Goods Receipt", 5), ev("Set Payment Block", 6),
        ev("Record Goods Receipt", 20),
    ], case_id="SECRET-LINE-ID")
    text = view.render(case, at(10), P2P, FLAG_TRUE)
    assert text.startswith("You are the accounts-payable control")
    assert '{"decision": "clear" or "hold", "p_hold": <number between 0 and 1>}' in text
    assert re.search(r"\{[a-z_]+\}", text) is None
    for line in (
        "ERP record as of 2018-03-11",
        "Item category: 3-way match, invoice after goods receipt",
        "GR-based invoice verification: yes", "Goods receipt required: yes",
        "Approved price (EUR): 100.00", "Approved quantity: not recorded in this system",
        "Invoice received: yes", "Invoice date: 2018-03-03", "Invoice value (EUR): 99.50",
        "Goods receipt recorded: yes", "Goods receipt date: 2018-03-06",
        "Changes since approval: price changed on 2018-03-04, quantity changed on 2018-03-05",
        "Payment block: set",
    ):
        assert line in text, line
    for leak in ("SECRET-LINE-ID", "user_9", "user_1", "Clear Invoice", "Record Goods Receipt"):
        assert leak not in text


def test_view_empty_line_and_approval_value():
    case = make_case([ev("Create Purchase Order Item", 0, value=None),
                      ev("Release Purchase Order", 1, value=42.0)], TWO_WAY)
    fields = view.view_fields(case, at(2), P2P, FLAG_TRUE)
    assert fields["approved_price"] == "42.00" and fields["category"] == "2-way match"
    assert fields["invoice_received"] == "no" and fields["invoice_date"] == "none" and fields["invoice_value"] == "none"
    assert fields["gr_recorded"] == "no" and fields["gr_date"] == "none"
    assert fields["changes"] == "none" and fields["payment_block"] == "not set"
    assert fields["gr_based_iv"] == "no" and fields["gr_required"] == "no"
    fallback = make_case([ev("Create Purchase Order Item", 0, value=7.0), ev("Release Purchase Order", 1)], TWO_WAY)
    assert view.view_fields(fallback, at(2), P2P, FLAG_TRUE)["approved_price"] == "7.00"
    with pytest.raises(ValueError):
        view.view_fields(make_case([], {"item_type": "Consignment"}), at(1), P2P, FLAG_TRUE)
    assert view.render(case, at(2), P2P, FLAG_TRUE, template="x {category} {unknown}") == "x 2-way match {unknown}"


def test_view_cancelled_receipt_shows_none():
    case = make_case([ev("Create Purchase Order Item", 0, value=1.0), ev("Record Goods Receipt", 1),
                      ev("Cancel Goods Receipt", 2)])
    fields = view.view_fields(case, at(3), P2P, FLAG_TRUE)
    assert fields["gr_recorded"] == "no" and fields["gr_date"] == "none"


def test_request_template_block_is_extracted():
    text = view.load_request_template()
    assert text.splitlines()[0].startswith("You are the accounts-payable control")
    assert text.splitlines()[-1] == "Payment block: {payment_block}"
    assert "===" not in text and "#" not in text


# ---- CLI --------------------------------------------------------------------

def run_cli(tmp_path, *extra):
    out = tmp_path / "ev.jsonl"
    counts = tmp_path / "frame.json"
    code = cli.main(["replay", str(XES), "--out", str(out), "--frame-counts", str(counts), "--min-month-events", "1", *extra])
    return code, out, counts


def test_cli_replay_bpi2019(tmp_path, capsys):
    code, out, counts = run_cli(tmp_path)
    assert code == 0
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 6
    data = json.loads(counts.read_text())
    assert data["framed"] == 6
    assert list(data)[: len(cli.STATUSES)] == list(cli.STATUSES)
    assert data["t_end"] == "2019-06-30T09:00:00+00:00" and data["t_end_month"] == "2019-06"
    assert data["dropped_events_after_t_end"] == 0
    assert "p2p_replay: 6 record(s)" in capsys.readouterr().out


def test_cli_is_byte_identical_across_runs(tmp_path):
    _, out1, c1 = run_cli(tmp_path / "a")
    _, out2, c2 = run_cli(tmp_path / "b")
    assert out1.read_bytes() == out2.read_bytes() and c1.read_bytes() == c2.read_bytes()


def test_cli_bpi2020_and_paths(tmp_path):
    out = tmp_path / "nested" / "e7.jsonl"
    counts = tmp_path / "e7-frame.json"
    code = cli.main(["replay", str(XES2020), "--dataset", "bpi2020", "--out", str(out), "--frame-counts", str(counts),
                     "--mapping", str(config.MAPPING_PATH), "--patterns", str(config.PATTERNS_PATH)])
    assert code == 0 and len(out.read_text().splitlines()) == 3
    assert json.loads(counts.read_text()) == {}


def test_cli_runs_outside_repository_root(tmp_path, monkeypatch):
    log = tmp_path / "copy.xes"
    shutil.copy(XES, log)
    monkeypatch.chdir(tmp_path)
    assert cli.main(["replay", "copy.xes", "--out", "out.jsonl", "--min-month-events", "1"]) == 0
    assert len((tmp_path / "out.jsonl").read_text().splitlines()) == 6


# ---- registered configuration -----------------------------------------------

def test_registered_numbers_match_the_registration():
    text = (ROOT / "prereg" / "p7-v1.1.md").read_text(encoding="utf-8")
    assert "[2018-01-01T00:00:00Z, 2018-12-31T23:59:59Z]" in text
    assert config.WINDOW_START.isoformat() == "2018-01-01T00:00:00+00:00"
    assert config.WINDOW_END.isoformat() == "2018-12-31T23:59:59+00:00"
    assert f"**K = {config.K_MAX_CLEARINGS}**" in text
    assert f"**W = {config.W_DAYS} days**" in text and f"**W = {config.W_SENSITIVITY_DAYS} days**" in text
    assert f"`{config.SEED}`" in text
    assert "T_end after 2019-12-31T23:59:59Z" in text
    assert config.T_END_LIMIT.isoformat() == "2019-12-31T23:59:59+00:00"
    assert "last calendar month (UTC) of the log that carries at least 1,000 events" in text
    assert config.T_END_MONTH_MIN_EVENTS == 1000
    assert config.REGISTRATION == "p7-v1.1" and config.REGISTRATION_PATH.name == "p7-v1.1.md"
    assert "| registration id | `p7-v1.1` |" in text
    assert P2P.window_days == config.W_DAYS and P2P.sensitivity_window_days == config.W_SENSITIVITY_DAYS
    assert DECL.window_days == config.W_DAYS


def test_outcome_list_matches_the_brief():
    assert P2P.outcome == {
        "Cancel Invoice Receipt", "Cancel Goods Receipt", "Change Price", "Change Quantity",
        "Delete Purchase Order Item", "Vendor creates debit memo", "Record Subsequent Invoice",
    }
    assert "Create Purchase Order Item" in P2P.approval_bearing


def test_loaders_match_the_registered_files():
    assert config.load_patterns() == (P2P, DECL)
    assert load_mapping("bpi2019") == MAPPING
    assert load_mapping("bpi2020")["event"]["role"] == "org:role"


def test_unknown_dataset_mapping():
    with pytest.raises(KeyError):
        load_mapping("bpi2099")


# ---- boundaries found by the mutation gate -----------------------------------

def test_source_hash_is_pinned():
    """Golden value: a change to the canonical serialisation changes every committed hash."""
    case = Case.build("L1", {}, [ev("A", 0, "u", 1.0), ev("B", 1, None, None)])
    assert evidence.source_hash(case, at(1)) == evidence.sha256_text(
        '{"case_id":"L1","events":[{"activity":"A","actor":"u","ts":"2018-03-01T12:00:00+00:00","value":1.0},'
        '{"activity":"B","actor":null,"ts":"2018-03-02T12:00:00+00:00","value":null}]}')
    rec = replay_fixture()["A_clean_3way_after"].records[0]
    assert rec.t_c == "2018-02-20T08:00:00+00:00"
    case_a = next(c for c in read_xes(XES, MAPPING) if c.case_id == "A_clean_3way_after")
    assert rec.source_sha256 == evidence.source_hash(case_a, case_a.events[-1].ts)


def test_declaration_boundaries():
    resubmitted_same_time = Case.build("d", {}, [ev("Declaration SUBMITTED by EMPLOYEE", 1),
                                                 ev("Declaration FINAL_APPROVED by SUPERVISOR", 1),
                                                 ev("Payment Handled", 2)])
    values = declarations.evaluate_payment(resubmitted_same_time, ev("Payment Handled", 2), DECL)
    assert values["D3'"] is declarations.Value.PASS
    t_end = at(62)
    on_horizon = Case.build("d", {}, [ev("Declaration FINAL_APPROVED by SUPERVISOR", 1), ev("Payment Handled", 2)])
    records = declarations.replay_declaration(on_horizon, DECL, t_end)
    assert len(records) == 1 and records[0].t_pay == at(2).isoformat()
    assert records[0].source_sha256 == evidence.source_hash(on_horizon, at(2))
    assert declarations.replay_declaration(on_horizon, DECL, t_end - timedelta(seconds=1)) == []


def test_view_boundaries():
    case = make_case([
        ev("Create Purchase Order Item", 0, value=None), ev("Record Invoice Receipt", 0, value=8.0),
        ev("Change Price", 0), ev("Set Payment Block", 1), ev("Remove Payment Block", 1),
        ev("Create Purchase Order Item", 0.5, value=3.0),
    ], TWO_WAY)
    fields = view.view_fields(case, at(2), P2P, FLAG_TRUE)
    assert fields["changes"] == "none"          # a change at the approval timestamp is not after it
    assert fields["payment_block"] == "not set"
    assert fields["approved_price"] == "3.00"   # the invoice value at an approval timestamp is not an approval value


def test_cli_csv_log_with_a_custom_mapping_file(tmp_path, capsys):
    import yaml

    mapping_file = tmp_path / "mapping.yaml"
    mapping_file.write_text(yaml.safe_dump({"bpi2019": {k: v for k, v in CSV_MAPPING.items() if k != "flag_true"}}),
                            encoding="utf-8")
    out = tmp_path / "a" / "b" / "ev.jsonl"
    counts = tmp_path / "frame.json"
    code = cli.main(["replay", str(CSV), "--mapping", str(mapping_file), "--out", str(out), "--frame-counts", str(counts),
                     "--min-month-events", "1"])
    assert code == 0
    # Without flag_true in the mapping the default is ["true"], which the fixture uses.
    assert len(out.read_text(encoding="utf-8").splitlines()) == 6
    assert "p2p_replay: 6 record(s)" in capsys.readouterr().out
    assert json.loads(counts.read_text()) == {
        "no_creation": 1, "consignment": 1, "undefined_category": 0, "zero_or_missing_value": 1,
        "more_than_k_clearings": 0, "outside_window": 1, "incomplete_outcome_window": 1, "framed": 6,
        "t_end": "2019-06-30T09:00:00+00:00", "t_end_month": "2019-06", "dropped_events_after_t_end": 0,
    }
    assert counts.read_text().startswith('{\n  "no_creation": 1,')


def test_cli_bpi2020_reports_its_count(tmp_path, capsys):
    out = tmp_path / "x" / "y" / "e7.jsonl"
    assert cli.main(["replay", str(XES2020), "--dataset", "bpi2020", "--out", str(out)]) == 0
    assert "p2p_replay: 3 record(s)" in capsys.readouterr().out


# ---- v1.1 observation end (prereg/p7-v1.1.md section 2) ----------------------

def _bulk_case(case_id, start, n, activity="Change Price"):
    return Case.build(case_id, {}, [Event(activity, start + timedelta(minutes=i), "u", None) for i in range(n)])


def test_observation_end_registered_threshold():
    """1,000 events in January 2019, then a sparse tail: T_end is January's latest event."""
    from p2p_replay.replay import observation_end
    jan = datetime(2019, 1, 1, tzinfo=timezone.utc)
    full = _bulk_case("FULL", jan, 1000)
    tail = Case.build("TAIL", {}, [Event("Change Price", t, "u", None) for t in (
        datetime(2019, 2, 3, tzinfo=timezone.utc), datetime(2019, 4, 9, tzinfo=timezone.utc),
        datetime(2020, 4, 9, 21, 59, tzinfo=timezone.utc))])
    end = observation_end([full, tail])
    assert end.month == "2019-01" and end.t_end == jan + timedelta(minutes=999)
    assert end.dropped_events == 3
    one_short = _bulk_case("SHORT", jan, 999)
    with pytest.raises(ValueError):
        observation_end([one_short, tail])
    assert observation_end([one_short, tail], min_month_events=999).month == "2019-01"
    # A later month reaching the threshold moves T_end to that month.
    later = _bulk_case("LATER", datetime(2019, 3, 1, tzinfo=timezone.utc), 1000)
    assert observation_end([full, later, tail]).month == "2019-03"


def test_observation_end_threshold_is_inclusive_and_months_are_utc():
    from p2p_replay.replay import observation_end
    from p2p_replay.model import parse_timestamp
    case = Case.build("X", {}, [
        Event("a", parse_timestamp("2019-01-31T23:30:00-01:00"), "u", None),  # 2019-02-01 00:30 UTC
        Event("a", parse_timestamp("2019-01-15T00:00:00+00:00"), "u", None),
        Event("a", parse_timestamp("2019-01-16T00:00:00+00:00"), "u", None),
    ])
    end = observation_end([case], min_month_events=2)
    assert end.month == "2019-01" and end.t_end == parse_timestamp("2019-01-16T00:00:00+00:00")
    assert end.dropped_events == 1
    assert observation_end([case], min_month_events=1).month == "2019-02"


def test_replay_log_excludes_events_after_t_end():
    """A clearing after T_end is excluded, so it does not count toward K (more than 12 clearings)."""
    from p2p_replay.replay import replay_log
    create = Event("Create Purchase Order Item", datetime(2018, 1, 2, tzinfo=timezone.utc), "user_1", 10.0)
    clears = [Event("Clear Invoice", datetime(2018, 1, 3 + i, tzinfo=timezone.utc), "user_2", 1.0) for i in range(12)]
    late = Event("Clear Invoice", datetime(2019, 6, 1, tzinfo=timezone.utc), "user_2", 1.0)
    line = Case.build("L13", TWO_WAY, [create, *clears, late])
    filler = Case.build("F", {}, [Event("x", datetime(2018, 6, d, tzinfo=timezone.utc), "u", None) for d in range(1, 21)])
    results = {r.case_id: r for r in replay_log(lambda: [line, filler], P2P, FLAG_TRUE, min_month_events=20)}
    assert results["L13"].frame.status == "framed" and len(results["L13"].frame.analysed) == 12
    # Without the exclusion the same line has 13 clearings and is a framework line.
    from p2p_replay import frame as fr
    assert fr.classify(line, P2P, FLAG_TRUE, datetime(2018, 6, 20, tzinfo=timezone.utc), 60).status == fr.FRAMEWORK
    truncated = line.truncated(datetime(2018, 6, 20, tzinfo=timezone.utc))
    assert len(truncated.events) == 13 and truncated.case_id == "L13" and truncated.attrs == line.attrs
