"""PROOF-STATUS lint.

Ported from paper 5's checkers/proof_status_lint.py (sarc-authority-derivation,
pinned in engines.lock), which ports it from sarc-suite-one-pass. Changed only
in what counts as a verification source: here a property test module under
`tests/` (paper 7 claims no proposition; tags apply only to the replay
engine's property tests, prereg/p7-v1.md section 10).

ALLOWED is small and closed. "proven" is deliberately absent: clearing a tag to
proven is human-only, and its appearance in a linted file is a failure.

Every "machine-checked" tag's own paragraph (up to the next blank line) must
name a property test module (`tests/test_*.py`) and an enumerated domain (a
count, such as the number of generated cases).

Usage: python -m lint.proof_status [FILE ...]. Exit 1 on any violation.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = {"machine-checked", "pending-human-review", "checked-scope-only"}
TAG_PATTERN = re.compile(r"PROOF-STATUS:\s*([A-Za-z][A-Za-z \-]*[A-Za-z])")
SOURCE_PATTERN = re.compile(r"tests/test_[A-Za-z0-9_]+\.py")
DOMAIN_PATTERN = re.compile(r"\b\d{1,3}(?:,\d{3})*\b")
TARGET_GLOBS = ("tests/test_properties.py", "paper/**/*.md")


def find_tags(text: str) -> list[str]:
    return [m.group(1).strip() for m in TAG_PATTERN.finditer(text)]


def scope_violations(text: str) -> list[dict[str, Any]]:
    out = []
    for m in TAG_PATTERN.finditer(text):
        if m.group(1).strip() != "machine-checked":
            continue
        end = text.find("\n\n", m.start())
        scope = text[m.start() : len(text) if end == -1 else end]
        has_source = bool(SOURCE_PATTERN.search(scope))
        has_domain = bool(DOMAIN_PATTERN.search(scope))
        if not (has_source and has_domain):
            out.append({"excerpt": scope[:200], "has_source": has_source, "has_domain": has_domain})
    return out


def lint_text(text: str) -> dict[str, Any]:
    tags = find_tags(text)
    forbidden = sorted({t for t in tags if t not in ALLOWED})
    violations = scope_violations(text)
    return {"tags": tags, "forbidden": forbidden, "scope_violations": violations,
            "clean": not forbidden and not violations}


def default_targets(root: Path = ROOT) -> list[Path]:
    found: set[Path] = set()
    for pattern in TARGET_GLOBS:
        found.update(p for p in root.glob(pattern) if p.is_file())
    return sorted(found)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    paths = [Path(a) for a in argv] if argv else default_targets()
    files = [dict(path=str(p), **lint_text(p.read_text(encoding="utf-8"))) for p in paths]
    result = {"files": files, "total_tags": sum(len(f["tags"]) for f in files),
              "all_clean": all(f["clean"] for f in files)}
    out = ROOT / "out" / "lint" / "proof_status.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"proof-status: {result['total_tags']} tag(s) in {len(files)} file(s), "
          f"{'clean' if result['all_clean'] else 'violations found'}")
    return 0 if result["all_clean"] else 1


if __name__ == "__main__":
    sys.exit(main())
