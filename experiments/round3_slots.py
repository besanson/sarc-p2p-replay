"""Round-3 slot (DECISIONS.md D-D-4), from the committed evidence set. No new experiment, no model call.

  results/e1/predicate-unknowns.json
      Per predicate D1 to D7, the number of analysed clearings whose value is unknown, with the pass
      and fail counts, over all analysed clearings and over those where the predicate is in the
      category's contract (field `applicable` of the evidence set).

Usage: python -m experiments.round3_slots [--out results]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from experiments.common import read_jsonl_gz, write_json
from p2p_replay.config import REGISTRATION, ROOT

PREDICATES = ("D1", "D2", "D3", "D4", "D5", "D6", "D7")
VALUES = ("pass", "fail", "unknown")


def predicate_unknowns_doc(e1_dir: Path) -> dict[str, Any]:
    records = read_jsonl_gz(e1_dir / "evidence-set.jsonl.gz")
    every: dict[str, Counter] = {d: Counter() for d in PREDICATES}
    applicable: dict[str, Counter] = {d: Counter() for d in PREDICATES}
    for r in records:
        for d in PREDICATES:
            v = r["predicates"][d]
            every[d][v] += 1
            if d in r["applicable"]:
                applicable[d][v] += 1
    return {
        "registration": REGISTRATION, "section": "3.2, 6 (DECISIONS.md D-D-4)",
        "source": "results/e1/evidence-set.jsonl.gz",
        "analysed_clearings": len(records),
        "predicates": {d: {"analysed_clearings": {v: every[d][v] for v in VALUES},
                           "applicable_clearings": {"total": sum(applicable[d].values()),
                                                    **{v: applicable[d][v] for v in VALUES}}}
                       for d in PREDICATES},
        "note": "unknown means a required input is missing (section 3.2); a predicate outside the category's "
                "contract is evaluated but does not enter the verdict",
    }


def run(root: Path = ROOT, e1_dir: Path | None = None, out: Path | None = None) -> dict[str, Any]:
    e1_dir = e1_dir or root / "results" / "e1"
    out = out or root / "results"
    docs = {"e1/predicate-unknowns.json": predicate_unknowns_doc(e1_dir)}
    for name, doc in docs.items():
        write_json(out / name, doc)
    return docs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.round3_slots")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    docs = run(out=args.out)
    print(json.dumps({d: v["analysed_clearings"] for d, v in docs["e1/predicate-unknowns.json"]["predicates"].items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
