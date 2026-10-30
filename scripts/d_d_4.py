"""DECISIONS.md D-D-4, the round-3 adjudication, and the "Changes since v0.3" list for the record.

One table over the three round-3 reviews (review-secondary/D3-review-arana.md, D3-review-chatgpt.md,
D3-review-perplexity.md): finding, who raised it, class, decision, reason, where applied. The
decisions are the author's (Phase D session 4), applied as written. Figures in the table are read
from the slots, never typed.

Usage: python scripts/d_d_4.py --date YYYY-MM-DD [--changes review-secondary/D-changes-v0.3-to-v1.0.md]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-D-4 "

A, C, P = "Arana", "ChatGPT", "Perplexity"


def _json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _block_holds() -> str:
    c = _json("results/e3/human-hold-composition.json")
    r = c["by_reason"]
    block = r["payment_block_before_first_clearing"] + r["both"]
    return f"{block:,} of {c['held_by_people']:,}"


def _first_jev() -> str:
    v = _json("results/e4/timeline.json")["calls"]["e4/jev"]["requests"]["attempt"]["earliest_sent_utc"]
    return f"{v[:10]} {v[11:19]} UTC"


def _checked_entries() -> str:
    # ChatGPT's own count, quoted from its reply (class (b) row), not a slot value.
    text = (ROOT / "review-secondary" / "D3-review-chatgpt.md").read_text(encoding="utf-8")
    return re.search(r"All (\d+) generated scalar entries matched", text).group(1)


def rows() -> list[dict[str, str]]:
    return [
        # accepted, deviation
        dict(f="The Jev reply-template adaptation (typed choice instead of the registered JSON reply) is recorded as a "
               "pipeline reading in D-C-3, not as a deviation", by=P, cls="(c)", d="accepted, deviation",
             r="the registration makes the companion templates binding and calls any post-tag template change a "
               f"deviation; the first Jev decision request ({_first_jev()}, results/e4/timeline.json) already carries "
               "the typed choice; the Haiku family received the template as registered; no result changes",
             w='prereg/DEVIATIONS.md, "E4 Jev request format"; Section 1 counts five deviations under v1.1; Section 4 '
               "lists it; one sentence in 5.4"),
        # accepted, wording
        dict(f="The Abstract calls every people hold an inferred non-release; the measure also includes a recorded "
               "payment block", by=P, cls="(a)", d="accepted, wording",
             r=f"{_block_holds()} people holds involve a payment block (results/e3/human-hold-composition.json)",
             w='Abstract: "where a hold is a recorded payment block or, in nearly every case, an inferred non-release '
               'within 60 days, not a recorded decision"'),
        dict(f='C9\'s "per-category matching rule" and its status "not supported" are not aligned with 5.5', by=P,
             cls="(a)", d="accepted, wording",
             r="the matching rule is the category contract of section 3.1, the comparator the registration's E5 row "
               "fixes; the before-receipt category recovers the narrow three-way match (D1 to D4)",
             w="CLAIMS.md reading notes and Appendix B: a C9 note; the status refers to the registered comparison"),
        dict(f='Section 7: "reported beside every estimate" overstates what the paper shows for 5.2 and 5.3', by=P,
             cls="(a)", d="accepted, wording",
             r="the per-stratum estimates exist in results/e2/confounders.json and results/e3/confounders.json",
             w="Appendix E (H1, H2 and gate by outcome per category, spend area, value quartile, vendor activity "
               "quartile and month), pointed to from 5.2, 5.3 and 7"),
        dict(f="What substantive assurance C1's sufficiency check adds", by=C, cls="question", d="accepted, wording",
             r="results/e5/sufficiency.json",
             w='Conclusion, one sentence: sufficient for "goods not received" and "changed amount", not for "pay '
               'twice" in the three-way categories, because no registered predicate reads the clearing\'s position'),
        dict(f="Which inferences the people, model and gate comparison supports", by=f"{C}; {P}", cls="question",
             d="accepted, wording", r="the people column is a process outcome, not a decision at t*",
             w="Section 7, one sentence: the only inference the three columns support; no decision quality is "
               "inferred for people"),
        dict(f="What the expected-correctives totals estimate", by=C, cls="question", d="accepted, wording",
             r="E2 rates applied to the lines each arm released, under the stated assignment",
             w="5.4, one sentence: a projection from observed rates onto the sample, not an observed count"),
        dict(f='Section 6 table: "n/a" for the unknown counts of every predicate but D5', by="author (from the "
               "D-D-3 report)", cls="(b)", d="accepted, wording",
             r="the evidence set records each predicate's value per analysed clearing",
             w="results/e1/predicate-unknowns.json (a new slot); the Section 6 table"),
        # rejected
        dict(f='Lexical hits on "fraud" (the coverage row and a reference title)', by=P, cls="(d)", d="rejected",
             r="as in D-D-2 and D-D-3: the coverage row disclaims the class; the reference title is verbatim",
             w="none"),
        dict(f="Provider names in 5.4 (TypeSafe, Anthropic)", by=P, cls="(f)", d="rejected",
             r="methodological attribution of the services the replay called, not the studied company or its vendors",
             w="none"),
    ]


def table(rs: list[dict[str, str]]) -> str:
    out = ["| # | finding | raised by | class | decision | reason | where applied |", "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rs, 1):
        out.append(f"| {i} | {r['f']} | {r['by']} | {r['cls']} | {r['d']} | {r['r']} | {r['w']} |")
    return "\n".join(out)


def changes_table() -> str:
    """Each accepted round-3 finding and where it was applied in the v1.0 candidate."""
    out = ["| # | finding (round 3) | where applied in the v1.0 candidate |", "|---|---|---|"]
    for i, r in enumerate(rows(), 1):
        if r["d"].startswith("accepted"):
            out.append(f"| {i} | {r['f']} | {r['w']} |")
    return "\n".join(out)


def render(date: str) -> str:
    rs = rows()
    acc = sum(r["d"].startswith("accepted") for r in rs)
    return f"""{HEADING}Round-3 adjudication ({date})

Three round-3 reviews of draft v0.3 (packet `review-secondary/D3-review-packet.md` at `a75be8d`):
Eduardo Arana (external), and two machine reviews, AI support (ChatGPT, model as it states it:
gpt-6-astra; Perplexity, which names no serving model and quotes the session label GPT-6 Astra). Each
is committed unedited with its attestation and SHA-256. The decisions are the author's, applied as
written: {acc} accepted, {len(rs) - acc} rejected with the reason.

- Arana: nothing further of substance ("I have nothing further of substance to add within the scope
  of this review").
- ChatGPT: "none found" in all six classes, (a) to (f), with {_checked_entries()} generated scalar
  entries checked against their cited files (its count); every row of "Changes since v0.2" marked yes.
  Its three hostile-reviewer questions are answered in rows 5 to 7.
- Perplexity: the findings below. Of "Changes since v0.2" it marked rows 2 and 8 partly and row 10
  yes for the listed deviations only; these are rows 3, 2 and 1 here. Its three hostile-reviewer
  questions are answered in rows 3, 1 and 6.

{table(rs)}

Row 8 was not raised in round 3: the D-D-3 report noted that no slot counted the unknowns of the
predicates other than D5, and the author decided to add one.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_d_4")
    parser.add_argument("--date", required=True)
    parser.add_argument("--changes", type=Path, default=None)
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
    if args.changes:
        args.changes.write_text(
            "# Changes since v0.3 (draft v0.3 to the v1.0 candidate)\n\n"
            "Generated from `DECISIONS.md` D-D-4 by `scripts/d_d_4.py`, for the record; there is no round-4 packet. "
            "Every round-3 finding the author accepted, numbering as in D-D-4, and where it was applied. The rejected "
            "findings and their reasons are in D-D-4.\n\n" + changes_table() + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
