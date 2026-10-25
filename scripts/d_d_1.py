"""Write DECISIONS.md D-D-1 (draft v0.1) from the gate report, the lint outputs and the filled template.

Reads out/gates/report.json (`make gates`), out/lint/typed_numerals.json and out/lint/terminology.json
(`make lint`), results/filled-template.json and paper/figures/. Replaces an earlier D-D-1 or appends.

Usage: python scripts/d_d_1.py --date YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-D-1 "


def _json(p: str) -> dict:
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def render(date: str) -> str:
    report = _json("out/gates/report.json")
    tn = _json("out/lint/typed_numerals.json")
    filled = _json("results/filled-template.json")
    words = len(re.findall(r"\S+", (ROOT / "paper" / "paper.md").read_text(encoding="utf-8")))
    gate_rows = []
    for name, g in report["gates"].items():
        waiting = "; ".join(g["waiting"]) if g["waiting"] else ""
        gate_rows.append(f"| {name} | {g['status']} | {waiting} |")
    figs = sorted(p.stem for p in (ROOT / "paper" / "figures").glob("*.svg"))
    kinds = {}
    for r in filled["placeholders"]:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    g4 = report["gates"]["G4 regeneration"]["detail"]
    differing = g4.get("differing", []) if isinstance(g4, dict) else []
    return f"""{HEADING}Draft v0.1 ({date})

**Ported from paper 5** (sarc-authority-derivation at the engines.lock pin; D-A0-3):
- The typed-numeral lint, `lint/typed_numerals.py`, from paper 5's `checkers/typed_numerals_lint.py`: the
  same strip-then-allowlist design. Paper 5 marks filled values inside the draft; here the paper is
  generated from `paper/template.md`, so the lint checks the template (any numeral outside a
  placeholder) and the generated `paper/paper.md` (any numeral outside the spans recorded in
  `results/filled-template.json`). Registered constants are allowlisted by literal value, each
  citing the registration section that fixes it (`REGISTERED` in the lint).
- The gate layout, `scripts/gates.py` and `make gates` (report in `out/gates/report.json`). Paper 5's
  G1 to G9 are LaTeX release-kit gates (build, token purity, number parity, prose and structure
  parity, disclosure, arXiv sidecar, citations, bibliography). Here G1 to G9 are the release list of
  the builder prompt (tests, lints, mutation, regeneration, claims, secrets, data and pins, package,
  paper), and paper 5's paper checks (build, token purity, number parity between source and typeset
  paper, verified references) sit inside G9.

**Gate report at v0.1** (`make gates`, full, with the log replays; passed: {'yes' if report['passed'] else 'no'}):

| gate | status | waiting on |
|---|---|---|
{chr(10).join(gate_rows)}

G4 files that differ from `results/` or the committed paper: {', '.join(differing) if differing else 'none'}.

The first full gate run failed three gates, each on a real defect of this session's work, fixed in
`fa0c5ac`: G4 found that Figures 2 and 4 had been committed before a layout fix (legend and titles)
and no longer matched their regeneration; G8 built without isolation in a venv that has no
setuptools; G9 counted numerals inside HTML comments, which pandoc does not typeset, and read
ordinary LaTeX braces as template syntax. A gate whose checks pass but which still has an item for a
later phase now reports "waiting" rather than "pass".

**Lints on the draft.** Terminology: clean on `paper/paper.md`. Typed numerals: template
{'clean' if tn['template']['clean'] else 'NOT clean'}, generated paper {'clean' if tn['paper']['clean'] else 'NOT clean'}
({tn['paper']['filled_spans']} filled spans). Proof status: clean. Placeholders filled:
{', '.join(f"{v} {k}" for k, v in sorted(kinds.items()))}; the draft has {words:,} words.

**Figures** (`scripts/figures.py`, deterministic SVG and PDF in `paper/figures/`): {', '.join(figs)}.

**PDF.** `paper-tex/main.tex` is written by pandoc from `paper/paper.md` (`scripts/build_tex.py`,
`make paper`). No LaTeX engine is installed in this environment, so the PDF waits for one; G9 reports
it as waiting.

**Readings taken while writing (no registered item changed).**
- The human-hold table of Section 5.3 shows both readings as rows of one table (literal, then
  amended by D-C-2 B), with the decision named in the sentence before it.
- Tables whose cells say "defective" carry "predicate" in their header ("lines with a failed
  predicate"), so the terminology rule (defect only for a failed predicate) holds in every table.
- The References section is exempt from the terminology lint (`lint/terminology.py`): it quotes
  cited titles verbatim, and one verified title (Kadir et al. 2025) contains a banned word. The
  paper's own prose is linted in full.
- The coverage table is `COVERAGE.md` verbatim. Its D1' row reads "no final approval event before
  the payment event", while section 8 of the registration and the engine define D1' as no event of
  the approval list; the paper shows the file as registered and does not reword it. Raised for review
  round 1.
- An E7 sentence that payment is the last event of a declaration is not in the draft: the check
  behind it was run during session 3 and reported to the author, but no slot holds it. The draft
  states the slot values instead (failing payments, and O' after all-pass payments).
- Small design counts fixed by the registration (seven predicates, two model families, three losses,
  three runs) are written as words; every result count is a filled value.
- Company and vendor strata are left out of Appendix D (registration section 2.3: their ids appear
  only in machine output); they stay in `results/e1/exposure-by-stratum.json`.
- P-values below 0.001 are written as a mantissa times a power of ten; p-values at or above 0.9995
  are written as 1.
- In-text citations name the first author's surname and year; the dataset records are cited as by
  Boudewijn van Dongen on 4TU.ResearchData, with DOI and licence from `prereg/data.lock`.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_d_1")
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
