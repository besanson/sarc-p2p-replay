"""Mutation gate, ported from paper 5's mutation_check.py (sarc-authority-derivation).

Reads mutants/mutmut-cicd-stats.json (written by `mutmut export-cicd-stats`)
and fails if the kill score killed / (killed + survived) on src/p2p_replay is
below 0.85, or if any mutant had no covering test. ``--out FILE`` also writes the result with the
commit and the git tree id of src/ the mutants were made from (results/mutation-release.json for
the release, D-E-2; results/mutation.json is the Phase B/C record).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

THRESHOLD = 0.85
STATS_PATH = Path(__file__).resolve().parent.parent / "mutants" / "mutmut-cicd-stats.json"


def run(stats_path: Path = STATS_PATH) -> dict:
    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    killed, survived, no_tests = stats["killed"], stats["survived"], stats["no_tests"]
    denominator = killed + survived
    score = killed / denominator if denominator else 0.0
    return {
        "killed": killed, "survived": survived, "no_tests": no_tests, "total": stats["total"],
        "kill_score": score, "threshold": THRESHOLD,
        "passes": score >= THRESHOLD and no_tests == 0,
    }


def provenance() -> dict:
    """The tree the mutants were made from: the commit and the git tree id of src/ (FINAL-AUDIT item 4)."""
    import subprocess  # noqa: PLC0415

    root = Path(__file__).resolve().parent.parent
    git = lambda *a: subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True).stdout.strip()  # noqa: E731
    return {"commit": git("rev-parse", "HEAD"), "src_tree": git("rev-parse", "HEAD:src"),
            "src_clean": git("status", "--porcelain", "--", "src") == ""}


def main() -> int:
    result = run()
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])
        out.write_text(json.dumps({**result, **provenance()}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"mutation: kill score {result['kill_score']:.4f} "
          f"({result['killed']}/{result['killed'] + result['survived']}), no_tests={result['no_tests']}, "
          f"threshold {THRESHOLD}: {'PASS' if result['passes'] else 'FAIL'}")
    return 0 if result["passes"] else 1


if __name__ == "__main__":
    sys.exit(main())
