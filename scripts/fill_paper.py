"""Fill paper/template.md from the slot files: writes paper/paper.md and paper/filled-template.json.

Every numeral in the paper reaches it through this script. Placeholders:

  {{SOURCE>key>key|fmt}}   one value. SOURCE is a file under results/ (e.g. e1/exposure.json),
                           `@datalock` (prereg/data.lock), `@claims` (the status column of
                           CLAIMS.md, by claim id) or `@cite` (an in-text citation of a record in
                           verified-citations.json, by id). Keys walk the JSON; a numeric key
                           indexes a list.
  {{#NAME}}                a generated block (a table or list), built by a function below from
                           named slot files.

Formats: int (thousands separator), pct (two decimals, %), pct1, prop (four decimals), prop3,
p (p-value), eur (whole anonymised EUR, thousands separator), usd (two decimals), usd4, usd6,
iv (interval of proportions, four decimals), ivpct (interval in %, two decimals), sec (seconds,
one decimal), str (as is), date (YYYY-MM-DD).

paper/filled-template.json records, for every placeholder, its text, source, key, raw value and
its character span in paper/paper.md; the typed-numeral lint reads the spans. Output is a pure
function of the template and the slots, so regeneration is byte-identical.

Usage: python scripts/fill_paper.py
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "paper" / "template.md"
PAPER = ROOT / "paper" / "paper.md"
FILLED = ROOT / "paper" / "filled-template.json"
RESULTS = ROOT / "results"
PLACEHOLDER = re.compile(r"\{\{(.*?)\}\}", re.DOTALL)
STRATA_IN_PAPER = ("category", "spend_area", "month", "line_value_quartile", "vendor_activity_quartile")
CLASS_ORDER = ("D1 class (absent receipt)", "D2 class (stale receipt)", "D3", "D4", "D5", "D6", "D7",
               "at least one defect")


# ------------------------------------------------------------------ sources

_cache: dict[str, Any] = {}


def load(source: str) -> Any:
    if source not in _cache:
        if source == "@datalock":
            _cache[source] = tomllib.loads((ROOT / "prereg" / "data.lock").read_text(encoding="utf-8"))
        elif source == "@claims":
            rows = {}
            for line in (ROOT / "CLAIMS.md").read_text(encoding="utf-8").splitlines():
                m = re.match(r"^\| (C\d+) \| (.*) \| ([^|]*) \| ([^|]*) \| ([^|]*) \|$", line)
                if m:
                    rows[m.group(1)] = {"claim": m.group(2).strip(), "type": m.group(3).strip(),
                                        "status": m.group(4).strip(), "evidence": m.group(5).strip()}
            _cache[source] = rows
        elif source == "@citations":
            cites = json.loads((ROOT / "verified-citations.json").read_text(encoding="utf-8"))["citations"]
            _cache[source] = {c["id"]: c for c in cites}
        else:
            _cache[source] = json.loads((RESULTS / source).read_text(encoding="utf-8"))
    return _cache[source]


def walk(obj: Any, keys: list[str]) -> Any:
    for k in keys:
        obj = obj[int(k)] if isinstance(obj, list) else obj[k]
    return obj


# ------------------------------------------------------------------ formats

def _p(v: float) -> str:
    if v >= 0.9995:
        return "1"
    if v >= 0.001:
        return f"{v:.3g}"
    mant, exp = f"{v:.2e}".split("e")
    return f"{mant} × 10^{int(exp)}^"


FORMATS: dict[str, Callable[[Any], str]] = {
    "int": lambda v: f"{int(v):,}",
    "pct": lambda v: f"{100 * v:.2f}%",
    "pct1": lambda v: f"{100 * v:.1f}%",
    "prop": lambda v: f"{v:.4f}",
    "prop3": lambda v: f"{v:.3f}",
    "p": _p,
    "eur": lambda v: f"{v:,.0f}",
    "usd": lambda v: f"{v:.2f}",
    "usd4": lambda v: f"{v:.4f}",
    "usd6": lambda v: f"{v:.6f}",
    "f6": lambda v: f"{v:.6f}",
    "iv": lambda v: f"[{v[0]:.4f}, {v[1]:.4f}]",
    "ivpct": lambda v: f"[{100 * v[0]:.2f}%, {100 * v[1]:.2f}%]",
    "sec": lambda v: f"{v:.1f}",
    "str": lambda v: str(v),
    "date": lambda v: str(v)[:10],
}


def fmt(value: Any, f: str) -> str:
    if value is None:
        return "n/a"
    return FORMATS[f](value)


# ------------------------------------------------------------------ citations

def cite_text(cid: str) -> str:
    c = load("@citations")[cid]
    authors = c.get("authors") or [c.get("first_author") or ""]
    surname = lambda a: a.split()[-1] if a else ""  # noqa: E731
    if cid.startswith("icpm-"):
        who = "ICPM"
    elif cid.startswith("pcaob-"):
        who = "PCAOB"
    elif len(authors) == 1:
        who = authors[0] if " " not in authors[0] else surname(authors[0])
        if c["first_author"] == "Wil van der Aalst":
            who = "van der Aalst"
    elif len(authors) == 2:
        who = f"{surname(authors[0])} and {surname(authors[1])}"
    else:
        first = authors[0]
        who = ("Meyer zu Wickern" if "Meyer zu Wickern" in first else surname(first)) + " et al."
    return f"{who} {c['year']}"


# ------------------------------------------------------------------ blocks


def _row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def block_exclusions() -> tuple[str, list[str]]:
    ex = load("e1/exclusions.json")
    rows = [_row(["step", "lines"]), _row(["---", "---:"]), _row(["lines in the log", fmt(ex["lines_in_log"], "int")])]
    for r in ex["exclusions_in_registered_order"]:
        rows.append(_row([r["registered_step"], fmt(r["lines"], "int")]))
    rows += [_row(["framed lines", fmt(ex["framed_lines"], "int")]),
             _row(["E0 pilot lines removed", fmt(ex["e0_lines_removed"], "int")]),
             _row(["framed lines analysed", fmt(ex["framed_lines_after_e0_removal"], "int")]),
             _row(["analysed clearings", fmt(ex["analysed_clearings"], "int")]),
             _row(["events after T_end excluded", fmt(ex["events_after_t_end_excluded"], "int")])]
    return "\n".join(rows), ["e1/exclusions.json"]


def block_exposure() -> tuple[str, list[str]]:
    e = load("e1/exposure.json")
    rows = [_row(["defect class", "clearings", "share", "Wilson 95%", "bootstrap 95%", "share of value", "bootstrap 95%"]),
            _row(["---", "---:", "---:", "---", "---", "---:", "---"])]
    for name in CLASS_ORDER:
        c = e["classes"][name]
        rows.append(_row([name, fmt(c["clearings"], "int"), fmt(c["share_of_clearings"], "pct"),
                          fmt(c["wilson95"], "ivpct"), fmt(c["bootstrap95"], "ivpct"),
                          fmt(c["share_of_value"], "pct"), fmt(c["value_bootstrap95"], "ivpct")]))
    h = e["held unknown"]
    rows.append(_row(["held on an unknown only (not a defect)", fmt(h["clearings"], "int"),
                      fmt(h["share_of_clearings"], "pct"), fmt(h["wilson95"], "ivpct"), fmt(h["bootstrap95"], "ivpct"),
                      fmt(h["share_of_value"], "pct"), fmt(h["value_bootstrap95"], "ivpct")]))
    return "\n".join(rows), ["e1/exposure.json"]


def block_hypotheses() -> tuple[str, list[str]]:
    h = load("e2/hypotheses.json")
    holm = {r["test"]: r for r in h["holm"]["table"]}
    rows = [_row(["test", "defect group (failed predicate): O rate", "comparison: O rate", "difference", "bootstrap SE", "z",
                  "p (raw, one-sided)", "p (Holm)"]),
            _row(["---", "---", "---", "---:", "---:", "---:", "---:", "---:"])]
    for name in ("H1", "H2", "H3"):
        w = h["estimates"][name]["W60"]
        d, c = w["defect_group"], w["comparison_group"]
        rows.append(_row([
            name, f"{fmt(d['with_O'], 'int')} of {fmt(d['clearings'], 'int')} ({fmt(d['O_rate'], 'pct')})",
            f"{fmt(c['with_O'], 'int')} of {fmt(c['clearings'], 'int')} ({fmt(c['O_rate'], 'pct')})",
            fmt(w["difference"], "prop"), fmt(w.get("bootstrap_se"), "prop"),
            fmt(w.get("z"), "prop3") if w.get("z") is not None else "n/a",
            fmt(w.get("p_one_sided_raw"), "p") if w.get("p_one_sided_raw") is not None else "not computable",
            fmt(holm[name]["p_holm"], "p")]))
    return "\n".join(rows), ["e2/hypotheses.json"]


def block_holm() -> tuple[str, list[str]]:
    h = load("e2/hypotheses.json")["holm"]
    rows = [_row(["test", "p (raw)", "rank", "multiplier", "p (Holm)", "below alpha"]),
            _row(["---", "---:", "---:", "---:", "---:", "---"])]
    for r in h["table"]:
        rows.append(_row([r["test"], fmt(r["p_raw"], "p"), fmt(r["rank"], "int"), fmt(r["multiplier"], "int"),
                          fmt(r["p_holm"], "p"), "yes" if r["below_alpha"] else "no"]))
    return "\n".join(rows), ["e2/hypotheses.json"]


def block_two_by_two() -> tuple[str, list[str]]:
    t = load("e3/verdict-by-outcome.json")["table"]["W60"]
    rows = [_row(["gate verdict", "corrective within W", "no corrective within W"]), _row(["---", "---:", "---:"])]
    for verdict, label in (("hold", "would have held"), ("allow", "would have allowed")):
        a, b = t[f"{verdict}_with_corrective"], t[f"{verdict}_without_corrective"]
        rows.append(_row([label, f"{fmt(a['clearings'], 'int')} ({fmt(a['cleared_value_eur'], 'eur')})",
                          f"{fmt(b['clearings'], 'int')} ({fmt(b['cleared_value_eur'], 'eur')})"]))
    return "\n".join(rows), ["e3/verdict-by-outcome.json"]


def block_lag_bands() -> tuple[str, list[str]]:
    lag = load("e3/lag-bands.json")["bands"]
    labels = {"0-1": "[0, 1] days", "1-7": "(1, 7] days", "7-30": "(7, 30] days", "over 30": "over 30 days",
              "never": "never (by T_end)"}
    rows = [_row(["lag band", "clearings", "cleared value"]), _row(["---", "---:", "---:"])]
    for k, label in labels.items():
        rows.append(_row([label, fmt(lag[k]["clearings"], "int"), fmt(lag[k]["cleared_value_eur"], "eur")]))
    return "\n".join(rows), ["e3/lag-bands.json"]


def block_human_hold() -> tuple[str, list[str]]:
    hh = load("e3/human-hold.json")
    rows = [_row(["reading", "predicate status at t*", "classified lines", "held by people", "human hold rate"]),
            _row(["---", "---", "---:", "---:", "---:"])]
    for key, label in (("registered_literal_reading", "literal (registered text)"),
                       ("amended_reading_D-C-2", "amended (D-C-2 B)")):
        rates = hh[key]["by_gate_status_at_t_star"]
        for s in ("defective", "clean", "held_unknown"):
            r = rates[s]
            rows.append(_row([label, s.replace("_", " "), fmt(r["classified_lines"], "int"),
                              fmt(r["held_by_people"], "int"), fmt(r["human_hold_rate"], "pct")]))
    return "\n".join(rows), ["e3/human-hold.json"]


def block_arms() -> tuple[str, list[str]]:
    h4 = load("e4/h4.json")["families"]
    rows = _arms_rows(load("e4/arms.json")["arms"])
    rows.append("")
    rows.append(_row(["family", "d (failed predicate minus clean)", "SE", "p, lower", "p, upper", "p_TOST"]))
    rows.append(_row(["---", "---:", "---:", "---:", "---:", "---:"]))
    for key in ("H4-Jev", "H4-Haiku"):
        x = h4[key]
        rows.append(_row([key, fmt(x["d"], "prop3"), fmt(x["se"], "prop"), fmt(x["p_lower"], "p"),
                          fmt(x["p_upper"], "p"), fmt(x["p_tost"], "p")]))
    rows += ["", "Source: `results/e4/arms.json`, `results/e4/h4.json`."]
    return "\n".join(rows), ["e4/arms.json", "e4/h4.json"]


def block_exploratory() -> tuple[str, list[str]]:
    a = load("e4-exploratory/arms-exploratory.json")["arms"]
    rows = [_row(["family (timeline view, exploratory)", "held, lines with a failed predicate", "held, clean lines",
                  "kappa with gate", "invalid replies"]), _row(["---", "---:", "---:", "---:", "---:"])]
    for key, label in (("jev", "Jev"), ("haiku", "Haiku")):
        x = a[key]
        rows.append(_row([label,
                          f"{fmt(x['defective']['held'], 'int')} of {fmt(x['defective']['lines'], 'int')} ({fmt(x['hold_rate_defective'], 'pct1')})",
                          f"{fmt(x['clean']['held'], 'int')} of {fmt(x['clean']['lines'], 'int')} ({fmt(x['hold_rate_clean'], 'pct1')})",
                          fmt(x["kappa_with_gate"], "prop3"), fmt(x["invalid"], "int")]))
    rows += ["", "Source: `results/e4-exploratory/arms-exploratory.json`; exploratory, no interval, outside the Holm family."]
    return "\n".join(rows), ["e4-exploratory/arms-exploratory.json"]


def _arms_rows(a: dict) -> list[str]:
    rows = [_row(["arm", "held, lines with a failed predicate", "held, clean lines", "kappa with gate",
                  "value released on lines with a failed predicate", "expected correctives"]),
            _row(["---", "---:", "---:", "---:", "---:", "---:"])]
    for key, label in (("people", "people (from the log)"), ("jev", "Jev"), ("haiku", "Haiku"), ("gate", "gate")):
        x = a[key]
        rows.append(_row([label,
                          f"{fmt(x['defective']['held'], 'int')} of {fmt(x['defective']['lines'], 'int')} ({fmt(x['hold_rate_defective'], 'pct1')})",
                          f"{fmt(x['clean']['held'], 'int')} of {fmt(x['clean']['lines'], 'int')} ({fmt(x['hold_rate_clean'], 'pct1')})",
                          fmt(x.get("kappa_with_gate"), "prop3") if x.get("kappa_with_gate") is not None else "n/a",
                          fmt(x["value_released_on_defective_lines_eur"], "eur"),
                          fmt(x["expected_correctives"], "prop3")]))
    return rows


def block_arms_classified() -> tuple[str, list[str]]:
    d = load("e4/arms-classified-lines.json")
    rows = _arms_rows(d["arms"])
    rows += ["", "Source: `results/e4/arms-classified-lines.json`; a re-tabulation on the lines the people arm classifies."]
    return "\n".join(rows), ["e4/arms-classified-lines.json"]


def block_hold_composition() -> tuple[str, list[str]]:
    c = load("e3/human-hold-composition.json")
    rows = [_row(["reading", "predicate status at t*", "held by people", "payment block before the first clearing",
                  "no clearing within W of the first invoice", "both"]),
            _row(["---", "---", "---:", "---:", "---:", "---:"])]
    for key, label in (("registered_literal_reading", "literal (registered text)"), ("amended_reading_D-C-2", "amended (D-C-2 B)")):
        for s in ("defective", "clean", "held_unknown"):
            x = c["by_status"][key][s]
            rows.append(_row([label, s.replace("_", " "), fmt(x["held_by_people"], "int"),
                              fmt(x["payment_block_before_first_clearing"], "int"),
                              fmt(x["no_clearing_within_W_of_first_invoice"], "int"), fmt(x["both"], "int")]))
    rows += ["", "Source: `results/e3/human-hold-composition.json`."]
    return "\n".join(rows), ["e3/human-hold-composition.json"]


def block_coverage_status() -> tuple[str, list[str]]:
    cov = load("e1/coverage-check.json")
    pred = load("e7/predicates.json")["counts"]
    rows = [_row(["log", "predicate", "failed", "unknown"]), _row(["---", "---", "---:", "---:"])]
    for r in cov["rows"]:
        rows.append(_row(["BPI 2019 (analysed clearings)", r["predicate"], fmt(r["failed_clearings"], "int"), "n/a"]))
    for log in ("domestic", "international"):
        for d in ("D1'", "D2'", "D3'"):
            x = pred[log][d]
            rows.append(_row([f"BPI 2020 {log} (payments)", d, fmt(x["fail"], "int"), fmt(x["unknown"], "int")]))
    rows += ["", "Sources: `results/e1/coverage-check.json`, `results/e7/predicates.json`."]
    return "\n".join(rows), ["e1/coverage-check.json", "e7/predicates.json"]


def block_e5() -> tuple[str, list[str]]:
    d = load("e5/derivation.json")["categories"]
    rows = [_row(["category", "clearings", "states", "L1", "L2", "L3", "fewest fields", "derived contract",
                  "registered contract", "result"]),
            _row(["---", "---:", "---:", "---:", "---:", "---:", "---", "---", "---", "---"])]
    for cat, s in d.items():
        loss = s["clearings_per_loss"]
        rows.append(_row([cat, fmt(s["analysed_clearings"], "int"), fmt(s["distinct_states"], "int"),
                          fmt(loss["L1"], "int"), fmt(loss["L2"], "int"), fmt(loss["L3"], "int"),
                          ", ".join(f"`{f}`" for f in s["minimum_cardinality_field_set"]),
                          ", ".join(s["derived_contract"]) or "none", ", ".join(s["registered_contract"]), s["result"]]))
    return "\n".join(rows), ["e5/derivation.json"]


def block_e7() -> tuple[str, list[str]]:
    u = load("e7/units.json")["logs"]
    c = load("e7/comparisons.json")["scopes"]
    rows = [_row(["log", "cases", "payments", "excluded after T_end' − W", "units"]), _row(["---", "---:", "---:", "---:", "---:"])]
    for log in ("domestic", "international"):
        x = u[log]
        rows.append(_row([log, fmt(x["cases"], "int"), fmt(x["payments_in_log"], "int"),
                          fmt(x["excluded_payments_after_t_end_prime_minus_w"], "int"), fmt(x["units"], "int")]))
    rows += ["", _row(["scope", "predicate", "failing payments", "O' rate, failing", "O' rate, all-pass", "difference",
                       "bootstrap 95%"]), _row(["---", "---", "---:", "---:", "---:", "---:", "---"])]
    for scope in ("domestic", "international", "pooled"):
        for d in ("D1'", "D2'", "D3'"):
            x = c[scope][d]
            rows.append(_row([scope, d, fmt(x["defect_group"]["payments"], "int"),
                              fmt(x["defect_group"]["O_prime_rate"], "prop3"),
                              fmt(x["all_pass_group"]["O_prime_rate"], "prop3"), fmt(x["difference"], "prop3"),
                              fmt(x["bootstrap95"], "iv")]))
    return "\n".join(rows), ["e7/units.json", "e7/comparisons.json"]


def block_coverage() -> tuple[str, list[str]]:
    text = (ROOT / "COVERAGE.md").read_text(encoding="utf-8")
    parts = []
    for heading in ("## Detected (BPI 2019, E1 to E6)", "## Detected (BPI 2020 declarations, E7, secondary)",
                    "## Undetected, with reason"):
        section = text.split(heading, 1)[1].split("\n## ", 1)[0]
        table = "\n".join(l for l in section.splitlines() if l.startswith("|"))
        parts.append(f"**{heading[3:]}**\n\n{table}")
    return "\n\n".join(parts), ["COVERAGE.md"]


def block_deviations() -> tuple[str, list[str]]:
    text = (ROOT / "prereg" / "DEVIATIONS.md").read_text(encoding="utf-8")
    items = []
    v1 = text.split("## p7-v1 to p7-v1.1", 1)[1].split("\n## ", 1)[0]
    for m in re.finditer(r"^\d+\. \*\*(.+?)\*\*", v1, re.MULTILINE):
        items.append(f"- p7-v1 to p7-v1.1: {m.group(1).rstrip('.')}.")
    under = text.split("## Under p7-v1.1", 1)[1]
    for m in re.finditer(r"^### (.+?) \(", under, re.MULTILINE):
        items.append(f"- Under p7-v1.1: {m.group(1)}.")
    return "\n".join(items), ["prereg/DEVIATIONS.md"]


def block_claims() -> tuple[str, list[str]]:
    rows = [_row(["claim", "status", "evidence"]), _row(["---", "---", "---"])]
    for cid, r in load("@claims").items():
        rows.append(_row([cid, r["status"], r["evidence"]]))
    return "\n".join(rows), ["CLAIMS.md"]


def block_strata() -> tuple[str, list[str]]:
    s = load("e1/exposure-by-stratum.json")
    titles = {"category": "Item category", "spend_area": "Spend area", "month": "Month of the clearing",
              "line_value_quartile": "Line value quartile", "vendor_activity_quartile": "Vendor activity quartile"}
    parts = []
    for var in STRATA_IN_PAPER:
        rows = [_row(["stratum", "defect class (failed predicate)", "clearings", "share", "clustered 95%",
                      "share of value", "clustered 95%"]),
                _row(["---", "---", "---:", "---:", "---", "---:", "---"])]
        for label, cell in s["strata"][var].items():
            for name in CLASS_ORDER:
                c = cell["classes"][name]
                if c["clearings"] == 0 and name != "at least one defect":
                    continue
                rows.append(_row([label, name, f"{fmt(c['clearings'], 'int')} of {fmt(cell['analysed_clearings'], 'int')}",
                                  fmt(c["share_of_clearings"], "pct"), fmt(c["bootstrap95"], "ivpct"),
                                  fmt(c["share_of_value"], "pct"), fmt(c["value_bootstrap95"], "ivpct")]))
        parts.append(f"**{titles[var]}**\n\n" + "\n".join(rows))
    return "\n\n".join(parts), ["e1/exposure-by-stratum.json"]


def block_registered_numbers() -> tuple[str, list[str]]:
    text = (ROOT / "prereg" / "p7-v1.1.md").read_text(encoding="utf-8")
    section = text.split("## 9. Registered numbers", 1)[1].split("\n## ", 1)[0]
    table = "\n".join(l for l in section.splitlines() if l.startswith("|"))
    return table, ["prereg/p7-v1.1.md section 9"]


def block_datasets() -> tuple[str, list[str]]:
    lock = load("@datalock")
    rows = [_row(["record", "DOI", "licence", "file", "cases", "events", "SHA-256"]),
            _row(["---", "---", "---", "---", "---:", "---:", "---"])]
    for key in ("bpi2019", "bpi2020_international", "bpi2020_domestic"):
        x = lock[key]
        rows.append(_row([x["title"], f"doi:{x['doi']}", x["licence"], f"`{x['file']}`", fmt(x["cases"], "int"),
                          fmt(x["events"], "int"), f"`{x['sha256']}`"]))
    return "\n".join(rows), ["prereg/data.lock"]


BLOCKS: dict[str, Callable[[], tuple[str, list[str]]]] = {
    "exclusions": block_exclusions, "exposure": block_exposure, "hypotheses": block_hypotheses,
    "holm": block_holm, "two_by_two": block_two_by_two, "lag_bands": block_lag_bands,
    "human_hold": block_human_hold, "arms": block_arms, "exploratory": block_exploratory,
    "e5": block_e5, "e7": block_e7, "coverage": block_coverage, "deviations": block_deviations,
    "claims": block_claims, "strata": block_strata, "registered_numbers": block_registered_numbers,
    "datasets": block_datasets, "arms_classified": block_arms_classified,
    "hold_composition": block_hold_composition, "coverage_status": block_coverage_status,
}


def references(cited: list[str]) -> str:
    cites = load("@citations")
    lock = load("@datalock")
    entries = []
    for cid in sorted(set(cited), key=lambda c: (cite_text(c).lower(), c)):
        c = cites[cid]
        if c["status"] != "verified":
            raise SystemExit(f"citation {cid} is not verified")
        authors = ", ".join(c.get("authors") or [c.get("first_author") or ""])
        loc = f"doi:{c['doi']}" if c.get("doi") else (c.get("url") or "")
        venue = f" {c['venue']}." if c.get("venue") else ""
        entries.append(f"- <!-- ref:{cid} -->{authors} ({c['year']}). {c['title']}.{venue} {loc}")
    for key in ("bpi2019", "bpi2020_international", "bpi2020_domestic"):
        x = lock[key]
        entries.append(f"- Boudewijn van Dongen. {x['title']}. 4TU.ResearchData, {x['licence']}. doi:{x['doi']}")
    return "\n".join(entries)


# ------------------------------------------------------------------ fill


def fill(template: str) -> tuple[str, dict[str, Any]]:
    out: list[str] = []
    records: list[dict[str, Any]] = []
    pos = 0
    cited: list[str] = []
    length = 0
    refs_marker = None

    for m in PLACEHOLDER.finditer(template):
        literal = template[pos:m.start()]
        out.append(literal)
        length += len(literal)
        body = m.group(1).strip()
        if body == "#references":
            refs_marker = (len(out), length)
            out.append("")
            pos = m.end()
            continue
        if body.startswith("#"):
            text, sources = BLOCKS[body[1:]]()
            rec = {"placeholder": body, "kind": "block", "sources": sources}
        else:
            spec, _, f = body.partition("|")
            source, *keys = spec.split(">")
            if source == "@cite":
                text = cite_text(keys[0])
                cited.append(keys[0])
                rec = {"placeholder": body, "kind": "citation", "source": "verified-citations.json", "key": keys[0]}
            else:
                value = walk(load(source), keys)
                text = fmt(value, f or "str")
                rec = {"placeholder": body, "kind": "value", "source": source if source.startswith("@")
                       else f"results/{source}", "key": keys, "value": value}
        rec.update({"text": text, "start": length, "end": length + len(text)})
        records.append(rec)
        out.append(text)
        length += len(text)
        pos = m.end()
    tail = template[pos:]
    out.append(tail)

    if refs_marker is not None:
        idx, start = refs_marker
        refs = references(cited)
        out[idx] = refs
        shift = len(refs)
        for r in records:
            if r["start"] >= start:
                r["start"] += shift
                r["end"] += shift
        records.append({"placeholder": "#references", "kind": "block", "sources": ["verified-citations.json",
                        "prereg/data.lock"], "text": refs, "start": start, "end": start + shift})
        records.sort(key=lambda r: r["start"])
    paper = "".join(out)
    filled = {
        "template": "paper/template.md",
        "template_sha256": hashlib.sha256(template.encode("utf-8")).hexdigest(),
        "paper": "paper/paper.md",
        "paper_sha256": hashlib.sha256(paper.encode("utf-8")).hexdigest(),
        "placeholders": records,
        "spans": [{"start": r["start"], "end": r["end"]} for r in records],
    }
    return paper, filled


def run(template: Path = TEMPLATE, out_paper: Path = PAPER, out_filled: Path = FILLED) -> dict[str, Any]:
    _cache.clear()
    paper, filled = fill(template.read_text(encoding="utf-8"))
    out_paper.parent.mkdir(parents=True, exist_ok=True)
    out_filled.parent.mkdir(parents=True, exist_ok=True)
    out_paper.write_text(paper, encoding="utf-8")
    out_filled.write_text(json.dumps(filled, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return filled


def main() -> int:
    filled = run()
    words = len(re.findall(r"\S+", PAPER.read_text(encoding="utf-8")))
    print(f"fill_paper: {len(filled['placeholders'])} placeholders filled; {words} words in paper/paper.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
