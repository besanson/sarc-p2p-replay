"""E6, timing part (prereg/p7-v1.1.md section 6, E6).

Runs the full E1 runner three times from the log, each into its own directory
under out/e6/, and writes results/e6/timing-e1.json: per run the wall time of
the replay (log read, observation end, replay of every line, evidence set
written) and of the whole E1 runner (with the bootstrap), the median of the
three, seconds per decision (median replay time over the analysed clearings),
the hardware, and whether the three runs wrote byte-identical files. The cost
column (USD per decision per family) waits for E4.

Usage: python -m experiments.e6 [--log data/BPI_Challenge_2019.xes] [--runs 3]
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import statistics
import sys
from pathlib import Path
from typing import Any

import numpy as np

from experiments import e1
from experiments.common import BOOTSTRAP_B, E0_LINES, write_json
from p2p_replay.config import REGISTRATION, ROOT, T_END_MONTH_MIN_EVENTS

DEFAULT_OUT = ROOT / "results" / "e6"
DEFAULT_WORK = ROOT / "out" / "e6"
RUNS = 3


def _proc(path: str, key: str) -> str | None:
    try:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.split(":", 1)[0].strip() == key:
                return line.split(":", 1)[1].strip()
    except OSError:
        return None
    return None


def hardware() -> dict[str, Any]:
    return {
        "cpu_model": _proc("/proc/cpuinfo", "model name") or platform.processor() or None,
        "cpu_cores": os.cpu_count(),
        "memory_total": _proc("/proc/meminfo", "MemTotal"),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "numpy": np.__version__,
    }


def tree_digest(directory: Path) -> dict[str, str]:
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob("*")) if p.is_file()}


def run(log: Path, out: Path, work: Path, runs: int = RUNS, e0_path: Path = E0_LINES,
        min_month_events: int = T_END_MONTH_MIN_EVENTS, b: int = BOOTSTRAP_B) -> dict[str, Any]:
    timings, digests, clearings = [], [], None
    for k in range(1, runs + 1):
        target = work / f"run-{k}" / "e1"
        result = e1.run(log, target, e0_path, min_month_events, b)
        timings.append({"run": k, "replay_seconds": round(result["seconds"]["replay"], 1),
                        "e1_runner_seconds": round(result["seconds"]["total"], 1)})
        digests.append(tree_digest(target))
        clearings = result["analysed_clearings"]
    replay = statistics.median(t["replay_seconds"] for t in timings)
    total = statistics.median(t["e1_runner_seconds"] for t in timings)
    report = {
        "registration": REGISTRATION,
        "section": "6, E6 (timing of E1)",
        "log": log.name,
        "runs": timings,
        "median_replay_seconds": replay,
        "median_e1_runner_seconds": total,
        "analysed_clearings": clearings,
        "seconds_per_decision": replay / clearings if clearings else None,
        "seconds_per_decision_rule": "median replay seconds over three full runs / analysed clearings",
        "outputs_byte_identical_across_runs": all(d == digests[0] for d in digests),
        "hardware": hardware(),
        "cost_usd_per_decision": None,
        "cost_status": "waits for E4",
    }
    write_json(out / "timing-e1.json", report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.e6")
    parser.add_argument("--log", type=Path, default=e1.DEFAULT_LOG)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--work", type=Path, default=DEFAULT_WORK)
    parser.add_argument("--runs", type=int, default=RUNS)
    args = parser.parse_args(argv)
    report = run(args.log, args.out, args.work, args.runs)
    print(f"E6: median replay {report['median_replay_seconds']} s over {len(report['runs'])} runs; "
          f"identical outputs: {report['outputs_byte_identical_across_runs']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
