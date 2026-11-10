"""DECISIONS.md D-F-3, external reproduction attempt 2 (issue #1, v1.0.1), from results/reproduction/attempt-2.json.
Nothing is typed.

Usage: python scripts/d_f_3.py --date YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-F-3 "


def render(date: str) -> str:
    a = json.loads((ROOT / "results" / "reproduction" / "attempt-2.json").read_text(encoding="utf-8"))
    e = a["environment"]
    tb = " -> ".join(f"`{f['file']}` {f['function']}" for f in a["traceback"])
    return f"""{HEADING}External reproduction attempt 2 (issue #{a['issue']}, {a['tag']}) ({date})

**The record, as found** (`{a['body']}`, the comment unedited, SHA-256 `{a['body_sha256']}`;
`results/reproduction/attempt-{a['attempt']}.json`, parsed by `scripts/reproduction_attempts.py --comment`).
Reproducer: {a['reproducer']} (comment by `{a['commented_by']}`, {a['created_at']}). In the same clone as
attempt 1, data kept: `{a['command']}`; the tag resolved to `{a['commit'][:7]}`. {e['operating_system']},
{e['architecture']}; Python {e['python']}; run date {a['run_date']}. Every regeneration step ran
({', '.join(a['steps_completed'])}); the run stopped in the step "{a['stopped_in_step']}" on
`{a['exception']}` ({tb}) for `{a['missing_path']}`; exit code {a['exit_code']}. Report written:
{'yes' if a['report_written'] else 'no'}; comparison reached: {'yes' if a['comparison_reached'] else 'no'}.

**Why.** `scripts/reproduce.py` regenerates the experiment results into `out/reproduce/root/results/`
and fills the paper from there. Before filling, it copied the machine-dependent records (`MACHINE`)
into that tree, but not the other committed files it does not regenerate (`RECORDS`). In 1.0.1 the
paper's Appendix C gained two sources that are records, `results/reproduction/attempt-1.json` and
`results/reproduction/comparison-rule.json`; the fill read them from the regenerated tree, where they
were absent.

**Two process gaps.** (1) The records were not copied: the copy covered one class of non-regenerated
files, not all of them. (2) The end-to-end check was not repeated after the template changed: release
1.0.1's `make reproduce` ran in its step 2, before step 3 added those sources, and was not run again on
the tree that was tagged.

**The fix** (1.0.2). Before filling, `regenerate_paper` copies from the commit every file under
`results/` that the regeneration did not produce, each with its reason (machine-dependent record,
verification record, record of an external attempt); the report lists them under "Copied from the
commit, not regenerated", and a copied file is never counted as reproduced. Two tests fail on the 1.0.1
code and pass on 1.0.2: `tests/test_reproduce_fill.py::test_every_paper_source_is_regenerated_or_copied`
(every source the paper, the README's blocks and the figures read is either regenerated or copied) and
`tests/test_reproduce_fill.py::test_paper_fills_from_regenerated_files_plus_copied_records` (the fill
succeeds on a tree of the regenerated files plus the copied ones, and gives the committed paper).

**New rule.** No release is pushed before the fresh-clone check passes on the tree pushed (the only
later change allowed is the decision entry that records the check, in `DECISIONS.md`): a clone
of the local checkout at HEAD, the three data files linked in, then REPRODUCE.md's commands in order
(`make bootstrap`, `make test`, `make gates`, `make reproduce`); `make reproduce` must write its report
with the verdict REPRODUCED, and `make gates` must leave the clone's tracked files unchanged
(`make fresh-clone-check`, D-F-4; FINAL-AUDIT item 9).
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_f_3")
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
