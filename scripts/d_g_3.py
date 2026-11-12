"""DECISIONS.md D-G-3, the exploratory timeline arm's views showed the clearing at t*: the audit, the correction, the
re-run on the corrected views and the strict-D4 re-tabulation of the E4 sample. Figures are read from the slots; the
parts whose slots do not exist yet say so.

Usage: python scripts/d_g_3.py --date YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-G-3 "


def _j(rel: str) -> dict | None:
    p = ROOT / "results" / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _r(cell: dict) -> str:
    return "n/a" if cell["hold_rate"] is None else f"{cell['hold_rate']:.4f} ({cell['held']:,}/{cell['lines']:,})"


def render(date: str) -> str:
    a = _j("exploratory/timeline-leakage.json")
    by = a["by_status_and_decision_point_kind"]
    hr = a["committed_exploratory_hold_rates"]
    split = "\n".join(
        f"  - {f}: defective {_r(c['views_with_the_clearing']['defective'])} with the clearing, "
        f"{_r(c['views_without_the_clearing']['defective'])} without; clean {_r(c['views_with_the_clearing']['clean'])} "
        f"with, {_r(c['views_without_the_clearing']['clean'])} without" for f, c in hr.items())
    erp = a["erp_view_check"]
    orig = _j("e4-exploratory/h4-exploratory.json")
    corr = _j("e4-exploratory/h4-exploratory-corrected.json")
    if corr is None:
        rerun = "Not yet run: the corrected arm is run after this entry is first committed (no call before it)."
    else:
        rows = []
        for name, c in corr["families"].items():
            o = orig["families"][name]
            rows.append(f"  - {name}: status {c['status']}; hold rate defective {c['hold_rate_defective']:.4f} "
                        f"(original {o['hold_rate_defective']:.4f}), clean {c['hold_rate_clean']:.4f} "
                        f"(original {o['hold_rate_clean']:.4f}), d = {c['d']:.4f} (original {o['d']:.4f})")
        rerun = ("The exploratory arm re-run on the corrected views, same 2,000 lines, both families, the same request "
                 "shapes and the same arm health rule; responses append-only in "
                 "`responses/e4-exploratory-corrected/<family>/responses.jsonl`, cap accounting in "
                 "`responses/e4-exploratory-corrected/manifest.json`; analysis in "
                 "`results/e4-exploratory/h4-exploratory-corrected.json` and `arms-exploratory-corrected.json`:\n"
                 + "\n".join(rows))
    x6 = _j("exploratory/e4-strict-d4.json")
    if x6 is None:
        strict = "Not yet written."
    else:
        cells = ", ".join(f"{k}: {v:,}" for k, v in x6["registered_x_strict"].items())
        arms = "\n".join(f"  - {n}: strict defective {_r(v['strict_groups']['defective'])}, strict clean "
                         f"{_r(v['strict_groups']['clean'])}" for n, v in x6["arms"].items())
        strict = (f"`results/exploratory/e4-strict-d4.json`: the 2,000 sample lines reclassified at t* under the strict "
                  f"reading of D4 (X1 reading (b)); registered -> strict: {cells}. The four arms' hold rates on the "
                  f"registered ERP view:\n{arms}\n  Statement: {x6['statement']}.")
    return f"""{HEADING}Exploratory timeline arm: the clearing event at t* was shown (pipeline defect) ({date})

**What happened.** The registration (prereg/p7-v1.1.md section 2) defines the evidence as recorded before t_c. The
exploratory timeline view (`experiments/e4_sample.py` `timeline_view`, 1.1.0) listed the events of `case.upto(t_star)`,
which includes events at t*; on a sample line whose decision point is its first clearing, the view therefore showed
that `Clear Invoice`, the decision being asked for. The registered ERP view is unaffected.

**Audit** (`results/exploratory/timeline-leakage.json`, no call). Of {a['sample_lines']:,} committed timeline views,
{a['views_with_the_clearing']:,} contain a `Clear Invoice` dated t* (every line whose t* is a clearing:
{a['lines_with_t_star_a_clearing']:,}); in {a['views_with_the_clearing_as_last_row']:,} a clearing is the last row, and in
{a['views_with_the_clearing_before_other_rows']:,} another event at t* follows the first clearing row
({a['views_with_more_than_one_clearing_row_at_t_star']:,} views carry two clearing records at t*). By status and
decision-point kind: defective {by['defective']['first clearing']['views_with_the_clearing']:,} of
{by['defective']['first clearing']['lines']:,} at a first clearing and {by['defective']['first invoice receipt + W']['views_with_the_clearing']:,}
of {by['defective']['first invoice receipt + W']['lines']:,} at receipt + W; clean {by['clean']['first clearing']['views_with_the_clearing']:,}
of {by['clean']['first clearing']['lines']:,} and {by['clean']['first invoice receipt + W']['views_with_the_clearing']:,} of
{by['clean']['first invoice receipt + W']['lines']:,}. The committed exploratory hold rates split by view (invalid replies
count as neither; not a stratified comparison):
{split}

ERP view: {erp['views_containing_a_clearing']:,} of {erp['views']:,} contain a clearing, and the
{erp['rerendered_without_the_clearing']['lines_rerendered']:,} lines whose t* is a clearing re-render byte-identical without
it ({erp['rerendered_without_the_clearing']['identical_to_committed']:,}); the registered arm is not re-run.

**Correction.** `timeline_view` now omits the clearing records at t* when t* is the line's first clearing; every other
event at t* stays (one line has a `Record Invoice Receipt` at t* after the clearing). Reading of the session's wording
("the decision's own Clear Invoice"): {a['views_with_more_than_one_clearing_row_at_t_star']:,} lines carry two `Clear Invoice`
records at the same t* with the same value, which nothing distinguishes; both are the clearing at the decision point,
and both are omitted, so that no corrected view shows a clearing ({a['corrected_views_check']['views_containing_a_clearing']:,}
of {a['corrected_views_check']['views']:,} do). The opening paragraph is the template's, unchanged: it still says "Using only the ERP record below" before a
timeline, as in the original run. Fixture tests: a line whose t* is its first clearing loses that row; a line whose t*
is receipt + W is unchanged. The corrected views are in `results/e4-exploratory/views-timeline-corrected.jsonl`; the
committed `results/e4/views-timeline.jsonl` stays and regenerates byte-identical (`with_own_clearing=True`). Appendix F's
synthetic example (X4) is regenerated from the corrected code. `prereg/DEVIATIONS.md` records the departure.

**Re-run.** {rerun}

**Strict-D4 re-tabulation.** {strict}

**Unchanged.** Every registered file except the logged DEVIATIONS entry; every committed slot, the original exploratory
run's views, responses and slots; the registered ERP arm, which is not re-run; every registered estimate and the Holm
family.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_g_3")
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
