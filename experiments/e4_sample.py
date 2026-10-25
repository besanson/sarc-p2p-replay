"""E4 sample draw and views (prereg/p7-v1.1.md section 7; DECISIONS.md D-C-2 B). No model call.

Eligible: framed lines (E0 lines removed) with at least one `Record Invoice Receipt`,
whose gate status at the decision point t* under D-C-2 B is defective or clean
(held-unknown lines are not sampled). N_d = 1,000 defective and N_c = 1,000
clean lines, at most one line per purchase document, stratified by category x
line-value quartile with proportional allocation (largest remainder), drawn with
random.Random(20261201) over the sorted line ids.

Draw: the eligible lines, sorted by line id (the hashed id of the evidence set,
section 3.9), are shuffled once with random.Random(20261201); walking that
order, a line is taken when its status x stratum quota is not yet filled and
its purchase document has no line in the sample yet. The registered sample order
(the order of every E4 call) is the sample sorted by line id.

Writes to results/e4/:
  sample.json            the 2,000 lines: hashed id, stratum, status, failed predicates, t*,
                         cleared or line value, the human arm's hold or release from the log (3.6)
  sample-frame.json      eligible lines per status and stratum, the allocation, the drawn counts
  views.jsonl            the ERP view of each line (prereg/erp-view-template.txt), keyed by order
  views-timeline.jsonl   the exploratory timeline view of each line, keyed by order

Usage: python -m experiments.e4_sample [--log data/BPI_Challenge_2019.xes] [--e1 results/e1] [--out results/e4]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from experiments.common import E0_LINES, Strata, read_e0_lines, write_json, write_jsonl
from experiments.e1 import DEFAULT_LOG, hashed, load, load_amended
from p2p_replay.category import Category
from p2p_replay.config import REGISTRATION, ROOT, SEED, W_DAYS, load_mapping, load_patterns
from p2p_replay.frame import cleared_value, clearings, line_value
from p2p_replay.model import Case, parse_timestamp
from p2p_replay.reader import read_log
from p2p_replay.replay import line_status, verdict_at_decision_point
from p2p_replay.view import load_request_template, render

DEFAULT_E1 = ROOT / "results" / "e1"
DEFAULT_OUT = ROOT / "results" / "e4"
N_PER_GROUP = {"defective": 1000, "clean": 1000}
TIMELINE_HEADER = "Event timeline up to {decision_date} (date, activity, value in EUR)"


def stratum(strata: Strata, line: dict) -> str:
    lab = strata.of_line(line, None)
    return f"{lab['category']} | {lab['line_value_quartile']}"


def largest_remainder(total: int, weights: dict[str, int]) -> dict[str, int]:
    """Proportional allocation of `total` over `weights`; remainders broken by size, then label."""
    whole = sum(weights.values())
    if whole == 0:
        return {k: 0 for k in weights}
    exact = {k: total * w / whole for k, w in weights.items()}
    alloc = {k: int(v) for k, v in exact.items()}
    rest = total - sum(alloc.values())
    for k in sorted(weights, key=lambda k: (-(exact[k] - alloc[k]), k))[:rest]:
        alloc[k] += 1
    return alloc


def draw(eligible: Sequence[dict], strata: Strata, seed: int = SEED,
         n_per_group: dict[str, int] = N_PER_GROUP) -> tuple[list[dict], dict[str, Any]]:
    by_group: dict[str, Counter[str]] = {g: Counter() for g in n_per_group}
    for line in eligible:
        by_group[line["status"]][stratum(strata, line)] += 1
    quota = {g: largest_remainder(n, dict(sorted(by_group[g].items()))) for g, n in n_per_group.items()}
    order = sorted(eligible, key=lambda l: l["case_id"])
    random.Random(seed).shuffle(order)
    taken: list[dict] = []
    used_docs: set[str | None] = set()
    filled = {g: Counter() for g in n_per_group}
    for line in order:
        g, s = line["status"], stratum(strata, line)
        if filled[g][s] >= quota[g][s] or line["purchase_document"] in used_docs:
            continue
        filled[g][s] += 1
        used_docs.add(line["purchase_document"])
        taken.append(line)
    frame = {
        g: {"eligible_lines": sum(by_group[g].values()),
            "strata": {s: {"eligible": by_group[g][s], "allocated": quota[g][s], "drawn": filled[g][s]}
                       for s in sorted(by_group[g])},
            "drawn": sum(filled[g].values()), "shortfall": n_per_group[g] - sum(filled[g].values())}
        for g in n_per_group}
    return sorted(taken, key=lambda l: l["case_id"]), frame


def timeline_view(case: Case, t_star: datetime) -> str:
    """Exploratory: the template's instruction with the line's event timeline up to t* instead of the
    ERP view; dates, activities and values only (no actor, id, company or vendor)."""
    lines = load_request_template().splitlines()
    head = lines[0]
    rows = [f"{e.ts.date().isoformat()}, {e.activity}, " + (f"{e.value:.2f}" if e.value is not None else "none")
            for e in case.upto(t_star)]
    return "\n".join([head, "", TIMELINE_HEADER.format(decision_date=t_star.date().isoformat()), *rows])


def run(log: Path, e1_dir: Path, out: Path, e0_path: Path = E0_LINES,
        n_per_group: dict[str, int] = N_PER_GROUP) -> dict[str, Any]:
    _, lines = load(e1_dir)
    amended = load_amended(e1_dir)
    strata = Strata(lines)
    t_end = parse_timestamp(json.loads((e1_dir / "exclusions.json").read_text(encoding="utf-8"))["t_end"])
    statuses = Counter(amended[l["case_id"]] or "no_invoice_receipt" for l in lines)
    eligible = [l | {"status": amended[l["case_id"]]} for l in lines
                if amended[l["case_id"]] in n_per_group]
    sample, frame = draw(eligible, strata, SEED, n_per_group)
    chosen = {l["case_id"]: i for i, l in enumerate(sample)}

    mapping = load_mapping("bpi2019")
    p2p, _ = load_patterns()
    flag_true = mapping.get("flag_true", ["true"])
    e0_ids = read_e0_lines(e0_path)
    rows: list[dict | None] = [None] * len(sample)
    views: list[dict | None] = [None] * len(sample)
    timelines: list[dict | None] = [None] * len(sample)
    for case in read_log(log, mapping):
        if case.case_id in e0_ids:
            continue
        key = hashed(case.case_id)
        if key not in chosen:
            continue
        i = chosen[key]
        line = sample[i]
        case = case.truncated(t_end)
        category = Category(line["category"])
        t_star, verdict = verdict_at_decision_point(case, category, p2p, W_DAYS, amended=True)
        if line_status(verdict) != line["status"]:
            raise RuntimeError("status at t* differs from the E1 line table")
        first = clearings(case, p2p)
        at_clearing = bool(first) and first[0].ts == t_star
        value, source = cleared_value(case, first[0], p2p) if at_clearing else (line_value(case, p2p), "line_value")
        human = line["human_hold"]
        rows[i] = {
            "order": i + 1,
            "case_id": key,
            "purchase_document": line["purchase_document"],
            "stratum": {"category": line["category"],
                        "line_value_quartile": strata.of_line(line, None)["line_value_quartile"]},
            "status": line["status"],
            "failed": list(verdict.failed),
            "t_star": t_star.isoformat(),
            "t_star_is_clearing": at_clearing,
            "t_star_after_t_end": t_star > t_end,
            "value_eur": value,
            "value_source": source,
            "human_arm": "unclassified" if human is None else ("hold" if human else "release"),
        }
        views[i] = {"order": i + 1, "view": render(case, t_star, p2p, flag_true)}
        timelines[i] = {"order": i + 1, "label": "exploratory", "view": timeline_view(case, t_star)}
    if any(r is None for r in rows):
        raise RuntimeError("a sampled line was not found in the log")

    human = Counter((r["status"], r["human_arm"]) for r in rows)
    sample_doc = {
        "registration": REGISTRATION, "section": "7", "amendment": "DECISIONS.md D-C-2 B",
        "seed": SEED, "n_per_group": n_per_group,
        "registered_order": "the sample sorted by hashed line id; field `order`",
        "drawn": dict(Counter(r["status"] for r in rows)),
        "purchase_documents": len({r["purchase_document"] for r in rows}),
        "human_arm": {f"{s} {h}": n for (s, h), n in sorted(human.items())},
        "t_star_after_t_end": sum(r["t_star_after_t_end"] for r in rows),
        "lines": rows,
    }
    frame_doc = {
        "registration": REGISTRATION, "section": "7", "amendment": "DECISIONS.md D-C-2 B",
        "framed_lines_after_e0_removal": len(lines),
        "status_at_t_star_amended": {k: statuses.get(k, 0) for k in
                                     ("defective", "clean", "held_unknown", "no_invoice_receipt")},
        "stratum": "category x line-value quartile (quartiles over framed lines, results/e1)",
        "cutpoints": strata.cutpoints(),
        "allocation": "proportional to eligible lines per stratum, largest remainder; ties by stratum label",
        "draw_rule": "eligible lines sorted by hashed line id, shuffled once with random.Random(seed); taken in "
                     "that order while the status x stratum quota is open and the purchase document is unused",
        "groups": frame,
    }
    write_json(out / "sample.json", sample_doc)
    write_json(out / "sample-frame.json", frame_doc)
    write_jsonl(out / "views.jsonl", views)
    write_jsonl(out / "views-timeline.jsonl", timelines)
    return {"sample": sample_doc, "frame": frame_doc}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.e4_sample")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--e1", type=Path, default=DEFAULT_E1)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--e0-lines", type=Path, default=E0_LINES)
    args = parser.parse_args(argv)
    out = run(args.log, args.e1, args.out, args.e0_lines)
    print(f"E4 sample: drawn {out['sample']['drawn']}, shortfall "
          f"{ {g: v['shortfall'] for g, v in out['frame']['groups'].items()} }")
    return 0


if __name__ == "__main__":
    sys.exit(main())
