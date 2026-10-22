"""Double run of E1, E2 and E3 from the log, with a byte comparison.

Runs E1 then E2 and E3 on its evidence set twice: run A into results/ (the
committed slots) and run B into out/repro/run-b/. Every file the runners write
is compared byte for byte. Writes results/reproducibility.json: per run the
wall time of each runner, and per file its SHA-256 in each run and whether
the two are identical.

Usage: python -m experiments.repro [--log data/BPI_Challenge_2019.xes]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path
from typing import Any

from experiments import e1, e2, e3
from experiments.common import BOOTSTRAP_B, E0_LINES, write_json
from p2p_replay.config import REGISTRATION, ROOT, T_END_MONTH_MIN_EVENTS

RUNNERS = ("e1", "e2", "e3")


def run_once(log: Path, base: Path, e0_path: Path, min_month_events: int, b: int) -> dict[str, float]:
    seconds = {}
    start = time.perf_counter()
    e1.run(log, base / "e1", e0_path, min_month_events, b)
    seconds["e1"] = time.perf_counter() - start
    start = time.perf_counter()
    e2.run(base / "e1", base / "e2", b)
    seconds["e2"] = time.perf_counter() - start
    start = time.perf_counter()
    e3.run(base / "e1", base / "e3", b)
    seconds["e3"] = time.perf_counter() - start
    return {k: round(v, 1) for k, v in seconds.items()}


def compare(a: Path, b: Path) -> list[dict[str, Any]]:
    rows = []
    for runner in RUNNERS:
        names = sorted({p.relative_to(a) for p in (a / runner).rglob("*") if p.is_file()}
                       | {p.relative_to(b) for p in (b / runner).rglob("*") if p.is_file()})
        for name in names:
            fa, fb = a / name, b / name
            ha = hashlib.sha256(fa.read_bytes()).hexdigest() if fa.is_file() else None
            hb = hashlib.sha256(fb.read_bytes()).hexdigest() if fb.is_file() else None
            rows.append({"file": str(name), "sha256_run_a": ha, "sha256_run_b": hb,
                         "identical": ha is not None and ha == hb})
    return rows


def code_digest(root: Path = ROOT) -> dict[str, str]:
    """SHA-256 of every runner, engine and registered companion file at run time."""
    paths = sorted([*(root / "experiments").glob("*.py"), *(root / "src" / "p2p_replay").glob("*.py"),
                    *(root / "prereg").glob("*.yaml"), root / "prereg" / "p7-v1.1.md"])
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def run(log: Path, run_a: Path, run_b: Path, report: Path, e0_path: Path = E0_LINES,
        min_month_events: int = T_END_MONTH_MIN_EVENTS, b: int = BOOTSTRAP_B) -> dict[str, Any]:
    seconds_a = run_once(log, run_a, e0_path, min_month_events, b)
    seconds_b = run_once(log, run_b, e0_path, min_month_events, b)
    files = compare(run_a, run_b)
    out = {"registration": REGISTRATION, "log": log.name,
           "runs": {"A": {"directory": "results", "seconds": seconds_a},
                    "B": {"directory": "out/repro/run-b", "seconds": seconds_b}},
           "code_sha256": code_digest(),
           "files": files, "files_compared": len(files),
           "all_identical": bool(files) and all(f["identical"] for f in files)}
    write_json(report, out)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.repro")
    parser.add_argument("--log", type=Path, default=e1.DEFAULT_LOG)
    parser.add_argument("--run-a", type=Path, default=ROOT / "results")
    parser.add_argument("--run-b", type=Path, default=ROOT / "out" / "repro" / "run-b")
    parser.add_argument("--report", type=Path, default=ROOT / "results" / "reproducibility.json")
    args = parser.parse_args(argv)
    out = run(args.log, args.run_a, args.run_b, args.report)
    print(f"repro: {out['files_compared']} files compared; all identical: {out['all_identical']}")
    return 0 if out["all_identical"] else 1


if __name__ == "__main__":
    sys.exit(main())
