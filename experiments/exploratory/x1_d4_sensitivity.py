"""X1, exploratory: sensitivity of the exposure to D4's approval anchor, and the materiality of the changes
D4 counts (DECISIONS.md D-G-1 a). Not registered; no p-value; never in the Holm family.

D4 (registered) fails when a `Change Price` or `Change Quantity` falls after the line's last
approval-bearing event before t_c, and the registered approval-bearing list includes the line's creation.
For every analysed clearing this script reads, from the log, what the evidence set does not keep: the
kind of that last approval-bearing event (the creation, or an explicit approval or release event: the
registered list minus the creation), whether any explicit event precedes t_c, and the
`Cumulative net worth (EUR)` carried by each change D4 counts and by the event before it. It joins these
to the committed evidence set (results/e1/evidence-set.jsonl.gz) and reports, over all analysed
clearings and by category:

  (a) the registered exposure: at least one failed predicate, as committed;
  (b) the exposure when D4 counts only changes after an explicit approval or release event;
  (c) the complement: D4 failures whose only approval-bearing event before t_c is the creation;

each in count and cleared value with Wilson and purchase-document-clustered bootstrap intervals
(B = 10,000, seed 20261201, as registered for E1); H2 recomputed descriptively under (b) (O rates at
W = 60, difference, clustered interval, no p-value); and materiality: the value differences the changes
carry, and the exposure when D4 failures are restricted to relative changes above 0, 1%, 5% and 10%
(unregistered thresholds). The values in this log are in effect a line attribute repeated on every
event, so a per-change difference is observable for very few changes; the slot says exactly how many,
and the thresholds apply to those only.

Writes results/exploratory/d4-sensitivity.json.

Usage: python -m experiments.exploratory.x1_d4_sensitivity [--log data/BPI_Challenge_2019.xes]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from experiments.common import (BOOTSTRAP_B, E0_LINES, ClusterBootstrap, cents, ratio, read_e0_lines,
                                read_jsonl_gz, write_json)
from experiments.e1 import DEFAULT_LOG, hashed, share_tables
from experiments.e2 import estimate
from p2p_replay.config import REGISTRATION, ROOT, SEED, T_END_MONTH_MIN_EVENTS, W_DAYS, load_mapping, load_patterns
from p2p_replay.frame import classify
from p2p_replay.predicates import last_approval
from p2p_replay.reader import read_log
from p2p_replay.replay import observation_end

OUT = ROOT / "results" / "exploratory" / "d4-sensitivity.json"
THRESHOLDS = ((0.0, "0"), (0.01, "1%"), (0.05, "5%"), (0.10, "10%"))
QUANTILES = (10, 25, 50, 75, 90, 99)
FLAGS = ("registered", "explicit_only", "creation_only_d4") + tuple(f"threshold_{lab}" for _, lab in THRESHOLDS)


def scan(log: Path, e0_path: Path = E0_LINES, min_month_events: int = T_END_MONTH_MIN_EVENTS) -> dict[tuple, dict]:
    """Per analysed clearing, keyed (hashed line id, t_c, occurrence): the D4 anchor and the changes' values."""
    mapping = load_mapping("bpi2019")
    p, _ = load_patterns()
    flag_true = mapping.get("flag_true", ["true"])
    end = observation_end(read_log(log, mapping), min_month_events)
    e0 = read_e0_lines(e0_path)
    explicit_kinds = set(p.approval_bearing) - {p.creation}
    out: dict[tuple, dict] = {}
    for case in read_log(log, mapping):
        case = case.truncated(end.t_end)
        frame = classify(case, p, flag_true, end.t_end, W_DAYS)
        if not frame.framed or case.case_id in e0:
            continue
        key_line = hashed(case.case_id)
        seen: Counter = Counter()
        for clearing in frame.analysed:
            events = case.upto(clearing.ts)
            approved = last_approval(events, p)
            explicit = [e.ts for e in events if e.activity in explicit_kinds]
            last_explicit = max(explicit) if explicit else None
            counted = [i for i, e in enumerate(events) if approved is not None and e.activity in p.changes and e.ts > approved]
            deltas = []
            for i in counted:
                prev = next((events[j].value for j in range(i - 1, -1, -1) if events[j].value is not None), None)
                v = events[i].value
                if prev is not None and v is not None:
                    deltas.append((abs(v - prev), abs(v - prev) / abs(prev) if prev else None))
            t_c = clearing.ts.isoformat()
            seen[t_c] += 1
            out[(key_line, t_c, seen[t_c])] = {
                "d4_fail": bool(counted),
                "anchor": None if approved is None else ("explicit" if last_explicit == approved else "creation"),
                "explicit_before_t_c": last_explicit is not None,
                "d4_explicit_fail": last_explicit is not None and any(
                    e.activity in p.changes and e.ts > last_explicit for e in events),
                "changes_counted": len(counted),
                "changes_with_values": len(deltas),
                "max_abs_change": max((d[0] for d in deltas), default=None),
                "max_rel_change": max((d[1] for d in deltas if d[1] is not None), default=None),
            }
    return out


def _quantiles(values: list[float]) -> dict[str, float] | None:
    if not values:
        return None
    return {f"p{q}": float(v) for q, v in zip(QUANTILES, np.percentile(np.asarray(values, dtype=np.float64), QUANTILES))}


def analyse(records: list[dict], scanned: dict[tuple, dict], b: int = BOOTSTRAP_B,
            results_dir: Path = ROOT / "results") -> dict[str, Any]:
    seen: Counter = Counter()
    joined = []
    for r in records:
        seen[(r["case_id"], r["t_c"])] += 1
        s = scanned[(r["case_id"], r["t_c"], seen[(r["case_id"], r["t_c"])])]
        if s["d4_fail"] != (r["predicates"]["D4"] == "fail"):
            raise RuntimeError("the scan's D4 differs from the registered evidence set")
        joined.append(s)
    flags: dict[str, np.ndarray] = defaultdict(lambda: np.zeros(len(records), dtype=bool))
    for i, (r, s) in enumerate(zip(records, joined)):
        others = any(d != "D4" for d in r["failed"])
        d4 = r["predicates"]["D4"] == "fail" and "D4" in r["applicable"]
        flags["registered"][i] = bool(r["defective"])
        flags["explicit_only"][i] = others or (s["d4_explicit_fail"] and "D4" in r["applicable"])
        flags["creation_only_d4"][i] = d4 and not s["explicit_before_t_c"]
        for t, lab in THRESHOLDS:
            flags[f"threshold_{lab}"][i] = others or (d4 and s["max_rel_change"] is not None and s["max_rel_change"] > t)
    flags = {k: flags[k] for k in FLAGS}
    value = np.array([cents(r["cleared_value"]) for r in records], dtype=np.float64)
    masks = {"all": np.ones(len(records), dtype=bool)}
    for cat in sorted({r["category"] for r in records}):
        masks[cat] = np.array([r["category"] == cat for r in records], dtype=bool)
    boot = ClusterBootstrap([r["purchase_document"] for r in records], b=b)
    tables = share_tables(boot, masks, flags, value)

    # H2 under (b), descriptive: D4 (explicit anchor) fail against pass, D4 unknown excluded as registered.
    known = np.array([r["predicates"]["D4"] != "unknown" for r in records], dtype=bool)
    d = np.array([s["d4_explicit_fail"] for s in joined], dtype=bool) & known
    c = ~d & known
    o = np.array([bool(r["outcome_w"]) for r in records], dtype=bool)
    columns = [x.astype(np.float64) for x in (d, d & o, c, c & o)]
    names = ("n_d", "o_d", "n_c", "o_c")
    h2 = estimate(columns, boot.totals(columns), lambda k: names.index(k), with_p=False)
    registered_h2 = json.loads((results_dir / "e2" / "hypotheses.json").read_text(encoding="utf-8"))
    registered_h2 = registered_h2["estimates"]["H2"][f"W{W_DAYS}"]

    d4 = [s for r, s in zip(records, joined) if s["d4_fail"]]
    anchors = Counter(s["anchor"] for s in d4)
    with_values = [s for s in d4 if s["changes_with_values"]]
    nonzero = [s for s in with_values if s["max_abs_change"]]
    materiality = {
        "what_the_values_allow": (
            f"the value field is in effect a line attribute repeated on every event: of {len(d4):,} D4 failures, "
            f"{len(nonzero):,} have a counted change whose value differs from the event before it; for the other "
            f"{len(d4) - len(nonzero):,} no per-change difference is observable, and they count as not above any threshold"),
        "d4_failures": len(d4),
        "d4_failures_with_values_on_counted_changes": len(with_values),
        "d4_failures_with_an_observable_nonzero_change": len(nonzero),
        "abs_change_eur_quantiles_over_observable": _quantiles([s["max_abs_change"] for s in nonzero]),
        "rel_change_quantiles_over_observable": _quantiles([s["max_rel_change"] for s in nonzero
                                                            if s["max_rel_change"] is not None]),
        "quantiles": list(QUANTILES),
        "per_clearing": "the largest absolute and relative difference over the changes D4 counts",
        "thresholds": [{"label": lab, "relative_change_above": t, "unregistered": True,
                        "exposure": tables["all"]["classes"][f"threshold_{lab}"]} for t, lab in THRESHOLDS],
    }
    return {
        "exploratory": True, "label": "exploratory, not registered; no p-value; not in the Holm family",
        "registration": REGISTRATION, "decision": "DECISIONS.md D-G-1 a",
        "definitions": {
            "registered": "at least one failed applicable predicate, as committed (results/e1/exposure.json)",
            "explicit_only": "as registered, but D4 fails only for a change after the last explicit approval or "
                             "release event (the registered approval-bearing list minus the creation) before t_c",
            "creation_only_d4": "D4 failures with no explicit approval or release event before t_c: the creation "
                                "is the only approval-bearing event",
            "threshold_X": "as registered, but a D4 failure counts only if a change D4 counts carries an observable "
                           "relative value difference above X (unregistered thresholds)",
        },
        "bootstrap": {"B": b, "seed": SEED, "generator": "numpy PCG64", "clusters": boot.n,
                      "cluster": "purchase document, sorted by its hashed id", "interval": "percentile 2.5 to 97.5"},
        "d4_failures_by_anchor_kind": dict(sorted(anchors.items())),
        "exploratory_all": tables["all"]["classes"] | {"analysed_clearings": tables["all"]["analysed_clearings"]},
        "exploratory_by_category": {k: v for k, v in tables.items() if k != "all"},
        "exploratory_h2_explicit_only": {"W": W_DAYS, **h2, "registered_h2": {
            "defect_O_rate": registered_h2["defect_group"]["O_rate"],
            "comparison_O_rate": registered_h2["comparison_group"]["O_rate"],
            "difference": registered_h2["difference"]}},
        "exploratory_materiality": materiality,
    }


def run(log: Path = DEFAULT_LOG, results_dir: Path = ROOT / "results", out: Path = OUT, e0_path: Path = E0_LINES,
        min_month_events: int = T_END_MONTH_MIN_EVENTS, b: int = BOOTSTRAP_B) -> dict[str, Any]:
    """results_dir holds the e1/ and e2/ slots read (the committed ones, or a reproduction's regenerated ones)."""
    doc = analyse(read_jsonl_gz(results_dir / "e1" / "evidence-set.jsonl.gz"), scan(log, e0_path, min_month_events), b,
                  results_dir)
    write_json(out, doc)
    return doc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.exploratory.x1_d4_sensitivity")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    doc = run(args.log, out=args.out)
    a = doc["exploratory_all"]
    for k in ("registered", "explicit_only", "creation_only_d4"):
        print(f"X1 {k}: {a[k]['clearings']} clearings, {a[k]['share_of_clearings']:.4f}, value {a[k]['share_of_value']:.4f}")
    print("X1", doc["exploratory_materiality"]["what_the_values_allow"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
