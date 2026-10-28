"""DECISIONS.md D-D-2, the round-1 adjudication, and the "Changes since v0.1" list for the round-2 packet.

One table over the three round-1 reviews (review-secondary/D1-review-arana.md, D1-review-chatgpt.md,
D1-review-perplexity.md): finding, who raised it, class, decision, reason, where applied. The
decisions are the author's (Phase D session 2), applied as written. Figures in the table are read
from the slots, never typed.

Usage: python scripts/d_d_2.py --date YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-D-2 "

A, C, P = "Arana", "ChatGPT", "Perplexity"


def _retained() -> tuple[str, str]:
    comp = json.loads((ROOT / "results" / "e7" / "comparisons.json").read_text(encoding="utf-8"))
    b = comp["bootstrap"]["B"]
    dom = comp["scopes"]["domestic"]["D1'"]["bootstrap_resamples_used"]
    pooled = comp["scopes"]["pooled"]["D1'"]["bootstrap_resamples_used"]
    return f"{dom:,} of {b:,}", f"{pooled:,} of {b:,}"


def rows() -> list[dict[str, str]]:
    dom, pooled = _retained()
    return [
        # accepted, wording
        dict(f='"Every clearing" is broader than the analysed population', by=f"{A}; {C}; {P}", cls="(a) wording",
             d="accepted", r="the analysed clearings are those left after the registered exclusions and the E0 removal (results/e1/exclusions.json)",
             w='Abstract, Section 1: "every analysed clearing", with the count and a pointer to the exclusion table'),
        dict(f='"Relied on" says what the decider used; the design reconstructs the log at t_c', by=P, cls="(a) wording",
             d="accepted", r="the evidence is reconstructed, not what the decider consulted (D-A1-1)",
             w='Abstract, Section 5.1, Section 8: "was made on evidence that failed"; CLAIMS.md C2 stays as registered and is read as "made on"'),
        dict(f="The E4 line status rests on D-C-2 B, decided after E3; the Abstract and Section 2 do not say so",
             by=P, cls="(c) disclosure", d="accepted",
             r="the decision preceded every model call; the commit order is the evidence",
             w="Abstract, Section 2; Section 4 cites the D-C-2 commit `7aea13f` before the first response commit `a475068`"),
        dict(f='"Amended once ... before any estimate" omits the two later deviations', by=P, cls="(a), (c)",
             d="accepted", r="the H3 convention and the D5 reading came after E2 and E3",
             w="Section 1: amended once after the pilot (v1.1), with two further deviations decided after E2 and E3 and before E4, all listed in Section 4"),
        dict(f="The fence review came after the p7-v1 tag", by=P, cls="(a) timing", d="accepted",
             r="the review was run after `prereg-p7-v1` and before `prereg-p7-v1.1` (D-A1-0)",
             w="Section 4, Acknowledgements"),
        dict(f='H3: "this log" and "the person who created its line" overstate; the timing has no source', by=P,
             cls="(a)", d="accepted", r="D5 compares with the actor of the earliest creation event, on analysed clearings",
             w='Section 5.2: "no analysed clearing was made by an actor of its line\'s earliest creation event"; the H3 convention cites the D-C-2 commit'),
        dict(f='"Never clean" is contradicted by the one held clean line; the D-C-2 B parenthesis is too broad', by=C,
             cls="(a)", d="accepted", r="the restriction concerns a t* that is not a clearing",
             w='Section 5.3: "a line with no clearing within W can never be clean under the literal reading"; the parenthesis restricted to "at a t* that is not a clearing"'),
        dict(f='"Holds" reads as the gate acting; "both arms" is ambiguous; spend and exploratory figures lack slots',
             by=P, cls="(a), (b), (e)", d="accepted", r="the gate's verdict is a replay; every figure names its slot",
             w='Section 5.4: "the gate\'s verdict holds"; "both families and both views"; spend cites results/e6/cost.json; the exploratory table gets counts and its slot path'),
        dict(f='"Guard losses" is loss wording', by=P, cls="(d), (e)", d="accepted", r="no loss claim is made",
             w='Section 5.5: "correspond to no declared loss", and one sentence on the three-way match in the narrow sense'),
        dict(f='Section 6: "every other detected class" is too broad (BPI 2020); the recovery row; the "detected" definition and the stale class',
             by=f"{C}; {P}", cls="(a)", d="accepted", r="the coverage check covers BPI 2019 only; the stale class uses events after t_c",
             w="Section 6: per-class statement for BPI 2019 and for BPI 2020; COVERAGE.md recovery row and definition"),
        dict(f='"Shows that a different view changes" is causal wording', by=f"{C}; {P}", cls="(d)", d="accepted",
             r="the exploratory arm has no interval and sits outside the Holm family",
             w='Section 7: "under the timeline view the same models held far fewer lines (exploratory, no interval)"'),
        dict(f='The H2 comparison group is called "clean clearings" in the Conclusion', by=f"{A}; {C}; {P}",
             cls="(a)", d="accepted", r="H2 compares D4 fail with D4 pass", w="Section 8: the group names of Section 5.2"),
        dict(f="A prevalence statement and the people-arm sentence read as claims about the company", by=P,
             cls="(e)", d="accepted", r="the non-claim concerns naming or characterising the company, its subsidiaries or vendors",
             w="Section 1: one sentence after the non-claims list"),
        dict(f='C1 "sufficiency-checked" has no certificate for D1 to D7', by=C, cls="(a)", d="accepted",
             r="the term means each predicate checks presence, freshness, validity, authority and scope (the SARC-DQ dimensions); it is not paper 5's sufficiency certificate",
             w="Section 3 and Appendix B; CLAIMS.md C1 evidence column: results/e1/evidence-set.jsonl.gz and tests/test_properties.py, with results/mutation.json as engine evidence"),
        dict(f="Papers 1 to 6 are asserted but not cited", by=P, cls="(a)", d="accepted",
             r="cite what has a verifiable record; name the rest",
             w="Section 1: paper 4 (arXiv:2608.18360) and paper 5 (arXiv:2609.26016) cited, paper 6 as its public repository; papers 1 to 3 have no record found (verified-citations.json)"),
        # accepted, registered-file descriptions
        dict(f='COVERAGE.md D1\' row says "final approval"', by=f"{A}; {C}", cls="(a)", d="accepted",
             r="registration section 8: any event of the approval list", w="COVERAGE.md, logged in prereg/DEVIATIONS.md"),
        dict(f="COVERAGE.md D6 and D7 rows describe a temporal rule, not the registered counts", by=C, cls="(a)",
             d="accepted", r="registration section 3.2 counts sets minus removals, and deletions plus blocks minus reactivations",
             w="COVERAGE.md, logged in prereg/DEVIATIONS.md"),
        # accepted, new slots
        dict(f='"Held by people" is an inferred non-release, not a decision like a model\'s hold', by=f"{A}; {P}",
             cls="(a)", d="accepted", r="the log records no hold decision except a payment block",
             w="results/e3/human-hold-composition.json; Section 5.4 paragraph on what the human arm measures"),
        dict(f="Zero D5 failures: are clearing and creation actors separate populations, or is the field unusable?",
             by=P, cls="question", d="accepted", r="answered from the log",
             w="results/e1/actors.json; Sections 5.2 and 6 worded from it"),
        dict(f="People and models are compared on different denominators", by=f"{A}; {C}; {P}", cls="(a)",
             d="accepted", r="the people arm classifies fewer lines (3.6)",
             w="results/e4/arms-classified-lines.json, a second table in Section 5.4; the unclassified lines and the eligible-versus-classified counts explained with their slots"),
        dict(f="Expected correctives: the rate assignment and the lines without an estimate are not stated; the gate's zero",
             by=f"{A}; {C}; {P}", cls="(a), (e)", d="accepted", r="registration section 7; H1 group first, else H2",
             w='Section 5.4: the convention with the counts from results/e4/arms.json; "held lines go somewhere the log does not show"'),
        dict(f="Appendix D is not per defect class and shows Wilson, not clustered, intervals", by=C, cls="(a)",
             d="accepted", r="results/e1/exposure-by-stratum.json carries both", w="Appendix D"),
        dict(f="Three registered slots are never reported (category cross-check, value fallback, the sample export)",
             by=P, cls="(c)", d="accepted", r="registration sections 3.1, 3.4, 3.9", w="Sections 4 and 5.1"),
        dict(f="E7 intervals discard bootstrap replicates with an empty comparison group, undisclosed", by=C,
             cls="(c)", d="accepted (pipeline reading)",
             r=f"retained replicates: {dom} domestic, {pooled} pooled (results/e7/comparisons.json)",
             w="Section 5.7; this entry"),
        # rejected
        dict(f='"At most t_c" is an unlogged deviation', by=P, cls="(c)", d="rejected",
             r='p7-v1 section 2 defines "before t_c" as less than or equal, excluding the clearing', w="Section 3 cites it"),
        dict(f="Section 5.5 changed the C9 comparator from the matching rule to D1 to D7", by=P, cls="(c)", d="rejected",
             r='registration section 6, E5: "whether the derived contract equals the category contract in 3.1"',
             w="Section 5.5 cites it"),
        dict(f="Spend-area labels in Appendix D narrow down the industry", by=P, cls="(f)", d="rejected",
             r="they are the public log's own strings and the registered strata; the challenge names the sector",
             w="Appendix D, one sentence"),
        dict(f='Lexical hits on "fraud"', by=f"{C}; {P}", cls="(d)", d="rejected",
             r="the coverage row disclaims the class; the reference title is verbatim", w="none"),
        dict(f='D5 "not demonstrated" on this log', by=P, cls="(a)", d="rejected",
             r="fixture and engine tests show D5 firing on synthetic lines (tests/test_engine_units.py::test_d5_actors, "
               "test_verdict_at_decision_point_d5_off_clearing; fixture line C in tests/test_pipeline.py); the actors slot answers the real question",
             w="Section 6"),
    ]


def table(rs: list[dict[str, str]]) -> str:
    out = ["| # | finding | raised by | class | decision | reason | where applied |", "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rs, 1):
        out.append(f"| {i} | {r['f']} | {r['by']} | {r['cls']} | {r['d']} | {r['r']} | {r['w']} |")
    return "\n".join(out)


def changes_table() -> str:
    """For the round-2 packet: each accepted finding and where it was applied."""
    out = ["| # | finding (round 1) | where applied in v0.2 |", "|---|---|---|"]
    for i, r in enumerate(rows(), 1):
        if r["d"].startswith("accepted"):
            out.append(f"| {i} | {r['f']} | {r['w']} |")
    return "\n".join(out)


def render(date: str) -> str:
    rs = rows()
    acc = sum(r["d"].startswith("accepted") for r in rs)
    return f"""{HEADING}Round-1 adjudication ({date})

Three round-1 reviews of draft v0.1 (packet `review-secondary/D1-review-packet.md` at `76264dd`):
Eduardo Arana (external), and two machine reviews, AI support (ChatGPT; Perplexity Computer, model as
it states it: Claude Opus 5.5). Each is committed unedited with its attestation and SHA-256. The
decisions are the author's, applied as written: {acc} accepted, {len(rs) - acc} rejected with the reason.

{table(rs)}

**Readings.** CLAIMS.md C2's "relied on" is read as "made on" (the claim text stays as registered).
The C1 clarification is placed in Section 3 and in the paper's claims table (Appendix B); in CLAIMS.md
only the evidence column of C1 changes. The E7 bootstrap convention (a replicate in which either
group is empty is discarded, and the percentiles are taken over the retained replicates) is a
pipeline reading of `experiments/e7.py`, recorded here; the retained counts are in
`results/e7/comparisons.json` (`bootstrap_resamples_used`). The A1 second sweep's attestation and
D-A1-0c carry the platform correction of 2026-10-28; the paper names machine sweeps and reviews by
platform with the model as self-reported.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_d_2")
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
