"""E2, consequence (prereg/p7-v1.1.md sections 3.7, 4 and 5).

Reads the E1 evidence set and line table (default results/e1/) and writes to
the output directory (default results/e2/):

  hypotheses.json   H1, H2 and H3 at W = 60: O rate per group, difference (defect
                    minus comparison), clustered bootstrap SE, z and the raw one-sided
                    p = 1 - Phi(z); the H1 all-category comparison beside it and every
                    comparison at W = 30, descriptive (no p). Holm is not applied here.
  confounders.json  per comparison, the O rates of both groups per stratum (2.3),
                    reported beside the estimates and never modelled in.

Holm over H1, H2, H3, H4-Jev and H4-Haiku is applied once H4 exists (after E4).

Usage: python -m experiments.e2 [--e1 results/e1] [--out results/e2]
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np

from experiments.common import (
    BOOTSTRAP_B, STRATA, ClusterBootstrap, Strata, cells, one_sided_p, ratio, write_json,
)
from experiments.e1 import load
from p2p_replay.config import REGISTRATION, ROOT, SEED, W_DAYS, W_SENSITIVITY_DAYS

DEFAULT_E1 = ROOT / "results" / "e1"
DEFAULT_OUT = ROOT / "results" / "e2"
THREE_WAY = ("3-way, invoice after receipt", "3-way, invoice before receipt")
OUTCOME = {W_DAYS: "outcome_w", W_SENSITIVITY_DAYS: "outcome_w_sensitivity"}


def _fails(pid: str) -> Callable[[dict], bool]:
    return lambda r: r["predicates"][pid] == "fail" and pid in r["applicable"]


def _passes(pid: str) -> Callable[[dict], bool]:
    return lambda r: r["predicates"][pid] == "pass" and pid in r["applicable"]


def _all_pass(r: dict) -> bool:
    return r["verdict"] == "allow"


# Each comparison: (defect group, comparison group, records excluded and counted, role).
COMPARISONS: dict[str, dict[str, Any]] = {
    "H1": {
        "claim": "C3", "role": "registered test",
        "defect": "3-way clearings with D1/D2 fail",
        "comparison": "3-way clearings with every applicable predicate passing",
        "d": lambda r: r["category"] in THREE_WAY and _fails("D1")(r),
        "c": lambda r: r["category"] in THREE_WAY and _all_pass(r),
    },
    "H1 all-category comparison": {
        "claim": "C3", "role": "descriptive, beside H1",
        "defect": "3-way clearings with D1/D2 fail",
        "comparison": "clearings of every category with every applicable predicate passing",
        "d": lambda r: r["category"] in THREE_WAY and _fails("D1")(r),
        "c": _all_pass,
    },
    "H2": {
        "claim": "C4", "role": "registered test",
        "defect": "D4 fail, all categories", "comparison": "D4 pass, all categories",
        "d": _fails("D4"), "c": _passes("D4"),
        "excluded": ("D4 unknown", lambda r: r["predicates"]["D4"] == "unknown"),
    },
    "H3": {
        "claim": "C5", "role": "registered test",
        "defect": "D5 fail, all categories", "comparison": "D5 pass, all categories",
        "d": _fails("D5"), "c": _passes("D5"),
        "excluded": ("D5 unknown", lambda r: r["predicates"]["D5"] == "unknown"),
    },
}


def group_columns(records: Sequence[dict]) -> tuple[list[np.ndarray], dict[tuple[str, int, str], int]]:
    columns: list[np.ndarray] = []
    index: dict[tuple[str, int, str], int] = {}
    for name, spec in COMPARISONS.items():
        d = np.array([spec["d"](r) for r in records], dtype=bool)
        c = np.array([spec["c"](r) for r in records], dtype=bool)
        for w, key in OUTCOME.items():
            o = np.array([bool(r[key]) for r in records], dtype=bool)
            for label, arr in (("n_d", d), ("o_d", d & o), ("n_c", c), ("o_c", c & o)):
                index[(name, w, label)] = len(columns)
                columns.append(arr.astype(np.float64))
    return columns, index


def estimate(columns: list[np.ndarray], reps: np.ndarray, at: Callable[[str], int], with_p: bool) -> dict[str, Any]:
    n_d, o_d, n_c, o_c = (int(columns[at(k)].sum()) for k in ("n_d", "o_d", "n_c", "o_c"))
    rate_d, rate_c = ratio(o_d, n_d), ratio(o_c, n_c)
    diff = rate_d - rate_c if rate_d is not None and rate_c is not None else None
    bn_d, bo_d, bn_c, bo_c = (reps[:, at(k)] for k in ("n_d", "o_d", "n_c", "o_c"))
    ok = (bn_d > 0) & (bn_c > 0)
    out: dict[str, Any] = {
        "defect_group": {"clearings": n_d, "with_O": o_d, "O_rate": rate_d},
        "comparison_group": {"clearings": n_c, "with_O": o_c, "O_rate": rate_c},
        "difference": diff,
        "bootstrap_resamples_used": int(ok.sum()),
    }
    empty = [g for g, n in (("defect group", n_d), ("comparison group", n_c)) if n == 0]
    if empty:
        out["not_computable"] = f"{' and '.join(empty)} has no analysed clearings"
    if ok.sum() > 1 and diff is not None:
        boot = bo_d[ok] / bn_d[ok] - bo_c[ok] / bn_c[ok]
        se = float(np.std(boot, ddof=1))
        out["bootstrap_se"] = se
        out["bootstrap95"] = [float(x) for x in np.percentile(boot, [2.5, 97.5])]
        if with_p:
            z = diff / se if se > 0 else None
            out["z"] = z
            out["p_one_sided_raw"] = one_sided_p(z) if z is not None and math.isfinite(z) else None
    else:
        out["bootstrap_se"] = None
    return out


def confounders(records: Sequence[dict], labels: Sequence[dict[str, str]]) -> dict[str, Any]:
    masks = cells(labels)
    outcome = {w: np.array([bool(r[key]) for r in records], dtype=bool) for w, key in OUTCOME.items()}
    out: dict[str, Any] = {}
    for name, spec in COMPARISONS.items():
        d = np.array([spec["d"](r) for r in records], dtype=bool)
        c = np.array([spec["c"](r) for r in records], dtype=bool)
        table: dict[str, Any] = {}
        for var in STRATA:
            rows = {}
            for value, m in masks[var].items():
                row = {}
                for w, o in outcome.items():
                    nd, od = int((m & d).sum()), int((m & d & o).sum())
                    nc, oc = int((m & c).sum()), int((m & c & o).sum())
                    rd, rc = ratio(od, nd), ratio(oc, nc)
                    row[f"W{w}"] = {"defect_clearings": nd, "defect_with_O": od, "defect_O_rate": rd,
                                    "comparison_clearings": nc, "comparison_with_O": oc, "comparison_O_rate": rc,
                                    "difference": rd - rc if rd is not None and rc is not None else None}
                rows[value] = row
            table[var] = rows
        out[name] = table
    return out


def analyse(records: list[dict], lines: list[dict], b: int = BOOTSTRAP_B) -> dict[str, Any]:
    strata = Strata(lines)
    labels = [strata.of_record(r) for r in records]
    columns, index = group_columns(records)
    boot = ClusterBootstrap([r["purchase_document"] for r in records], b=b)
    reps = boot.totals(columns)
    estimates: dict[str, Any] = {}
    for name, spec in COMPARISONS.items():
        entry: dict[str, Any] = {"claim": spec["claim"], "role": spec["role"],
                                 "defect_group_definition": spec["defect"],
                                 "comparison_group_definition": spec["comparison"]}
        if "excluded" in spec:
            label, rule = spec["excluded"]
            entry["excluded"] = {"rule": label, "clearings": sum(1 for r in records if rule(r))}
        for w in OUTCOME:
            registered = spec["role"] == "registered test" and w == W_DAYS
            est = estimate(columns, reps, lambda k, name=name, w=w: index[(name, w, k)], with_p=registered)
            est["status"] = "registered test, W = 60 (primary)" if registered else "descriptive"
            entry[f"W{w}"] = est
        estimates[name] = entry
    hypotheses = {
        "registration": REGISTRATION,
        "statistic": "difference in O rate, defect group minus comparison group; SE = standard deviation "
                     "(ddof 1) of the difference over the bootstrap resamples; z = difference / SE; "
                     "one-sided p = 1 - Phi(z)",
        "bootstrap": {"B": b, "seed": SEED, "generator": "numpy PCG64", "clusters": boot.n,
                      "cluster": "purchase document, sorted by its hashed id"},
        "analysed_clearings": len(records),
        "holm": {"family": ["H1", "H2", "H3", "H4-Jev", "H4-Haiku"], "alpha": 0.05, "applied": False,
                 "status": "deferred: Holm over the five-test family is applied once H4-Jev and H4-Haiku "
                           "exist (after E4); the p-values here are raw"},
        "estimates": estimates,
    }
    return {"hypotheses.json": hypotheses,
            "confounders.json": {"registration": REGISTRATION, "cutpoints": strata.cutpoints(),
                                 "note": "reported beside every estimate, never modelled in",
                                 "comparisons": confounders(records, labels)}}


def run(e1_dir: Path, out: Path, b: int = BOOTSTRAP_B) -> dict[str, Any]:
    records, lines = load(e1_dir)
    slots = analyse(records, lines, b)
    for name, obj in slots.items():
        write_json(out / name, obj)
    return slots


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.e2")
    parser.add_argument("--e1", type=Path, default=DEFAULT_E1)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--bootstrap-b", type=int, default=BOOTSTRAP_B, help="registered: 10000")
    args = parser.parse_args(argv)
    slots = run(args.e1, args.out, args.bootstrap_b)
    for name in ("H1", "H2", "H3"):
        e = slots["hypotheses.json"]["estimates"][name]["W60"]
        print(f"E2 {name}: difference {e['difference']}, raw one-sided p {e.get('p_one_sided_raw')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
