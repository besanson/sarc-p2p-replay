"""DECISIONS.md D-D-5, Phase D closed: the three review rounds, the slot record, the deviations, the
lints' and gates' state, and what Phases E and F need.

Counts come from the adjudication scripts (scripts/d_d_2.py to d_d_4.py), the slot record from git,
the deviations from prereg/DEVIATIONS.md, and the gate state from out/gates/report.json (run
`make gates` first). Nothing is typed.

Usage: python scripts/d_d_5.py --date YYYY-MM-DD
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
HEADING = "## D-D-5 "
PHASE_C_CLOSED = "14842cc"  # the commit of D-C-5, Phase C closed
# Records of the paper, not experiment slots: the index and the filled template (moved to paper/ in D-D-3).
NOT_SLOTS = {"results/README.md", "results/filled-template.json"}

sys.path.insert(0, str(ROOT / "scripts"))


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def rounds() -> list[dict]:
    import d_d_2  # noqa: PLC0415
    import d_d_3  # noqa: PLC0415
    import d_d_4  # noqa: PLC0415

    out = []
    for rnd, mod, draft_in, draft_out, dec in ((1, d_d_2, "v0.1", "v0.2", "D-D-2"), (2, d_d_3, "v0.2", "v0.3", "D-D-3"),
                                                (3, d_d_4, "v0.3", "v1.0 candidate", "D-D-4")):
        rs = mod.rows()
        acc = sum(r["d"].startswith("accepted") for r in rs)
        out.append({"round": rnd, "draft": draft_in, "produced": draft_out, "decision": dec, "raised": len(rs),
                    "accepted": acc, "rejected": len(rs) - acc})
    return out


def slot_record() -> tuple[list[str], list[tuple[str, str, str]]]:
    changed = _git("log", "--format=", "--name-only", "--diff-filter=MDRT", f"{PHASE_C_CLOSED}..HEAD", "--",
                   "results/").split()
    changed = sorted(set(changed) - NOT_SLOTS)
    added = []
    for block in _git("log", "--reverse", "--format=@%h %cI", "--name-only", "--diff-filter=A",
                      f"{PHASE_C_CLOSED}..HEAD", "--", "results/").split("@")[1:]:
        head, *files = [x for x in block.split("\n") if x]
        sha, when = head.split()
        added += [(f, sha, when[:10]) for f in files if f not in NOT_SLOTS]
    return changed, added


def deviations() -> list[str]:
    text = (ROOT / "prereg" / "DEVIATIONS.md").read_text(encoding="utf-8")
    under = text.split("## Under p7-v1.1", 1)[1]
    return re.findall(r"^### (.+)$", under, re.MULTILINE)


def render(date: str) -> str:
    rs = rounds()
    table = ["| round | draft reviewed | reviewers | findings | accepted | rejected | adjudication | draft produced |",
             "|---|---|---|---:|---:|---:|---|---|"]
    for r in rs:
        table.append(f"| {r['round']} | {r['draft']} | Arana (external); ChatGPT, Perplexity (machine, AI support) | "
                     f"{r['raised']} | {r['accepted']} | {r['rejected']} | {r['decision']} | {r['produced']} |")
    changed, added = slot_record()
    added_rows = "\n".join(f"| `{f}` | `{sha}` | {when} |" for f, sha, when in added)
    devs = deviations()
    report = json.loads((ROOT / "out" / "gates" / "report.json").read_text(encoding="utf-8"))
    gates = "\n".join(f"| {name} | {g['status']} | {'; '.join(g['waiting'])} |" for name, g in report["gates"].items())
    counts = {s: sum(g["status"] == s for g in report["gates"].values()) for s in ("pass", "waiting", "fail")}
    unchanged = ("No committed experiment slot under `results/` changed during Phase D" if not changed else
                 "Committed experiment slots changed during Phase D: " + ", ".join(f"`{c}`" for c in changed))
    return f"""{HEADING}Phase D closed ({date})

**Review rounds.** Findings are the rows of each adjudication table (round 3 includes one row the
author added, D-D-4 row 8).

{chr(10).join(table)}

**Slots.** {unchanged} (git, from `{PHASE_C_CLOSED}`, Phase C closed, to this commit). Under `results/`
only the index (`results/README.md`) changed, and the paper's filled template, which was written there
in Phase D, regenerated with each draft and moved to `paper/filled-template.json` in D-D-3. Slot files
added in Phase D, each with its first commit:

| file | first commit | date |
|---|---|---|
{added_rows}

**Deviations under p7-v1.1 ({len(devs)}).**

{chr(10).join(f"{i}. {d}" for i, d in enumerate(devs, 1))}

**Lints and gates.** The terminology, typed-numeral and proof-status lints pass on the v1.0 candidate.
`make gates` (`out/gates/report.json`): {counts['pass']} pass, {counts['waiting']} waiting, {counts['fail']} fail.

| gate | status | waiting on |
|---|---|---|
{gates}

**Phase E (release) needs:** CI run ids on Python 3.11 and 3.12 for the release commit (G1); a LaTeX
engine to build the PDF from `paper-tex/main.tex` (G9); the fresh-venv package smoke test (G8,
`make package-smoke-test`); FINAL-AUDIT items 1 to 10; a Zenodo DOI; an arXiv id; the release tag,
which the author sets.

**Phase F needs:** external reproduction from a clean clone (FINAL-AUDIT item 11, G4), which settles
C13's pending part ("external reproduction pending").
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_d_5")
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
