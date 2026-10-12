"""Terminology lint for sarc-p2p-replay (brief section 6).

Conventions ported from paper 5's checkers/terminology_lint.py
(sarc-authority-derivation, pinned in engines.lock): paragraph scope (blank-line
delimited), fenced and inline code blanked before matching so identifiers are
never read as prose, and a negation local to the match (in the ~40 characters
immediately before it) rather than anywhere in the paragraph.

Rules, applied to live prose (README.md, paper/**/*.md, results/**/*.md):

  replay-not-simulation  "simulation", "simulate(d)" never describe this work;
                         the word is "replay". Allowed only under a local
                         negation ("a replay, not a simulation").
  defect-scope           "defect", "defects", "defective" only for a failed
                         predicate: the same paragraph must name a predicate
                         (D1 to D7, D1' to D3'), the word "predicate", or a
                         "defect class" / "Silent Evidence Defect".
  would-have-held-scope  "would have held" only for the gate verdict: the same
                         paragraph must contain "gate".
  banned                 "prevent*", "cause", "caused", "causes", "causing",
                         "causal*", "lost", "fraud*", "ready", "readiness" never
                         appear, except under a local negation ("no causal
                         claim", "not ready").

The registration documents (prereg/, CLAIMS.md, COVERAGE.md, NOVELTY.md,
DECISIONS.md) are not targets: they name these words in order to forbid them.

Usage: python -m lint.terminology [FILE ...]. Writes out/lint/terminology.json
and exits 1 if any target has a violation.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "out" / "lint" / "terminology.json"
TARGET_GLOBS = ("README.md", "paper/**/*.md", "results/**/*.md")
# Directory notes that only describe what a directory will hold.
EXEMPT = {"paper/README.md", "results/README.md"}

_FENCED = re.compile(r"```.*?```", re.DOTALL)
_INLINE = re.compile(r"`[^`\n]+`")
_NEGATION_LOCAL = re.compile(
    r"\b(?:not|never|no|nor|without|cannot|n't|neither|rather than|instead of)\b[^.;:]{0,40}$",
    re.IGNORECASE,
)

SIMULATION = re.compile(r"\bsimulat(?:ion|ions|e|ed|es|ing|or)\b", re.IGNORECASE)
DEFECT = re.compile(r"\bdefect(?:s|ive)?\b", re.IGNORECASE)
DEFECT_ANCHOR = re.compile(
    r"\bD[1-7]\b|\bD[1-3]'|\bpredicates?\b|\bdefect class(?:es)?\b|\bSilent Evidence Defects?\b",
    re.IGNORECASE,
)
WOULD_HAVE_HELD = re.compile(r"\bwould have held\b", re.IGNORECASE)
GATE = re.compile(r"\bgate\b", re.IGNORECASE)
BANNED = re.compile(
    r"\b(?:prevent\w*|cause|caused|causes|causing|causal\w*|lost|fraud\w*|ready|readiness)\b",
    re.IGNORECASE,
)


def _blank(match: re.Match[str]) -> str:
    return "".join(c if c == "\n" else " " for c in match.group(0))


def strip_code(text: str) -> str:
    """Blank fenced and inline code, keeping line numbers."""
    return _INLINE.sub(_blank, _FENCED.sub(_blank, text))


def _paragraphs(text: str) -> list[tuple[int, str]]:
    out, start = [], 0
    for m in re.finditer(r"\n[ \t]*\n", text):
        out.append((start, text[start : m.start()]))
        start = m.end()
    out.append((start, text[start:]))
    return out


def _negated(para: str, pos: int) -> bool:
    return bool(_NEGATION_LOCAL.search(para[max(0, pos - 60) : pos]))


def lint_text(text: str) -> list[dict[str, Any]]:
    stripped = strip_code(text)
    violations: list[dict[str, Any]] = []

    def add(rule: str, offset: int, para: str, word: str) -> None:
        violations.append({
            "rule": rule,
            "word": word,
            "line": stripped.count("\n", 0, offset) + 1,
            "excerpt": " ".join(para.split())[:200],
        })

    for start, para in _paragraphs(stripped):
        if not para.strip():
            continue
        for m in SIMULATION.finditer(para):
            if not _negated(para, m.start()):
                add("replay-not-simulation", start + m.start(), para, m.group(0))
        if DEFECT.search(para) and not DEFECT_ANCHOR.search(para):
            m = DEFECT.search(para)
            add("defect-scope", start + m.start(), para, m.group(0))
        if WOULD_HAVE_HELD.search(para) and not GATE.search(para):
            m = WOULD_HAVE_HELD.search(para)
            add("would-have-held-scope", start + m.start(), para, m.group(0))
        for m in BANNED.finditer(para):
            if not _negated(para, m.start()):
                add("banned", start + m.start(), para, m.group(0))
    return violations


def default_targets(root: Path = ROOT) -> list[Path]:
    paths: set[Path] = set()
    for pattern in TARGET_GLOBS:
        paths.update(p for p in root.glob(pattern) if p.is_file())
    return sorted(p for p in paths if p.relative_to(root).as_posix() not in EXEMPT)


def lint(paths: list[Path] | None = None) -> dict[str, Any]:
    paths = default_targets() if paths is None else paths
    files = []
    for path in paths:
        violations = lint_text(path.read_text(encoding="utf-8"))
        files.append({"path": str(path), "violations": violations, "clean": not violations})
    return {"files": files, "all_clean": all(f["clean"] for f in files)}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    result = lint([Path(a) for a in argv] if argv else None)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for f in result["files"]:
        for v in f["violations"]:
            print(f"{f['path']}:{v['line']}: {v['rule']}: '{v['word']}': {v['excerpt']}")
    print(f"terminology: {len(result['files'])} file(s), {'clean' if result['all_clean'] else 'violations found'}")
    return 0 if result["all_clean"] else 1


if __name__ == "__main__":
    sys.exit(main())
