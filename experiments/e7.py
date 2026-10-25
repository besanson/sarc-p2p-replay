"""E7, replication on the BPI 2020 declaration logs (prereg/p7-v1.1.md section 8; claim C11).

Descriptive and secondary: no p-value, not in the Holm family.

Unit: each payment event (registered `payment` list) on a declaration case, in either log, with
t_pay at most T_end' - W (T_end' the latest timestamp in that log; W = 60 days). D1' approval
present, D2' approval by the required role, D3' unchanged after approval (unknown when no
approval precedes the payment, D-B-1), evaluated on events at or before t_pay; O' = any
`outcome_prime` event on the case in (t_pay, t_pay + W]. The engine's registered implementation
(`p2p_replay.declarations.replay_declaration`) is used unchanged.

Per log and pooled: unit counts and exclusions; per predicate pass, fail and unknown; the share of
payments and of paid value (the case attribute `Amount`, read beside the registered mapping;
every payment of a case carries its case's amount) with at least one failed predicate; and for
each of D1', D2', D3' the O' rate of payments failing it against payments with every predicate
passing, with the difference and a case-clustered bootstrap percentile interval (B = 10,000,
numpy PCG64 seeded 20261201, cases in sorted id order).

Writes results/e7/: units.json, predicates.json, exposure.json, comparisons.json and
evidence-set.jsonl.gz (one record per payment, ids hashed).

Usage: python -m experiments.e7 [--out results/e7]
"""

from __future__ import annotations

import argparse
import copy
import math
import sys
import tomllib
from collections import Counter
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np

from experiments.common import (
    BOOTSTRAP_B, ClusterBootstrap, ratio, write_json, write_jsonl_gz,
)
from experiments.e7_check import LOGS
from p2p_replay.config import REGISTRATION, ROOT, SEED, load_mapping, load_patterns
from p2p_replay.declarations import PREDICATES_PRIME, replay_declaration
from p2p_replay.evidence import sha256_text
from p2p_replay.reader import read_log
from p2p_replay.replay import log_end

DEFAULT_OUT = ROOT / "results" / "e7"
AMOUNT_ATTRIBUTE = "Amount"


def hashed(value: str) -> str:
    return sha256_text(value)[:16]


def mapping_with_amount() -> dict[str, Any]:
    """The registered bpi2020 mapping, plus the case amount for the value shares (read only here)."""
    m = copy.deepcopy(load_mapping("bpi2020"))
    m["case"]["amount"] = AMOUNT_ATTRIBUTE
    return m


def _amount(text: str | None) -> float | None:
    try:
        return float(text) if text is not None else None
    except ValueError:
        return None


def replay_log(name: str, path: Path, p) -> tuple[list[dict], dict[str, Any]]:
    mapping = mapping_with_amount()
    t_end = log_end(read_log(path, mapping))
    horizon = t_end - timedelta(days=p.window_days)
    records: list[dict] = []
    counts = Counter()
    for case in read_log(path, mapping):
        counts["cases"] += 1
        payments = case.of(p.payment)
        counts["payments_in_log"] += len(payments)
        counts["payments_after_horizon"] += sum(1 for e in payments if e.ts > horizon)
        if not payments:
            counts["cases_without_payment"] += 1
        amount = _amount(case.attr("amount"))
        cluster = hashed(f"{name}:{case.case_id}")
        for rec in replay_declaration(case, p, t_end):
            records.append({
                "log": name, "case_id": cluster, "t_pay": rec.t_pay, "predicates": rec.predicates,
                "verdict": rec.verdict, "defective": rec.defective, "outcome_prime": rec.outcome_prime,
                "amount": amount, "source_sha256": rec.source_sha256,
            })
    records.sort(key=lambda r: (r["case_id"], r["t_pay"], r["source_sha256"]))
    units = {"file": path.name, "t_end_prime": t_end.isoformat(), "horizon": horizon.isoformat(),
             "cases": counts["cases"], "cases_without_payment": counts["cases_without_payment"],
             "payments_in_log": counts["payments_in_log"],
             "excluded_payments_after_t_end_prime_minus_w": counts["payments_after_horizon"],
             "units": len(records), "cases_with_units": len({r["case_id"] for r in records}),
             "units_without_amount": sum(1 for r in records if r["amount"] is None)}
    return records, units


def predicate_counts(records: list[dict]) -> dict[str, dict[str, int]]:
    return {d: {v: sum(1 for r in records if r["predicates"][d] == v) for v in ("pass", "fail", "unknown")}
            for d in PREDICATES_PRIME}


def exposure(records: list[dict]) -> dict[str, Any]:
    n = len(records)
    k = sum(1 for r in records if r["defective"])
    with_amount = [r for r in records if r["amount"] is not None]
    # The anonymised amounts carry many decimals; fsum gives the correctly rounded sum, order-free.
    v = math.fsum(r["amount"] for r in with_amount)
    kv = math.fsum(r["amount"] for r in with_amount if r["defective"])
    return {"units": n, "with_a_failed_predicate": k, "share_of_payments": ratio(k, n),
            "paid_value_eur": round(v, 2), "paid_value_with_a_failed_predicate_eur": round(kv, 2),
            "share_of_paid_value": kv / v if v else None, "units_with_amount": len(with_amount)}


def comparisons(records: list[dict], b: int) -> dict[str, Any]:
    if not records:
        return {}
    boot = ClusterBootstrap([r["case_id"] for r in records], b=b, seed=SEED)
    allpass = np.array([r["verdict"] == "allow" for r in records], dtype=bool)
    o = np.array([bool(r["outcome_prime"]) for r in records], dtype=bool)
    columns = [allpass.astype(np.float64), (allpass & o).astype(np.float64)]
    fails = {}
    for d in PREDICATES_PRIME:
        f = np.array([r["predicates"][d] == "fail" for r in records], dtype=bool)
        fails[d] = f
        columns += [f.astype(np.float64), (f & o).astype(np.float64)]
    reps = boot.totals(columns)
    n_c, o_c = int(allpass.sum()), int((allpass & o).sum())
    out: dict[str, Any] = {"clusters": boot.n}
    for i, d in enumerate(PREDICATES_PRIME):
        f = fails[d]
        n_d, o_d = int(f.sum()), int((f & o).sum())
        rd, rc = ratio(o_d, n_d), ratio(o_c, n_c)
        diff = rd - rc if rd is not None and rc is not None else None
        bn_d, bo_d = reps[:, 2 + 2 * i], reps[:, 3 + 2 * i]
        bn_c, bo_c = reps[:, 0], reps[:, 1]
        ok = (bn_d > 0) & (bn_c > 0)
        interval = None
        if ok.any() and diff is not None:
            lo, hi = np.percentile(bo_d[ok] / bn_d[ok] - bo_c[ok] / bn_c[ok], [2.5, 97.5])
            interval = [float(lo), float(hi)]
        out[d] = {
            "defect_group": {"payments": n_d, "with_O_prime": o_d, "O_prime_rate": rd},
            "all_pass_group": {"payments": n_c, "with_O_prime": o_c, "O_prime_rate": rc},
            "difference": diff, "bootstrap95": interval, "bootstrap_resamples_used": int(ok.sum()),
            "h1_shape": bool(diff is not None and diff > 0 and interval is not None and interval[0] > 0),
        }
    return out


def run(out: Path = DEFAULT_OUT, root: Path = ROOT, data: Path | None = None, b: int = BOOTSTRAP_B,
        lock: dict[str, Any] | None = None) -> dict[str, Any]:
    lock = lock if lock is not None else tomllib.loads((root / "prereg" / "data.lock").read_text(encoding="utf-8"))
    _, p = load_patterns()
    per_log: dict[str, list[dict]] = {}
    units: dict[str, Any] = {}
    for name, key in LOGS.items():
        per_log[name], units[name] = replay_log(name, (data or root / "data") / lock[key]["file"], p)
    pooled = sorted((r for rs in per_log.values() for r in rs), key=lambda r: (r["case_id"], r["t_pay"], r["source_sha256"]))
    scopes = {**per_log, "pooled": pooled}
    common = {"registration": REGISTRATION, "section": "8", "claim": "C11",
              "status": "descriptive, secondary; no p-value; not in the Holm family"}
    units["pooled"] = {"units": len(pooled), "cases_with_units": len({r["case_id"] for r in pooled})}
    docs = {
        "units.json": common | {"window_days": p.window_days, "unit": "payment event with t_pay <= T_end' - W",
                                "logs": units},
        "predicates.json": common | {"counts": {s: predicate_counts(rs) for s, rs in scopes.items()},
                                     "rule": "D3' is unknown when no approval precedes the payment (D-B-1)"},
        "exposure.json": common | {"value": f"case attribute `{AMOUNT_ATTRIBUTE}`, read beside the registered "
                                            "mapping; each payment carries its case's amount",
                                   "scopes": {s: exposure(rs) for s, rs in scopes.items()}},
        "comparisons.json": common | {
            "statistic": "O' rate of payments failing the predicate minus O' rate of payments with every predicate "
                         "passing; case-clustered bootstrap percentile interval",
            "bootstrap": {"B": b, "seed": SEED, "generator": "numpy PCG64",
                          "cluster": "declaration case, sorted by its hashed id (log name and case id)"},
            "h1_shape_rule": "difference above zero with the 95% interval excluding zero",
            "scopes": {s: comparisons(rs, b) for s, rs in scopes.items()}},
    }
    for name, doc in docs.items():
        write_json(out / name, doc)
    write_jsonl_gz(out / "evidence-set.jsonl.gz", pooled)
    return docs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.e7")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--bootstrap-b", type=int, default=BOOTSTRAP_B, help="registered: 10000")
    args = parser.parse_args(argv)
    docs = run(args.out, b=args.bootstrap_b)
    for scope, comp in docs["comparisons.json"]["scopes"].items():
        for d in PREDICATES_PRIME:
            if d in comp:
                print(f"E7 {scope} {d}: difference {comp[d]['difference']}, interval {comp[d]['bootstrap95']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
