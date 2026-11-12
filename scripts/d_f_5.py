"""DECISIONS.md D-F-5, external reproduction completed (issue #1, attempt 3), from
results/reproduction/attempt-3.json and results/reproduction/comparison-rule.json. Nothing is typed.

Usage: python scripts/d_f_5.py --date YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-F-5 "


def render(date: str) -> str:
    a = json.loads((ROOT / "results" / "reproduction" / "attempt-3.json").read_text(encoding="utf-8"))
    rule = json.loads((ROOT / "results" / "reproduction" / "comparison-rule.json").read_text(encoding="utf-8"))
    e, r = a["environment"], a["run_utc"]
    tagged = subprocess.run(["git", "-C", str(ROOT), "rev-parse", f"{a['tag']}^{{commit}}"], capture_output=True,
                            text=True).stdout.strip()
    tol = "\n".join(f"| `{f['file']}` | {f['max_abs_difference']:g} |" for f in a["within_tolerance_files"])
    boot = [f for f in a["within_tolerance_files"] if f["file"].startswith("results/")]
    return f"""{HEADING}External reproduction completed (issue #{a['issue']}, attempt {a['attempt']}) ({date})

**The record, as found** (`{a['body']}`, the comment unedited, SHA-256 `{a['body_sha256']}`;
`results/reproduction/attempt-{a['attempt']}.json`, parsed by `scripts/reproduction_attempts.py --comment`).
Reproducer: {a['reproducer']} (comment by `{a['commented_by']}`, {a['created_at']}; the comment names no
person, so the name is taken from attempt 1's record, posted by the same account). Tag `{a['tag']}`, commit
`{a['commit'][:7]}`; {e['operating_system']} {e['architecture']} (`{e['platform']}`), Python {e['python']}, pandoc
{e['pandoc']}. `{a['command']}` ran on {r['date']} from {r['start']} to {r['end']} UTC, in the clone of attempt 1
with its data and environment kept and its tracked files clean before and after; only that command was
run (tests and gates were not re-run there). Exit code {a['exit_code']}; the report was written and is pasted
unchanged in the comment. Verdict line:

> {a['verdict']}

{a['files_compared']} files compared: {a['files_equal']} equal, {a['byte_identical']} byte-identical, {a['within_tolerance']} within
tolerance (|a - b| <= {rule['relative_tolerance']:g} x max(1, |a|, |b|)), none unequal; {a['copied_records']} committed records
copied, not regenerated. The within-tolerance files and their largest absolute differences:

| file | maximum absolute difference |
|---|---:|
{tol}

For information, as reported: {a['pdf']}

**The tag.** The release tag of 1.0.2 is spelled `{a['tag']}`, with a capital V: the author's tag. Git tags are
case-sensitive; REPRODUCE.md and D-F-4 say `v1.0.2`. `{a['tag']}` refers to commit `{tagged[:7]}`, the commit D-F-4
names; no second tag was added.

**Conclusion.** Every experiment slot regenerated on another machine and architecture ({e['architecture']} against the
builder's {rule['builder']['architecture']}): byte-identical except {len(boot)} bootstrap outputs
({', '.join(f'`{f["file"]}`' for f in boot)}), equal within {rule['relative_tolerance']:g}; `paper/filled-template.json`,
which records their raw values beside the paper text, is equal within the same tolerance; the paper text,
its TeX and the README are byte-identical. FINAL-AUDIT item 11 is closed with
`results/reproduction/attempt-{a['attempt']}.json` and {a['url'].split('#')[0]}; C13 is supported.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_f_5")
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
