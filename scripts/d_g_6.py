"""DECISIONS.md D-G-6, release 1.1.2, from pyproject.toml and CITATION.cff. Nothing is typed.

Usage: python scripts/d_g_6.py --date YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-G-6 "


def render(date: str) -> str:
    import yaml  # noqa: PLC0415

    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    cff = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    return f"""{HEADING}Release {version} ({date})

1.1.0 and 1.1.1 were not tagged and are superseded by this release.

**What changed** since 1.1.1: the three presentation items of D-G-5 (the hold-rates figure's exploratory panel title and
the tight figure export; the strict-D4 sentences in 5.4 and Section 7; the introduction sentence); Appendix C names the
release. No model call; no registered file, committed slot or registered estimate changed; CLAIMS.md unchanged.

`pyproject.toml` and `CITATION.cff` {version}, date-released {cff['date-released']}; README status; REPRODUCE.md
`git checkout v{version}`. The fresh-clone check (D-F-3) runs on this commit before it is pushed.

The author tags v{version} on <sha>, the commit that adds this entry ("paper 7: D-G-6, release {version}"); a commit cannot
name its own hash, so the builder's report gives it.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_g_6")
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
