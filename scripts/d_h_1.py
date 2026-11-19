"""DECISIONS.md D-H-1, the preprint, from results/release/preprint.json. Nothing is typed.

Usage: python scripts/d_h_1.py --date YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "DECISIONS.md"
HEADING = "## D-H-1 "


def render(date: str) -> str:
    doc = json.loads((ROOT / "results" / "release" / "preprint.json").read_text(encoding="utf-8"))
    p, cr, src = doc["preprint"], doc["crossref"], doc["source"]
    if cr["http_status"] == 200:
        cross = (f"Crossref answers {cr['http_status']} for `{p['doi']}` (checked {cr['checked_on']}): registered title "
                 f"\"{cr['registered_title']}\", deposited {cr['deposit_date']}.")
    else:
        cross = f"Crossref, checked {cr['checked_on']}: {cr['result']}."
    return f"""{HEADING}Preprint ({date})

**arXiv.** Paper v1.1.2 was submitted to arXiv on the submission date (the date was not supplied to the builder and is
not recorded in this repository; the author adds it). On 2026-11-13 arXiv moderation declined it without review: "does not
contain sufficient original or substantive scholarly research". An appeal is possible only after journal acceptance.

**SSRN.** The same paper text, v1.1.2, unchanged between the two submissions, is posted on SSRN as abstract
{p['abstract_id']} ({p['url']}), doi {p['doi']}; the citation block dates it {p['date_as_printed']} ({p['date']}). The
record: {src['attestation']} The block is committed byte for byte as `{src['file']}` (SHA-256 `{src['sha256']}`) and parsed
by `scripts/preprint_record.py` into `results/release/preprint.json`. {cross} The record is in
`verified-citations.json` (`besanson-paper7-ssrn-2026`, status author-supplied).

**Stamp (1.1.3).** `CITATION.cff`: the SSRN DOI (preprint) and the Zenodo DOI {doc['code_and_reproduction_doi']} (code, data
hashes, registration and reproduction record) as identifiers, and a preferred-citation pointing at the SSRN preprint; the
README status and its generated Cite block (the preprint first, then the code record); a front-matter line in the paper,
filled from `results/release/preprint.json`. Section 1's sentence that the six earlier papers are on arXiv is unchanged
and still true. No registered file, committed slot or paper number changed.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="d_h_1")
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
