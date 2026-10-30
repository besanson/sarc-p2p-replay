r"""Typed-numeral lint for the paper (FINAL-AUDIT item 5).

Ported from paper 5's checkers/typed_numerals_lint.py (sarc-authority-derivation, pinned in
engines.lock): every numeral in the paper's prose must be filled from a slot, never typed by
hand, except a declared, narrow allowlist. The strip-then-allowlist design is paper 5's; what
counts as "filled" differs. Paper 5 marks filled values in the draft itself
(`[GENERATED: ...]`); here the paper is generated from `paper/template.md` by
`scripts/fill_paper.py`, so the lint checks:

- the template: every numeral outside a `{{...}}` placeholder (the template is where a
  hand-typed number would be written);
- the generated paper: every numeral outside the spans the filler recorded in
  `paper/filled-template.json` (so a hand edit of `paper/paper.md` is caught too).

Stripped before the allowlist: filled spans or placeholders; inline code and fenced code
(identifiers, model and package names, file paths); bare URLs and DOIs; HTML comments; double-quoted
spans on one line (a direct quotation, as paper 5 strips them).

Allowlist, applied to what remains:
1. Structure: Section, Figure, Table, Appendix, paper N, Phase, markdown heading numbers and
   ordered-list ordinals.
2. Years (1900 to 2099) and full dates.
3. Identifiers in the house style: D1 to D7, D1' to D3', C1 to C13, H1 to H4, E0 to E7, L1 to
   L3, G1 to G9, CMF 3 style ids (letters plus digits, optional prime), and H4-Jev, H4-Haiku.
4. Tag and version names (`p7-v1.1`, `v0.1`), category names (`3-way`, `2-way`) and the
   table name `2 x 2`.
5. Registered constants, by literal value, each citing the registration section that fixes it
   (REGISTERED below). A different bare numeral is still caught.

Usage: python -m lint.typed_numerals [--template paper/template.md] [--paper paper/paper.md]
Writes out/lint/typed_numerals.json; exits 1 on any violation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Pattern

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "paper" / "template.md"
PAPER = ROOT / "paper" / "paper.md"
FILLED = ROOT / "paper" / "filled-template.json"
OUTPUT_PATH = ROOT / "out" / "lint" / "typed_numerals.json"

_MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"

# Registered constants: literal text -> where the registration fixes it.
REGISTERED: dict[str, str] = {
    r"\b60 days\b": "prereg/p7-v1.1.md section 9 (W)",
    r"\b30 days\b": "prereg/p7-v1.1.md section 9 (W sensitivity)",
    r"W = 60\b": "prereg/p7-v1.1.md section 9 (W)",
    r"W = 30\b": "prereg/p7-v1.1.md section 9 (W sensitivity)",
    r"\[0, 1\]": "prereg/p7-v1.1.md section 9 (lag band; also the probability range of section 7)",
    r"\(1, 7\]": "prereg/p7-v1.1.md section 9 (lag band)",
    r"\(7, 30\]": "prereg/p7-v1.1.md section 9 (lag band)",
    r"\bover 30 days\b": "prereg/p7-v1.1.md section 9 (lag band)",
    r"\bK = 12\b": "prereg/p7-v1.1.md section 9 (K)",
    r"\bmore than 12 clearings\b": "prereg/p7-v1.1.md section 9 (K)",
    r"\b500 (?:E0 )?lines\b": "prereg/p7-v1.1.md section 9 (E0)",
    r"\bN_d = 1,000\b": "prereg/p7-v1.1.md section 9 (E4)",
    r"\bN_c = 1,000\b": "prereg/p7-v1.1.md section 9 (E4)",
    r"\b1,000 defective and 1,000 clean\b": "prereg/p7-v1.1.md section 9 (E4)",
    r"\bm = 0\.05\b": "prereg/p7-v1.1.md section 9 (E4 margin)",
    r"\b(?:alpha|α) = 0\.05\b": "prereg/p7-v1.1.md section 9 (alpha)",
    r"\bB = 10,000\b": "prereg/p7-v1.1.md section 9 (bootstrap)",
    r"\b20261201\b": "prereg/p7-v1.1.md section 9 (seed)",
    r"\bUSD 60\b": "prereg/p7-v1.1.md section 9 (cap)",
    r"\b1,000 events\b": "prereg/p7-v1.1.md section 2 (observation end threshold)",
    r"\b95%": "prereg/p7-v1.1.md section 5 (interval level)",
    r"\b1,000-record\b": "prereg/p7-v1.1.md section 3.9 (evidence-set sample export)",
    r"\bfive tests\b": "prereg/p7-v1.1.md section 4 (Holm family)",
    r"\bCC BY(?:-NC)? 4\.0\b": "prereg/p7-v1.1.md section Data (licences as the record pages state them)",
    r"\bSHA-256\b": "hash algorithm name",
    r"\bO'? = 1\b": "prereg/p7-v1.1.md sections 3.7 and 8 (definition of the outcome proxy)",
    r"\bp = 1\b": "prereg/DEVIATIONS.md, H3 convention (the p-value H3 enters Holm with)",
}

_STRIP_URLS: list[Pattern] = [
    re.compile(r"<!--.*?-->", re.DOTALL),
    re.compile(r"```.*?```", re.DOTALL),
    re.compile(r"`[^`\n]*`"),
    re.compile(r"https?://\S+"),
    re.compile(r"\bdoi:\s*\S+"),
    re.compile(r"\b10\.\d{4,9}/\S+"),
    re.compile(r"\]\([^)\s]*\)"),  # markdown link and image targets (file names, anchors)
    re.compile(r'"[^"\n]*"'),  # a direct quotation (as paper 5: quoted text is not the paper's own number)
]
_PLACEHOLDER = re.compile(r"\{\{.*?\}\}", re.DOTALL)

_ALLOWED: list[Pattern] = [
    re.compile(r"\b(?:[Ss]ections?|Figures?|Tables?|Appendix|Appendices|[Pp]aper|[Pp]apers|Phase)\s+"
               r"\d+(?:\.\d+)?(?:\s*(?:to|and|-)\s*\d+(?:\.\d+)?)?\b"),
    re.compile(r"^#+\s*\d+(?:\.\d+)*\.?\s", re.MULTILINE),
    re.compile(r"^\s*\d+\.\s", re.MULTILINE),
    re.compile(rf"\b\d{{1,2}}\s+(?:{_MONTHS})\s+(?:19|20)\d{{2}}\b"),
    re.compile(r"\b(?:19|20)\d{2}[a-z]?\b"),
    re.compile(r"\bH4-(?:Jev|Haiku)\b"),
    re.compile(r"\bD-[A-Z]+\d*-\d+[a-z]?\b"),  # decision ids (D-A1-1, D-C-2)
    re.compile(r"\b[A-Z]{1,3}\d{1,2}'?(?!\d|[.,]\d)"),
    re.compile(r"\bp7-v\d+(?:\.\d+)?\b"),
    re.compile(r"\bv\d+(?:\.\d+){0,2}\b"),
    re.compile(r"\b[23]-way\b"),
    re.compile(r"\b2 x 2\b"),
    re.compile(r"\b4TU\b"),
    # A registered constant may wrap across a line: its spaces match any whitespace.
    *[re.compile(p.replace(" ", r"\s+")) for p in REGISTERED],
]


def _blank(text: str, start: int, end: int) -> str:
    return text[:start] + "".join(c if c == "\n" else " " for c in text[start:end]) + text[end:]


def _redact(text: str, patterns: list[Pattern]) -> str:
    for pattern in patterns:
        text = pattern.sub(lambda m: "".join(c if c == "\n" else " " for c in m.group(0)), text)
    return text


def find_violations(text: str, filled_spans: list[tuple[int, int]] | None = None) -> list[dict[str, Any]]:
    redacted = text
    for start, end in filled_spans or []:
        redacted = _blank(redacted, start, end)
    redacted = _redact(redacted, [_PLACEHOLDER, *_STRIP_URLS])
    redacted = _redact(redacted, _ALLOWED)
    out = []
    for m in re.finditer(r"\S*\d\S*", redacted):
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", m.start())
        out.append({"line": text.count("\n", 0, m.start()) + 1, "token": text[m.start():m.end()],
                    "context": text[line_start:line_end if line_end != -1 else len(text)].strip()[:200]})
    return out


def run(template: Path = TEMPLATE, paper: Path = PAPER, filled: Path = FILLED) -> dict[str, Any]:
    result: dict[str, Any] = {"registered_allowlist": REGISTERED}
    if template.exists():
        v = find_violations(template.read_text(encoding="utf-8"))
        result["template"] = {"path": str(template.relative_to(ROOT)), "violations": v, "clean": not v}
    if paper.exists() and filled.exists():
        spans = [(s["start"], s["end"]) for s in json.loads(filled.read_text(encoding="utf-8"))["spans"]]
        v = find_violations(paper.read_text(encoding="utf-8"), spans)
        result["paper"] = {"path": str(paper.relative_to(ROOT)), "filled_spans": len(spans), "violations": v,
                           "clean": not v}
    # Before Phase D there is no paper to lint; that is not a violation.
    result["clean"] = all(result[k]["clean"] for k in ("template", "paper") if k in result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lint.typed_numerals")
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    parser.add_argument("--paper", type=Path, default=PAPER)
    parser.add_argument("--filled", type=Path, default=FILLED)
    args = parser.parse_args(argv)
    result = run(args.template, args.paper, args.filled)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for part in ("template", "paper"):
        if part in result:
            print(f"typed-numerals {part}: {len(result[part]['violations'])} violation(s)")
            for v in result[part]["violations"][:20]:
                print(f"  line {v['line']}: {v['token']!r}  {v['context'][:120]}")
    if "template" not in result and "paper" not in result:
        print("typed-numerals: no paper/template.md or paper/paper.md yet")
    return 0 if result["clean"] else 1


if __name__ == "__main__":
    sys.exit(main())
