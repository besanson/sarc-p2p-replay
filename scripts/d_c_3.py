"""Write DECISIONS.md D-C-3 from the slot files, so that no figure in it is hand-entered.

Reads results/e4/{sample,sample-frame,arms,h4,double-run}.json, results/e6/cost.json and, when
present, results/e4-exploratory/. Replaces any earlier D-C-3 section or appends one.

Usage: python scripts/d_c_3.py --date YYYY-MM-DD
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
HEADING = "## D-C-3 "


def _load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def _n(x: int) -> str:
    return f"{x:,}"


def _p(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.3g}"


def _r(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.4f}"


def render(date: str) -> str:
    sample = _load("e4/sample.json")
    frame = _load("e4/sample-frame.json")
    arms = _load("e4/arms.json")["arms"]
    h4 = _load("e4/h4.json")
    dr = _load("e4/double-run.json")
    cost = _load("e6/cost.json")
    g = frame["groups"]
    st = frame["status_at_t_star_amended"]
    fam_rows = []
    for fam, label in (("jev", "H4-Jev"), ("haiku", "H4-Haiku")):
        a, h = arms[fam], h4["families"][label]
        per = "n/a" if a["cost_usd_per_decision"] is None else f"{a['cost_usd_per_decision']:.6f}"
        fam_rows.append(
            f"| {fam} | {a['status']} | {_n(a['lines_called'])} | {_n(a['invalid'])} | "
            f"{_r(h['hold_rate_defective'])} | {_r(h['hold_rate_clean'])} | {_r(h['d'])} | {_p(h['p_tost'])} | "
            f"{_r(a['kappa_with_gate'])} | {a['spend_usd']:.4f} | {per} |")
    holm_rows = [f"| {r['test']} | {_p(r['p_raw'])} | {r['rank']} | {r['multiplier']} | {_p(r['p_holm'])} | "
                 f"{'yes' if r['below_alpha'] else 'no'} |" for r in h4["holm"]["table"]]
    people = arms["people"]
    expl = (RESULTS / "e4-exploratory" / "arms-exploratory.json").exists()
    if expl:
        ea = json.loads((RESULTS / "e4-exploratory" / "arms-exploratory.json").read_text(encoding="utf-8"))["arms"]
        edr = json.loads((RESULTS / "e4-exploratory" / "double-run.json").read_text(encoding="utf-8"))
        expl_line = (f"Exploratory timeline arm ran (labelled exploratory, never in Holm): jev {ea['jev']['status']} "
                     f"({_n(ea['jev']['lines_called'])} lines, {_n(ea['jev']['invalid'])} invalid), haiku "
                     f"{ea['haiku']['status']} ({_n(ea['haiku']['lines_called'])} lines, "
                     f"{_n(ea['haiku']['invalid'])} invalid); results in `results/e4-exploratory/`; analysis "
                     f"double run byte-identical: {'yes' if edr['all_identical'] else 'no'}.")
    else:
        expl_line = "Exploratory timeline arm: not run."
    spend_lines = "; ".join(f"{arm}/{fam} USD {v['spend_usd']:.4f}" for arm, fams in cost["arms"].items()
                            for fam, v in fams.items())
    return f"""{HEADING}E4 run ({date})

**Sample (section 7, D-C-2 B; `results/e4/sample-frame.json`).** Framed lines after E0
removal {_n(frame['framed_lines_after_e0_removal'])}; status at t* under B: defective {_n(st['defective'])},
clean {_n(st['clean'])}, held-unknown {_n(st['held_unknown'])}, no invoice receipt {_n(st['no_invoice_receipt'])}.
Eligible: {_n(g['defective']['eligible_lines'])} defective, {_n(g['clean']['eligible_lines'])} clean. Drawn:
{_n(g['defective']['drawn'])} defective and {_n(g['clean']['drawn'])} clean (shortfall {_n(g['defective']['shortfall'])} and
{_n(g['clean']['shortfall'])}), from {_n(sample['purchase_documents'])} purchase documents. The draw was committed and
pushed before any call. Human arm from the log on these lines: unclassified {_n(people['unclassified'])}.

**Families.** Statuses, invalid replies (after the one re-request), H4 and spend
(`results/e4/arms.json`, `results/e4/h4.json`):

| family | status | lines | invalid | hold rate, defective | hold rate, clean | d | p_TOST | kappa with gate | spend USD | USD per decision |
|---|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(fam_rows)}

People (from the log): hold rate on defective lines {_r(people['hold_rate_defective'])}, on clean
lines {_r(people['hold_rate_clean'])}. Gate: holds every defective line and allows every clean one.

**Spend.** Total USD {cost['spend_usd_total']:.4f} against the cap of USD {cost['cap_usd']:.0f}
(`results/e6/cost.json`): {spend_lines}.

**Holm over the five-test family** (alpha {h4['holm']['alpha']}; H3 enters with p = 1, D-C-2 A;
written to `results/e2/hypotheses.json` under `holm` and to `results/e4/h4.json`):

| test | p raw | rank | multiplier | p Holm | below alpha |
|---|---|---|---|---|---|
{chr(10).join(holm_rows)}

**Double run.** The E4 analysis run twice from the committed responses: byte-identical:
{'yes' if dr['all_identical'] else 'no'} (`results/e4/double-run.json`). {expl_line}

**Pipeline readings (no registered item changed).**

- Jev request. System One answers typed questions about a state; it has no free-text reply,
  so the registered template's JSON reply cannot apply to it. The view's task sentences
  (up to the reply-format sentence) are the state's `context`, the ERP record its `record`,
  and the question is one `choice` with labels `clear` and `hold`; `decision` is the selected
  label and `p_hold` the probability of `hold`. A reply without a valid choice or a `hold`
  probability in [0, 1] is invalid; a 422 is re-requested once, as an invalid reply. Model
  alias `jev-latest`; MODEL_VERSION_CHANGED for Jev means a returned model other than the
  first one it returned.
- Registered sample order: the sample sorted by hashed line id (field `order`). Line ids
  are the hashed ids of the evidence set, as for every E1 to E3 output (D-C-1).
- Draw: eligible lines sorted by hashed id, shuffled once with `random.Random(20261201)`, then
  taken in that order while the status x stratum quota is open and the purchase document is
  unused. Stratum quartiles are those of E1 (framed lines).
- Lines whose t* (first invoice receipt + W) falls after T_end stay in the frame as section 7
  defines it; their view is built from events up to T_end. Count in the sample:
  {_n(sample['t_star_after_t_end'])}.
- Hold rates, kappa and released value use valid replies only; an invalid reply counts as
  neither hold nor clear. The human arm uses classified lines only (3.6).
- Expected correctives: a released defective line carries the E2 O rate at W = 60 of the H1
  defect group if D1/D2 fails, else of the H2 defect group if D4 fails; lines failing
  neither (D3, D6 or D7 only) have no E2 group and are counted, not imputed.
- Cost: every attempt is charged from the reported token usage at the prices recorded in the
  manifest (paper 6's prices), or at the worst-case bound when no usage is reported;
  retries and re-requests included.
- Exploratory view: the template's task paragraph followed by the line's events up to t*
  (date, activity, value), with no actor, id, company or vendor.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_c_3")
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
