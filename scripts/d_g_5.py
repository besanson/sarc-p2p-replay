"""DECISIONS.md D-G-5, the author's final verification of 1.1.1: three presentation items and their application.
Figures are read from the slots.

Usage: python scripts/d_g_5.py --date YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-G-5 "


def render(date: str) -> str:
    x6 = json.loads((ROOT / "results" / "exploratory" / "e4-strict-d4.json").read_text(encoding="utf-8"))
    cell = "defective -> clean"
    a = x6["arms"]
    return f"""{HEADING}Author's final verification of 1.1.1 ({date})

Three presentation items; no model call, no registered file, committed slot or registered estimate changes.

1. **Figure panel title.** The hold-rates figure's exploratory panel title, "timeline view (exploratory, corrected)",
   was cut off in the PDF. Applied: the title is "timeline view (corrected)" (`scripts/figures.py`), and every figure is
   saved with `bbox_inches="tight"` (pad 0.04 in), which fits the saved figure to its drawn extent. That extent is
   computed from the drawn text, so a second run gives the same bytes. The SVG, PDF and `figure-data.json` files are
   regenerated, and two runs are byte-identical. In the rebuilt PDF every panel title of the four figures is fully
   visible (checked by rendering the pages).
2. **Strict-D4 sentences.** 5.4 (exploratory paragraph) and Section 7 state, from
   `results/exploratory/e4-strict-d4.json` and through the template, that under the strict reading of D4
   {x6['registered_x_strict'][cell]:,} of the {a['gate (registered)']['registered_groups']['defective']['lines']:,} sample lines
   with a failed registered predicate become clean; that the models held nearly all of them (Jev
   {a['jev']['cells'][cell]['held']:,}, Haiku {a['haiku']['cells'][cell]['held']:,}); that their hold rates on strict-clean lines
   are {a['jev']['strict_groups']['clean']['hold_rate']:.1%} and {a['haiku']['strict_groups']['clean']['hold_rate']:.1%};
   that the apparent selectivity of a model-based decision depends on the contract it is measured against; and that the
   sample was stratified under the registered contract, not the strict one. Both are labelled exploratory.
   `scripts/fill_paper.py` now reads " -> " inside a placeholder key as part of the key, not as a path separator, so that
   the slot's cell keys can be addressed.
3. **Introduction sentence.** "This paper is the number, on one real process." becomes "This paper measures those defects
   on one real process." The paragraph defines the defect as a decision on evidence that fails a predicate, so the
   terminology lint's defect rule holds; it passes.

The paper, figures, `main.tex` and `main.pdf` regenerate byte-identically twice; CLAIMS.md is unchanged.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_g_5")
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
