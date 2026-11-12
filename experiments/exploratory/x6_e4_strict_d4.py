"""X6, exploratory: the E4 sample under the strict D4 reading of X1 (DECISIONS.md D-G-3). No model call.

X1 (experiments/exploratory/x1_d4_sensitivity.py, reading (b)) counts a D4 failure only for a `Change Price`
or `Change Quantity` after an explicit approval or release event (the registered approval-bearing list minus
the line's creation). This script reclassifies the 2,000 E4 sample lines (results/e4/sample.json) at their
decision point t* under that reading: the failed predicates other than D4 as registered, D4 failing only by
the strict reading (where D4 is applicable), the unknown predicates as registered; status defective if any
predicate fails, else held-unknown if any is unknown, else clean. It then re-tabulates the four arms' hold
rates (people from the log, the gate as registered, Jev and Haiku on the registered ERP view,
responses/e4/) over the strict groups and over the cells registered status x strict status.

The sample was stratified by the registered status (category x line-value quartile within each status); the
strict groups are not a stratified sample, and the rates here describe these lines only.

Writes results/exploratory/e4-strict-d4.json.

Usage: python -m experiments.exploratory.x6_e4_strict_d4
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
from p2p_replay.category import Category
from p2p_replay.config import REGISTRATION, ROOT, W_DAYS, load_mapping, load_patterns
from p2p_replay.contract import applicable
from p2p_replay.model import parse_timestamp
from p2p_replay.predicates import last_approval
from p2p_replay.reader import read_log
from p2p_replay.replay import verdict_at_decision_point

OUT = ROOT / "results" / "exploratory" / "e4-strict-d4.json"
STATUSES = ("defective", "held_unknown", "clean")
STATEMENT = ("the sample was stratified by the registered status at t*; the groups reclassified under the strict "
             "D4 reading are not a stratified sample, and their hold rates describe these 2,000 lines only")


def scan(log: Path, sample: list[dict], e0_path: Path, t_end: str) -> dict[str, dict[str, Any]]:
    """Per sampled line (hashed id): the verdict at t* and D4 under the registered and the strict reading."""
    mapping = load_mapping("bpi2019")
    p, _ = load_patterns()
    explicit_kinds = set(p.approval_bearing) - {p.creation}
    end = parse_timestamp(t_end)
    want = {r["case_id"]: r for r in sample}
    e0 = read_e0_lines(e0_path)
    out: dict[str, dict[str, Any]] = {}
    for case in read_log(log, mapping):
        if case.case_id in e0:
            continue
        key = hashed(case.case_id)
        r = want.get(key)
        if r is None:
            continue
        case = case.truncated(end)
        category = Category(r["stratum"]["category"])
        t_star, verdict = verdict_at_decision_point(case, category, p, W_DAYS, amended=True)
        if t_star.isoformat() != r["t_star"] or list(verdict.failed) != r["failed"]:
            raise RuntimeError(f"order {r['order']}: the verdict at t* differs from results/e4/sample.json")
        events = case.upto(t_star)
        approved = last_approval(events, p)
        explicit = [e.ts for e in events if e.activity in explicit_kinds]
        last_explicit = max(explicit) if explicit else None
        d4_applicable = "D4" in applicable(category)
        registered_d4 = approved is not None and any(e.activity in p.changes and e.ts > approved for e in events)
        if d4_applicable and registered_d4 != ("D4" in verdict.failed):
            raise RuntimeError(f"order {r['order']}: the scan's D4 differs from the registered verdict")
        out[key] = {"failed": list(verdict.failed), "unknown": list(verdict.unknown), "d4_applicable": d4_applicable,
                    "explicit_before_t_star": last_explicit is not None,
                    "d4_strict_fail": d4_applicable and last_explicit is not None and any(
                        e.activity in p.changes and e.ts > last_explicit for e in events)}
    if len(out) != len(sample):
        raise RuntimeError("a sampled line was not found in the log")
    return out


def strict_status(s: dict[str, Any]) -> tuple[str, list[str]]:
    failed = [f for f in s["failed"] if f != "D4"] + (["D4"] if s["d4_strict_fail"] else [])
    failed = sorted(failed)
    if failed:
        return "defective", failed
    return ("held_unknown" if s["unknown"] else "clean"), failed


def _rate(held: int, n: int) -> dict[str, Any]:
    return {"lines": n, "held": held, "hold_rate": ratio(held, n)}


def analyse(sample: list[dict], scanned: dict[str, dict], calls: dict[str, dict[int, dict]]) -> dict[str, Any]:
    rows = []
    for r in sorted(sample, key=lambda r: r["order"]):
        status, failed = strict_status(scanned[r["case_id"]])
        rows.append({"order": r["order"], "registered_status": r["status"], "strict_status": status,
                     "registered_failed": r["failed"], "strict_failed": failed,
                     "explicit_before_t_star": scanned[r["case_id"]]["explicit_before_t_star"],
                     "human_arm": r["human_arm"]})
    cells = Counter((x["registered_status"], x["strict_status"]) for x in rows)

    def arm_holds(name: str) -> dict[int, bool | None]:
        """order -> held (True), released (False), or not counted (None)."""
        if name == "people":
            return {x["order"]: None if x["human_arm"] == "unclassified" else x["human_arm"] == "hold" for x in rows}
        if name == "gate (registered)":
            return {x["order"]: x["registered_status"] == "defective" for x in rows}
        fam = calls[name]
        return {x["order"]: (fam[x["order"]]["decision"] == "hold") if x["order"] in fam and
                fam[x["order"]]["status"] == "ok" else None for x in rows}

    arms: dict[str, Any] = {}
    for name in ("people", "gate (registered)", *FAMILIES):
        h = arm_holds(name)

        def tab(sel):
            got = [h[x["order"]] for x in rows if sel(x) and h[x["order"]] is not None]
            return _rate(sum(got), len(got))

        arms[name] = {
            "registered_groups": {s: tab(lambda x, s=s: x["registered_status"] == s) for s in ("defective", "clean")},
            "strict_groups": {s: tab(lambda x, s=s: x["strict_status"] == s) for s in STATUSES},
            "cells": {f"{a} -> {b}": tab(lambda x, a=a, b=b: (x["registered_status"], x["strict_status"]) == (a, b))
                      for (a, b) in sorted(cells)},
        }
    arms["gate (registered)"]["note"] = "holds every line defective under the registered reading"
    arms["people"]["note"] = "from the log (section 3.6); unclassified lines count as neither"
    for f in FAMILIES:
        arms[f]["note"] = "registered ERP view (responses/e4/); invalid replies count as neither"
    return {
        "exploratory": True, "label": "exploratory, not registered; no p-value; not in the Holm family",
        "registration": REGISTRATION, "decision": "DECISIONS.md D-G-3",
        "strict_d4": "X1 reading (b): D4 fails only for a change after an explicit approval or release event "
                     "(the registered approval-bearing list minus the creation) before t*",
        "statement": STATEMENT,
        "sample_lines": len(rows),
        "registered_x_strict": {f"{a} -> {b}": n for (a, b), n in sorted(cells.items())},
        "strict_groups": dict(Counter(x["strict_status"] for x in rows)),
        "arms": arms,
        "lines": rows,
    }


def run(log: Path = DEFAULT_LOG, results_dir: Path = ROOT / "results", out: Path = OUT, e0_path: Path = E0_LINES,
        root: Path = ROOT) -> dict[str, Any]:
    """results_dir holds the e1/ and e4/ slots read; the responses are the committed ones under root."""
    sample = json.loads((results_dir / "e4" / "sample.json").read_text(encoding="utf-8"))["lines"]
    t_end = json.loads((results_dir / "e1" / "exclusions.json").read_text(encoding="utf-8"))["t_end"]
    calls = {f: {r["order"]: r for r in Log(root / "responses" / "e4" / f / "responses.jsonl").records()
                 if r.get("kind") == "call"} for f in FAMILIES}
    doc = analyse(sample, scan(log, sample, e0_path, t_end), calls)
    write_json(out, doc)
    return doc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.exploratory.x6_e4_strict_d4")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    doc = run(args.log, out=args.out)
    print(f"X6: {doc['registered_x_strict']}")
    for name, a in doc["arms"].items():
        print(f"X6 {name}: " + ", ".join(f"{s} {c['hold_rate']}" for s, c in a["strict_groups"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
