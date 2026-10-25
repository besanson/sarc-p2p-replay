"""Review packet, round 1 (Phase D): review-secondary/D1-review-packet.md.

Carries, verbatim and each with its SHA-256, paper/paper.md (draft v0.1, generated from the slots),
CLAIMS.md, COVERAGE.md and prereg/DEVIATIONS.md, with the instructions to the reviewer. Layout as
the A1 fence packet. The reply is committed unedited, with its SHA-256.

Usage: python scripts/review_packet.py --date YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "review-secondary" / "D1-review-packet.md"
PARTS = (("Part 1. The paper, draft v0.1", "paper/paper.md"),
         ("Part 2. Claims and statuses", "CLAIMS.md"),
         ("Part 3. Coverage matrix", "COVERAGE.md"),
         ("Part 4. Deviations from the registration", "prereg/DEVIATIONS.md"))
INSTRUCTIONS = ("Read the paper against its registration. Say where a sentence claims more than its slot supports, where "
                "a number lacks a source, where the writing hides a deviation, and what a hostile reviewer would ask "
                "first. Reply in any form; your text is committed unedited.")


def render(date: str) -> str:
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    lines = [
        "# D1 review packet, round 1: paper 7", "",
        "| field | value |", "|---|---|",
        "| paper | Silent Evidence Defects in the Wild: A Registered Replay of a Real Purchase-to-Pay Process |",
        "| author | Gaston Besanson, Universidad Torcuato Di Tella |",
        "| registration | `p7-v1.1`, tag `prereg-p7-v1.1` on commit `d8cdb2d` (supersedes `p7-v1`, tag `prereg-p7-v1` on `e239864`) |",
        f"| draft | v0.1, generated from the slot files by `scripts/fill_paper.py` |",
        f"| packet date | {date}, built on the commit after `{head}` |",
        "| repository | https://github.com/besanson/sarc-p2p-replay |", "",
        "The registration itself is `prereg/p7-v1.1.md` in the repository; every number in the paper is traceable to "
        "its slot file through `results/filled-template.json`. The reply is committed to the repository unedited, "
        "with its SHA-256.", "",
        "## Instructions to the reviewer", "", INSTRUCTIONS, "",
    ]
    for title, rel in PARTS:
        data = (ROOT / rel).read_bytes()
        lines += [f"## {title} ({rel})", "",
                  f"Source: `{rel}`, SHA-256 `{hashlib.sha256(data).hexdigest()}`. Copied verbatim between the rules.",
                  "", "---", "", data.decode("utf-8").rstrip("\n"), "", "---", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="review_packet")
    parser.add_argument("--date", required=True)
    args = parser.parse_args(argv)
    OUT.write_text(render(args.date), encoding="utf-8")
    print(f"review packet: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
