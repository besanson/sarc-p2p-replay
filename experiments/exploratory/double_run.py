"""The exploratory analyses run twice from the committed slots and the log: byte comparison of the two runs
and with the committed files. Writes results/exploratory/double-run.json.

Usage: python -m experiments.exploratory.double_run
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

from experiments.common import write_json
from experiments.e1 import DEFAULT_LOG
from experiments.exploratory.steps import STEPS, run_all
from p2p_replay.config import ROOT

OUT = ROOT / "out" / "exploratory-double-run"


def sha(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def main() -> int:
    shutil.rmtree(OUT, ignore_errors=True)
    runs = {}
    for name in ("a", "b"):
        runs[name] = run_all(DEFAULT_LOG, ROOT / "results", OUT / name / "results", OUT / name / "paper")
    rows = []
    for rel in runs["a"]:
        side = (lambda r: Path(*r.split("/")[1:])) if rel.startswith("paper/") else None
        a = OUT / "a" / ("paper" if side else "results") / (side(rel) if side else rel)
        b = OUT / "b" / ("paper" if side else "results") / (side(rel) if side else rel)
        committed = ROOT / rel if side else ROOT / "results" / rel
        rows.append({"file": rel if side else f"results/{rel}", "sha256_run_a": sha(a), "sha256_run_b": sha(b),
                     "sha256_committed": sha(committed),
                     "identical": sha(a) is not None and sha(a) == sha(b) == sha(committed)})
    doc = {"exploratory": True, "steps": list(STEPS), "runs": "two runs into out/exploratory-double-run/{a,b}",
           "files": rows, "all_identical": bool(rows) and all(r["identical"] for r in rows)}
    write_json(ROOT / "results" / "exploratory" / "double-run.json", doc)
    print(f"exploratory double run: {len(rows)} files, all identical: {doc['all_identical']}")
    return 0 if doc["all_identical"] else 1


if __name__ == "__main__":
    sys.exit(main())
