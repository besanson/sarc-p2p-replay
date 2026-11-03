"""DECISIONS.md D-E-2, release 1.0.0, from the records: CITATION.cff, pyproject.toml,
results/mutation-release.json, results/ci-runs.json, out/reproduce/report.md (run `make reproduce`
first), scripts/reproduce.py (the excluded files) and FINAL-AUDIT.md. Nothing is typed.

Usage: python scripts/d_e_2.py --date YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-E-2 "


def render(date: str) -> str:
    import reproduce  # noqa: PLC0415
    import yaml  # noqa: PLC0415

    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    cff = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    m = json.loads((ROOT / "results" / "mutation-release.json").read_text(encoding="utf-8"))
    ci = json.loads((ROOT / "results" / "ci-runs.json").read_text(encoding="utf-8"))
    runs = "\n".join(f"- `{c['commit'][:7]}`: " + "; ".join(f"[{r['run_id']}]({r['url']}) {r['conclusion']}" for r in c["runs"])
                     for c in ci["commits"])
    rep = (ROOT / "out" / "reproduce" / "report.md").read_text(encoding="utf-8")
    verdict = re.search(r"\*\*(.+?)\*\*", rep).group(1)
    ran_on = re.search(r"Commit `([0-9a-f]{7})", rep).group(1)
    pdf = re.search(r"For information: (.+)", rep).group(1)
    audit = (ROOT / "FINAL-AUDIT.md").read_text(encoding="utf-8")
    summary = re.search(r"## Summary\n\n(.+)", audit).group(1)
    machine = "\n".join(f"  - `{k}`: {v}" for k, v in reproduce.MACHINE.items())
    records = "\n".join(f"  - `{k}`: {v}" for k, v in reproduce.RECORDS.items())
    return f"""{HEADING}Release {version} ({date})

**Version.** `pyproject.toml` {version}; `CITATION.cff` version {cff['version']}, date-released
{cff['date-released']}, the repository URL and the three event logs as data references, no `doi`
field. The DOI is minted by Zenodo's GitHub integration when the author publishes the GitHub
release of the tag; it is stamped afterwards, in the stamp commit. The README's status line and its
"Cite" block (generated from `CITATION.cff` by `scripts/fill_paper.py`, checked by the typed-numeral
lint as the headline block is) follow.

**Mutation** (FINAL-AUDIT item 4). `make mutate-release` on the release tree: kill score
{m['kill_score']:.4f} ({m['killed']} of {m['killed'] + m['survived']} killed, {m['no_tests']} without a covering test),
threshold {m['threshold']}: {'pass' if m['passes'] else 'FAIL'}. Recorded with the `src/` tree id
`{m['src_tree'][:12]}` in `results/mutation-release.json` (new); `results/mutation.json` stays as the
Phase B/C record. G3 now checks the release record against the current `src/` tree.

**Reproduction.** `REPRODUCE.md` (clone at the tag, `make bootstrap`, `make test`, `make gates`,
`make reproduce`) and `scripts/reproduce.py`, which regenerates every deterministic result into
`out/reproduce/` and compares SHA-256 with the committed files. Run at `{ran_on}` (the commits after it
change no result, paper or figure): {verdict}
For information: {pdf}

Excluded by name as machine-dependent:

{machine}

Not regenerated, verification records of earlier runs that a reproduction replaces:

{records}

**CI.** The run on the release commit cannot be recorded inside that commit; it is recorded in the
stamp commit. Recorded now (`results/ci-runs.json`, `scripts/ci_runs.py`):

{runs}

**FINAL-AUDIT.** Item 4 closed with `results/mutation-release.json`. {summary}

The author tags v{version} on the commit that adds this entry ("paper 7: D-E-2, release {version}"); a
commit cannot name its own hash, so the builder's report gives it.

**The stamp commit** (after the GitHub release and the arXiv submission) will carry: the Zenodo DOI
(`CITATION.cff`, the README's Cite block and status line), the arXiv id, the CI run of the release
commit (`results/ci-runs.json`), the reproduction issue once an external reproducer opens it, and
then C13's status, FINAL-AUDIT item 11 and Appendix C's sentence on external reproduction.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_e_2")
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
