"""DECISIONS.md D-G-1, the author's final verification of 1.0.3: the observations and the decisions on
each, and a record of every exploratory analysis whose slot exists under results/exploratory/ (X1 to X4).
Nothing is typed: every figure of the records is read from its slot.

Usage: python scripts/d_g_1.py --date YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-G-1 "
EXPLORATORY = ROOT / "results" / "exploratory"

OBSERVATIONS = """The author read the released paper (1.0.3, tag v1.0.3, externally reproduced) and decided on
each observation below. Every addition is exploratory or wording: none changes a registered file, a
committed experiment slot, `CLAIMS.md`, the Holm family or a registered estimate. Exploratory slots live
under `results/exploratory/`, are labelled exploratory in every file name, field and heading, carry no
p-value and never enter the Holm family.

a. D4 accounts for most clearings with a failed predicate, and the headline exposure rests on one
   predicate whose "last approval-bearing event" is often the line's creation. Decision: an exploratory
   sensitivity analysis (X1) and, in session 2, a sentence distinguishing a failed registered predicate
   from a confirmed violation of the company's approval policy.
b. The people column measures observed non-release within W, not a decision; it must be named and tabled
   as such, at the top of 5.4. Decision: wording and table changes in session 2.
c. D-C-2 B needs its conceptual justification in the paper: "not applicable" (no clearing actor exists)
   is not "unknown" (an actor field is empty); with the list of what is invariant to it and what depends
   on it. Decision: a Section 3 paragraph in session 2.
d. The model comparison must be auditable: the registered ERP view template, one synthetic example of
   both views, both request formats including the Jev deviation, and the statement that the design does
   not separate wording, structure and information content. Decision: X4, and an appendix in session 2.
e. H1 and H2 are unadjusted; an exploratory standardised estimate shows whether the associations survive
   observed composition. Decision: X2.
f. The compiler's negative result is a contribution: incomplete loss specification against insufficient
   observables, minimal against normative contract, losses absent from history. Decision: discussion in
   session 2.
g. Holds with no corrective within W are an operational cost worth stating in proportions. Decision: X3.
   Hypothetical review-cost or resolution-time scenarios are declined: the log carries no parameter for
   them, and every figure would be assumed.
h. E7 shows that the procedure applies to another log, not external validity; the characteristics an
   informative replication needs are listed. Decision: wording in session 2.
i. Editorial: figure numbering and captions checked; the AI disclosure shortened; confirmatory,
   exploratory and secondary labels on every result heading; the abstract observational. Decision:
   session 2."""


def _load(name: str) -> dict | None:
    p = EXPLORATORY / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _pct(x: float | None) -> str:
    return "n/a" if x is None else f"{100 * x:.2f}%"


def _iv(iv: list | None) -> str:
    return "n/a" if not iv else f"[{100 * iv[0]:.2f}%, {100 * iv[1]:.2f}%]"


def _share(e: dict) -> str:
    return (f"{e['clearings']:,} clearings, {_pct(e['share_of_clearings'])} {_iv(e['bootstrap95'])}; "
            f"{_pct(e['share_of_value'])} of cleared value {_iv(e['value_bootstrap95'])}")


def records() -> str:
    out = []
    x1 = _load("d4-sensitivity.json")
    if x1:
        a = x1["exploratory_all"]
        rows = [f"  - (a) registered, at least one failed predicate: {_share(a['registered'])}",
                f"  - (b) D4 counting only changes after an explicit approval or release event: {_share(a['explicit_only'])}",
                f"  - (c) D4 failures whose only approval-bearing event is the creation: {_share(a['creation_only_d4'])}"]
        m = x1["exploratory_materiality"]
        rows.append(f"  - materiality: {m['what_the_values_allow']}")
        for t in m["thresholds"]:
            rows.append(f"  - D4 failures restricted to an observable relative change above {t['label']}: "
                        f"{_share(t['exposure'])}")
        out.append("**X1, D4 sensitivity (exploratory)** (`results/exploratory/d4-sensitivity.json`, "
                   "`experiments/exploratory/x1_d4_sensitivity.py`):\n" + "\n".join(rows))
    x2 = _load("adjusted-h1-h2.json")
    if x2:
        rows = []
        for h, block in x2["exploratory_estimates"].items():
            rows.append(f"  - {h}: registered unadjusted difference {block['registered_unadjusted_difference']:.4f}")
            for s, e in block["standardised"].items():
                iv = e["bootstrap95"]
                rows.append(f"    - by {s}: standardised difference {e['standardised_difference']:.4f} "
                            f"[{iv[0]:.4f}, {iv[1]:.4f}]" if iv else f"    - by {s}: not computable")
        out.append("**X2, standardised H1 and H2 (exploratory)** (`results/exploratory/adjusted-h1-h2.json`, "
                   "`experiments/exploratory/x2_adjusted_h1_h2.py`):\n" + "\n".join(rows))
    x3 = _load("hold-friction.json")
    if x3:
        rows = []
        for w, e in x3["exploratory_overall"].items():
            rows.append(f"  - {w}: of {e['holds']:,} gate holds, {_pct(e['share_without_corrective'])} "
                        f"{_iv(e['bootstrap95'])} had no corrective; {_pct(e['value_share_without_corrective'])} "
                        f"{_iv(e['value_bootstrap95'])} of their cleared value")
        out.append("**X3, hold friction (exploratory)** (`results/exploratory/hold-friction.json`, "
                   "`experiments/exploratory/x3_hold_friction.py`):\n" + "\n".join(rows))
    x4 = _load("prompt-examples.json")
    if x4:
        out.append("**X4, prompt examples (exploratory)** (`results/exploratory/prompt-examples.json`, "
                   "`paper/appendix-prompts.md`, `experiments/exploratory/x4_prompt_examples.py`): the registered "
                   f"template verbatim; the synthetic fixture line `{x4['synthetic_line']['case_id']}` rendered as the "
                   f"ERP view ({'yes' if x4['renders']['erp_view'] else 'no'}) and as the timeline view "
                   f"({'yes' if x4['renders']['timeline_view'] else 'no'}) by the code E4 used; both request bodies; "
                   "the fields each view exposes and omits. Nothing from a real line.")
    return "\n\n".join(out)


def render(date: str) -> str:
    rec = records()
    return f"""{HEADING}Author's final verification of 1.0.3 ({date})

{OBSERVATIONS}
""" + (f"""
**Exploratory analyses (records).** Each is computed from the committed evidence set, lines table,
responses and slots (X1 also from the log, for the event kinds and values the evidence set does not
keep), runs twice byte-identically, and is a step of `make reproduce` and of gate G4.

{rec}
""" if rec else "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_g_1")
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
