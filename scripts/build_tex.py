"""paper-tex/main.tex from paper/paper.md, and the PDF when a LaTeX engine is installed.

As paper 5 (sarc-authority-derivation, paper-tex/): the typeset paper is generated from the
markdown source, never edited by hand. Here pandoc writes a standalone LaTeX file; figures are
referenced as the PDF versions in paper/figures/. Paper 5's canonical engine is Tectonic, with
latexmk as the supported alternative; this script uses the first of tectonic, latexmk, pdflatex,
xelatex that is installed. With none installed it writes main.tex and says so: the PDF waits for
an environment with a LaTeX engine.

Usage: python scripts/build_tex.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper" / "paper.md"
TEX_DIR = ROOT / "paper-tex"
MAIN_TEX = TEX_DIR / "main.tex"
ENGINES = ("tectonic", "latexmk", "pdflatex", "xelatex")


def _markdown_for_tex(text: str) -> str:
    # Figures: the PDF twin of each SVG, relative to paper-tex/.
    text = re.sub(r"\]\(figures/([^)]+)\.svg\)", r"](../paper/figures/\1.pdf)", text)
    # Scientific notation as LaTeX math, and the Unicode minus as a hyphen, so that every engine,
    # pdflatex included, typesets the file without extra Unicode declarations.
    text = re.sub(r"(\d(?:\.\d+)?) × 10\^(-?\d+)\^", r"$\1 \\times 10^{\2}$", text)
    return text.replace("\u2212", "-")


def write_tex(paper: Path = PAPER, out: Path = MAIN_TEX) -> None:
    if shutil.which("pandoc") is None:
        raise SystemExit("pandoc is not installed; see make bootstrap-paper")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "paper.md"
        src.write_text(_markdown_for_tex(paper.read_text(encoding="utf-8")), encoding="utf-8")
        subprocess.run(["pandoc", str(src), "--from", "markdown+superscript+pipe_tables+yaml_metadata_block",
                        "--to", "latex", "--standalone", "-V", "geometry:margin=2.5cm", "-V", "fontsize=10pt",
                        "-V", "colorlinks=true", "-o", str(out)], check=True)


def body_of(tex: str) -> str:
    m = re.search(r"\\begin\{document\}(.*)\\end\{document\}", tex, re.DOTALL)
    return m.group(1) if m else tex


def latex_engine() -> str | None:
    return next((e for e in ENGINES if shutil.which(e)), None)


def build_pdf(engine: str) -> bool:
    cmd = {"tectonic": ["tectonic", "main.tex"], "latexmk": ["latexmk", "-pdf", "-interaction=nonstopmode", "main.tex"],
           "pdflatex": ["pdflatex", "-interaction=nonstopmode", "main.tex"],
           "xelatex": ["xelatex", "-interaction=nonstopmode", "main.tex"]}[engine]
    r = subprocess.run(cmd, cwd=TEX_DIR, capture_output=True, text=True)
    return r.returncode == 0 and (TEX_DIR / "main.pdf").exists()


def main() -> int:
    write_tex()
    engine = latex_engine()
    if engine is None:
        print(f"build_tex: wrote {MAIN_TEX.relative_to(ROOT)}; no LaTeX engine ({', '.join(ENGINES)}) installed, "
              "so the PDF waits for an environment that has one")
        return 0
    ok = build_pdf(engine)
    print(f"build_tex: wrote {MAIN_TEX.relative_to(ROOT)}; PDF with {engine}: {'built' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
