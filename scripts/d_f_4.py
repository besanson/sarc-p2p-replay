"""DECISIONS.md D-F-4, release 1.0.2, from out/fresh-clone-check/summary.json and report.md (run
`make fresh-clone-check` first), CITATION.cff and pyproject.toml. Nothing is typed.

Usage: python scripts/d_f_4.py --date YYYY-MM-DD
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
HEADING = "## D-F-4 "
CHECK = ROOT / "out" / "fresh-clone-check"


def render(date: str) -> str:
    import yaml  # noqa: PLC0415

    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    cff = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    s = json.loads((CHECK / "summary.json").read_text(encoding="utf-8"))
    if not s["passed"]:
        raise SystemExit("the fresh-clone check did not pass: no D-F-4")
    rows = []
    for c in s["commands"]:
        extra = ""
        if "tests_passed" in c:
            extra = f"; {c['tests_passed']} passed, {c['tests_skipped']} skipped"
        if "gates_summary" in c:
            extra = f"; {c['gates_summary']}; tracked files unchanged: {'yes' if c['tracked_files_unchanged'] else 'no'}"
        rows.append(f"| `{c['command']}` | {c['exit']} | {c['seconds']:.0f} s{extra} |")
    report = (CHECK / "report.md").read_text(encoding="utf-8")
    pdf = re.search(r"For information: (.+)", report).group(1)
    return f"""{HEADING}Release {version} ({date})

**What changed** since 1.0.1 (D-F-3): `scripts/reproduce.py` copies every committed file it does not
regenerate into the regenerated tree before filling the paper, lists them in the report and never
counts them as reproduced; two tests; attempt 2 recorded; Appendix C, C13 (Appendix B), FINAL-AUDIT
item 11 and the README status; the fresh-clone check (`make fresh-clone-check`,
`scripts/fresh_clone_check.py`), now part of FINAL-AUDIT item 9's evidence. No experiment slot and no
number in the paper changed. `pyproject.toml` and `CITATION.cff` {version}, date-released
{cff['date-released']}, `doi` {cff['doi']} (the concept DOI); REPRODUCE.md re-runs with
`git fetch --tags && git checkout v{version} && make reproduce`.

**The fresh-clone check**, before the push: a clone of the local checkout (file:// URL) at
`{s['commit']}`, the three data files linked into its `data/` (bootstrap verified them by size and
SHA-256 and downloaded nothing), then REPRODUCE.md's commands in order:

| command | exit | time and result |
|---|---:|---|
{chr(10).join(rows)}

`make reproduce` wrote `out/reproduce/report.md`: {s['rows']} files compared, {s['rows_not_equal']} not equal;
{s['copied_records']} committed records copied into the regenerated tree, not regenerated. Verdict line:

> {s['verdict']}

For information: {pdf}

The check ran on `{s['commit'][:7]}`. The commit that adds this entry changes `DECISIONS.md` (this
entry) and adds `scripts/d_f_4.py`, the script that writes it from the check's output; no make target,
test or gate runs that script, so the checked tree and the pushed tree run the same code.

The author tags v{version} on the commit that adds this entry ("paper 7: D-F-4, release {version} after
fresh-clone check"); a commit cannot name its own hash, so the builder's report gives it.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_f_4")
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
