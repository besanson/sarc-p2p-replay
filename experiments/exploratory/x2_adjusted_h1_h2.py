"""X2, exploratory: directly standardised H1 and H2 at W = 60 (DECISIONS.md D-G-1 e). Not registered; no
p-value; never in the Holm family; no regression.

For H1 (3-way clearings with D1/D2 fail against 3-way clearings with every applicable predicate passing)
and H2 (D4 fail against D4 pass), with the groups of the registered E2 (experiments/e2.py), and for each of
three stratifications (category x line-value quartile; spend area; month of t_c): the stratum-specific O
rates and differences, and the difference standardised to the comparison group's stratum distribution,

    sum over strata s of w_s * (rate_defect,s - rate_comparison,s),  w_s = n_comparison,s / sum n_comparison,

over the strata that have both defect and comparison clearings; strata with no defect clearings are listed
with their weight and excluded, and the weights renormalised over the strata kept. The interval is the
purchase-document-clustered bootstrap percentile interval (B = 10,000, seed 20261201, as registered for
E2), the weights recomputed in each resample over the kept strata that have clearings of both groups in it.
The registered unadjusted difference is reported beside each.

Writes results/exploratory/adjusted-h1-h2.json.

Usage: python -m experiments.exploratory.x2_adjusted_h1_h2
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from experiments.common import BOOTSTRAP_B, ClusterBootstrap, Strata, ratio, write_json
from experiments.e1 import load
from experiments.e2 import COMPARISONS, OUTCOME
from p2p_replay.config import REGISTRATION, ROOT, SEED, W_DAYS

OUT = ROOT / "results" / "exploratory" / "adjusted-h1-h2.json"
TESTS = ("H1", "H2")
STRATIFICATIONS = {
    "category x line-value quartile": lambda lab: f"{lab['category']} | {lab['line_value_quartile']}",
    "spend area": lambda lab: lab["spend_area"],
    "month of t_c": lambda lab: lab["month"],
}


def standardise(rates: dict[str, tuple[int, int, int, int]]) -> tuple[float | None, list[str], dict[str, float]]:
    """(standardised difference, strata kept, weight of every stratum in the comparison distribution)."""
    total = sum(n_c for _, _, n_c, _ in rates.values())
    weights = {s: (n_c / total if total else 0.0) for s, (_, _, n_c, _) in rates.items()}
    kept = [s for s, (n_d, _, n_c, _) in rates.items() if n_d > 0 and n_c > 0]
    w = sum(rates[s][2] for s in kept)
    if not kept or not w:
        return None, kept, weights
    diff = sum(rates[s][2] / w * (rates[s][1] / rates[s][0] - rates[s][3] / rates[s][2]) for s in kept)
    return diff, kept, weights


def analyse(records: list[dict], lines: list[dict], b: int = BOOTSTRAP_B,
            results_dir: Path = ROOT / "results") -> dict[str, Any]:
    strata = Strata(lines)
    labels = [strata.of_record(r) for r in records]
    o = np.array([bool(r[OUTCOME[W_DAYS]]) for r in records], dtype=bool)
    boot = ClusterBootstrap([r["purchase_document"] for r in records], b=b)
    registered = json.loads((results_dir / "e2" / "hypotheses.json").read_text(encoding="utf-8"))["estimates"]
    estimates: dict[str, Any] = {}
    for test in TESTS:
        spec = COMPARISONS[test]
        d = np.array([spec["d"](r) for r in records], dtype=bool)
        c = np.array([spec["c"](r) for r in records], dtype=bool)
        block: dict[str, Any] = {"defect": spec["defect"], "comparison": spec["comparison"],
                                 "registered_unadjusted_difference": registered[test][f"W{W_DAYS}"]["difference"],
                                 "standardised": {}}
        for name, key in STRATIFICATIONS.items():
            column = [key(lab) for lab in labels]
            cells = sorted(set(column))
            masks = {s: np.fromiter((x == s for x in column), dtype=bool, count=len(column)) for s in cells}
            rates = {s: (int((m & d).sum()), int((m & d & o).sum()), int((m & c).sum()), int((m & c & o).sum()))
                     for s, m in masks.items()}
            diff, kept, weights = standardise(rates)
            cols = []
            for s in kept:
                m = masks[s]
                cols += [(m & d).astype(np.float64), (m & d & o).astype(np.float64),
                         (m & c).astype(np.float64), (m & c & o).astype(np.float64)]
            reps = boot.totals(cols) if cols else np.zeros((0, 0))
            per_rep = []
            for row in reps:
                q = {s: tuple(int(round(x)) for x in row[4 * i:4 * i + 4]) for i, s in enumerate(kept)}
                v, _, _ = standardise(q)
                if v is not None:
                    per_rep.append(v)
            iv = [float(x) for x in np.percentile(per_rep, [2.5, 97.5])] if per_rep else None
            block["standardised"][name] = {
                "standardised_difference": diff, "bootstrap95": iv, "bootstrap_resamples_used": len(per_rep),
                "strata": {s: {"defect_clearings": rates[s][0], "defect_with_O": rates[s][1],
                               "defect_O_rate": ratio(rates[s][1], rates[s][0]),
                               "comparison_clearings": rates[s][2], "comparison_with_O": rates[s][3],
                               "comparison_O_rate": ratio(rates[s][3], rates[s][2]),
                               "difference": (rates[s][1] / rates[s][0] - rates[s][3] / rates[s][2])
                               if rates[s][0] and rates[s][2] else None,
                               "comparison_weight": weights[s], "kept": s in kept} for s in cells},
                "excluded_strata": {s: weights[s] for s in cells if s not in kept},
                "excluded_comparison_weight": sum(weights[s] for s in cells if s not in kept),
            }
        estimates[test] = block
    return {
        "exploratory": True, "label": "exploratory, not registered; no p-value; not in the Holm family; no regression",
        "registration": REGISTRATION, "decision": "DECISIONS.md D-G-1 e", "W": W_DAYS,
        "method": "direct standardisation to the comparison group's stratum distribution, over the strata with "
                  "defect and comparison clearings, weights renormalised; excluded strata listed with their weight",
        "bootstrap": {"B": b, "seed": SEED, "generator": "numpy PCG64", "clusters": boot.n,
                      "cluster": "purchase document, sorted by its hashed id", "interval": "percentile 2.5 to 97.5"},
        "cutpoints": strata.cutpoints(),
        "exploratory_estimates": estimates,
    }


def run(results_dir: Path = ROOT / "results", out: Path = OUT, b: int = BOOTSTRAP_B) -> dict[str, Any]:
    """results_dir holds the e1/ and e2/ slots read (the committed ones, or a reproduction's regenerated ones)."""
    records, lines = load(results_dir / "e1")
    doc = analyse(records, lines, b, results_dir)
    write_json(out, doc)
    return doc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.exploratory.x2_adjusted_h1_h2")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    doc = run(out=args.out)
    for test, block in doc["exploratory_estimates"].items():
        for name, e in block["standardised"].items():
            print(f"X2 {test} {name}: {e['standardised_difference']} {e['bootstrap95']} "
                  f"(registered {block['registered_unadjusted_difference']:.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
