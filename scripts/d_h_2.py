"""DECISIONS.md D-H-2, release 1.1.3, from pyproject.toml, CITATION.cff and results/release/preprint.json. Nothing is typed.

Usage: python scripts/d_h_2.py --date YYYY-MM-DD
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
HEADING = "## D-H-2 "


def render(date: str) -> str:
    import yaml  # noqa: PLC0415

    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    cff = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    pre = json.loads((ROOT / "results" / "release" / "preprint.json").read_text(encoding="utf-8"))["preprint"]
    return f"""{HEADING}Release {version} ({date})

**What changed** since 1.1.2 (D-H-1): the preprint record (`results/release/`), the SSRN DOI {pre['doi']} and the
Zenodo DOI {cff['doi']} as identifiers in `CITATION.cff` with a preferred-citation pointing at the preprint, the README
status and Cite block, the paper's front-matter line, and Appendix C naming the release. `pyproject.toml` and
`CITATION.cff` {version}, date-released {cff['date-released']}; REPRODUCE.md `git checkout v{version}`. No model call; no
registered file, committed slot or paper number changed. The fresh-clone check (D-F-3) runs on this commit before it is
pushed.

**What remains.** Journal submission, in Phase H session 2, to a venue of the author's choice; an arXiv appeal becomes
possible after a journal acceptance.

The author tags v{version} on <sha>, the commit that adds this entry ("paper 7: D-H-2, release {version}"); a commit cannot
name its own hash, so the builder's report gives it.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_h_2")
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
