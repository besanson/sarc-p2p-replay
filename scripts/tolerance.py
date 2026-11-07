"""Comparison of a regenerated file with the committed one: byte identity, and for JSON and JSON lines
(plain or gzip) equality within tolerance (D-F-1, release 1.0.1).

Within tolerance: the parsed structures are equal, every string, boolean and null equal, and every pair of
numbers a, b satisfies |a - b| <= REL * max(1, |a|, |b|). Floating-point last digits can differ across
machines and architectures; text files (the paper, its TeX, the README) are compared by bytes only.
Used by scripts/reproduce.py and by gate G4 (scripts/gates.py). `python scripts/tolerance.py --record`
writes the rule, with the builder's architecture, to results/reproduction/comparison-rule.json, the
slot the paper's Appendix C reads it from.

Usage: python scripts/tolerance.py --record
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any

REL = 1e-12
PARSED = (".json", ".jsonl", ".jsonl.gz")


def sha256(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def parsed(p: Path) -> Any:
    name = p.name
    if name.endswith(".jsonl.gz"):
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]
    text = p.read_text(encoding="utf-8")
    if name.endswith(".jsonl"):
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return json.loads(text)


def diff(a: Any, b: Any, rel: float = REL) -> tuple[bool, float]:
    """(equal within tolerance, maximum absolute difference between paired numbers)."""
    if isinstance(a, bool) or isinstance(b, bool) or a is None or b is None or isinstance(a, str) or isinstance(b, str):
        return a == b and type(a) is type(b), 0.0
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
            return True, 0.0
        d = abs(a - b)
        return d <= rel * max(1.0, abs(a), abs(b)), float(d)
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return False, 0.0
        ok, worst = True, 0.0
        for k in a:
            o, w = diff(a[k], b[k], rel)
            ok, worst = ok and o, max(worst, w)
        return ok, worst
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return False, 0.0
        ok, worst = True, 0.0
        for x, y in zip(a, b):
            o, w = diff(x, y, rel)
            ok, worst = ok and o, max(worst, w)
        return ok, worst
    return False, 0.0


def compare(committed: Path, regenerated: Path) -> dict[str, Any]:
    """Byte identity for every file; for JSON and JSON lines also equality within tolerance."""
    ha, hb = sha256(committed), sha256(regenerated)
    row: dict[str, Any] = {"committed": ha, "regenerated": hb, "byte_identical": ha is not None and ha == hb,
                           "parsed": committed.name.endswith(PARSED)}
    if not row["parsed"]:
        row.update(within_tolerance=row["byte_identical"], max_abs_difference=None)
    elif hb is None or ha is None:
        row.update(within_tolerance=False, max_abs_difference=None)
    elif row["byte_identical"]:
        row.update(within_tolerance=True, max_abs_difference=0.0)
    else:
        try:
            ok, worst = diff(parsed(committed), parsed(regenerated))
        except (ValueError, OSError):
            ok, worst = False, None
        row.update(within_tolerance=ok, max_abs_difference=worst)
    row["equal"] = row["within_tolerance"]
    return row


def main(argv: list[str]) -> int:
    if "--record" not in argv:
        print(f"tolerance: |a - b| <= {REL:g} x max(1, |a|, |b|)")
        return 0
    out = Path(__file__).resolve().parent.parent / "results" / "reproduction" / "comparison-rule.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "relative_tolerance": REL,
        "rule": "parsed structures and strings equal; every number pair a, b with |a - b| <= relative_tolerance "
                "x max(1, |a|, |b|); text files (paper, TeX, README) by bytes; figure SVG and PDF bytes not "
                "compared, the plotted numbers (paper/figures/figure-data.json) within tolerance",
        "applies_to": "scripts/reproduce.py and gate G4, from release 1.0.1 (DECISIONS.md D-F-1, D-F-2)",
        "builder": {"system": platform.system(), "architecture": platform.machine()},
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"tolerance: wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
