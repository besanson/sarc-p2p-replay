"""Write DECISIONS.md D-C-4 (E5 and E7 run) and D-C-5 (Phase C closed) from the slot files.

No figure in either entry is hand-entered. Replaces earlier D-C-4 and D-C-5 sections or appends.

Usage: python scripts/d_c_4_5.py --date YYYY-MM-DD
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
PRIMES = ("D1'", "D2'", "D3'")


def _load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def _n(x: int) -> str:
    return f"{x:,}"


def _r(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.4f}"


def _iv(x: list | None) -> str:
    return "n/a" if x is None else f"[{x[0]:.4f}, {x[1]:.4f}]"


def d_c_4(date: str) -> str:
    e5 = _load("e5/derivation.json")
    voc = _load("e7/vocabulary.json")
    units = _load("e7/units.json")["logs"]
    preds = _load("e7/predicates.json")["counts"]
    expo = _load("e7/exposure.json")["scopes"]
    comp = _load("e7/comparisons.json")["scopes"]
    dr5, dr7 = _load("e5/double-run.json"), _load("e7/double-run.json")
    e5_rows = []
    for cat, s in e5["categories"].items():
        loss = ", ".join(f"{k} {_n(v)}" for k, v in s["clearings_per_loss"].items())
        e5_rows.append(f"| {cat} | {_n(s['analysed_clearings'])} | {_n(s['distinct_states'])} | {loss} | "
                       f"{', '.join(s['minimum_cardinality_field_set'])} | {', '.join(s['derived_contract']) or 'none'} | "
                       f"{', '.join(s['registered_contract'])} | {s['result']} |")
    absent = voc["registered_names_absent_per_log"]
    absent_txt = "; ".join(f"{log}: {', '.join(f'`{n}`' for n in names) if names else 'none'}"
                           for log, names in absent.items())
    unit_rows = [f"| {log} | {_n(u['cases'])} | {_n(u['payments_in_log'])} | "
                 f"{_n(u['excluded_payments_after_t_end_prime_minus_w'])} | {_n(u['units'])} | {u['t_end_prime']} |"
                 for log, u in units.items() if log != "pooled"]
    comp_rows = []
    for scope, c in comp.items():
        for d in PRIMES:
            x = c[d]
            comp_rows.append(f"| {scope} | {d} | {_n(x['defect_group']['payments'])} | {_r(x['defect_group']['O_prime_rate'])} | "
                             f"{_n(x['all_pass_group']['payments'])} | {_r(x['all_pass_group']['O_prime_rate'])} | "
                             f"{_r(x['difference'])} | {_iv(x['bootstrap95'])} | {'yes' if x['h1_shape'] else 'no'} |")
    pred_txt = "; ".join(f"{scope}: " + ", ".join(f"{d} fail {_n(v[d]['fail'])}, unknown {_n(v[d]['unknown'])}" for d in PRIMES)
                         for scope, v in preds.items())
    expo_txt = "; ".join(f"{scope} {_n(v['with_a_failed_predicate'])} of {_n(v['units'])} payments "
                         f"(value share {_r(v['share_of_paid_value'])})" for scope, v in expo.items())
    return f"""## D-C-4 E5 and E7 run ({date})

**What ran.** E5 (`experiments/e5.py`) on the E1 evidence set, with paper 5's compiler; the E7
vocabulary check (`experiments/e7_check.py`) and the E7 replication (`experiments/e7.py`) on the
two BPI 2020 declaration logs (SHA-256 as registered, checked by the runner). No model call.

**Compiler.** `{e5['compiler']['entry_point']}` from `{e5['compiler']['repository']}` at
`{e5['compiler']['commit']}` (the engines.lock pin, checked by the runner), imported from the
sibling checkout unmodified (package version string `{e5['compiler']['version']}` when not
installed); its dependency python-sat at the version of its own `constraints.txt` (pinned in
`pyproject.toml`). The adapter lives in `experiments/e5.py`: per category, one state per distinct
combination of the evidence-set observations (a frozen dataclass, as the compiler's
`participation` module reads states), the candidate context the values each observation takes,
and the three registered losses as predicates over the state. Observations: `receipts`
(uncancelled receipts, read by D1 and D2), `invoices` (D3), `changes` (changes since approval, D4),
`distinct_actors` (D5's recorded value; the evidence set does not carry the creator), `blocks`
(D6), `closed` (D7), and `clearing_ordinal` (the clearing's position among the line's analysed
clearings, from the evidence set's own case_id and t_c; read by no predicate). Losses: L1 pay for
goods not received = the category requires a goods receipt and `receipts <= 0`; L2 pay twice =
`clearing_ordinal > invoices`; L3 pay a changed amount = `changes > 0`. The derived contract is the
set of registered predicates whose observation is in the compiler's minimum-cardinality reduct.

**E5 result** (`results/e5/derivation.json`; the compiler's full output per category in
`results/e5/trace-*.json`):

| category | clearings | states | clearings per loss | minimum-cardinality field set | derived contract | registered contract | result |
|---|---|---|---|---|---|---|---|
{chr(10).join(e5_rows)}

Each category has a single minimal reduct (`minimal_reducts` in the slot). No declared loss reads
the observations of D5, D6 or D7, so they never enter a sufficient set; L2 needs
`clearing_ordinal`, an observation no registered predicate reads.

**E7 vocabulary** (`results/e7/vocabulary.json`). Registered names absent from both logs:
{', '.join(voc['registered_names_absent_from_both_logs']) or 'none'}. Absent per log: {absent_txt}; each
is reported with a zero count and stays in its list. Every attribute the registered bpi2020
mapping names is present in both logs: {'no' if voc['stop'] else 'yes'}.

**E7 results** (`results/e7/`; descriptive, secondary, no p-value, not in the Holm family):

| log | cases | payments | excluded after T_end' - W | units | T_end' |
|---|---|---|---|---|---|
{chr(10).join(unit_rows)}

Predicates: {pred_txt}. Payments with at least one failed predicate: {expo_txt}.

| scope | predicate | failing payments | O' rate | all-pass payments | O' rate | difference | 95% interval | H1 shape |
|---|---|---|---|---|---|---|---|---|
{chr(10).join(comp_rows)}

**Double runs.** E5 twice, byte-identical: {'yes' if dr5['all_identical'] else 'no'}
(`results/e5/double-run.json`); E7 vocabulary check and replication twice, byte-identical:
{'yes' if dr7['all_identical'] else 'no'} (`results/e7/double-run.json`).

**Pipeline readings (no registered item changed).**

- The three losses are expressed over the evidence set as above. L1 is a loss only where the
  category requires a goods receipt (on a 2-way line no receipt is recorded by design). L2 has no
  single evidence-set field; it is expressed with the clearing's position on its line, derived from
  the evidence set's own line id and clearing time, against the invoice count. The compiler needs
  every loss to be a function of the candidate observations, so that position is a candidate.
- Identical observation vectors are one state; the number of clearings each stands for is in the
  trace. The compiler's partitions, core and reducts do not depend on repeats.
- E7 paid value is the case attribute `Amount`, read beside the registered bpi2020 mapping (which
  names no amount field) for the value share only; every payment of a case carries its case's
  amount; sums use `math.fsum` (the anonymised amounts carry many decimals).
- E7 bootstrap clusters are declaration cases, identified by the hash of log name and case id so
  that the pooled scope keeps the two logs' cases apart; sorted by that hash.
- T_end' is the latest timestamp of each log (section 8, unchanged by v1.1).
"""


def d_c_5(date: str) -> str:
    sys.path.insert(0, str(ROOT / "scripts"))
    from claim_statuses import statuses  # noqa: PLC0415

    table = statuses()
    rows = [f"| {cid} | {status} | {evidence} |" for cid, (status, evidence) in table.items()]
    dev = (ROOT / "prereg" / "DEVIATIONS.md").read_text(encoding="utf-8").split("## Under p7-v1.1", 1)[1]
    devs = [m.group(1) for m in re.finditer(r"^### (.+)$", dev, re.MULTILINE)]
    cost = _load("e6/cost.json")
    return f"""## D-C-5 Phase C closed ({date})

Every Phase C experiment of the registration (E0 to E7) has run; every figure is in a slot file
under `results/` (index: `results/README.md`). Claim statuses, set from the slots by
`scripts/claim_statuses.py` (`CLAIMS.md`):

| claim | status | evidence |
|---|---|---|
{chr(10).join(rows)}

**Deviations under p7-v1.1** (`prereg/DEVIATIONS.md`): {'; '.join(devs)}.

**Spend.** USD {cost['spend_usd_total']:.4f} of the USD {cost['cap_usd']:.0f} cap, E4 and the exploratory
arm together (`results/e6/cost.json`).

No registered item changed after the tag prereg-p7-v1.1 except as logged in prereg/DEVIATIONS.md.
"""


def replace(text: str, heading: str, entry: str) -> str:
    if heading in text:
        head, rest = text.split(heading, 1)
        tail = re.search(r"\n## ", rest)
        return head + entry + ("\n" + rest[tail.start() + 1:] if tail else "")
    return text.rstrip("\n") + "\n\n" + entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_c_4_5")
    parser.add_argument("--date", required=True)
    args = parser.parse_args(argv)
    text = DECISIONS.read_text(encoding="utf-8")
    text = replace(text, "## D-C-4 ", d_c_4(args.date))
    text = replace(text, "## D-C-5 ", d_c_5(args.date))
    DECISIONS.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
