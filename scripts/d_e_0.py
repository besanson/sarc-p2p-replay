"""DECISIONS.md D-E-0, the author's read of the v1.0 candidate (review-secondary/D-author-read-v1.0-candidate.md):
the four points, the six series records as verified (from verified-citations.json), and, with
`--layout`, the PDF table layout (overfull boxes from out/paper-tex/overfull.json, written by
scripts/build_tex.py). Nothing is typed.

Usage: python scripts/d_e_0.py --date YYYY-MM-DD [--layout]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-E-0 "
SERIES = ("besanson-paper1-2026", "besanson-paper2-2026", "besanson-paper3-2026", "besanson-paper4-2026",
          "besanson-paper5-2026", "besanson-paper6-2026")


def records() -> str:
    cites = {c["id"]: c for c in json.loads((ROOT / "verified-citations.json").read_text(encoding="utf-8"))["citations"]}
    rows = ["| paper | arXiv id | title | v1 submitted | status |", "|---|---|---|---|---|"]
    for n, cid in enumerate(SERIES, 1):
        c = cites[cid]
        arxiv = re.search(r"arXiv:(\d{4}\.\d{5})", c["venue"]).group(1)
        v1 = re.search(r"v1 submitted ([^.]+UTC)", c["verified_via"]).group(1)
        rows.append(f"| {n} | {arxiv} | {c['title']} | {v1} | {c['status']} |")
    return "\n".join(rows)


def layout() -> str:
    o = json.loads((ROOT / "out" / "paper-tex" / "overfull.json").read_text(encoding="utf-8"))
    return f"""
**PDF table layout** (layout only, no wording). The overfull boxes of the v1.0 candidate's PDF came
from wide tables. `scripts/build_tex.py` now post-processes pandoc's LaTeX: every table is set in a
smaller font with its columns as fixed fractions of the text width (`p{{}}` columns in the
longtable, wrapping the cells), so that no table runs past the margin. The Markdown paper and the
template are unchanged. pdflatex now reports {o['overfull_hboxes']} overfull hboxes, {o['overfull_hboxes_over_10pt']}
wider than 10pt (before: {o['before_overfull_hboxes']}). The build stays deterministic: G9 rebuilds twice and compares both
with the committed `paper-tex/main.pdf`.
"""


def render(date: str, with_layout: bool) -> str:
    return f"""{HEADING}Author's read of the v1.0 candidate ({date})

The author's read (`review-secondary/D-author-read-v1.0-candidate.md`, committed unedited with its
attestation) raised four points; the author accepted all four, applied as written through
`paper/template.md`:

a. Section 1, the SARC series: the arXiv search for "Besanson"
   (https://arxiv.org/search/?query=Besanson&searchtype=all&source=header) returned ten records whose
   author is Gaston Besanson; six are the series, the other four (2604.17431, 2604.00218, 2602.22750,
   2602.13283) are outside it and are not cited. Each abstract page was fetched on {date}; title,
   author ("Besanson, Gaston") and submission date are recorded in `verified-citations.json`. Mapped
   to papers 1 to 6 by title and role, the ids agree with the author's list (2605.07728, 2606.15954,
   2607.26313, 2608.18360, 2609.26016, 2610.10978), and the existing paper 4 and paper 5 records carry
   2608.18360 and 2609.26016. No disagreement. Paper 6 is cited by its arXiv record; the repository
   record stays in `verified-citations.json`, no longer cited. "We found no record that identifies
   papers 1 to 3, and do not cite them." is replaced by one sentence citing all six, Besanson 2026a
   to 2026f in series order; the letters are now assigned among the records the paper cites.

{records()}

b. Section 7: the three-column sentence names its lines ("on the 1,848 sample lines the log
   classifies") and gives the clean-line hold rates on both bases (classified lines and all sample
   lines), each figure from its slot (`results/e4/arms-classified-lines.json`, `results/e4/arms.json`).
c. Appendix B (C13): the paper's status reads "supported for the internal double runs; external
   reproduction from a clean clone is pending", without the internal label "(FINAL-AUDIT item 11)";
   `CLAIMS.md` keeps its status and evidence path. Appendix C already read so.
d. Acknowledgements: the platforms' model strings are introduced once as "unverified in-chat
   self-reports of the platforms".
""" + (layout() if with_layout else "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_e_0")
    parser.add_argument("--date", required=True)
    parser.add_argument("--layout", action="store_true")
    args = parser.parse_args(argv)
    entry = render(args.date, args.layout)
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
