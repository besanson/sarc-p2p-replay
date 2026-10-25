"""Double run of the E4 analysis: writes into out/e4-check/ and compares with the committed files.

Writes results/e4/double-run.json (arm e4) or results/e4-exploratory/double-run.json.

Usage: python scripts/recheck_e4.py [--arm e4|e4-exploratory]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from experiments import e4  # noqa: E402


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="recheck_e4")
    parser.add_argument("--arm", default="e4")
    args = parser.parse_args(argv)
    target = ROOT / "results" / ("e4" if args.arm == "e4" else "e4-exploratory")
    work = ROOT / "out" / f"{args.arm}-check"
    suffix = "" if args.arm == "e4" else "-exploratory"
    e4.run(args.arm, out=work, hypotheses=work / "hypotheses.json")
    pairs = [(target / f"arms{suffix}.json", work / f"arms{suffix}.json"),
             (target / f"h4{suffix}.json", work / f"h4{suffix}.json")]
    if args.arm == "e4":
        pairs.append((ROOT / "results" / "e2" / "hypotheses.json", work / "hypotheses.json"))
    rows = [{"file": str(a.relative_to(ROOT)), "sha256_committed": digest(a), "sha256_rerun": digest(b),
             "identical": digest(a) == digest(b)} for a, b in pairs]
    doc = {"arm": args.arm, "files": rows, "all_identical": all(r["identical"] for r in rows)}
    (target / "double-run.json").write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"all_identical": doc["all_identical"]}))
    return 0 if doc["all_identical"] else 1


if __name__ == "__main__":
    sys.exit(main())
