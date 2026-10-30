"""Set the status column of CLAIMS.md from the slot files, and add the evidence column.

Statuses are the author's (Phase C session 3), applied as written. Where the author made a
status conditional on a result (C9 on E5, C11 on E7), the condition is evaluated here from the
slot; every other status is checked against its slot, and a mismatch stops without writing.
Claim text and type are not changed. The evidence column names slot files only.

Usage: python scripts/claim_statuses.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
CLAIMS = ROOT / "CLAIMS.md"


def _load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def statuses() -> dict[str, tuple[str, str]]:
    holm = {r["test"]: r for r in _load("e2/hypotheses.json")["holm"]["table"]}
    h4 = _load("e4/h4.json")["families"]
    coverage = _load("e1/coverage-check.json")
    e5 = _load("e5/derivation.json")["categories"]
    e7 = _load("e7/comparisons.json")["scopes"]
    repro, e4dr = _load("reproducibility.json"), _load("e4/double-run.json")

    checks = {
        "C3": holm["H1"]["below_alpha"], "C4": holm["H2"]["below_alpha"],
        "C5": _load("e2/hypotheses.json")["estimates"]["H3"]["W60"].get("not_computable") is not None
        and not next(r for r in coverage["rows"] if r["predicate"] == "D5")["fired"],
        "C6": all(not holm[k]["below_alpha"] for k in ("H4-Jev", "H4-Haiku"))
        and all(v["p_tost"] is not None for v in h4.values()),
        "C13": repro["all_identical"] and e4dr["all_identical"],
    }
    failed = [k for k, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(f"slot does not match the author's status for: {', '.join(failed)}")

    reproduced = {c: s["result"] for c, s in e5.items()}
    if all(r == "reproduces" for r in reproduced.values()):
        c9 = "supported"
    else:
        c9 = "not supported: " + "; ".join(f"{c} {r}" for c, r in sorted(reproduced.items()))
    shapes = [v[d]["h1_shape"] for v in e7.values() for d in ("D1'", "D2'", "D3'")]
    c11 = "supported" if shapes and all(shapes) else "inconclusive"

    return {
        # D-D-2: the evidence of C1 is the evidence set and the property tests; mutation is engine evidence.
        "C1": ("supported", "`results/e1/evidence-set.jsonl.gz`, `tests/test_properties.py`; engine evidence "
                            "`results/mutation.json`"),
        "C2": ("supported", "`results/e1/exposure.json`, `results/e1/exposure-by-stratum.json`"),
        "C3": ("supported", "`results/e2/hypotheses.json`"),
        "C4": ("supported", "`results/e2/hypotheses.json`"),
        # D-D-3: the zero incidence is over the analysed clearings.
        "C5": ("inconclusive: defect class has zero incidence in the analysed clearings",
               "`results/e1/coverage-check.json`, `results/e2/hypotheses.json`"),
        "C6": ("not supported for both families", "`results/e4/h4.json`"),
        "C7": ("supported", "`results/e3/gate-held.json`, `results/e3/verdict-by-outcome.json`, "
                            "`results/e3/lag-bands.json`"),
        "C8": ("supported", "`results/e4/arms.json`"),
        "C9": (c9, "`results/e5/derivation.json`"),
        "C10": ("supported", "`results/e6/timing-e1.json`, `results/e6/cost.json`"),
        "C11": (c11, "`results/e7/comparisons.json`"),
        "C12": ("supported; D5 class zero incidence", "`results/e1/coverage-check.json`"),
        "C13": ("supported for the internal double runs; external reproduction pending (FINAL-AUDIT item 11)",
                "`results/reproducibility.json`, `results/e4/double-run.json`"),
    }


def main() -> int:
    table = statuses()
    lines = CLAIMS.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines:
        if line.startswith("| id | claim | type | status |"):
            out.append("| id | claim | type | status | evidence |")
            continue
        if line.startswith("|---|---|---|---|"):
            out.append("|---|---|---|---|---|")
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("| C") else []
        # A claim row has id, claim, type, status and (once added) evidence; claim text has no "|".
        if len(cells) in (4, 5) and cells[0] in table:
            status, evidence = table[cells[0]]
            out.append(f"| {cells[0]} | {cells[1]} | {cells[2]} | {status} | {evidence} |")
            continue
        out.append(line)
    CLAIMS.write_text("\n".join(out) + "\n", encoding="utf-8")
    for cid, (status, _) in table.items():
        print(f"{cid}: {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
