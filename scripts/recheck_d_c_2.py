"""Checks for D-C-2 B, written to results/checks-d-c-2.json.

1. A fresh E1 run from the log (given with --rerun-e1) against the committed results/e1/:
   every committed file byte-identical; files new in the rerun are listed and copied in.
2. E2 re-run on results/e1 into out/: every results/e2 file byte-identical.
3. E3 run twice on results/e1 (results/e3 and out/): byte-identical.

Usage: python scripts/recheck_d_c_2.py --rerun-e1 out/c2/e1
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from experiments import e2, e3  # noqa: E402

RESULTS = ROOT / "results"


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def compare(a: Path, b: Path) -> list[dict]:
    names = sorted({p.name for p in a.iterdir()} | {p.name for p in b.iterdir()})
    return [{"file": n,
             "sha256_a": digest(a / n) if (a / n).exists() else None,
             "sha256_b": digest(b / n) if (b / n).exists() else None,
             "identical": (a / n).exists() and (b / n).exists() and digest(a / n) == digest(b / n)}
            for n in names]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="recheck_d_c_2")
    parser.add_argument("--rerun-e1", type=Path, required=True)
    parser.add_argument("--work", type=Path, default=ROOT / "out" / "c2")
    args = parser.parse_args(argv)
    committed = sorted(p.name for p in (RESULTS / "e1").iterdir())
    e1_rows = [r for r in compare(RESULTS / "e1", args.rerun_e1) if r["file"] in committed]
    new = sorted(p.name for p in args.rerun_e1.iterdir() if p.name not in committed)
    for name in new:
        shutil.copyfile(args.rerun_e1 / name, RESULTS / "e1" / name)
    e2.run(RESULTS / "e1", args.work / "e2")
    e2_rows = compare(RESULTS / "e2", args.work / "e2")
    e3.run(RESULTS / "e1", RESULTS / "e3")
    e3.run(RESULTS / "e1", args.work / "e3")
    e3_rows = compare(RESULTS / "e3", args.work / "e3")
    out = {
        "amendment": "DECISIONS.md D-C-2 B",
        "e1_rerun_from_log": {"committed_files": e1_rows, "all_committed_identical": all(r["identical"] for r in e1_rows),
                              "new_files": new},
        "e2_rerun": {"files": e2_rows, "all_identical": all(r["identical"] for r in e2_rows)},
        "e3_double_run": {"files": e3_rows, "all_identical": all(r["identical"] for r in e3_rows)},
    }
    (RESULTS / "checks-d-c-2.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v.get("all_committed_identical", v.get("all_identical")) for k, v in out.items()
                      if isinstance(v, dict)}))
    return 0 if all(v.get("all_committed_identical", v.get("all_identical", True)) for v in out.values()
                    if isinstance(v, dict)) else 1


if __name__ == "__main__":
    sys.exit(main())
