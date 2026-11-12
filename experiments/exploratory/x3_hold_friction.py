"""X3, exploratory: hold friction, the share of gate holds followed by no corrective (DECISIONS.md D-G-1 g).
Not registered; no p-value; never in the Holm family; no cost or time assumption anywhere.

From the committed evidence set: among the analysed clearings the gate would have held, the share with and
without a corrective event within W = 60 days and W = 30 days, in count and in cleared value, overall and
by item category and line-value quartile, with purchase-document-clustered bootstrap intervals
(B = 10,000, seed 20261201). The overall counts equal the registered verdict-by-outcome table
(results/e3/verdict-by-outcome.json); the script stops if they do not. Review cost, resolution time and
similar quantities are not computed: the log carries no parameter for them.

Writes results/exploratory/hold-friction.json.

Usage: python -m experiments.exploratory.x3_hold_friction
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from experiments.common import BOOTSTRAP_B, ClusterBootstrap, Strata, cents, eur, percentile95, ratio, write_json
from experiments.e1 import load
from experiments.e2 import OUTCOME
from p2p_replay.config import REGISTRATION, ROOT, SEED

OUT = ROOT / "results" / "exploratory" / "hold-friction.json"


def analyse(records: list[dict], lines: list[dict], b: int = BOOTSTRAP_B,
            results_dir: Path = ROOT / "results") -> dict[str, Any]:
    strata = Strata(lines)
    labels = [strata.of_record(r) for r in records]
    hold = np.array([r["verdict"] == "hold" for r in records], dtype=bool)
    value = np.array([cents(r["cleared_value"]) for r in records], dtype=np.float64)
    masks: dict[str, dict[str, np.ndarray]] = {"overall": {"all": np.ones(len(records), dtype=bool)}}
    for var in ("category", "line_value_quartile"):
        column = [lab[var] for lab in labels]
        masks[var] = {v: np.fromiter((x == v for x in column), dtype=bool, count=len(column)) for v in sorted(set(column))}
    boot = ClusterBootstrap([r["purchase_document"] for r in records], b=b)
    committed = json.loads((results_dir / "e3" / "verdict-by-outcome.json").read_text(encoding="utf-8"))["table"]
    out: dict[str, Any] = {}
    for w, key in OUTCOME.items():
        o = np.array([bool(r[key]) for r in records], dtype=bool)
        cells = [(var, v, m) for var, group in masks.items() for v, m in group.items()]
        cols = []
        for _, _, m in cells:
            h, hn = m & hold, m & hold & ~o
            cols += [h.astype(np.float64), hn.astype(np.float64), np.where(h, value, 0.0), np.where(hn, value, 0.0)]
        reps = boot.totals(cols)
        per: dict[str, Any] = {}
        for i, (var, v, m) in enumerate(cells):
            h, hn = m & hold, m & hold & ~o
            n, k = int(h.sum()), int(hn.sum())
            vn, vk = int(value[h].sum()), int(value[hn].sum())
            per.setdefault(var, {})[v] = {
                "holds": n, "with_corrective": n - k, "without_corrective": k,
                "share_without_corrective": ratio(k, n), "share_with_corrective": ratio(n - k, n),
                "bootstrap95": percentile95(reps[:, 4 * i + 1], reps[:, 4 * i])["interval"],
                "held_value_eur": eur(vn), "value_without_corrective_eur": eur(vk),
                "value_share_without_corrective": ratio(vk, vn),
                "value_bootstrap95": percentile95(reps[:, 4 * i + 3], reps[:, 4 * i + 2])["interval"],
            }
        all_ = per["overall"]["all"]
        table = committed[f"W{w}"]
        if (all_["with_corrective"], all_["without_corrective"]) != (table["hold_with_corrective"]["clearings"],
                                                                      table["hold_without_corrective"]["clearings"]):
            raise RuntimeError(f"hold counts at W = {w} differ from results/e3/verdict-by-outcome.json")
        out[f"W{w}"] = per
    return {
        "exploratory": True, "label": "exploratory, not registered; no p-value; not in the Holm family",
        "registration": REGISTRATION, "decision": "DECISIONS.md D-G-1 g",
        "note": "shares of gate holds (verdict hold on an analysed clearing) with and without a corrective event "
                "within W; no review cost, resolution time or other assumed parameter is computed",
        "bootstrap": {"B": b, "seed": SEED, "generator": "numpy PCG64", "clusters": boot.n,
                      "cluster": "purchase document, sorted by its hashed id", "interval": "percentile 2.5 to 97.5"},
        "cutpoints": strata.cutpoints(),
        "exploratory_overall": {w: per["overall"]["all"] for w, per in out.items()},
        "exploratory_by_category": {w: per["category"] for w, per in out.items()},
        "exploratory_by_line_value_quartile": {w: per["line_value_quartile"] for w, per in out.items()},
    }


def run(results_dir: Path = ROOT / "results", out: Path = OUT, b: int = BOOTSTRAP_B) -> dict[str, Any]:
    """results_dir holds the e1/ and e3/ slots read (the committed ones, or a reproduction's regenerated ones)."""
    records, lines = load(results_dir / "e1")
    doc = analyse(records, lines, b, results_dir)
    write_json(out, doc)
    return doc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.exploratory.x3_hold_friction")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    doc = run(out=args.out)
    for w, e in doc["exploratory_overall"].items():
        print(f"X3 {w}: {e['holds']} holds, without corrective {e['share_without_corrective']:.4f} {e['bootstrap95']}, "
              f"value {e['value_share_without_corrective']:.4f} {e['value_bootstrap95']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
