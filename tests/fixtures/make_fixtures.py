"""Generate the synthetic fixture logs. Hand-built; no line comes from the registered data.

    python tests/fixtures/make_fixtures.py   # rewrites mini2019.xes, mini2019.csv, mini2020.xes

tests/test_fixtures.py checks the committed files equal a fresh generation.
Each BPI 2019 case is built for one expected outcome, listed in EXPECTED.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from xml.sax.saxutils import quoteattr

HERE = Path(__file__).resolve().parent

T, F = "true", "false"
# case id -> (case attributes, events [(activity, timestamp, actor, value)])
CASES_2019 = {
    "A_clean_3way_after": (
        {"Item Type": "Standard", "GR-Based Inv. Verif.": T, "Goods Receipt": T, "Item Category": "3-way match, invoice after GR", "Company": "c1", "Spend area text": "s1", "Vendor": "v1", "Name": "vendor name 1", "Purchasing Document": "P1"},
        [("Create Purchase Order Item", "2018-02-01T09:00:00+01:00", "user_001", 100.0),
         ("Record Goods Receipt", "2018-02-10T09:00:00+01:00", "user_005", 100.0),
         ("Record Invoice Receipt", "2018-02-12T09:00:00+01:00", "user_006", 100.0),
         ("Clear Invoice", "2018-02-20T09:00:00+01:00", "user_002", 100.0)],
    ),
    "B_stale_receipt_3way_before": (
        {"Item Type": "Standard", "GR-Based Inv. Verif.": F, "Goods Receipt": T, "Item Category": "3-way match, invoice before GR", "Company": "c1", "Spend area text": "s2", "Vendor": "v2", "Name": "vendor name 2", "Purchasing Document": "P2"},
        [("Create Purchase Order Item", "2018-03-01T09:00:00+00:00", "user_001", 200.0),
         ("Record Invoice Receipt", "2018-03-05T09:00:00+00:00", "user_006", 200.0),
         ("Clear Invoice", "2018-03-10T09:00:00+00:00", "user_002", 200.0),
         ("Record Goods Receipt", "2018-03-12T09:00:00+00:00", "user_005", 200.0),
         ("Change Price", "2018-03-20T09:00:00+00:00", "user_001", 210.0)],
    ),
    "C_same_actor_changed_2way": (
        {"Item Type": "Service", "GR-Based Inv. Verif.": F, "Goods Receipt": F, "Item Category": "2-way match", "Company": "c2", "Spend area text": "s1", "Vendor": "v1", "Name": "vendor name 1", "Purchasing Document": "P3"},
        [("Create Purchase Order Item", "2018-04-01T09:00:00+00:00", "user_003", 50.0),
         ("Change Price", "2018-04-02T09:00:00+00:00", "user_003", 55.0),
         ("Record Invoice Receipt", "2018-04-03T09:00:00+00:00", "user_006", 55.0),
         ("Clear Invoice", "2018-04-05T09:00:00+00:00", "user_003", 55.0)],
    ),
    "D_consignment": (
        {"Item Type": "Consignment", "GR-Based Inv. Verif.": F, "Goods Receipt": T, "Item Category": "Consignment", "Company": "c1", "Spend area text": "s1", "Vendor": "v3", "Name": "vendor name 3", "Purchasing Document": "P4"},
        [("Create Purchase Order Item", "2018-04-01T09:00:00+00:00", "user_001", 10.0),
         ("Record Goods Receipt", "2018-04-02T09:00:00+00:00", "user_005", 10.0)],
    ),
    "E_no_creation": (
        {"Item Type": "Standard", "GR-Based Inv. Verif.": F, "Goods Receipt": F, "Item Category": "2-way match", "Company": "c1", "Spend area text": "s1", "Vendor": "v1", "Name": "vendor name 1", "Purchasing Document": "P5"},
        [("Record Invoice Receipt", "2018-05-01T09:00:00+00:00", "user_006", 30.0),
         ("Clear Invoice", "2018-05-02T09:00:00+00:00", "user_002", 30.0)],
    ),
    "F_open_block_unknown_creator": (
        {"Item Type": "Standard", "GR-Based Inv. Verif.": T, "Goods Receipt": T, "Item Category": "3-way match, invoice after GR", "Company": "c2", "Spend area text": "s2", "Vendor": "v2", "Name": "vendor name 2", "Purchasing Document": "P6"},
        [("Create Purchase Order Item", "2018-05-01T09:00:00+00:00", "NONE", 80.0),
         ("Record Goods Receipt", "2018-05-02T09:00:00+00:00", "user_005", 80.0),
         ("Record Invoice Receipt", "2018-05-03T09:00:00+00:00", "user_006", 80.0),
         ("Set Payment Block", "2018-05-04T09:00:00+00:00", "user_006", None),
         ("Clear Invoice", "2018-05-06T09:00:00+00:00", "user_004", 80.0)],
    ),
    "G_outside_window": (
        {"Item Type": "Standard", "GR-Based Inv. Verif.": F, "Goods Receipt": F, "Item Category": "2-way match", "Company": "c1", "Spend area text": "s1", "Vendor": "v1", "Name": "vendor name 1", "Purchasing Document": "P7"},
        [("Create Purchase Order Item", "2017-06-01T09:00:00+00:00", "user_001", 40.0),
         ("Record Invoice Receipt", "2017-06-02T09:00:00+00:00", "user_006", 40.0),
         ("Clear Invoice", "2017-06-03T09:00:00+00:00", "user_002", 40.0)],
    ),
    "H_incomplete_window": (
        {"Item Type": "Standard", "GR-Based Inv. Verif.": F, "Goods Receipt": T, "Item Category": "3-way match, invoice before GR", "Company": "c1", "Spend area text": "s1", "Vendor": "v1", "Name": "vendor name 1", "Purchasing Document": "P8"},
        [("Create Purchase Order Item", "2018-12-01T09:00:00+00:00", "user_001", 60.0),
         ("Record Invoice Receipt", "2019-05-20T09:00:00+00:00", "user_006", 60.0),
         ("Clear Invoice", "2019-06-01T09:00:00+00:00", "user_002", 60.0),
         ("Record Goods Receipt", "2019-06-30T09:00:00+00:00", "user_005", 60.0)],
    ),
    "I_zero_value": (
        {"Item Type": "Standard", "GR-Based Inv. Verif.": F, "Goods Receipt": F, "Item Category": "2-way match", "Company": "c1", "Spend area text": "s1", "Vendor": "v1", "Name": "vendor name 1", "Purchasing Document": "P9"},
        [("Create Purchase Order Item", "2018-06-01T09:00:00+00:00", "user_001", 0.0),
         ("Record Invoice Receipt", "2018-06-02T09:00:00+00:00", "user_006", 0.0),
         ("Clear Invoice", "2018-06-03T09:00:00+00:00", "user_002", 0.0)],
    ),
    "K_absent_receipt": (
        {"Item Type": "Standard", "GR-Based Inv. Verif.": T, "Goods Receipt": T, "Item Category": "3-way match, invoice after GR", "Company": "c2", "Spend area text": "s1", "Vendor": "v3", "Name": "vendor name 3", "Purchasing Document": "P10"},
        [("Create Purchase Order Item", "2018-06-01T09:00:00+00:00", "user_001", 10.0),
         ("Record Invoice Receipt", "2018-06-02T09:00:00+00:00", "user_006", 10.0),
         ("Clear Invoice", "2018-06-03T09:00:00+00:00", "user_002", None)],
    ),
    "L_deleted_2way": (
        {"Item Type": "Standard", "GR-Based Inv. Verif.": F, "Goods Receipt": F, "Item Category": "2-way match", "Company": "c1", "Spend area text": "s2", "Vendor": "v2", "Name": "vendor name 2", "Purchasing Document": "P11"},
        [("Create Purchase Order Item", "2018-07-01T09:00:00+00:00", "user_001", 30.0),
         ("Delete Purchase Order Item", "2018-07-02T09:00:00+00:00", "user_001", None),
         ("Record Invoice Receipt", "2018-07-03T09:00:00+00:00", "user_006", 30.0),
         ("Clear Invoice", "2018-07-04T09:00:00+00:00", "user_002", 30.0)],
    ),
}

# Expected frame status, and for framed cases (verdict, failed predicates, unknown,
# receipt class, lag band, O at W=60).
EXPECTED = {
    "A_clean_3way_after": ("framed", [("allow", [], [], None, None, False)]),
    "B_stale_receipt_3way_before": ("framed", [("hold", ["D1", "D2"], [], "stale receipt", "1-7", True)]),
    "C_same_actor_changed_2way": ("framed", [("hold", ["D4", "D5"], [], None, None, False)]),
    "D_consignment": ("consignment", []),
    "E_no_creation": ("no_creation", []),
    "F_open_block_unknown_creator": ("framed", [("hold", ["D6"], ["D5"], None, None, False)]),
    "G_outside_window": ("outside_window", []),
    "H_incomplete_window": ("incomplete_outcome_window", []),
    "I_zero_value": ("zero_or_missing_value", []),
    "K_absent_receipt": ("framed", [("hold", ["D1", "D2"], [], "absent receipt", "never", False)]),
    "L_deleted_2way": ("framed", [("hold", ["D7"], [], None, None, False)]),
}

CASES_2020 = {
    "decl_ok": [
        ("Declaration SUBMITTED by EMPLOYEE", "2018-01-02T10:00:00+00:00"),
        ("Declaration APPROVED by ADMINISTRATION", "2018-01-03T10:00:00+00:00"),
        ("Declaration FINAL_APPROVED by SUPERVISOR", "2018-01-04T10:00:00+00:00"),
        ("Request Payment", "2018-01-05T10:00:00+00:00"),
        ("Payment Handled", "2018-01-08T10:00:00+00:00"),
    ],
    "decl_wrong_role_resubmitted": [
        ("Declaration SUBMITTED by EMPLOYEE", "2018-02-02T10:00:00+00:00"),
        ("Declaration APPROVED by ADMINISTRATION", "2018-02-03T10:00:00+00:00"),
        ("Declaration SUBMITTED by EMPLOYEE", "2018-02-04T10:00:00+00:00"),
        ("Payment Handled", "2018-02-08T10:00:00+00:00"),
        ("Declaration REJECTED by ADMINISTRATION", "2018-02-20T10:00:00+00:00"),
    ],
    "decl_unapproved": [
        ("Declaration SUBMITTED by EMPLOYEE", "2018-03-02T10:00:00+00:00"),
        ("Payment Handled", "2018-03-08T10:00:00+00:00"),
    ],
    "decl_late_payment": [
        ("Declaration SUBMITTED by EMPLOYEE", "2018-12-01T10:00:00+00:00"),
        ("Declaration FINAL_APPROVED by SUPERVISOR", "2018-12-02T10:00:00+00:00"),
        ("Payment Handled", "2018-12-20T10:00:00+00:00"),
    ],
}


def _attr(tag: str, key: str, value) -> str:
    return f"<{tag} key={quoteattr(key)} value={quoteattr(str(value))}/>"


def _case_attr(key: str, value: str) -> str:
    return _attr("boolean" if value in (T, F) else "string", key, value)


def xes_2019() -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<log xes.version="1.0" xmlns="http://www.xes-standard.org/">',
             '  <global scope="event">' + _attr("string", "concept:name", "__INVALID__") + "</global>"]
    for cid, (attrs, events) in CASES_2019.items():
        lines.append("  <trace>")
        lines.append("    " + _attr("string", "concept:name", cid))
        lines.extend("    " + _case_attr(k, v) for k, v in attrs.items())
        for activity, ts, actor, value in events:
            parts = [_attr("string", "concept:name", activity), _attr("date", "time:timestamp", ts),
                     _attr("string", "org:resource", actor), _attr("string", "User", actor)]
            if value is not None:
                parts.append(_attr("float", "Cumulative net worth (EUR)", value))
            parts.append('<list key="ignored"><string key="nested" value="x"/></list>')
            lines.append("    <event>" + "".join(parts) + "</event>")
        lines.append("  </trace>")
    lines.append("</log>")
    return "\n".join(lines) + "\n"


def csv_2019() -> str:
    keys = ["case:concept:name", "Purchasing Document", "Item Type", "GR-Based Inv. Verif.", "Goods Receipt",
            "Item Category", "Company", "Spend area text", "Vendor", "Name",
            "concept:name", "time:timestamp", "org:resource", "Cumulative net worth (EUR)"]
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(keys)
    # Rows interleaved across cases on purpose: the reader must group by case id.
    rows = []
    for cid, (attrs, events) in CASES_2019.items():
        for i, (activity, ts, actor, value) in enumerate(events):
            rows.append((i, [cid] + [attrs[k] for k in keys[1:10]] + [activity, ts, actor, "" if value is None else value]))
    for _, row in sorted(rows, key=lambda r: r[0]):
        writer.writerow(row)
    return buf.getvalue()


def xes_2020() -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<log xes.version="1.0">']
    for cid, events in CASES_2020.items():
        lines.append("  <trace>" + _attr("string", "concept:name", cid))
        for activity, ts in events:
            lines.append("    <event>" + _attr("string", "concept:name", activity) + _attr("date", "time:timestamp", ts)
                         + _attr("string", "org:resource", "STAFF MEMBER") + _attr("string", "org:role", "EMPLOYEE") + "</event>")
        lines.append("  </trace>")
    lines.append("</log>")
    return "\n".join(lines) + "\n"


OUTPUTS = {"mini2019.xes": xes_2019, "mini2019.csv": csv_2019, "mini2020.xes": xes_2020}


def main() -> None:
    for name, make in OUTPUTS.items():
        (HERE / name).write_text(make(), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
