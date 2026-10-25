"""Byte comparison of a runner's committed output directory with a second run's, as a slot file.

Usage: python scripts/compare_dirs.py COMMITTED_DIR RERUN_DIR OUT_JSON
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def digest(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def main(argv: list[str]) -> int:
    a, b, out = Path(argv[0]), Path(argv[1]), Path(argv[2])
    names = sorted({p.name for p in a.iterdir() if p.is_file()} | {p.name for p in b.iterdir() if p.is_file()}
                   - {out.name})
    rows = [{"file": n, "sha256_committed": digest(a / n), "sha256_rerun": digest(b / n),
             "identical": digest(a / n) is not None and digest(a / n) == digest(b / n)} for n in names]
    doc = {"committed": str(a.resolve().relative_to(ROOT)), "files": rows,
           "all_identical": bool(rows) and all(r["identical"] for r in rows)}
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(rows), "all_identical": doc["all_identical"]}))
    return 0 if doc["all_identical"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
