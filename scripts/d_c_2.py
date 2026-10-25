"""Write DECISIONS.md D-C-2 from the slot files, so that no figure in it is hand-entered.

Reads results/e2/hypotheses.json and results/e3/human-hold.json (the literal
reading, under `registered_literal_reading` once step 2 has run) and, when
given, results/mutation.json (step 2). Replaces any earlier D-C-2 section of
DECISIONS.md or inserts it after D-C-1.

Usage: python scripts/d_c_2.py --date YYYY-MM-DD
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
HEADING = "## D-C-2 "


def _load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def _n(x: int) -> str:
    return f"{x:,}"


def literal_hold() -> dict:
    hold = _load("e3/human-hold.json")
    return hold.get("registered_literal_reading", hold)


def step2(date: str) -> str:
    path = RESULTS / "mutation.json"
    if not path.exists():
        return ""
    m = json.loads(path.read_text(encoding="utf-8"))
    hold = _load("e3/human-hold.json")
    lit = hold["registered_literal_reading"]["by_gate_status_at_t_star"]
    amd = hold["amended_reading_D-C-2"]["by_gate_status_at_t_star"]
    return f"""
**Applied ({date}).** `src/p2p_replay/contract.py` gains `decide_at`, the
verdict at a decision point: D5 is dropped from the contract when the decision
point is not a clearing, and an actual clearing keeps the registered contract.
`experiments/e1.py` writes the line table's status at t* under both readings
(`t_star_status` literal, `t_star_status_amended` under B). E1 was re-run from
the log and its evidence set and every E1 slot except `lines.jsonl.gz`
(which gains the amended column) are byte-identical to the committed ones;
E2 is unchanged (`results/e2/` re-run byte-identical). `results/e3/human-hold.json`
carries both readings, `registered_literal_reading` and `amended_reading_D-C-2`.
Clean lines at t* with a human hold classification: {_n(lit['clean']['classified_lines'])}
under the literal reading, {_n(amd['clean']['classified_lines'])} under B; held-unknown:
{_n(lit['held_unknown']['classified_lines'])} and {_n(amd['held_unknown']['classified_lines'])}.
Mutation gate (`make mutate`, results/mutation.json): {_n(m['total'])} mutants,
{_n(m['killed'])} killed, {_n(m['survived'])} survived, {_n(m['no_tests'])} without a covering
test; kill score {m['kill_score']:.4f} (gate {m['threshold']}, {'passed' if m['passes'] else 'FAILED'}).
"""


def render(date: str) -> str:
    hyp = _load("e2/hypotheses.json")["estimates"]
    lit = literal_hold()["by_gate_status_at_t_star"]
    p1, p2 = hyp["H1"]["W60"]["p_one_sided_raw"], hyp["H2"]["W60"]["p_one_sided_raw"]
    return f"""{HEADING}Author decisions before E4 ({date})

The author's decisions, final; recorded here with their reasons and logged as
deviations in `prereg/DEVIATIONS.md` (A, B) or as a status correction there (C).

**A. H3 convention.** H3 is not computable: the D5 defect group is empty
({_n(hyp['H3']['W60']['defect_group']['clearings'])} analysed clearings fail D5, D-C-1). The Holm family stays at five tests
and H3 enters it with p = 1. C5 will read "inconclusive: defect class has zero
incidence in this log" at the end of Phase C. Reason: the hypothesis cannot be
tested on this log, and p = 1 is the conservative convention.
Chosen after the raw p-values of H1 ({p1:.3g}) and H2 ({p2:.3g}) were known and
before any H4 value existed.

**B. D5 at a decision point that is not a clearing.** At a t* that is not a
clearing (first invoice receipt + W, section 7), D5 is not applicable and counts
as pass: the predicate asks whether the decider is the line's creator, and at a
replayed decision the decider is the gate or the model. Reason: a definitional
gap in section 7. Under the literal reading (D5 unknown, D-C-1) a line held by
people can never be clean: {_n(lit['clean']['held_by_people'])} of {_n(lit['clean']['classified_lines'])} clean lines
are held, against {_n(lit['held_unknown']['classified_lines'])} held-unknown lines all held
(rate {lit['held_unknown']['human_hold_rate']}), so the human arm on clean lines would be degenerate by
construction. B changes line status at t* for E3's human-hold slot and for the
E4 sample; it changes no predicate at an actual clearing (E1 and E2 untouched).
Decided before any E4 call.

**C. Status line.** `prereg/DEVIATIONS.md`: "p7-v1.1: no deviations (pending
tag)" becomes "p7-v1.1: tagged `prereg-p7-v1.1` on d8cdb2d."
{step2(date)}"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_c_2")
    parser.add_argument("--date", required=True)
    args = parser.parse_args(argv)
    entry = render(args.date).rstrip("\n") + "\n"
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
