"""DECISIONS.md D-F-6, release 1.0.3, from CITATION.cff, pyproject.toml and git. Nothing is typed.

Usage: python scripts/d_f_6.py --date YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-F-6 "


def render(date: str) -> str:
    import yaml  # noqa: PLC0415

    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    cff = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    changed = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only", "V1.0.2", "--", "results/"],
                             capture_output=True, text=True, check=True).stdout.split()
    return f"""{HEADING}Release {version} ({date})

**What changed** since 1.0.2: the external reproduction is recorded (D-F-5; `results/reproduction/attempt-3.json`);
C13 is supported, with that record and issue #1 as evidence (Appendix B); Appendix C states the
reproduction with its counts, filled from the attempt slot; the Acknowledgements thank the reproducer;
FINAL-AUDIT item 11 is closed (12 of 12 items met); gate G4 is met by a recorded attempt with the verdict
REPRODUCED; the README status. Under `results/` only records changed ({', '.join(f'`{f}`' for f in changed)}:
the new attempt and the smoke test of the {version} wheel); no experiment slot and no number in the paper
changed, except those filled from the new attempt slot.
`pyproject.toml` and `CITATION.cff` {version}, date-released {cff['date-released']}, `doi` {cff['doi']}
(the concept DOI); REPRODUCE.md: `git fetch --tags && git checkout v{version} && make reproduce`.

**The arXiv stamp**, after the submission, will add the arXiv id to the README's status line and to
`CITATION.cff` (and so to the README's generated Cite block), and change nothing else.

The author tags v{version} on the commit that adds this entry ("paper 7: D-F-6, release {version}"); a commit
cannot name its own hash, so the builder's report gives it.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_f_6")
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
