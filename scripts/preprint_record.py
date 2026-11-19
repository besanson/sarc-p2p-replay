"""The preprint record (DECISIONS.md D-H-1): parses the SSRN suggested citation the author supplied
(results/release/ssrn-suggested-citation.txt; SSRN answers automated readers with HTTP 403) into
results/release/preprint.json, with one cross-check against Crossref (GET api.crossref.org/works/<doi>): the registered
title and deposit date if it answers 200, "not yet registered at Crossref on <date>" on 404, and "Crossref not reachable
from the builder" if the host cannot be reached. Nothing is typed: the Zenodo DOI comes from CITATION.cff.

Usage: python scripts/preprint_record.py [--checked-on YYYY-MM-DD] [--no-crossref]
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "results" / "release" / "ssrn-suggested-citation.txt"
OUT = ROOT / "results" / "release" / "preprint.json"
CROSSREF = "https://api.crossref.org/works/"
ATTESTATION = ("SSRN page not machine-readable (403 to automated requests, 2026-11-19); citation block supplied by the "
               "author from the SSRN page on 2026-11-19.")
PATTERN = re.compile(
    r"^(?P<family>[^,]+), (?P<given>[^,]+), (?P<title>.+) \((?P<date>[A-Z][a-z]+ \d{2}, \d{4})\)\. "
    r"Available at SSRN: (?P<url>https://ssrn\.com/abstract=(?P<abstract>\d+)) or "
    r"(?P<doi_url>https?://dx\.doi\.org/(?P<doi>10\.\d+/\S+))$")


def parse(text: str) -> dict:
    m = PATTERN.match(text.strip())
    if m is None:
        raise SystemExit("the SSRN citation block does not have the expected form")
    date = dt.datetime.strptime(m["date"], "%B %d, %Y").date().isoformat()
    return {"author": f"{m['given']} {m['family']}", "family_name": m["family"], "given_name": m["given"],
            "title": m["title"], "date_as_printed": m["date"], "date": date, "abstract_id": m["abstract"],
            "url": m["url"], "doi": m["doi"], "doi_url_as_printed": m["doi_url"]}


def crossref(doi: str, checked_on: str) -> dict:
    url = CROSSREF + doi
    req = urllib.request.Request(url, headers={"User-Agent": "sarc-p2p-replay preprint check"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            msg = json.loads(resp.read().decode("utf-8"))["message"]
        deposited = (msg.get("deposited") or {}).get("date-time")
        return {"url": url, "checked_on": checked_on, "http_status": 200, "result": "registered",
                "registered_title": (msg.get("title") or [None])[0], "deposit_date": deposited}
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"url": url, "checked_on": checked_on, "http_status": 404,
                    "result": f"not yet registered at Crossref on {checked_on}"}
        return {"url": url, "checked_on": checked_on, "http_status": exc.code,
                "result": "Crossref not reachable from the builder"}
    except (urllib.error.URLError, OSError):
        return {"url": url, "checked_on": checked_on, "http_status": None,
                "result": "Crossref not reachable from the builder"}


def run(checked_on: str, check: bool = True, out: Path = OUT) -> dict:
    import yaml  # noqa: PLC0415

    raw = SOURCE.read_bytes()
    record = parse(raw.decode("utf-8"))
    cff = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    zenodo = next((i["value"] for i in cff.get("identifiers", []) if "code" in i.get("description", "")), cff["doi"])
    doc = {
        "decision": "DECISIONS.md D-H-1",
        "source": {"file": "results/release/ssrn-suggested-citation.txt", "sha256": hashlib.sha256(raw).hexdigest(),
                   "attestation": ATTESTATION},
        "preprint": {"server": "SSRN", **record},
        "code_and_reproduction_doi": zenodo,
        "crossref": crossref(record["doi"], checked_on) if check else
        {"url": CROSSREF + record["doi"], "checked_on": checked_on, "http_status": None, "result": "not checked"},
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return doc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="preprint_record")
    parser.add_argument("--checked-on", default=dt.date.today().isoformat())
    parser.add_argument("--no-crossref", action="store_true")
    args = parser.parse_args(argv)
    doc = run(args.checked_on, not args.no_crossref)
    p = doc["preprint"]
    print(f"preprint: {p['author']}, {p['title']} ({p['date']}), SSRN {p['abstract_id']}, doi {p['doi']}; "
          f"Crossref: {doc['crossref']['result']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
