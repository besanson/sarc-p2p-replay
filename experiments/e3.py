"""E3, gate effect, and the human hold (prereg/p7-v1.1.md sections 3.6, 3.8 and 6, E3).

Reads the E1 evidence set and line table (default results/e1/) and writes to
the output directory (default results/e3/):

  gate-held.json           share of analysed clearings the gate would have held, in count
                           (Wilson and clustered bootstrap) and cleared value (clustered bootstrap)
  verdict-by-outcome.json  the 2 x 2 table verdict x O in count and cleared value, at W = 60
                           and W = 30: holds with a corrective after, holds without, allows
                           with, allows without
  lag-bands.json           D1/D2 failures by lag band (3.8) in count and cleared value
  human-hold.json          the 3.6 classification of every framed line (E0 lines removed),
                           the unclassified count, and the human hold rate on defective and
                           on clean lines (gate status at the E4 decision point t*, section 7),
                           under the literal reading and under D-C-2 B
  confounders.json         the same quantities per stratum (2.3), beside, never modelled in

Usage: python -m experiments.e3 [--e1 results/e1] [--out results/e3]
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from experiments.common import (
    BOOTSTRAP_B, STRATA, ClusterBootstrap, Strata, cells, cents, eur, percentile95, ratio, wilson, write_json,
)
from experiments.e1 import load, load_amended
from p2p_replay.config import REGISTRATION, ROOT, SEED, W_DAYS, W_SENSITIVITY_DAYS
from p2p_replay.outcome import ABSENT, LAG_BANDS, STALE

DEFAULT_E1 = ROOT / "results" / "e1"
DEFAULT_OUT = ROOT / "results" / "e3"
OUTCOME = {W_DAYS: "outcome_w", W_SENSITIVITY_DAYS: "outcome_w_sensitivity"}
CELLS = {
    "hold_with_corrective": ("hold", True),
    "hold_without_corrective": ("hold", False),
    "allow_with_corrective": ("allow", True),
    "allow_without_corrective": ("allow", False),
}
LINE_STATUSES = ("defective", "clean", "held_unknown")


def gate_held(records: Sequence[dict], value: np.ndarray, b: int) -> dict[str, Any]:
    held = np.array([r["verdict"] == "hold" for r in records], dtype=bool)
    every = np.ones(len(records), dtype=np.float64)
    boot = ClusterBootstrap([r["purchase_document"] for r in records], b=b)
    reps = boot.totals([every, value, held.astype(np.float64), np.where(held, value, 0.0)])
    n, k = len(records), int(held.sum())
    v, kv = int(value.sum()), int(value[held].sum())
    return {
        "registration": REGISTRATION,
        "bootstrap": {"B": b, "seed": SEED, "generator": "numpy PCG64", "clusters": boot.n,
                      "cluster": "purchase document, sorted by its hashed id", "interval": "percentile 2.5 to 97.5"},
        "analysed_clearings": n,
        "held": {
            "clearings": k, "share_of_clearings": ratio(k, n), "wilson95": wilson(k, n),
            "bootstrap95": percentile95(reps[:, 2], reps[:, 0])["interval"],
            "cleared_value_eur": eur(kv), "share_of_value": ratio(kv, v),
            "value_bootstrap95": percentile95(reps[:, 3], reps[:, 1])["interval"],
        },
        "held_with_a_failed_predicate": sum(1 for r in records if r["verdict"] == "hold" and r["defective"]),
        "held_unknown_only": sum(1 for r in records if r["verdict"] == "hold" and not r["defective"]),
        "cleared_value_eur": eur(v),
    }


def cell_masks(records: Sequence[dict]) -> dict[tuple[int, str], np.ndarray]:
    return {(w, name): np.array([r["verdict"] == verdict and bool(r[key]) == corrective for r in records], dtype=bool)
            for w, key in OUTCOME.items() for name, (verdict, corrective) in CELLS.items()}


def two_by_two(cm: dict[tuple[int, str], np.ndarray], value: np.ndarray, mask: np.ndarray | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for w in OUTCOME:
        table = {}
        for name in CELLS:
            sel = cm[(w, name)] if mask is None else cm[(w, name)] & mask
            table[name] = {"clearings": int(sel.sum()), "cleared_value_eur": eur(int(value[sel].sum()))}
        out[f"W{w}"] = table
    return out


def lag_bands(records: Sequence[dict], value: np.ndarray) -> dict[str, Any]:
    failed = [i for i, r in enumerate(records) if r["receipt_class"] is not None]
    bands = {}
    for band in LAG_BANDS:
        idx = [i for i in failed if records[i]["lag_band"] == band]
        bands[band] = {"clearings": len(idx), "cleared_value_eur": eur(int(value[idx].sum())) if idx else 0.0}
    classes = Counter(records[i]["receipt_class"] for i in failed)
    return {"registration": REGISTRATION, "section": "3.8",
            "unit": "analysed clearings with D1/D2 fail; lag from t_c to the first uncancelled receipt after t_c, "
                    "up to T_end",
            "clearings": len(failed),
            "bands": bands,
            "receipt_class": {STALE: classes.get(STALE, 0), ABSENT: classes.get(ABSENT, 0)}}


def hold_rates(lines: Sequence[dict], status: Sequence[str | None]) -> dict[str, Any]:
    out = {}
    for s in LINE_STATUSES:
        group = [l for l, st in zip(lines, status) if st == s and l["human_hold"] is not None]
        held = sum(1 for l in group if l["human_hold"])
        out[s] = {"classified_lines": len(group), "held_by_people": held,
                  "human_hold_rate": ratio(held, len(group))}
    d, c = out["defective"]["human_hold_rate"], out["clean"]["human_hold_rate"]
    out["difference_defective_minus_clean"] = d - c if d is not None and c is not None else None
    return out


RULES = {
    "registered_literal_reading": "gate verdict at the E4 decision point t* (section 7): defective if at least one "
                                  "applicable predicate fails, clean if every applicable predicate passes, otherwise "
                                  "held_unknown; at a t* with no clearing D5 is unknown (no clearing actor)",
    "amended_reading_D-C-2": "as the literal reading, except that at a t* that is not a clearing D5 is not "
                             "applicable and counts as pass (DECISIONS.md D-C-2 B; prereg/DEVIATIONS.md)",
}


def readings(lines: Sequence[dict], amended: dict[str, str | None]) -> dict[str, list[str | None]]:
    return {"registered_literal_reading": [l["t_star_status"] for l in lines],
            "amended_reading_D-C-2": [amended[l["case_id"]] for l in lines]}


def human_hold(lines: Sequence[dict], amended: dict[str, str | None]) -> dict[str, Any]:
    classified = [l for l in lines if l["human_hold"] is not None]
    out: dict[str, Any] = {
        "registration": REGISTRATION, "section": "3.6",
        "framed_lines": len(lines),
        "held_by_people": sum(1 for l in classified if l["human_hold"]),
        "released_by_people": sum(1 for l in classified if not l["human_hold"]),
        "unclassified_no_invoice_receipt_by_t_end_minus_w": len(lines) - len(classified),
    }
    for name, status in readings(lines, amended).items():
        counts = Counter(s or "no_invoice_receipt" for s in status)
        out[name] = {
            "line_status_rule": RULES[name],
            "gate_status_at_t_star": {k: counts.get(k, 0) for k in (*LINE_STATUSES, "no_invoice_receipt")},
            "by_gate_status_at_t_star": hold_rates(lines, status),
        }
    return out


def confounders(records: Sequence[dict], lines: Sequence[dict], amended: dict[str, str | None], strata: Strata,
                value: np.ndarray) -> dict[str, Any]:
    rec_masks = cells([strata.of_record(r) for r in records])
    line_labels = [strata.of_line(l, l["t_star"][:7] if l["t_star"] else None) for l in lines]
    line_masks = cells(line_labels)
    clearing_tables: dict[str, Any] = {}
    line_tables: dict[str, Any] = {}
    held = np.array([r["verdict"] == "hold" for r in records], dtype=bool)
    cm = cell_masks(records)
    by_reading = readings(lines, amended)
    for var in STRATA:
        clearing_tables[var] = {}
        for label, m in rec_masks[var].items():
            n, k = int(m.sum()), int((m & held).sum())
            clearing_tables[var][label] = {
                "analysed_clearings": n, "held": k, "held_share": ratio(k, n),
                "cleared_value_eur": eur(int(value[m].sum())),
                "held_value_eur": eur(int(value[m & held].sum())),
                "verdict_by_outcome": two_by_two(cm, value, m),
            }
        line_tables[var] = {
            label: {name: hold_rates([l for l, keep in zip(lines, m) if keep],
                                     [s for s, keep in zip(status, m) if keep])
                    for name, status in by_reading.items()}
            for label, m in line_masks[var].items()}
    return {"registration": REGISTRATION, "cutpoints": strata.cutpoints(),
            "note": "reported beside every estimate, never modelled in; for lines, month is the month of t*",
            "clearings": clearing_tables, "human_hold_lines": line_tables}


def analyse(records: list[dict], lines: list[dict], amended: dict[str, str | None],
            b: int = BOOTSTRAP_B) -> dict[str, Any]:
    strata = Strata(lines)
    value = np.array([cents(r["cleared_value"]) for r in records], dtype=np.float64)
    return {
        "gate-held.json": gate_held(records, value, b),
        "verdict-by-outcome.json": {"registration": REGISTRATION, "section": "6, E3",
                                    "analysed_clearings": len(records),
                                    "cells": "corrective = O (section 3.7) within W after t_c",
                                    "table": two_by_two(cell_masks(records), value)},
        "lag-bands.json": lag_bands(records, value),
        "human-hold.json": human_hold(lines, amended),
        "confounders.json": confounders(records, lines, amended, strata, value),
    }


def run(e1_dir: Path, out: Path, b: int = BOOTSTRAP_B) -> dict[str, Any]:
    records, lines = load(e1_dir)
    slots = analyse(records, lines, load_amended(e1_dir), b)
    for name, obj in slots.items():
        write_json(out / name, obj)
    return slots


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.e3")
    parser.add_argument("--e1", type=Path, default=DEFAULT_E1)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--bootstrap-b", type=int, default=BOOTSTRAP_B, help="registered: 10000")
    args = parser.parse_args(argv)
    slots = run(args.e1, args.out, args.bootstrap_b)
    held = slots["gate-held.json"]["held"]
    print(f"E3: gate would have held {held['clearings']} of {slots['gate-held.json']['analysed_clearings']} clearings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
