"""E0 pilot (prereg/p7-v1.md sections 2.2 and 6, E0). Pipeline only.

Three passes over the BPI 2019 log:

1. Raw XES inventory, independent of the column mapping: T_end, every trace-
   and event-level attribute key with its count, every activity name with its
   count, and the share of `Create Purchase Order Item` events inside the window.
2. The registered reader and frame over every case: frame status counts,
   flag-derived category counts, and the cross-tab of flag-derived category
   against the `Item Category` string (cross-check, section 3.1).
3. The 500 E0 lines, drawn with random.Random(20261201) uniformly from the
   sorted framed line ids, replayed through the engine; per predicate the
   pass/fail/unknown counts, and per outcome activity the number of analysed
   clearings it follows within W.

The four stop conditions of section 2.2 are evaluated and reported. Nothing
here computes a rate, an interval or a test on the registered quantities; the
E0 lines are removed from every later estimate (`results/e0/e0-lines.txt`).

Usage: python -m experiments.e0 [--log data/BPI_Challenge_2019.xes] [--out results/e0]
"""

from __future__ import annotations

import argparse
import gzip
import json
import random
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import timedelta
from pathlib import Path
from typing import Any, Iterable

from p2p_replay.category import Category, category_of
from p2p_replay.config import (
    ROOT, SEED, T_END_LIMIT, W_DAYS, WINDOW_END, WINDOW_START, load_mapping, load_patterns,
)
from p2p_replay.frame import FRAMED, STATUSES, classify
from p2p_replay.model import parse_timestamp
from p2p_replay.reader import ATTRIBUTE_TAGS, read_log
from p2p_replay.replay import replay_case

E0_SIZE = 500
CREATE_SHARE_MIN = 0.5
UNDEFINED_SHARE_MAX = 0.01
DEFAULT_LOG = ROOT / "data" / "BPI_Challenge_2019.xes"
DEFAULT_OUT = ROOT / "results" / "e0"


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def raw_inventory(path: Path, creation: str, activity_key: str = "concept:name",
                  timestamp_key: str = "time:timestamp") -> dict[str, Any]:
    """Pass 1: attribute keys, activity names, T_end and creation events in the window."""
    trace_keys: Counter[str] = Counter()
    event_keys: Counter[str] = Counter()
    activities: Counter[str] = Counter()
    traces = events = 0
    t_end = None
    created = created_in_window = 0
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as fh:
        stack: list[str] = []
        root = None
        ev: dict[str, str] = {}
        for kind, el in ET.iterparse(fh, events=("start", "end")):
            tag = _local(el.tag)
            if kind == "start":
                if root is None:
                    root = el
                stack.append(tag)
                if tag == "event":
                    ev = {}
                continue
            stack.pop()
            if tag in ATTRIBUTE_TAGS and stack:
                parent = stack[-1]
                if parent == "event":
                    event_keys[el.get("key")] += 1
                    ev[el.get("key")] = el.get("value")
                elif parent == "trace":
                    trace_keys[el.get("key")] += 1
            elif tag == "event":
                events += 1
                name = ev.get(activity_key)
                if name is not None:
                    activities[name] += 1
                stamp = ev.get(timestamp_key)
                if stamp is not None:
                    ts = parse_timestamp(stamp)
                    if t_end is None or ts > t_end:
                        t_end = ts
                    if name == creation:
                        created += 1
                        created_in_window += WINDOW_START <= ts <= WINDOW_END
            elif tag == "trace":
                traces += 1
                el.clear()
                if root is not None:
                    root.clear()
    return {
        "traces": traces, "events": events, "t_end": t_end,
        "trace_keys": dict(sorted(trace_keys.items())), "event_keys": dict(sorted(event_keys.items())),
        "activities": dict(sorted(activities.items())),
        "creation_events": created, "creation_events_in_window": created_in_window,
    }


def mapped_keys(mapping: dict[str, Any]) -> dict[str, list[str]]:
    case = [v for k, v in mapping["case"].items() if v]
    event = [v for k, v in mapping["event"].items() if v]
    return {"case": sorted(set(case)), "event": sorted(set(event))}


def stop_conditions(inv: dict[str, Any], mapping: dict[str, Any], undefined: int, lines: int) -> dict[str, Any]:
    keys = mapped_keys(mapping)
    missing_case = [k for k in keys["case"] if k not in inv["trace_keys"]]
    missing_event = [k for k in keys["event"] if k not in inv["event_keys"]]
    share_created = inv["creation_events_in_window"] / inv["creation_events"] if inv["creation_events"] else 0.0
    share_undefined = undefined / lines if lines else 0.0
    checks = {
        "creation_events_in_window": {
            "rule": "at least 50% of Create Purchase Order Item events in [2018-01-01, 2018-12-31]",
            "value": share_created, "count": inv["creation_events_in_window"], "of": inv["creation_events"],
            "fires": share_created < CREATE_SHARE_MIN},
        "t_end": {
            "rule": "T_end not after 2019-12-31T23:59:59Z",
            "value": inv["t_end"].isoformat() if inv["t_end"] else None,
            "fires": inv["t_end"] is None or inv["t_end"] > T_END_LIMIT},
        "mapped_attributes_present": {
            "rule": "every attribute in prereg/column-mapping.yaml (bpi2019) present in the log",
            "missing_case": missing_case, "missing_event": missing_event,
            "fires": bool(missing_case or missing_event)},
        "undefined_category": {
            "rule": "flag-derived category undefined for at most 1% of lines",
            "value": share_undefined, "count": undefined, "of": lines,
            "fires": share_undefined > UNDEFINED_SHARE_MAX},
    }
    return {"checks": checks, "any_fires": any(c["fires"] for c in checks.values())}


def frame_pass(cases: Iterable, p2p, flag_true, t_end) -> dict[str, Any]:
    statuses: Counter[str] = Counter()
    categories: Counter[str] = Counter()
    crosstab: Counter[tuple[str, str]] = Counter()
    framed: list[str] = []
    lines = 0
    for case in cases:
        lines += 1
        cat = category_of(case, flag_true)
        categories[cat.value] += 1
        crosstab[(cat.value, case.attr("item_category") or "")] += 1
        result = classify(case, p2p, flag_true, t_end, W_DAYS)
        statuses[result.status] += 1
        if result.framed:
            framed.append(case.case_id)
    return {
        "lines": lines,
        "statuses": {s: statuses.get(s, 0) for s in STATUSES},
        "categories": dict(sorted(categories.items())),
        "undefined": categories.get(Category.UNDEFINED.value, 0),
        "category_vs_item_category": [
            {"flag_category": a, "item_category": b, "lines": n} for (a, b), n in sorted(crosstab.items())],
        "framed_ids": sorted(framed),
    }


def draw_e0(framed_ids: list[str], seed: int = SEED, size: int = E0_SIZE) -> list[str]:
    """Uniform draw without replacement over the sorted framed ids."""
    ordered = sorted(framed_ids)
    return sorted(random.Random(seed).sample(ordered, min(size, len(ordered))))


def pilot_pass(cases: Iterable, chosen: set[str], p2p, flag_true, t_end) -> dict[str, Any]:
    predicate_counts: dict[str, Counter[str]] = {}
    outcome_hits: Counter[str] = Counter()
    clearings = lines = 0
    verdicts: Counter[str] = Counter()
    errors: list[str] = []
    for case in cases:
        if case.case_id not in chosen:
            continue
        lines += 1
        try:
            result = replay_case(case, p2p, flag_true, t_end)
        except Exception as exc:  # pipeline check: report, do not stop
            errors.append(f"{case.case_id}: {type(exc).__name__}: {exc}")
            continue
        for rec in result.records:
            clearings += 1
            verdicts[rec.verdict] += 1
            for pid, value in rec.predicates.items():
                if pid in rec.applicable:
                    predicate_counts.setdefault(pid, Counter())[value] += 1
            t_c = parse_timestamp(rec.t_c)
            end = t_c + timedelta(days=W_DAYS)
            seen = {e.activity for e in case.events if e.activity in p2p.outcome and t_c < e.ts <= end}
            for act in seen:
                outcome_hits[act] += 1
    return {
        "lines": lines, "analysed_clearings": clearings, "errors": errors,
        "verdicts": dict(sorted(verdicts.items())),
        "predicates": {pid: dict(sorted(predicate_counts.get(pid, Counter()).items()))
                       for pid in ("D1", "D2", "D3", "D4", "D5", "D6", "D7")},
        "outcome_activity_follows_clearing": {a: outcome_hits.get(a, 0) for a in sorted(p2p.outcome)},
    }


def registered_name_frequencies(activities: dict[str, int], p2p) -> dict[str, int]:
    names = {p2p.clearing, p2p.creation, p2p.goods_receipt, p2p.goods_receipt_cancel, p2p.invoice_receipt,
             p2p.payment_block_set, p2p.payment_block_remove}
    names |= set(p2p.changes) | set(p2p.approval_bearing) | set(p2p.line_closed) | set(p2p.line_reopened) | set(p2p.outcome)
    return {n: activities.get(n, 0) for n in sorted(names)}


def run(log: Path, out: Path) -> dict[str, Any]:
    started = time.time()
    mapping = load_mapping("bpi2019")
    p2p, _ = load_patterns()
    flag_true = mapping.get("flag_true", ["true"])

    inv = raw_inventory(log, p2p.creation)
    t1 = time.time()
    frame = frame_pass(read_log(log, mapping), p2p, flag_true, inv["t_end"])
    t2 = time.time()
    stops = stop_conditions(inv, mapping, frame["undefined"], frame["lines"])
    chosen = draw_e0(frame["framed_ids"])
    pilot = pilot_pass(read_log(log, mapping), set(chosen), p2p, flag_true, inv["t_end"])
    t3 = time.time()

    report = {
        "registration": "p7-v1 (tag prereg-p7-v1, e239864)",
        "log": {"file": log.name, "traces": inv["traces"], "events": inv["events"]},
        "t_end": inv["t_end"].isoformat() if inv["t_end"] else None,
        "stop_conditions": stops,
        "attribute_inventory": {"trace_keys": inv["trace_keys"], "event_keys": inv["event_keys"],
                                "mapped_keys": mapped_keys(mapping)},
        "registered_activity_frequencies": registered_name_frequencies(inv["activities"], p2p),
        "all_activity_frequencies": inv["activities"],
        "frame": {k: v for k, v in frame.items() if k != "framed_ids"} | {"framed_lines": len(frame["framed_ids"])},
        "e0": {"seed": SEED, "size": len(chosen), "drawn_from": len(frame["framed_ids"])} | pilot,
        "seconds": {"inventory": round(t1 - started, 1), "frame": round(t2 - t1, 1), "pilot": round(t3 - t2, 1)},
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "e0-lines.txt").write_text("".join(f"{c}\n" for c in chosen), encoding="utf-8")
    timing = report.pop("seconds")
    (out / "e0-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "e0-timing.json").write_text(json.dumps(timing, indent=2) + "\n", encoding="utf-8")
    report["seconds"] = timing
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.e0")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    report = run(args.log, args.out)
    for name, check in report["stop_conditions"]["checks"].items():
        print(f"stop condition {name}: {'FIRES' if check['fires'] else 'clear'}")
    print(f"E0: {report['e0']['size']} lines, {report['e0']['analysed_clearings']} analysed clearings, "
          f"{len(report['e0']['errors'])} errors")
    return 3 if report["stop_conditions"]["any_fires"] else 0


if __name__ == "__main__":
    sys.exit(main())
