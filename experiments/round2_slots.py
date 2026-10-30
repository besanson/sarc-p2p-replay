"""Round-2 slots (DECISIONS.md D-D-3), from data already in the repository. No new experiment, no model call.

  results/e5/sufficiency.json
      Per category, the registered contract read through paper 5's sufficiency function
      (`reduct.sufficiency`, Definition 4, from the pinned sibling, unmodified) over the observed
      states of E5 (`experiments/e5.py`, same adapter): the observation fields the registered
      predicates read, sufficiency for each declared loss and for the three together (paper 5's
      verdict: a state is hazardous if any loss fires), the counterexample where it fails,
      minimality (no field of the registered set can be dropped while every loss it is sufficient
      for stays so), and the derived contract of results/e5/derivation.json against the
      registered one.
  results/e4/timeline.json
      When the E4 model calls were made, from the committed response logs (`sent_utc` written by
      the client before each request), beside the git commit times of the D-C-2 decision, the
      sample draw, the first committed responses and the first H4 values.
  results/e1/analysed-clearing-actors.json
      From the log: analysed clearings (section 2, E0 removed) whose `Clear Invoice` actor or
      earliest-creation actor is missing, and the D5 unknown count of the evidence set; the
      `Clear Invoice` events with a missing actor on framed lines, split into analysed and after
      the horizon T_end - W.
  results/e7/unknown-overlap.json
      From results/e7/evidence-set.jsonl.gz: per log, the payments with a predicate unknown, and how
      many of them fail another predicate, so that "every predicate passing" can be read exactly.

Usage: python -m experiments.round2_slots [--log data/BPI_Challenge_2019.xes] [--out results]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import timedelta
from pathlib import Path
from typing import Any

from experiments import e5
from experiments.common import E0_LINES, read_e0_lines, read_jsonl_gz, write_json
from experiments.e1 import DEFAULT_LOG
from p2p_replay.config import REGISTRATION, ROOT, T_END_MONTH_MIN_EVENTS, W_DAYS, load_mapping, load_patterns
from p2p_replay.frame import classify
from p2p_replay.predicates import actor_missing, creation_actors
from p2p_replay.reader import read_log
from p2p_replay.replay import observation_end

# Commits named in DECISIONS.md: the D-C-2 decision (D5 reading, H3 convention) and the E4 sample draw.
DECISION_COMMIT = "7aea13f"
SAMPLE_COMMIT = "5ffd887"
FAMILIES = ("jev", "haiku")


# --- results/e5/sufficiency.json -------------------------------------------------------------------

def registered_fields(category: str) -> list[str]:
    reg = set(e5.REGISTERED_CONTRACT[category])
    return [f for f in e5.FIELDS if reg & set(e5.FIELD_PREDICATES[f])]


def _state(s) -> dict[str, Any]:
    return {f: getattr(s, f) for f in e5.FIELDS}


def _check(sufficiency, fields: list[str], reachable: list, registry: dict) -> tuple[bool, dict | None]:
    ok, detail = sufficiency(tuple(fields), reachable, registry)
    if ok:
        return True, None
    return False, {"state_a": detail["tuple_a"], "state_a_prime": detail["tuple_a_prime"],
                   "verdict_a": detail["verdict_a"], "verdict_a_prime": detail["verdict_a_prime"],
                   "differing_fields": [f for f in e5.FIELDS if detail["tuple_a"][f] != detail["tuple_a_prime"][f]]}


def sufficiency_category(category: str, counts: Counter, derived: list[str], sufficiency) -> dict[str, Any]:
    reachable = sorted(counts, key=lambda s: tuple(str(getattr(s, f)) for f in e5.FIELDS))
    model = e5.loss_model(category)
    fields = registered_fields(category)
    per_loss = {}
    for loss, fn in model.items():
        ok, cx = _check(sufficiency, fields, reachable, {loss: fn})
        per_loss[loss] = {"analysed_clearings_with_loss": sum(n for s, n in counts.items() if fn(s)),
                          "sufficient": ok, "counterexample": cx}
    together, cx_all = _check(sufficiency, fields, reachable, model)
    covered = [k for k, v in per_loss.items() if v["sufficient"]]
    covered_model = {k: model[k] for k in covered}
    droppable = [f for f in fields
                 if covered and all(_check(sufficiency, [g for g in fields if g != f], reachable, {k: covered_model[k]})[0]
                                    for k in covered)]
    registered = list(e5.REGISTERED_CONTRACT[category])
    return {
        "analysed_clearings": sum(counts.values()), "distinct_states": len(reachable),
        "registered_contract": registered, "registered_fields": fields,
        "fields_read_by_no_registered_predicate": [f for f in e5.FIELDS if f not in fields],
        "per_loss": per_loss,
        "all_three_losses": {"sufficient": together, "counterexample": cx_all},
        "sufficient_for": covered, "not_sufficient_for": [k for k in model if k not in covered],
        "minimal_for_the_losses_it_is_sufficient_for": not droppable,
        "fields_droppable_keeping_sufficiency": droppable,
        "derived_contract": derived,
        "derived_subset_of_registered": set(derived) <= set(registered),
        "derived_proper_subset_of_registered": set(derived) < set(registered),
    }


def sufficiency_doc(e1_dir: Path, e5_dir: Path, root: Path = ROOT) -> dict[str, Any]:
    path, head = e5.sibling_path(root)
    e5.import_compiler(path)
    from reduct import sufficiency  # noqa: PLC0415

    derivation = json.loads((e5_dir / "derivation.json").read_text(encoding="utf-8"))["categories"]
    per = e5.states(read_jsonl_gz(e1_dir / "evidence-set.jsonl.gz"))
    cats = {c: sufficiency_category(c, per[c], derivation[c]["derived_contract"], sufficiency) for c in sorted(per)}
    return {
        "registration": REGISTRATION, "section": "6, E5 (DECISIONS.md D-D-3)", "claims": ["C1", "C9"],
        "function": {"repository": e5.SIBLING, "commit": head, "entry_point": "reduct.sufficiency",
                     "definition": "paper 5, Definition 4: a field set is sufficient for a loss model on the reachable "
                                   "states when every cell of the partition by those fields carries one verdict",
                     "modified": False},
        "states": "the observed states of E5 (experiments/e5.py states(), from results/e1/evidence-set.jsonl.gz)",
        "losses": e5.LOSSES,
        "fields": {f: list(e5.FIELD_PREDICATES[f]) for f in e5.FIELDS},
        "verdict_of_all_three": "hazardous if any declared loss fires (paper 5's m_verdict)",
        "categories": cats,
    }


# --- results/e4/timeline.json -----------------------------------------------------------------------

def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


def _commit(root: Path, rev: str) -> dict[str, str]:
    full, committed, authored, subject = _git(root, "log", "-1", "--format=%H%n%cI%n%aI%n%s", rev).split("\n")
    return {"commit": full[:7], "commit_full": full, "committer_utc": committed, "author_utc": authored,
            "subject": subject}


def _first_commit(root: Path, path: str) -> dict[str, str]:
    revs = _git(root, "log", "--reverse", "--format=%H", "--", path).split("\n")
    return _commit(root, revs[0])


def timeline_doc(root: Path) -> dict[str, Any]:
    arms: dict[str, Any] = {}
    for arm in ("e4", "e4-exploratory"):
        for family in FAMILIES:
            rel = f"responses/{arm}/{family}/responses.jsonl"
            kinds: dict[str, list[str]] = {}
            for line in (root / rel).read_text(encoding="utf-8").splitlines():
                r = json.loads(line)
                if "sent_utc" in r:
                    kinds.setdefault(r["kind"], []).append(r["sent_utc"])
            arms[f"{arm}/{family}"] = {
                "file": rel,
                "requests": {k: {"count": len(v), "earliest_sent_utc": min(v), "latest_sent_utc": max(v)}
                             for k, v in sorted(kinds.items())},
                "earliest_sent_utc": min(min(v) for v in kinds.values()),
            }
    decision, sample = _commit(root, DECISION_COMMIT), _commit(root, SAMPLE_COMMIT)
    first_responses = {f: _first_commit(root, f"responses/e4/{f}") for f in FAMILIES}
    first_h4 = _first_commit(root, "results/e4/h4.json")
    earliest = min(a["earliest_sent_utc"] for a in arms.values())
    return {
        "registration": REGISTRATION, "section": "7, E4 (DECISIONS.md D-D-3)",
        "sources": {"calls": "sent_utc of every request in the committed response logs, written by the client "
                             "before the request is sent",
                    "commits": "git committer and author times, as recorded by the committing machine"},
        "calls": arms,
        "earliest_sent_utc_any_call": earliest,
        "commits": {"D-C-2 decision (D5 reading, H3 convention)": decision, "E4 sample draw": sample,
                    **{f"first committed responses, {f}": c for f, c in first_responses.items()},
                    "first committed H4 values (results/e4/h4.json)": first_h4},
        "order": {
            "decision_commit_before_earliest_call": decision["committer_utc"] < earliest,
            "sample_commit_before_earliest_call": sample["committer_utc"] < earliest,
            "decision_commit_before_first_h4_commit": decision["committer_utc"] < first_h4["committer_utc"],
        },
        "note": "times compared as UTC ISO 8601 strings of the same form",
    }


# --- results/e1/analysed-clearing-actors.json ---------------------------------------------------------

def actors_doc(log: Path, e1_dir: Path, e0_path: Path, min_month_events: int) -> dict[str, Any]:
    mapping = load_mapping("bpi2019")
    p, _ = load_patterns()
    flag_true = mapping.get("flag_true", ["true"])
    end = observation_end(read_log(log, mapping), min_month_events)
    horizon = end.t_end - timedelta(days=W_DAYS)
    e0 = read_e0_lines(e0_path)
    analysed = Counter()
    framed_missing = Counter()
    for case in read_log(log, mapping):
        case = case.truncated(end.t_end)
        frame = classify(case, p, flag_true, end.t_end, W_DAYS)
        if not frame.framed or case.case_id in e0:
            continue
        for e in frame.analysed:
            analysed["clearings"] += 1
            analysed["clearing_actor_missing"] += actor_missing(e.actor, p)
            analysed["earliest_creation_actor_missing"] += all(actor_missing(a, p)
                                                               for a in creation_actors(case.upto(e.ts), p))
        kept = {id(e) for e in frame.analysed}
        for e in case.of(p.clearing):
            if actor_missing(e.actor, p):
                framed_missing["total"] += 1
                if id(e) in kept:
                    framed_missing["analysed"] += 1
                elif e.ts > horizon:
                    framed_missing["after_horizon"] += 1
                else:
                    framed_missing["other"] += 1
    evidence = read_jsonl_gz(e1_dir / "evidence-set.jsonl.gz")
    return {
        "registration": REGISTRATION, "section": "3.2, D5 (DECISIONS.md D-D-3)",
        "missing_actor_rule": "empty or NONE (registered actor_missing); D5 is unknown if either actor is missing",
        "t_end": end.t_end.isoformat(), "horizon_t_end_minus_W": horizon.isoformat(),
        "analysed_clearings": analysed["clearings"],
        "analysed_clearings_in_evidence_set": len(evidence),
        "analysed_clearings_clearing_actor_missing": analysed["clearing_actor_missing"],
        "analysed_clearings_earliest_creation_actor_missing": analysed["earliest_creation_actor_missing"],
        "analysed_clearings_D5_unknown": sum(1 for r in evidence if r["predicates"]["D5"] == "unknown"),
        "framed_lines_clear_invoice_missing_actor": {
            "total": framed_missing["total"], "analysed": framed_missing["analysed"],
            "after_horizon": framed_missing["after_horizon"], "other": framed_missing["other"]},
        "note": "framed lines with the E0 lines removed, as in results/e1/actors.json (scope framed)",
    }


# --- results/e7/unknown-overlap.json --------------------------------------------------------------------

def unknown_overlap_doc(e7_dir: Path) -> dict[str, Any]:
    records = read_jsonl_gz(e7_dir / "evidence-set.jsonl.gz")
    logs: dict[str, Any] = {}
    for log in sorted({r["log"] for r in records}):
        rs = [r for r in records if r["log"] == log]
        unknown = [r for r in rs if "unknown" in r["predicates"].values()]
        logs[log] = {
            "payments": len(rs),
            "with_a_predicate_unknown": len(unknown),
            "unknown_per_predicate": {d: sum(1 for r in rs if r["predicates"][d] == "unknown")
                                      for d in sorted(rs[0]["predicates"])} if rs else {},
            "with_a_predicate_unknown_and_another_failing": sum(1 for r in unknown if "fail" in r["predicates"].values()),
            "every_predicate_passing": sum(1 for r in rs if set(r["predicates"].values()) == {"pass"}),
        }
    return {"registration": REGISTRATION, "section": "8, E7 (DECISIONS.md D-D-3)",
            "source": "results/e7/evidence-set.jsonl.gz", "logs": logs}


def run(log: Path = DEFAULT_LOG, root: Path = ROOT, e1_dir: Path | None = None, e5_dir: Path | None = None,
        e7_dir: Path | None = None, e0_path: Path = E0_LINES, out: Path | None = None, min_month_events: int = T_END_MONTH_MIN_EVENTS,
        parts: tuple[str, ...] = ("sufficiency", "timeline", "actors", "e7")) -> dict[str, Any]:
    """root carries the response logs, the git history and engines.lock; e1_dir, e5_dir, e7_dir the slots read."""
    e1_dir = e1_dir or root / "results" / "e1"
    e5_dir = e5_dir or root / "results" / "e5"
    e7_dir = e7_dir or root / "results" / "e7"
    out = out or root / "results"
    docs: dict[str, Any] = {}
    if "sufficiency" in parts:
        docs["e5/sufficiency.json"] = sufficiency_doc(e1_dir, e5_dir, root)
    if "timeline" in parts:
        docs["e4/timeline.json"] = timeline_doc(root)
    if "actors" in parts:
        docs["e1/analysed-clearing-actors.json"] = actors_doc(log, e1_dir, e0_path, min_month_events)
    if "e7" in parts:
        docs["e7/unknown-overlap.json"] = unknown_overlap_doc(e7_dir)
    for name, doc in docs.items():
        write_json(out / name, doc)
    return docs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.round2_slots")
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    docs = run(args.log, out=args.out)
    for c, s in docs["e5/sufficiency.json"]["categories"].items():
        print(f"{c}: sufficient for {s['sufficient_for']}, not for {s['not_sufficient_for']}; "
              f"minimal {s['minimal_for_the_losses_it_is_sufficient_for']}")
    print(json.dumps(docs["e4/timeline.json"]["order"]))
    a = docs["e1/analysed-clearing-actors.json"]
    print({k: v for k, v in a.items() if k.startswith("analysed") or k.startswith("framed")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
