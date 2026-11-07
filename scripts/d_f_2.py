"""DECISIONS.md D-F-2, release 1.0.1, from CITATION.cff, pyproject.toml, out/reproduce/report.md (run
`make reproduce` first) and git (which slot files changed since v1.0.0). Nothing is typed.

Usage: python scripts/d_f_2.py --date YYYY-MM-DD
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
HEADING = "## D-F-2 "
# Records the 1.0.1 work adds or refreshes under results/: none is an experiment slot.
RECORDS = ("results/reproduction/", "results/package-smoke.json", "results/ci-runs.json")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def render(date: str) -> str:
    import yaml  # noqa: PLC0415

    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    cff = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    changed = [f for f in git("diff", "--name-only", "v1.0.0", "--", "results/").splitlines() if f]
    slots = [f for f in changed if not f.startswith(RECORDS)]
    numbers = git("diff", "--stat", "v1.0.0", "--", "paper/paper.md")
    verdict = re.search(r"\*\*(.+?)\*\*", (ROOT / "out" / "reproduce" / "report.md").read_text(encoding="utf-8")).group(1)
    return f"""{HEADING}Release {version} ({date})

**What changed** (tooling after external attempt 1, D-F-1):

- Timestamps: the git dates of the timeline slot are parsed and written as ISO 8601 with "+00:00", so
  "Z" (Apple Git) and "+00:00" give the same string; the committed `results/e4/timeline.json` is
  unchanged, and a test feeds both forms.
- `scripts/reproduce.py` and gate G4: beside the byte comparison, JSON and JSON lines are compared
  within tolerance (`scripts/tolerance.py`; rule recorded in `results/reproduction/comparison-rule.json`);
  text files by bytes; the figures by the numbers they plot (`paper/figures/figure-data.json`, new),
  their SVG and PDF bytes listed as machine-dependent. The verdict distinguishes byte-identical from
  within tolerance. The optional PDF step cannot stop the run; the report is always written.
- `scripts/build_tex.py`: pdflatex is preferred (the committed PDF is a pdflatex build); with another
  engine the overfull count is skipped and the engine recorded; G9 waits, never fails, when the PDF
  cannot be checked.
- `make gates` writes its report to `out/gates/` only; `make gates-record` also writes
  `results/gates-report.json`, so a reproducer's checkout stays clean.
- `scripts/fetch_data.py`: size before hash; a size or hash mismatch is deleted and fetched once more,
  resuming where the server allows; every attempt logged.
- Wording (D-F-1): Appendix C, C13's status (Appendix B) and FINAL-AUDIT item 11 state the result of
  attempt 1 and the claim's new form; README status.

**What did not change.** No experiment slot under `results/` changed since v1.0.0 (git: changed there
only {', '.join(f'`{f}`' for f in changed) or 'nothing'}; experiment slots among them: {len(slots)}). No number in the
paper changed: the paper differs from v1.0.0 only in Appendix C's wording and C13's status
({numbers.splitlines()[-1].strip() if numbers else 'no change'}). On this tree `make reproduce` gives: {verdict}

**Version and DOI.** `pyproject.toml` and `CITATION.cff` {version}, date-released
{cff['date-released']}; `doi` {cff['doi']}, the concept DOI of the GitHub-linked Zenodo record, which
resolves to its latest version. Each GitHub release also gets its own version DOI from Zenodo; the
stamp commit can add v{version}'s.

The author tags v{version} on the commit that adds this entry ("paper 7: D-F-2, release {version}"); a
commit cannot name its own hash, so the builder's report gives it.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_f_2")
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
