"""DECISIONS.md D-G-2, paper v1.1 and release 1.1.0: every change with its slot, the registered items
unchanged, and the departures from the session's wording. Figures are read from the slots.

Usage: python scripts/d_g_2.py --date YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-G-2 "


def _j(rel: str) -> dict:
    return json.loads((ROOT / "results" / rel).read_text(encoding="utf-8"))


def render(date: str) -> str:
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    x1 = _j("exploratory/d4-sensitivity.json")
    a3 = _j("reproduction/attempt-3.json")
    b = x1["exploratory_all"]["explicit_only"]
    return f"""{HEADING}Paper v1.1 and release {version} ({date})

Paper v1.1 applies the decisions of D-G-1 through `paper/template.md`; every new number is filled from a slot.

**Changes, with their slots.**

- Abstract and Conclusion: the strict reading of D4 beside the registered exposure ({b['share_of_clearings']:.4f} of
  clearings, {b['share_of_value']:.4f} of value; `results/exploratory/d4-sensitivity.json`), and the sentence that a failed
  registered predicate is not a confirmed violation of the approval policy.
- Section 3: the registered reading of D4 (the creation is approval-bearing) and the strict reading reported as
  exploratory; the rationale of D-C-2 B (not applicable is not unknown), with what is invariant to it and what depends on it.
- 5.1: D4 sensitivity (exploratory): the three readings with intervals, the split of D4 failures, H2 under the strict
  reading, and the materiality finding (`results/exploratory/d4-sensitivity.json`).
- 5.2: the standardised H1 and H2 beside the registered differences (`results/exploratory/adjusted-h1-h2.json`).
- 5.3: hold friction at both windows (`results/exploratory/hold-friction.json`).
- 5.4: the measurement asymmetry first (`results/e3/human-hold-composition.json`); the people column named "people
  (observed non-release within W)" in both tables, with the composition in a note; the views do not separate wording,
  structure and information content; the gate's column is contract enforcement, not decision accuracy.
- 5.5: the negative result discussed: a loss not declared (D5, D6, D7), an observable not carried (L2), losses absent from
  history (L1 after receipt), and what paper 5's method would need.
- 5.7: reframed as applicability to another log, with what an informative replication needs.
- COVERAGE.md: an undetected class, the magnitude of a price or quantity change, logged in `prereg/DEVIATIONS.md` as a
  description addition; CLAIMS.md: a reading note on C2's D4 component; Appendix B follows.
- Appendix F (model inputs, from `paper/appendix-prompts.md`, X4) and Appendix G (the full X1 to X3 tables); Appendix C:
  the reproduced release named and the exploratory slots' regeneration stated.
- Editorial: every result heading labelled registered, exploratory or secondary; figures renumbered in order of first
  appearance (1 exposure, 2 verdict by outcome, 3 lag bands, 4 hold rates; the files keep their names); the AI disclosure
  shortened to one paragraph that keeps its facts; in the PDF build, code blocks and hashes in running text wrap at the
  margin (layout only).
- Version {version} in `pyproject.toml` and `CITATION.cff`; README status; REPRODUCE.md re-run line.

**Departures from the session's wording, to keep the paper true and the lints passing.** The abstract sentence says
"fail D4", not "fail only D4" ({x1['exploratory_all']['creation_only_d4']['clearings']:,} clearings fail D4 with the creation as the only
approval-bearing event, and some of them fail another predicate as well), and "before the clearing", not "on the line"
(X1 looks for explicit events before t_c). Appendix C names the reproduced release by its tag, `{a3['tag']}`, whose registered
results 1.0.3 and 1.1.0 carry unchanged, not "release 1.0.3". The terminology lint forbids "cause" and allows "defect" only
for a failed predicate: 5.5 says "the reason", the exploratory tables say "failing group", and the replication list says
"enough failed predicates".

**Unchanged.** Every registered file except the COVERAGE.md description addition; every committed slot under `results/`;
every registered estimate, the Holm family and table; every claim status in CLAIMS.md; the related-work section.

The author tags v{version} on the commit that adds this entry ("paper 7: D-G-2, release {version}"); a commit cannot name its
own hash, so the builder's report gives it.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_g_2")
    parser.add_argument("--date", required=True)
    args = parser.parse_args(argv)
    entry = render(args.date)
    text = DECISIONS.read_text(encoding="utf-8")
    if HEADING in text:
        head, rest = text.split(HEADING, 1)
        tail = re.search(r"\n## ", rest)
        text = head + entry + ("\n" + rest[tail.start() + 1:] if tail else "")
    else:
        text = text.rstrip("\n") + "\n\n" + entry
    DECISIONS.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
