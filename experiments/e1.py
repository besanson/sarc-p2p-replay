"""E1, exposure (prereg/p7-v1.1.md sections 2, 3, 5 and 6, E1).

Replays every analysed clearing on every framed line of the v1.1 frame, with
the E0 lines (results/e0/run-2/e0-lines.txt) removed, and writes to the output
directory (default results/e1/):

  evidence-set.jsonl.gz     one record per analysed clearing (section 3.9), ids hashed
  lines.jsonl.gz            one record per framed line: category, value, strata,
                            human hold (3.6), E4 decision point t* and the gate status there
                            (literal reading of section 7)
  lines-t-star-amended.jsonl.gz
                            the gate status at t* under D-C-2 B (D5 not applicable at a t*
                            that is not a clearing), by line
  exclusions.json           exclusion counts in registered order (2.1), T_end,
                            events after T_end, E0 removal
  exposure.json             per defect class and overall: share of clearings (Wilson and
                            clustered bootstrap) and of cleared value (clustered bootstrap);
                            held-unknown share separately
  exposure-by-stratum.json  the same per stratum (2.3)
  value-fallback.json       cleared-value sources (3.4)
  category-crosscheck.json  lines whose Item Category string disagrees with the flags (3.1)
  coverage-check.json       each COVERAGE.md "detected" row of BPI 2019 and whether its
                            predicate failed at least once
  evidence-sample.jsonl     the seeded 1,000-record sample export (3.9)

Every number is written by this code; nothing is hand-entered.

Usage: python -m experiments.e1 [--log data/BPI_Challenge_2019.xes] [--out results/e1]
"""

from __future__ import annotations

import argparse
import hashlib
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from experiments.common import (
    BOOTSTRAP_B, E0_LINES, ClusterBootstrap, Strata, cells, cents, eur, percentile95, ratio, read_e0_lines,
    read_jsonl_gz, wilson, write_json, write_jsonl, write_jsonl_gz,
)
from p2p_replay.category import Category, category_of
from p2p_replay.config import REGISTRATION, ROOT, SEED, T_END_MONTH_MIN_EVENTS, W_DAYS, load_mapping, load_patterns
from p2p_replay.evidence import export_record, sha256_text
from p2p_replay.frame import human_hold, line_value
from p2p_replay.model import Case
from p2p_replay.outcome import ABSENT, STALE
from p2p_replay.reader import read_log
from p2p_replay.replay import line_status, observation_end, replay_case, verdict_at_decision_point

DEFAULT_LOG = ROOT / "data" / "BPI_Challenge_2019.xes"
DEFAULT_OUT = ROOT / "results" / "e1"
COVERAGE_PATH = ROOT / "COVERAGE.md"
SAMPLE_SIZE = 1000

# Section 2.1 order; the undefined category (3.1) sits where the engine applies it.
REGISTERED_STEP = {
    "no_creation": "2.1 (1) no Create Purchase Order Item",
    "consignment": "2.1 (2) consignment",
    "undefined_category": "3.1 category undefined by the flags",
    "zero_or_missing_value": "2.1 (3) zero or missing line value",
    "more_than_k_clearings": "2.1 (4) more than K = 12 clearings",
    "outside_window": "2.1 (5) outside the window",
    "incomplete_outcome_window": "2.1 (5) failing the frame condition",
    "framed": "framed",
}
# The record's Item Category string for each flag-derived category (cross-check only, 3.1).
ITEM_CATEGORY = {
    Category.THREE_WAY_AFTER: "3-way match, invoice after GR",
    Category.THREE_WAY_BEFORE: "3-way match, invoice before GR",
    Category.TWO_WAY: "2-way match",
    Category.CONSIGNMENT: "Consignment",
}
CLASSES = ("D1 class (absent receipt)", "D2 class (stale receipt)", "D3", "D4", "D5", "D6", "D7",
           "at least one defect")
HELD_UNKNOWN = "held unknown"


def hashed(value: str | None) -> str | None:
    """Identifier as in every export (section 3.9; evidence.export_record)."""
    return sha256_text(value)[:16] if value is not None else None


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# ---------------------------------------------------------------- replay

def disagrees(case: Case, category: Category) -> bool:
    expected = ITEM_CATEGORY.get(category)
    found = case.attr("item_category")
    return expected is None or found is None or found.strip() != expected


def decision_status(case: Case, category: Category, p, amended: bool = False) -> tuple[str | None, str | None]:
    """Gate status of the line at the E4 decision point t* (section 7): defective, clean or held_unknown.

    `amended=False` is the literal reading of section 7 (D5 unknown at a t* with no clearing);
    `amended=True` is D-C-2 B (D5 not applicable there).
    """
    t_star, verdict = verdict_at_decision_point(case, category, p, W_DAYS, amended=amended)
    if t_star is None:
        return None, None
    return t_star.isoformat(), line_status(verdict)


def line_row(case: Case, category: Category, n_records: int, p, t_end) -> dict[str, Any]:
    t_star, status = decision_status(case, category, p)
    return {
        "case_id": hashed(case.case_id),
        "purchase_document": hashed(case.attr("purchase_document")),
        "category": category.value,
        "line_value": line_value(case, p),
        "strata": {"company": hashed(case.attr("company")), "spend_area": case.attr("spend_area"),
                   "vendor": hashed(case.attr("vendor"))},
        "human_hold": human_hold(case, p, t_end, W_DAYS),
        "t_star": t_star,
        "t_star_status": status,
        "analysed_clearings": n_records,
    }


def replay(log: Path, e0_ids: set[str], min_month_events: int = T_END_MONTH_MIN_EVENTS) -> dict[str, Any]:
    mapping = load_mapping("bpi2019")
    p2p, _ = load_patterns()
    flag_true = mapping.get("flag_true", ["true"])
    end = observation_end(read_log(log, mapping), min_month_events)
    statuses: Counter[str] = Counter()
    crosscheck = Counter()
    records: list[dict] = []
    lines: list[dict] = []
    amended: list[dict] = []
    raw_docs: set[str] = set()
    raw_lines: set[str] = set()
    e0_found = 0
    for case in read_log(log, mapping):
        case = case.truncated(end.t_end)
        result = replay_case(case, p2p, flag_true, end.t_end)
        statuses[result.frame.status] += 1
        mismatch = disagrees(case, category_of(case, flag_true))
        crosscheck["all_lines"] += 1
        crosscheck["all_lines_disagreeing"] += mismatch
        if not result.frame.framed:
            continue
        if case.case_id in e0_ids:
            e0_found += 1
            continue
        crosscheck["framed_lines"] += 1
        crosscheck["framed_lines_disagreeing"] += mismatch
        raw_lines.add(case.case_id)
        raw_docs.add(case.attr("purchase_document") or "")
        lines.append(line_row(case, result.frame.category, len(result.records), p2p, end.t_end))
        amended.append({"case_id": lines[-1]["case_id"],
                        "t_star_status": decision_status(case, result.frame.category, p2p, amended=True)[1]})
        records.extend(export_record(r) for r in result.records)
    # Hashed ids must stay distinct, or a cluster or a line would merge.
    if len({l["case_id"] for l in lines}) != len(raw_lines) or \
            len({l["purchase_document"] for l in lines}) != len(raw_docs):
        raise RuntimeError("hashed identifier collision")
    records.sort(key=lambda r: (r["case_id"], r["t_c"]))
    lines.sort(key=lambda l: l["case_id"])
    amended.sort(key=lambda l: l["case_id"])
    return {"end": end, "statuses": statuses, "crosscheck": dict(crosscheck), "records": records, "lines": lines,
            "lines_amended": amended,
            "e0_found": e0_found, "e0_listed": len(e0_ids)}


# ---------------------------------------------------------------- analysis

def class_flags(rec: dict) -> dict[str, bool]:
    flags = {
        CLASSES[0]: rec["receipt_class"] == ABSENT,
        CLASSES[1]: rec["receipt_class"] == STALE,
    }
    for d in ("D3", "D4", "D5", "D6", "D7"):
        flags[d] = d in rec["failed"]
    flags[CLASSES[-1]] = bool(rec["defective"])
    flags[HELD_UNKNOWN] = rec["verdict"] == "hold" and not rec["defective"]
    return flags


def applicable_counts(records: Sequence[dict]) -> dict[str, int]:
    receipt = sum("D1" in r["applicable"] for r in records)
    out = {CLASSES[0]: receipt, CLASSES[1]: receipt}
    for d in ("D3", "D4", "D5", "D6", "D7"):
        out[d] = sum(d in r["applicable"] for r in records)
    out[CLASSES[-1]] = out[HELD_UNKNOWN] = len(records)
    return out


def share_tables(boot: ClusterBootstrap, masks: dict[str, np.ndarray], flags: dict[str, np.ndarray],
                 value: np.ndarray) -> dict[str, dict]:
    """For each cell mask: per indicator the share of clearings and of cleared value, with intervals."""
    names = list(flags)
    columns: list[np.ndarray] = []
    for m in masks.values():
        columns += [m.astype(np.float64), np.where(m, value, 0.0)]
        for name in names:
            sel = m & flags[name]
            columns += [sel.astype(np.float64), np.where(sel, value, 0.0)]
    reps = boot.totals(columns)
    out: dict[str, dict] = {}
    width = 2 + 2 * len(names)
    for c, (cell, m) in enumerate(masks.items()):
        base = c * width
        n, v = int(m.sum()), int(value[m].sum())
        block = {"analysed_clearings": n, "cleared_value_eur": eur(v), "classes": {}}
        for i, name in enumerate(names):
            j = base + 2 + 2 * i
            sel = m & flags[name]
            k, kv = int(sel.sum()), int(value[sel].sum())
            entry = {
                "clearings": k,
                "share_of_clearings": ratio(k, n),
                "wilson95": wilson(k, n),
                "bootstrap95": percentile95(reps[:, j], reps[:, base])["interval"],
                "cleared_value_eur": eur(kv),
                "share_of_value": ratio(kv, v),
                "value_bootstrap95": percentile95(reps[:, j + 1], reps[:, base + 1])["interval"],
            }
            if name == HELD_UNKNOWN:
                block[HELD_UNKNOWN] = entry
            else:
                block["classes"][name] = entry
        out[cell] = block
    return out


def coverage_check(records: Sequence[dict], path: Path = COVERAGE_PATH) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    section = text.split("## Detected (BPI 2019", 1)[1].split("\n## ", 1)[0]
    fails = Counter(d for r in records for d in r["failed"])
    rows = []
    for line in section.splitlines():
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*(D[1-7])\b", line)
        if m:
            rows.append({"defect_class": m.group(1), "predicate": m.group(2),
                         "failed_clearings": fails.get(m.group(2), 0), "fired": fails.get(m.group(2), 0) > 0})
    return {"source": "COVERAGE.md, section Detected (BPI 2019, E1 to E6)", "rows": rows,
            "every_detected_row_fired": bool(rows) and all(r["fired"] for r in rows),
            "note": "D1 and D2 have the same truth value at t_c (section 3.3); the BPI 2020 rows belong to E7"}


def analyse(rep: dict[str, Any], log_name: str, log_sha256: str, b: int = BOOTSTRAP_B) -> dict[str, Any]:
    records, lines, end = rep["records"], rep["lines"], rep["end"]
    framed = rep["statuses"].get("framed", 0)
    exclusions = {
        "registration": REGISTRATION,
        "log": {"file": log_name, "sha256": log_sha256},
        "lines_in_log": sum(rep["statuses"].values()),
        "t_end": end.t_end.isoformat(),
        "t_end_month": end.month,
        "events_after_t_end_excluded": end.dropped_events,
        "exclusions_in_registered_order": [
            {"status": s, "registered_step": step, "lines": rep["statuses"].get(s, 0)}
            for s, step in REGISTERED_STEP.items() if s != "framed"],
        "framed_lines": framed,
        "e0_lines_listed": rep["e0_listed"],
        "e0_lines_removed": rep["e0_found"],
        "framed_lines_after_e0_removal": len(lines),
        "framed_lines_with_analysed_clearings": sum(1 for l in lines if l["analysed_clearings"]),
        "analysed_clearings": len(records),
        "purchase_documents_with_analysed_clearings": len({r["purchase_document"] for r in records}),
    }
    if rep["e0_found"] != rep["e0_listed"]:
        raise RuntimeError("an E0 line is not in the v1.1 frame")

    strata = Strata(lines)
    labels = [strata.of_record(r) for r in records]
    value = np.array([cents(r["cleared_value"]) for r in records], dtype=np.float64)
    per = [class_flags(r) for r in records]
    flags = {name: np.array([f[name] for f in per], dtype=bool) for name in (*CLASSES, HELD_UNKNOWN)}
    boot = ClusterBootstrap([r["purchase_document"] for r in records], b=b)
    boot_note = {"B": b, "seed": SEED, "generator": "numpy PCG64", "clusters": boot.n,
                 "cluster": "purchase document, sorted by its hashed id", "interval": "percentile 2.5 to 97.5"}

    overall = share_tables(boot, {"all": np.ones(len(records), dtype=bool)}, flags, value)["all"]
    exposure = {"registration": REGISTRATION, "bootstrap": boot_note, "wilson": "95%, shares of clearings",
                "denominator": "all analysed clearings (E0 lines removed); D1 and D2 classes apply to 3-way categories",
                "applicable_clearings": applicable_counts(records)} | overall
    by_stratum = {"registration": REGISTRATION, "bootstrap": boot_note, "cutpoints": strata.cutpoints(),
                  "strata": {var: share_tables(boot, masks, flags, value) for var, masks in cells(labels).items()}}

    sources = Counter(r["cleared_value_source"] for r in records)
    fallback = {"registration": REGISTRATION, "section": "3.4",
                "analysed_clearings": len(records),
                "cleared_value_source": {s: sources.get(s, 0) for s in ("clearing", "invoice_receipt", "line_value")}}
    crosscheck = {"registration": REGISTRATION, "section": "3.1",
                  "rule": "Item Category string differs from the record's string for the flag-derived category",
                  "expected_item_category": {k.value: v for k, v in ITEM_CATEGORY.items()}} | rep["crosscheck"]

    rng = random.Random(SEED)
    picks = sorted(rng.sample(range(len(records)), min(SAMPLE_SIZE, len(records))))
    return {
        "exclusions.json": exclusions,
        "exposure.json": exposure,
        "exposure-by-stratum.json": by_stratum,
        "value-fallback.json": fallback,
        "category-crosscheck.json": crosscheck,
        "coverage-check.json": coverage_check(records),
        "_sample": [records[i] for i in picks],
    }


def run(log: Path, out: Path, e0_path: Path = E0_LINES, min_month_events: int = T_END_MONTH_MIN_EVENTS,
        b: int = BOOTSTRAP_B) -> dict[str, Any]:
    started = time.perf_counter()
    rep = replay(log, read_e0_lines(e0_path), min_month_events)
    write_jsonl_gz(out / "evidence-set.jsonl.gz", rep["records"])
    write_jsonl_gz(out / "lines.jsonl.gz", rep["lines"])
    write_jsonl_gz(out / "lines-t-star-amended.jsonl.gz", rep["lines_amended"])
    replayed = time.perf_counter()
    slots = analyse(rep, log.name, file_sha256(log), b)
    write_jsonl(out / "evidence-sample.jsonl", slots.pop("_sample"))
    for name, obj in slots.items():
        write_json(out / name, obj)
    done = time.perf_counter()
    return {"slots": slots, "seconds": {"replay": replayed - started, "analysis": done - replayed,
                                        "total": done - started},
            "analysed_clearings": len(rep["records"])}


def load(out: Path) -> tuple[list[dict], list[dict]]:
    return read_jsonl_gz(out / "evidence-set.jsonl.gz"), read_jsonl_gz(out / "lines.jsonl.gz")


def load_amended(out: Path) -> dict[str, str | None]:
    """Line status at t* under D-C-2 B, by hashed line id."""
    return {r["case_id"]: r["t_star_status"] for r in read_jsonl_gz(out / "lines-t-star-amended.jsonl.gz")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.e1")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--e0-lines", type=Path, default=E0_LINES)
    parser.add_argument("--min-month-events", type=int, default=T_END_MONTH_MIN_EVENTS)
    parser.add_argument("--bootstrap-b", type=int, default=BOOTSTRAP_B, help="registered: 10000")
    args = parser.parse_args(argv)
    result = run(args.log, args.out, args.e0_lines, args.min_month_events, args.bootstrap_b)
    s = result["seconds"]
    print(f"E1: {result['analysed_clearings']} analysed clearings; replay {s['replay']:.1f} s, "
          f"analysis {s['analysis']:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
