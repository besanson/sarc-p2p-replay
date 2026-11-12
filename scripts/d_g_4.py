"""DECISIONS.md D-G-4, release 1.1.1, from pyproject.toml, CITATION.cff and the slots. Nothing is typed.

Usage: python scripts/d_g_4.py --date YYYY-MM-DD
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
HEADING = "## D-G-4 "


def _j(rel: str) -> dict:
    return json.loads((ROOT / "results" / rel).read_text(encoding="utf-8"))


def render(date: str) -> str:
    import yaml  # noqa: PLC0415

    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    cff = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    cost = _j("e6/cost.json")
    corr = cost["arms"]["e4-exploratory-corrected"]
    spent = sum(v["spend_usd"] for v in corr.values())
    return f"""{HEADING}Release {version} ({date})

1.1.0 was not tagged and is superseded by this release.

**What changed** since 1.1.0 (decision D-G-3): the exploratory timeline view omits the decision's own clearing; the
audit of the original views (`results/exploratory/timeline-leakage.json`); the corrected views
(`results/e4-exploratory/views-timeline-corrected.jsonl`); the exploratory arm re-run on them, both families
({', '.join(f'{k} {v["status"]}' for k, v in corr.items())}, USD {spent:.4f}; total since E4 USD
{cost['spend_usd_total']:.4f} of the USD {cost['cap_usd']:.0f} cap), analysed in
`results/e4-exploratory/h4-exploratory-corrected.json` and `arms-exploratory-corrected.json` (double run byte-identical,
`results/e4-exploratory/double-run-corrected.json`); the E4 sample under the strict reading of D4
(`results/exploratory/e4-strict-d4.json`); the exploratory double run over X1 to X6
(`results/exploratory/double-run.json`); `results/e6/cost.json` with the corrected arm's spend.

Paper: 5.4 reports both runs, the original with the error stated in one sentence and the corrected run as the
exploratory result; Figure 4's exploratory panel plots the corrected run; Appendix F's synthetic timeline is regenerated
from the corrected code; Appendix G adds the audit, the corrected tables and the strict-D4 re-tabulation; Section 7 and
the Acknowledgements gain one sentence each; Appendix C names the release. The TeX build strips the markdown caption's own
"Figure n:" (the figure number printed twice). CLAIMS.md is unchanged.

`pyproject.toml` and `CITATION.cff` {version}, date-released {cff['date-released']}; README status; REPRODUCE.md
`git checkout v{version}`. Unchanged: every registered file except the logged DEVIATIONS entry; every committed slot of the
registered experiments; the original exploratory run's views, responses and slots; every registered estimate and the
Holm family. The fresh-clone check (D-F-3) runs on this commit before it is pushed.

The author tags v{version} on <sha>, the commit that adds this entry ("paper 7: paper v{version}, caption fix, D-G-4"); a
commit cannot name its own hash, so the builder's report gives it.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_g_4")
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
