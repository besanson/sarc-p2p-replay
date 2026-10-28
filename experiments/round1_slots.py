"""Round-1 slots (DECISIONS.md D-D-2), from data already in the repository. No new experiment.

  results/e3/human-hold-composition.json
      Among framed lines (E0 removed) held by people (section 3.6), how many were held by a
      `Set Payment Block` before the first clearing and how many by no clearing within W of the
      first invoice receipt (and how many meet both), by line status at t* under both readings.
      The line tables of E1 record whether a line was held, not why, so the reason is read from
      the log with the engine's own section 3.6 rule (`p2p_replay.frame`); the statuses are joined
      from results/e1/lines.jsonl.gz and lines-t-star-amended.jsonl.gz.
  results/e1/actors.json
      From the log (events up to T_end): `Clear Invoice` events by batch users and by other users,
      a batch user being an actor whose name starts with the registered `batch_actor_prefix`
      (prereg/outcome-patterns.yaml, case-insensitive; the record page states that batch users
      are indicated by their name), and events with a missing actor; the number of distinct
      `Clear Invoice` actors, of distinct earliest-creation actors, and of their intersection, over
      all lines and over framed lines (E0 removed).
  results/e4/arms-classified-lines.json
      The four E4 arms re-tabulated on the sample lines the human arm classifies, from
      results/e4/sample.json and the committed responses, with the E4 analysis code unchanged
      (experiments/e4.py on a sample restricted to those lines). A re-tabulation; the full
      sample stays primary.

Usage: python -m experiments.round1_slots [--log data/BPI_Challenge_2019.xes]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import Counter
from datetime import timedelta
from pathlib import Path
from typing import Any

from experiments import e4
from experiments.common import E0_LINES, read_e0_lines, read_jsonl_gz, write_json
from experiments.e1 import DEFAULT_LOG, hashed, load_amended
from p2p_replay.config import REGISTRATION, ROOT, T_END_MONTH_MIN_EVENTS, W_DAYS, load_mapping, load_patterns
from p2p_replay.frame import clearings, classify, creation_time, first_invoice
from p2p_replay.reader import read_log
from p2p_replay.replay import observation_end

READINGS = {"registered_literal_reading": "t_star_status", "amended_reading_D-C-2": "amended"}
STATUSES = ("defective", "clean", "held_unknown")


def hold_reason(case, p, t_end) -> str | None:
    """Section 3.6 split: None when not held or not classified."""
    invoiced = first_invoice(case, p)
    if invoiced is None or invoiced > t_end - timedelta(days=W_DAYS):
        return None
    cleared = clearings(case, p)
    first = cleared[0].ts if cleared else None
    blocks = case.of(p.payment_block_set)
    by_block = bool(blocks) and (first is None or blocks[0].ts <= first)
    by_delay = first is None or first > invoiced + timedelta(days=W_DAYS)
    if by_block and by_delay:
        return "both"
    if by_block:
        return "payment_block_before_first_clearing"
    if by_delay:
        return "no_clearing_within_W_of_first_invoice"
    return None


def scan(log: Path, e0_path: Path, min_month_events: int = T_END_MONTH_MIN_EVENTS) -> dict[str, Any]:
    mapping = load_mapping("bpi2019")
    p, _ = load_patterns()
    flag_true = mapping.get("flag_true", ["true"])
    end = observation_end(read_log(log, mapping), min_month_events)
    e0 = read_e0_lines(e0_path)
    prefix = p.batch_actor_prefix.lower()
    reasons: dict[str, str] = {}
    clear = {"all": Counter(), "framed": Counter()}
    clear_actors = {"all": set(), "framed": set()}
    create_actors = {"all": set(), "framed": set()}
    missing = set(p.actor_missing)

    def kind(actor: str | None) -> str:
        if actor is None or actor.strip() in missing:
            return "missing"
        return "batch" if actor.lower().startswith(prefix) else "other"

    for case in read_log(log, mapping):
        case = case.truncated(end.t_end)
        frame = classify(case, p, flag_true, end.t_end, W_DAYS)
        scopes = ["all"] + (["framed"] if frame.framed and case.case_id not in e0 else [])
        created = creation_time(case, p)
        creators = {e.actor for e in case.of(p.creation) if e.ts == created} if created else set()
        for scope in scopes:
            for e in case.of(p.clearing):
                clear[scope][kind(e.actor)] += 1
                if kind(e.actor) != "missing":
                    clear_actors[scope].add(e.actor)
            create_actors[scope].update(a for a in creators if kind(a) != "missing")
        if "framed" in scopes:
            r = hold_reason(case, p, end.t_end)
            if r is not None:
                reasons[hashed(case.case_id)] = r
    actors = {}
    for scope in ("all", "framed"):
        inter = clear_actors[scope] & create_actors[scope]
        actors[scope] = {
            "clear_invoice_events": dict(sorted(clear[scope].items())),
            "distinct_clear_invoice_actors": len(clear_actors[scope]),
            "distinct_clear_invoice_actors_batch": sum(1 for a in clear_actors[scope] if a.lower().startswith(prefix)),
            "distinct_earliest_creation_actors": len(create_actors[scope]),
            "distinct_earliest_creation_actors_batch": sum(1 for a in create_actors[scope] if a.lower().startswith(prefix)),
            "intersection": len(inter),
        }
    return {"reasons": reasons, "actors": actors, "prefix": p.batch_actor_prefix}


def composition(lines: list[dict], amended: dict[str, str | None], reasons: dict[str, str]) -> dict[str, Any]:
    held = [l for l in lines if l["human_hold"]]
    missing_reason = [l["case_id"] for l in held if l["case_id"] not in reasons]
    if missing_reason or any(r for cid, r in reasons.items() if cid not in {l["case_id"] for l in held}):
        raise RuntimeError("the log's section 3.6 split disagrees with the E1 line table")
    out: dict[str, Any] = {}
    for name, field in READINGS.items():
        table = {}
        for s in STATUSES:
            group = [l for l in held if (l["t_star_status"] if field == "t_star_status" else amended[l["case_id"]]) == s]
            c = Counter(reasons[l["case_id"]] for l in group)
            table[s] = {"held_by_people": len(group),
                        "payment_block_before_first_clearing": c.get("payment_block_before_first_clearing", 0),
                        "no_clearing_within_W_of_first_invoice": c.get("no_clearing_within_W_of_first_invoice", 0),
                        "both": c.get("both", 0)}
        out[name] = table
    total = Counter(reasons.values())
    return {"held_by_people": len(held), "by_reason": {k: total.get(k, 0) for k in
            ("payment_block_before_first_clearing", "no_clearing_within_W_of_first_invoice", "both")},
            "by_status": out}


def arms_classified(root: Path = ROOT) -> dict[str, Any]:
    sample = json.loads((root / "results" / "e4" / "sample.json").read_text(encoding="utf-8"))
    kept = [r for r in sample["lines"] if r["human_arm"] != "unclassified"]
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "results" / "e4").mkdir(parents=True)
        (t / "results" / "e4" / "sample.json").write_text(json.dumps(sample | {"lines": kept}), encoding="utf-8")
        os.symlink(root / "results" / "e2", t / "results" / "e2")
        os.symlink(root / "responses", t / "responses")
        arms = e4.analyse("e4", t)["arms"]
    return {"registration": REGISTRATION, "section": "7 (E4), re-tabulation (DECISIONS.md D-D-2)",
            "label": "re-tabulation on the lines the human arm classifies; the full sample (results/e4/arms.json) is primary",
            "sample_lines": len(sample["lines"]), "classified_lines": len(kept),
            "unclassified_lines": len(sample["lines"]) - len(kept),
            "unclassified_rule": "section 3.6: no invoice receipt by T_end - W",
            "classified_by_status": dict(sorted(Counter(r["status"] for r in kept).items())),
            "expected_correctives_rule": arms["expected_correctives_rule"],
            "arms": arms["arms"]}


def run(log: Path = DEFAULT_LOG, root: Path = ROOT, e1_dir: Path | None = None, e0_path: Path = E0_LINES,
        out: Path | None = None, min_month_events: int = T_END_MONTH_MIN_EVENTS, with_arms: bool = True) -> dict[str, Any]:
    e1_dir = e1_dir or root / "results" / "e1"
    out = out or root / "results"
    s = scan(log, e0_path, min_month_events)
    lines = read_jsonl_gz(e1_dir / "lines.jsonl.gz")
    docs = {
        "e3/human-hold-composition.json": {
            "registration": REGISTRATION, "section": "3.6 (DECISIONS.md D-D-2)",
            "source": "the reason from the log with the section 3.6 rule (p2p_replay.frame); held-or-not and the "
                      "statuses at t* from results/e1/lines.jsonl.gz and lines-t-star-amended.jsonl.gz",
            "note": "the log records no hold decision except a payment block; 'held by people' is a payment block "
                    "before the first clearing, or no clearing within W of the first invoice receipt",
            **composition(lines, load_amended(e1_dir), s["reasons"])},
        "e1/actors.json": {
            "registration": REGISTRATION, "section": "3.2, D5 (DECISIONS.md D-D-2)",
            "batch_user_rule": f"actor name starts with '{s['prefix']}' (registered batch_actor_prefix, case-insensitive)",
            "missing_actor_rule": "empty or NONE (registered actor_missing)",
            "events": "up to T_end; framed lines are those of E1 with the E0 lines removed",
            "scopes": s["actors"]},
    }
    for name, doc in docs.items():
        write_json(out / name, doc)
    if with_arms:
        docs["e4/arms-classified-lines.json"] = arms_classified(root)
        write_json(out / "e4/arms-classified-lines.json", docs["e4/arms-classified-lines.json"])
    return docs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.round1_slots")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    docs = run(args.log, out=args.out)
    print(json.dumps(docs["e1/actors.json"]["scopes"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
