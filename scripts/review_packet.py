"""Review packets (Phase D): review-secondary/D<round>-review-packet.md.

Carries, verbatim and each with its SHA-256, paper/paper.md (the current draft, generated from the slots),
CLAIMS.md, COVERAGE.md and prereg/DEVIATIONS.md, with the instructions to the reviewer. Layout as
the A1 fence packet. The reply is committed unedited, with its SHA-256. From round 2 on, the packet
adds "Changes since" the previous draft, generated from the adjudication table (scripts/d_d_2.py for
round 2), so that reviewers can check each accepted finding where it was applied.

Usage: python scripts/review_packet.py --date YYYY-MM-DD [--round 2]
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFTS = {1: "v0.1", 2: "v0.2"}
PARTS = (("Part 1. The paper, draft {draft}", "paper/paper.md"),
         ("Part 2. Claims and statuses", "CLAIMS.md"),
         ("Part 3. Coverage matrix", "COVERAGE.md"),
         ("Part 4. Deviations from the registration", "prereg/DEVIATIONS.md"))
INSTRUCTIONS = ("Read the paper against its registration. Say where a sentence claims more than its slot supports, where "
                "a number lacks a source, where the writing hides a deviation, and what a hostile reviewer would ask "
                "first. Reply in any form; your text is committed unedited.")


def render(date: str, rnd: int = 1) -> str:
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    draft = DRAFTS[rnd]
    lines = [
        f"# D{rnd} review packet, round {rnd}: paper 7", "",
        "| field | value |", "|---|---|",
        "| paper | Silent Evidence Defects in the Wild: A Registered Replay of a Real Purchase-to-Pay Process |",
        "| author | Gaston Besanson, Universidad Torcuato Di Tella |",
        "| registration | `p7-v1.1`, tag `prereg-p7-v1.1` on commit `d8cdb2d` (supersedes `p7-v1`, tag `prereg-p7-v1` on `e239864`) |",
        f"| draft | {draft}, generated from the slot files by `scripts/fill_paper.py` |",
        f"| packet date | {date}, built on the commit after `{head}` |",
        "| repository | https://github.com/besanson/sarc-p2p-replay |", "",
        "The registration itself is `prereg/p7-v1.1.md` in the repository; every number in the paper is traceable to "
        "its slot file through `results/filled-template.json`. The reply is committed to the repository unedited, "
        "with its SHA-256.", "",
        "## Instructions to the reviewer", "", INSTRUCTIONS, "",
    ]
    if rnd == 2:
        sys.path.insert(0, str(ROOT / "scripts"))
        import d_d_2  # noqa: PLC0415

        lines += ["## Changes since v0.1", "",
                  "Every round-1 finding the author accepted (`DECISIONS.md` D-D-2, numbering as there), and where it was "
                  "applied in this draft or in the registered files. The rejected findings and their reasons are in D-D-2.",
                  "", d_d_2.changes_table(), ""]
    for title, rel in PARTS:
        data = (ROOT / rel).read_bytes()
        lines += [f"## {title.format(draft=draft)} ({rel})", "",
                  f"Source: `{rel}`, SHA-256 `{hashlib.sha256(data).hexdigest()}`. Copied verbatim between the rules.",
                  "", "---", "", data.decode("utf-8").rstrip("\n"), "", "---", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="review_packet")
    parser.add_argument("--date", required=True)
    parser.add_argument("--round", type=int, default=1, choices=sorted(DRAFTS))
    args = parser.parse_args(argv)
    out = ROOT / "review-secondary" / f"D{args.round}-review-packet.md"
    out.write_text(render(args.date, args.round), encoding="utf-8")
    print(f"review packet: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
