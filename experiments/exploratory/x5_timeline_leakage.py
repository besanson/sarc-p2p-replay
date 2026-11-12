"""X5, exploratory: audit of the exploratory timeline arm's views (DECISIONS.md D-G-3). No model call.

The registration (prereg/p7-v1.1.md section 2) defines the evidence as what is recorded before t_c; the
exploratory timeline view as committed in 1.1.0 (results/e4/views-timeline.jsonl) listed every event at or
before t*, so on a sample line whose decision point t* is its first `Clear Invoice` the view showed that
clearing, the decision being asked for. For every sample line this script reads the committed timeline view
and reports whether it contains a `Clear Invoice` row dated t* (a line can carry two such records at t*) and
whether the view's last row is one of them;
the counts by status and by decision-point kind (the first clearing, or the first invoice receipt + W); the
committed exploratory replies' hold rates (results/e4-exploratory/, responses/e4-exploratory/) split by
views with and without that row; and two checks. The ERP view (registered): no committed ERP view contains a
clearing, and re-rendering each line whose t* is a clearing without that clearing gives the committed ERP
view byte for byte (no field of the ERP view is derived from it). The corrected views
(results/e4-exploratory/views-timeline-corrected.jsonl): each equals the committed view with exactly the
clearing rows at t* removed, and no corrected view contains a `Clear Invoice`.

Writes results/exploratory/timeline-leakage.json.

Usage: python -m experiments.exploratory.x5_timeline_leakage
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from experiments.common import E0_LINES, ratio, read_e0_lines, write_json
from experiments.e1 import DEFAULT_LOG, hashed
from experiments.e4_run import FAMILIES, Log
from p2p_replay.config import REGISTRATION, ROOT, load_mapping, load_patterns
from p2p_replay.frame import clearings
from p2p_replay.model import Case, parse_timestamp
from p2p_replay.reader import read_log
from p2p_replay.view import render

OUT = ROOT / "results" / "exploratory" / "timeline-leakage.json"
CLEARING = "Clear Invoice"
KINDS = {True: "first clearing", False: "first invoice receipt + W"}
STATUSES = ("defective", "clean")


def _jsonl(path: Path) -> dict[int, dict]:
    return {r["order"]: r for r in (json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip())}


def _rows(view: str) -> list[str]:
    return view.split("\n\n", 1)[1].splitlines()[1:]


def erp_rerender(log: Path, sample: list[dict], erp: dict[int, dict], e0_path: Path, t_end: str) -> dict[str, Any]:
    """Re-render the ERP view of every line whose t* is a clearing, with the clearings at t* removed."""
    mapping = load_mapping("bpi2019")
    p, _ = load_patterns()
    flag_true = mapping.get("flag_true", ["true"])
    end = parse_timestamp(t_end)
    want = {r["case_id"]: r for r in sample if r["t_star_is_clearing"]}
    e0 = read_e0_lines(e0_path)
    checked = equal = 0
    for case in read_log(log, mapping):
        if case.case_id in e0:
            continue
        r = want.get(hashed(case.case_id))
        if r is None:
            continue
        case = case.truncated(end)
        t_star = parse_timestamp(r["t_star"])
        first = clearings(case, p)
        if not first or first[0].ts != t_star:
            raise RuntimeError("t* is not the first clearing on a line marked t_star_is_clearing")
        without = Case(case.case_id, case.attrs,
                       tuple(e for e in case.events if not (e.activity == p.clearing and e.ts == t_star)))
        checked += 1
        equal += render(without, t_star, p, flag_true) == erp[r["order"]]["view"]
    if checked != len(want):
        raise RuntimeError("a sampled line was not found in the log")
    return {"lines_rerendered": checked, "identical_to_committed": equal}


def analyse(sample: list[dict], timeline: dict[int, dict], corrected: dict[int, dict], erp: dict[int, dict],
            calls: dict[str, dict[int, dict]], rerender: dict[str, Any]) -> dict[str, Any]:
    lines = []
    for r in sorted(sample, key=lambda r: r["order"]):
        rows = _rows(timeline[r["order"]]["view"])
        day = r["t_star"][:10]
        at_t = [i for i, row in enumerate(rows) if row.startswith(f"{day}, {CLEARING},")]
        any_clearing = any(f", {CLEARING}," in row for row in rows)
        leaked = bool(at_t)
        if leaked != r["t_star_is_clearing"] or any_clearing != leaked:
            raise RuntimeError(f"order {r['order']}: the view's clearing rows differ from t_star_is_clearing")
        fixed = _rows(corrected[r["order"]]["view"])
        if fixed != [row for i, row in enumerate(rows) if i not in at_t] or any(f", {CLEARING}," in x for x in fixed):
            raise RuntimeError(f"order {r['order']}: the corrected view is not the committed view without its clearing")
        lines.append({"order": r["order"], "status": r["status"], "kind": KINDS[r["t_star_is_clearing"]],
                      "leaked": leaked, "clearing_rows_at_t_star": len(at_t),
                      "clearing_is_last_row": leaked and at_t[-1] == len(rows) - 1,
                      "rows_after_first_clearing_row": len(rows) - 1 - at_t[0] if leaked else None})

    count = Counter((l["status"], l["kind"], l["leaked"]) for l in lines)
    by_status_kind = {s: {k: {"lines": sum(n for (s2, k2, _), n in count.items() if (s2, k2) == (s, k)),
                              "views_with_the_clearing": count[(s, k, True)]} for k in KINDS.values()}
                      for s in STATUSES}

    families: dict[str, Any] = {}
    for family in FAMILIES:
        fam = calls[family]
        cells: dict[str, Any] = {}
        for leaked, name in ((True, "views_with_the_clearing"), (False, "views_without_the_clearing")):
            cell = {}
            for s in STATUSES:
                group = [l for l in lines if l["leaked"] == leaked and l["status"] == s]
                valid = [fam[l["order"]] for l in group if l["order"] in fam and fam[l["order"]]["status"] == "ok"]
                held = sum(c["decision"] == "hold" for c in valid)
                cell[s] = {"lines": len(group), "valid_replies": len(valid),
                           "invalid": sum(1 for l in group if l["order"] in fam and fam[l["order"]]["status"] == "invalid"),
                           "held": held, "hold_rate": ratio(held, len(valid))}
            cells[name] = cell
        families[family] = cells

    erp_with_clearing = sum(CLEARING in v["view"] for v in erp.values())
    leaked_n = sum(l["leaked"] for l in lines)
    last_n = sum(l["clearing_is_last_row"] for l in lines)
    return {
        "exploratory": True, "label": "exploratory, not registered; an audit of committed files; no model call",
        "registration": REGISTRATION, "decision": "DECISIONS.md D-G-3",
        "defect": "the exploratory timeline view (results/e4/views-timeline.jsonl, experiments/e4_sample.py in 1.1.0) "
                  "listed the events at or before t*, so on a line whose t* is its first Clear Invoice it showed "
                  "that clearing; prereg/p7-v1.1.md section 2 defines the evidence as recorded before t_c",
        "sample_lines": len(lines),
        "views_with_the_clearing": leaked_n,
        "views_with_the_clearing_as_last_row": last_n,
        "views_with_the_clearing_before_other_rows": leaked_n - last_n,
        "views_with_more_than_one_clearing_row_at_t_star": sum(l["clearing_rows_at_t_star"] > 1 for l in lines),
        "rows_after_the_first_clearing_row": {str(k): n for k, n in sorted(Counter(
            l["rows_after_first_clearing_row"] for l in lines if l["leaked"]).items())},
        "lines_with_t_star_a_clearing": sum(r["t_star_is_clearing"] for r in sample),
        "by_status_and_decision_point_kind": by_status_kind,
        "committed_exploratory_hold_rates": families,
        "hold_rate_note": "invalid replies count as neither, as in results/e4-exploratory/h4-exploratory.json; the "
                          "split is by view, not a stratified comparison: the lines with and without the clearing "
                          "differ in decision-point kind and in what else their views show",
        "erp_view_check": {"views": len(erp), "views_containing_a_clearing": erp_with_clearing,
                           "rerendered_without_the_clearing": rerender,
                           "unaffected": erp_with_clearing == 0 and
                           rerender["identical_to_committed"] == rerender["lines_rerendered"]},
        "corrected_views_check": {
            "file": "results/e4-exploratory/views-timeline-corrected.jsonl", "views": len(corrected),
            "views_containing_a_clearing": sum(CLEARING in v["view"] for v in corrected.values()),
            "rule": "each corrected view equals the committed view without the clearing rows at t*; the "
                    "opening paragraph is the template's, unchanged (it says \"Using only the ERP record below\")"},
        "lines": lines,
    }


def run(log: Path = DEFAULT_LOG, results_dir: Path = ROOT / "results", out: Path = OUT, e0_path: Path = E0_LINES,
        root: Path = ROOT, corrected_views: Path | None = None) -> dict[str, Any]:
    """results_dir holds the e1/ and e4/ slots read; corrected_views defaults to results_dir's e4-exploratory/."""
    sample = json.loads((results_dir / "e4" / "sample.json").read_text(encoding="utf-8"))["lines"]
    timeline = _jsonl(results_dir / "e4" / "views-timeline.jsonl")
    corrected = _jsonl(corrected_views or results_dir / "e4-exploratory" / "views-timeline-corrected.jsonl")
    erp = _jsonl(results_dir / "e4" / "views.jsonl")
    calls = {f: {r["order"]: r for r in Log(root / "responses" / "e4-exploratory" / f / "responses.jsonl").records()
                 if r.get("kind") == "call"} for f in FAMILIES}
    t_end = json.loads((results_dir / "e1" / "exclusions.json").read_text(encoding="utf-8"))["t_end"]
    doc = analyse(sample, timeline, corrected, erp, calls, erp_rerender(log, sample, erp, e0_path, t_end))
    write_json(out, doc)
    return doc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.exploratory.x5_timeline_leakage")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    doc = run(args.log, out=args.out)
    print(f"X5: {doc['views_with_the_clearing']} of {doc['sample_lines']} views show the clearing at t* "
          f"({doc['views_with_the_clearing_as_last_row']} as the last row); ERP unaffected: "
          f"{doc['erp_view_check']['unaffected']}")
    for f, cells in doc["committed_exploratory_hold_rates"].items():
        print(f"X5 {f}: " + "; ".join(f"{k} " + ", ".join(f"{s} {c['hold_rate']}" for s, c in v.items())
                                      for k, v in cells.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
