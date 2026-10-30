"""DECISIONS.md D-D-3, the round-2 adjudication, and the "Changes since v0.2" list for the round-3 packet.

The entry opens with the records of Phase D session 3 (the A1 sweep statements, the filled template
moved beside the paper, the commits that fail the paper-regeneration test), then one table over the
three round-2 reviews (review-secondary/D2-review-arana.md, D2-review-chatgpt.md,
D2-review-perplexity.md): finding, who raised it, class, decision, reason, where applied. The
decisions are the author's (Phase D session 3), applied as written. Figures in the table are read
from the slots, never typed.

Usage: python scripts/d_d_3.py --date YYYY-MM-DD [--records-only]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-D-3 "

RECORDS = """**Records.**

- *A1 sweep statements.* The attestation of the A1 second sweep
  (`review-secondary/A1-fence-sweep-deepseek.attestation.md`) and D-A1-0c carry a second dated
  paragraph: in the same Perplexity Computer session, after the round-1 review, the platform
  identified the model of the 2026-10-14 sweep as DeepSeek V4 Pro and the model of the round-1 review
  as Claude Opus 5.5 (`review-secondary/D2-review-perplexity.md`, the Acknowledgements row). Both
  statements are on record, in order; the Acknowledgements say the same.
- *Filled template moved.* `results/filled-template.json` is now `paper/filled-template.json`; its
  readers (the typed-numeral lint, G4 and G9 in `scripts/gates.py`, `tests/test_paper.py`,
  `scripts/fill_paper.py`, `scripts/review_packet.py`, the results and paper READMEs) follow. The
  rule: experiment slots under `results/` never change once committed (new slot files may be added);
  derived records of the paper live beside the paper and regenerate with it.
- *Paper-regeneration test.* Commits `a09c4b1` (D-D-2) and `08d860c` (round-1 slots) fail
  `tests/test_paper.py::test_committed_paper_matches_the_template`: the slots changed before the
  paper was regenerated, and the failing exit code was hidden by a pipe. `b01be29` (draft v0.2)
  passes. The builder's test runs now fail on a failing exit code (`set -o pipefail`).
"""


A, C, P = "Arana", "ChatGPT", "Perplexity"


def _retained() -> tuple[str, str]:
    comp = json.loads((ROOT / "results" / "e7" / "comparisons.json").read_text(encoding="utf-8"))
    b = comp["bootstrap"]["B"]
    dom = comp["scopes"]["domestic"]["D1'"]["bootstrap_resamples_used"]
    pooled = comp["scopes"]["pooled"]["D1'"]["bootstrap_resamples_used"]
    return f"{dom:,} of {b:,}", f"{pooled:,} of {b:,}"


def _l1_after_receipt() -> int:
    d = json.loads((ROOT / "results" / "e5" / "derivation.json").read_text(encoding="utf-8"))
    return d["categories"]["3-way, invoice after receipt"]["clearings_per_loss"]["L1"]


def rows() -> list[dict[str, str]]:
    dom, pooled = _retained()
    l1 = _l1_after_receipt()
    return [
        # accepted, new evidence
        dict(f="C1 is supported without evidence of paper 5's sufficiency; Section 3 and Appendix B say each predicate "
               "checks all five SARC-DQ dimensions", by=f"{C}; {P}", cls="(a)", d="accepted, new evidence",
             r="paper 5's sufficiency function (reduct.sufficiency) run on the registered contract per category: "
               "sufficient for every declared loss in 2-way; sufficient for L1 and L3 and not for L2 in both three-way "
               "categories (L2 reads the clearing's position on its line, which no registered predicate reads); minimal "
               "in none; the derived contract is a subset of the registered one in every category (author, 2026-10-30: "
               "qualify, C1 stays supported)",
             w="results/e5/sufficiency.json; Section 3 and Appendix B (each predicate checks one SARC-DQ dimension, "
               "the table; the contract's sufficiency per category and loss, not minimal); C1 evidence column; one "
               "sentence in 5.5 (sufficient, not derived)"),
        dict(f="C9's claim text and status disagree with 5.5's narrow-sense sentence", by=P, cls="(a)",
             d="accepted, new evidence", r="C9 stays not supported: the comparison is the registered one (registration "
               "section 6, E5); C1 and C9 are tied by one sentence: sufficient, not derived",
             w="Section 5.5"),
        dict(f="Commit order does not date the model calls (D-C-2 and the H3 convention before any H4 value)",
             by=f"{C}; {P}", cls="(a)", d="accepted, new evidence",
             r="the response logs carry sent_utc for every request; the earliest call of each family follows the "
               "D-C-2 commit and the sample-draw commit",
             w="results/e4/timeline.json; Sections 4 and 5.2 (the commit-order sentences replaced)"),
        dict(f='Section 5.5: "in the two three-way categories the derived D1 to D4 is the three-way match"',
             by=f"{A}; {C}; {P}", cls="(a)", d="accepted, new evidence",
             r="in the after-receipt category the compiler derives D3 and D4 only, because L1 occurs on "
               f"{l1:,} analysed clearings there (clearings_per_loss in results/e5/derivation.json); a limit of deriving from one log",
             w="Section 5.5: before receipt, D1 to D4 and three predicates beyond; after receipt, D3 and D4 and five "
               "beyond"),
        dict(f="D5: 7,941 `Clear Invoice` events carry no actor, yet D5 has no unknown and the Section 6 table shows "
               '"n/a"', by=P, cls="(a)", d="accepted, new evidence",
             r="the missing-actor clearings all lie outside the analysed set; those on framed lines fall after the "
               "horizon T_end - W",
             w="results/e1/analysed-clearing-actors.json; Sections 5.2 and 6; the Section 6 table shows the D5 "
               "unknown count"),
        dict(f="E7 intervals rest on fewer than the registered B replicates; recorded in D-D-2, not as a deviation",
             by=P, cls="(b), (c)", d="accepted, new evidence",
             r=f"retained replicates: {dom} domestic, {pooled} pooled (results/e7/comparisons.json)",
             w='prereg/DEVIATIONS.md, "E7 bootstrap replicates with an empty group discarded"; Sections 1 and 4 '
               "count and list it; 5.7 cites the slot"),
        dict(f="Expected correctives attributed to registration section 7", by=C, cls="(a)",
             d="accepted, new evidence", r="the metric is registration section 6 (E4 row); the precedence and the "
               "unmatched-group rules are D-C-3", w="Section 5.4"),
        # accepted, wording
        dict(f='Abstract puts "people held" beside "models held" as the same act', by=f"{A}; {C}; {P}", cls="(a)",
             d="accepted, wording", r="section 3.6: a people hold is inferred, the log records no hold decision "
               "except a payment block",
             w='Abstract: "where a hold is an inferred non-release within 60 days, not a recorded decision"'),
        dict(f="Section 7 compares the people column with the model verdicts as if they were the same act",
             by=f"{A}; {C}; {P}", cls="(a)", d="accepted, wording",
             r="the comparison is of outcomes of three deciders, not three acts",
             w="Section 7, one sentence: the people column reports what the process did within W"),
        dict(f="Section 1 counts two deviations after v1.1", by=P, cls="(c)", d="accepted, wording",
             r="DEVIATIONS.md lists four under p7-v1.1 with the E7 entry", w="Section 1"),
        dict(f="5.7: 16,227 all-pass payments is right only if the 2 D3' unknowns are the 2 that fail", by=P,
             cls="(a)", d="accepted, wording", r="they are the same 2 payments (results/e7/evidence-set.jsonl.gz)",
             w="Section 5.7"),
        dict(f="Section 4: no slot path for the category cross-check and the value fallbacks", by=P, cls="(b)",
             d="accepted, wording", r="results/e1/category-crosscheck.json, results/e1/value-fallback.json",
             w="Section 4"),
        dict(f='5.5: "would be such losses" names undeclared losses', by=P, cls="(d)", d="accepted, wording",
             r="the registration declares three losses only", w="Section 5.5, the parenthesis removed"),
        dict(f='Papers 4 and 5 are both cited as "Besanson 2026"', by=P, cls="(a)", d="accepted, wording",
             r="two records, one author-year", w='References and in-text: "Besanson 2026a/2026b"'),
        dict(f='CLAIMS.md C1 still says "(paper 5)" and C2 still says "relied on"', by=P, cls="(a)",
             d="accepted, wording", r="claim text stays as registered; the readings are stated beside it",
             w='CLAIMS.md "Reading notes" under the table; Appendix B follows'),
        dict(f='C5 status says "in this log" where 5.2 says "analysed clearings"', by=P, cls="(a)",
             d="accepted, wording", r="the zero incidence is over the analysed clearings",
             w='CLAIMS.md and Appendix B: "inconclusive: defect class has zero incidence in the analysed clearings"'),
        dict(f="Acknowledgements record only the Claude statement for the second sweep", by=P, cls="(a)",
             d="accepted, wording", r="the platform also identified the sweep's model as DeepSeek V4 Pro",
             w="Acknowledgements; the A1 attestation and D-A1-0c (Records above)"),
        # accepted, COVERAGE.md
        dict(f="COVERAGE.md D1 row describes a temporal rule", by=P, cls="(a)", d="accepted, COVERAGE.md",
             r="section 3.2 defines D1 by counts",
             w='COVERAGE.md and the paper\'s coverage table: "receipts minus cancellations at most zero before t_c, on '
               'a line whose category requires receipt"; DEVIATIONS.md addendum'),
        dict(f='D1\' class label "paid without final approval"', by=f"{A}; {C}; {P}", cls="(a)",
             d="accepted, COVERAGE.md", r="D1' fails when no registered approval event exists; final approval is D2'",
             w='COVERAGE.md and the paper\'s coverage table: "paid without an approval event"; DEVIATIONS.md addendum'),
        # rejected
        dict(f='Lexical hits on "fraud"', by=P, cls="(d)", d="rejected",
             r="as in D-D-2: the coverage row disclaims the class; the reference title is verbatim", w="none"),
        dict(f="Spend-area labels and a reference title point to the sector", by=P, cls="(f)", d="rejected",
             r="as in D-D-2: they are the public log's own strings and the registered strata; the challenge names "
               "the sector", w="none"),
    ]


def table(rs: list[dict[str, str]]) -> str:
    out = ["| # | finding | raised by | class | decision | reason | where applied |", "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rs, 1):
        out.append(f"| {i} | {r['f']} | {r['by']} | {r['cls']} | {r['d']} | {r['r']} | {r['w']} |")
    return "\n".join(out)


def changes_table() -> str:
    """For the round-3 packet: each accepted finding and where it was applied."""
    out = ["| # | finding (round 2) | where applied in v0.3 |", "|---|---|---|"]
    for i, r in enumerate(rows(), 1):
        if r["d"].startswith("accepted"):
            out.append(f"| {i} | {r['f']} | {r['w']} |")
    return "\n".join(out)


def render(date: str, records_only: bool = False) -> str:
    entry = f"{HEADING}Round-2 adjudication ({date})\n\n{RECORDS}"
    if records_only:
        return entry
    rs = rows()
    acc = sum(r["d"].startswith("accepted") for r in rs)
    return entry + f"""
**Adjudication.** Three round-2 reviews of draft v0.2 (packet `review-secondary/D2-review-packet.md` at
`b01be29`): Eduardo Arana (external), and two machine reviews, AI support (ChatGPT, model as it states it:
OpenAI Codex; Perplexity Computer, model as it states it: Claude Opus 5.5). Each is committed unedited
with its attestation and SHA-256. The decisions are the author's, applied as written: {acc} accepted,
{len(rs) - acc} rejected with the reason. Papers 1 to 3: no record given, so the sentence stays as in v0.2.

{table(rs)}

**C1 and paper 5's sufficiency.** The author's decision as given read: "per category, the derived
contract is a subset of the registered one, so the registered contract is sufficient for the three
declared losses over the observed states in paper 5's sense, and minimal in none". Before applying it,
the builder ran paper 5's sufficiency function on the registered contract. The subset relation holds in
every category, but it does not imply sufficiency, because the derived field sets of the three-way
categories include the clearing's position on its line, which no registered predicate reads. The
registered contract is sufficient for every declared loss in 2-way, and in both three-way categories
for L1 and L3 but not for L2; it is minimal in none (`results/e5/sufficiency.json`). The author chose
(2026-10-30) to qualify the statement and keep C1 supported: Section 3, Appendix B and the slot state
sufficiency per category and per loss.

**Rule.** Experiment slots under `results/` never change once committed; new slot files may be added.
The analysed-clearing actor count is therefore a new slot (`results/e1/analysed-clearing-actors.json`),
not a field added to `results/e1/actors.json`.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_d_3")
    parser.add_argument("--date", required=True)
    parser.add_argument("--records-only", action="store_true")
    args = parser.parse_args(argv)
    entry = render(args.date, args.records_only)
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
