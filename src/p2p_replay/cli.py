"""Command line: replay an event log and write the evidence sets.

    python -m p2p_replay replay LOG --out EVIDENCE.jsonl [--dataset bpi2019]
        [--mapping prereg/column-mapping.yaml] [--patterns prereg/outcome-patterns.yaml]
        [--frame-counts FRAME.json]

`--dataset bpi2019` writes one evidence set per analysed clearing;
`--dataset bpi2020` writes one record per payment (E7). Any log in XES or CSV
runs with a mapping in the registered shape (C13). The command writes records
and frame counts only; it computes no rate, interval or test.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from .config import MAPPING_PATH, PATTERNS_PATH, load_mapping, load_patterns
from .declarations import replay_declarations
from .frame import STATUSES
from .reader import read_log
from .replay import replay_log


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="p2p_replay")
    sub = parser.add_subparsers(dest="command", required=True)
    rep = sub.add_parser("replay", help="replay a log and write evidence sets as JSON lines")
    rep.add_argument("log", type=Path)
    rep.add_argument("--out", type=Path, required=True)
    rep.add_argument("--dataset", choices=("bpi2019", "bpi2020"), default="bpi2019")
    rep.add_argument("--mapping", type=Path, default=MAPPING_PATH)
    rep.add_argument("--patterns", type=Path, default=PATTERNS_PATH)
    rep.add_argument("--frame-counts", type=Path, default=None)
    return parser


def run_replay(args: argparse.Namespace) -> int:
    mapping = load_mapping(args.dataset, args.mapping)
    p2p, decl = load_patterns(args.patterns)

    def open_cases():
        return read_log(args.log, mapping)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    counts: Counter[str] = Counter()
    with args.out.open("w", encoding="utf-8", newline="\n") as out:
        if args.dataset == "bpi2019":
            for result in replay_log(open_cases, p2p, mapping.get("flag_true", ["true"])):
                counts[result.frame.status] += 1
                for record in result.records:
                    out.write(record.to_json() + "\n")
                    written += 1
        else:
            for record in replay_declarations(open_cases, decl):
                out.write(record.to_json() + "\n")
                written += 1
    if args.frame_counts is not None:
        ordered = {s: counts.get(s, 0) for s in STATUSES} if args.dataset == "bpi2019" else {}
        args.frame_counts.write_text(json.dumps(ordered, indent=2) + "\n", encoding="utf-8")
    print(f"p2p_replay: {written} record(s) written to {args.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "replay":
        return run_replay(args)
    return 2  # pragma: no cover - argparse rejects unknown commands


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
