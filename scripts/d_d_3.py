"""DECISIONS.md D-D-3, the round-2 adjudication, and the "Changes since v0.2" list for the round-3 packet.

The entry opens with the records of Phase D session 3 (the A1 sweep statements, the filled template
moved beside the paper, the commits that fail the paper-regeneration test), then one table over the
three round-2 reviews (review-secondary/D2-review-arana.md, D2-review-chatgpt.md,
D2-review-perplexity.md): finding, who raised it, class, decision, reason, where applied. The
decisions are the author's (Phase D session 3), applied as written. Figures in the table are read
from the slots, never typed.

Usage: python scripts/d_d_3.py --date YYYY-MM-DD [--records-only]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-D-3 "

RECORDS = """**Records.**

- *A1 sweep statements.* The attestation of the A1 second sweep
  (`review-secondary/A1-fence-sweep-deepseek.attestation.md`) and D-A1-0c carry a second dated
  paragraph: in the same Perplexity Computer session, after the round-1 review, the platform
  identified the model of the 2026-10-14 sweep as DeepSeek V4 Pro and the model of the round-1 review
  as Claude Opus 5.5 (`review-secondary/D2-review-perplexity.md`, the Acknowledgements row). Both
  statements are on record, in order; the Acknowledgements say the same.
- *Filled template moved.* `results/filled-template.json` is now `paper/filled-template.json`; its
  readers (the typed-numeral lint, G4 and G9 in `scripts/gates.py`, `tests/test_paper.py`,
  `scripts/fill_paper.py`, `scripts/review_packet.py`, the results and paper READMEs) follow. The
  rule: experiment slots under `results/` never change once committed (new slot files may be added);
  derived records of the paper live beside the paper and regenerate with it.
- *Paper-regeneration test.* Commits `a09c4b1` (D-D-2) and `08d860c` (round-1 slots) fail
  `tests/test_paper.py::test_committed_paper_matches_the_template`: the slots changed before the
  paper was regenerated, and the failing exit code was hidden by a pipe. `b01be29` (draft v0.2)
  passes. The builder's test runs now fail on a failing exit code (`set -o pipefail`).
"""


def render(date: str, records_only: bool = False) -> str:
    entry = f"{HEADING}Round-2 adjudication ({date})\n\n{RECORDS}"
    if records_only:
        return entry
    return entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_d_3")
    parser.add_argument("--date", required=True)
    parser.add_argument("--records-only", action="store_true")
    args = parser.parse_args(argv)
    entry = render(args.date, args.records_only)
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
