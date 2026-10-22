"""Write DECISIONS.md D-C-1 from the slot files, so that no figure in it is hand-entered.

Reads results/e1/exclusions.json, results/e2/hypotheses.json,
results/reproducibility.json and results/e6/timing-e1.json, renders the entry
and replaces any earlier D-C-1 section of DECISIONS.md (or appends one).

Usage: python scripts/d_c_1.py --date YYYY-MM-DD --base SHA
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-C-1 "


def _load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def _n(x: int) -> str:
    return f"{x:,}"


def _s(seconds: float) -> str:
    m, s = divmod(round(seconds), 60)
    return f"{m} min {s:02d} s" if m else f"{s} s"


def exclusion_table(ex: dict) -> str:
    rows = ["| step | status | lines |", "|---|---|---|", f"| lines in the log | | {_n(ex['lines_in_log'])} |"]
    for r in ex["exclusions_in_registered_order"]:
        rows.append(f"| {r['registered_step']} | `{r['status']}` | {_n(r['lines'])} |")
    rows += [
        f"| framed | `framed` | {_n(ex['framed_lines'])} |",
        f"| E0 lines removed (section 2) | | {_n(ex['e0_lines_removed'])} |",
        f"| framed lines after E0 removal | | {_n(ex['framed_lines_after_e0_removal'])} |",
        f"| analysed clearings | | {_n(ex['analysed_clearings'])} |",
        f"| events after T_end ({ex['t_end']}) excluded | | {_n(ex['events_after_t_end_excluded'])} |",
    ]
    return "\n".join(rows)


def render(date: str, base: str) -> str:
    ex = _load("e1/exclusions.json")
    hyp = _load("e2/hypotheses.json")
    rep = _load("reproducibility.json")
    timing = _load("e6/timing-e1.json")
    coverage = _load("e1/coverage-check.json")
    hold = _load("e3/human-hold.json")
    h3 = hyp["estimates"]["H3"]["W60"]
    unfired = [f"{r['predicate']} ({r['defect_class']})" for r in coverage["rows"] if not r["fired"]]
    rates = hold["by_gate_status_at_t_star"]
    a, b = rep["runs"]["A"]["seconds"], rep["runs"]["B"]["seconds"]
    differing = [f["file"] for f in rep["files"] if not f["identical"]]
    diff_line = (f"all {_n(rep['files_compared'])} files byte-identical between run A and run B"
                 if rep["all_identical"] else f"files that differ: {', '.join(differing)}")
    runs = ", ".join(_s(r["replay_seconds"]) for r in timing["runs"])
    return f"""{HEADING}E1 to E3 run ({date})

**What ran.** E1 (`experiments/e1.py`), E2 (`experiments/e2.py`) and E3
(`experiments/e3.py`) on `data/BPI_Challenge_2019.xes` (SHA-256 as registered,
recorded in `results/e1/exclusions.json`), on base commit `{base}` (tag
`prereg-p7-v1.1`) with the runners committed in this session; `src/` is
unchanged since the tag, so the mutation gate was not re-run. No model call.
Shared analysis code is `experiments/common.py`; the SHA-256 of every runner
and engine source file at run time is in `results/reproducibility.json`.

**Run times.** Run A (written to `results/`): E1 {_s(a['e1'])}, E2 {_s(a['e2'])},
E3 {_s(a['e3'])}. Run B (`out/repro/run-b/`): E1 {_s(b['e1'])}, E2 {_s(b['e2'])},
E3 {_s(b['e3'])}. E6 timing (`results/e6/timing-e1.json`): replay of the full
E1 over three further runs {runs}; median {_s(timing['median_replay_seconds'])}.

**Double run.** `experiments/repro.py` ran E1, E2 and E3 twice from the log and
compared every file they write: {diff_line}. The three E6 runs of E1 wrote
byte-identical files: {"yes" if timing["outputs_byte_identical_across_runs"] else "no"}.

**Holm deferred.** The Holm adjustment over the registered five-test family
(H1, H2, H3, H4-Jev, H4-Haiku; alpha {hyp['holm']['alpha']}) is applied once
H4-Jev and H4-Haiku exist, after E4. `results/e2/hypotheses.json` holds raw
one-sided p-values for H1 to H3 only, and its `holm` field says so.

**For the author (reported, nothing changed).** H3: the D5 defect group has
{_n(h3["defect_group"]["clearings"])} analysed clearings and the D5-unknown
exclusion {_n(hyp["estimates"]["H3"]["excluded"]["clearings"])}, so the registered H3
statistic is {"not computable (" + h3["not_computable"] + ")" if h3.get("not_computable") else "computed"};
`results/e2/hypotheses.json` says so and carries no p-value for it. Across the
whole log no `Clear Invoice` actor equals an actor of the line's earliest
creation, and the clearings recorded with actor `NONE` lie on lines outside the
frame or after the outcome horizon. Coverage check: every detected row fired:
{"yes" if coverage["every_detected_row_fired"] else "no; not fired: " + "; ".join(unfired)}.
Human hold by gate status at t*: {_n(rates["held_unknown"]["classified_lines"])} classified
lines are held_unknown at t* (no failed predicate, at least one unknown; at a
t* that is not a clearing D5 is unknown, having no clearing actor), and their
human hold rate is {rates["held_unknown"]["human_hold_rate"]}. Under this reading a line
with no clearing within W can be defective or held_unknown but never clean, so
the defective and clean rates are read with that in mind. How E4 treats such lines
is the author's decision before E4.

**Pipeline readings (no registered item changed).**

- numpy is added as a pinned dependency (`numpy==2.3.4`, extras `dev` and
  `analysis`): section 5 registers the `numpy.random.Generator` (PCG64).
- Bootstrap clusters are the purchase documents of the analysed clearings,
  sorted by the id the evidence set carries (the first 16 hex digits of its
  SHA-256, section 3.9), so every interval can be recomputed from the committed
  evidence set. Each bootstrap starts one generator seeded 20261201 and draws
  B resamples in order; every statistic of a runner uses the same resamples.
  Counts and values (integer cents; the log's values carry at most two
  decimals, checked) are summed exactly. Percentile interval: 2.5 and 97.5
  (numpy linear). The H1 to H3 SE is the standard deviation (ddof 1) of the
  bootstrap differences.
- Shares per defect class use every analysed clearing as denominator; the
  number of clearings to which each class applies is reported beside them
  (D1 and D2 classes apply to 3-way categories). "D1 class" is the absent
  receipt and "D2 class" the stale receipt of section 3.3.
- Strata: quartiles are numpy linear quantiles over framed lines (E0 lines
  removed); vendor activity is the number of framed lines of the line's
  vendor, with quartiles over framed lines; a value at a cutpoint falls in the
  lower quartile.
- Category cross-check (3.1): a line disagrees when its `Item Category` string
  is not the record's string for the flag-derived category (`3-way match,
  invoice after GR`, `3-way match, invoice before GR`, `2-way match`,
  `Consignment`); counted over all lines and over framed lines.
- H2 excludes clearings with D4 unknown, and counts them, as H3 does for D5.
- Human hold rate on defective and clean lines (E3): a line's status is the
  gate verdict at the E4 decision point t* of section 7. At a t* that is not a
  clearing (first invoice receipt + W) there is no clearing actor, so D5 is
  unknown and such a line cannot be clean. This reading also fixes which lines
  E4 can sample as clean; it is flagged to the author before E4.
- The evidence-set sample (3.9) is `random.Random(20261201)` over the evidence
  set sorted by hashed line id and t_c.

**Exclusion counts** (generated from `results/e1/exclusions.json`):

{exclusion_table(ex)}
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_c_1")
    parser.add_argument("--date", required=True)
    parser.add_argument("--base", required=True)
    args = parser.parse_args(argv)
    entry = render(args.date, args.base)
    text = DECISIONS.read_text(encoding="utf-8")
    if HEADING in text:
        head, rest = text.split(HEADING, 1)
        tail = re.search(r"\n## ", rest)
        text = head + entry + (rest[tail.start() + 1:] if tail else "")
    else:
        text = text.rstrip("\n") + "\n\n" + entry
    DECISIONS.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
