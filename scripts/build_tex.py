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

import os
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


MAIN_PDF = TEX_DIR / "main.pdf"
# pdfTeX: no creation or modification date, no trailer id, no pdfTeX info dictionary entry, so that
# the PDF depends only on main.tex, the figures and the TeX installation (Phase E, D-E-1).
DETERMINISTIC = r"\pdfinfoomitdate=1\pdftrailerid{}\pdfsuppressptexinfo=-1\input{main.tex}"


def source_date_epoch() -> str:
    """The commit date of the last commit that changed paper/paper.md (the source of main.tex)."""
    r = subprocess.run(["git", "log", "-1", "--format=%ct", "--", "paper/paper.md"], cwd=ROOT, capture_output=True,
                       text=True)
    return r.stdout.strip() or "0"


def build_pdf(engine: str, out: Path = MAIN_PDF) -> bool:
    """Build main.pdf into `out`; aux files stay in a temporary directory. pdflatex runs twice (tables, refs)."""
    with tempfile.TemporaryDirectory() as tmp:
        if engine == "pdflatex":
            cmds = [["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory", tmp,
                     "-jobname", "main", DETERMINISTIC]] * 2
        else:
            cmds = [{"tectonic": ["tectonic", "--outdir", tmp, "main.tex"],
                     "latexmk": ["latexmk", "-pdf", "-interaction=nonstopmode", f"-outdir={tmp}", "main.tex"],
                     "xelatex": ["xelatex", "-interaction=nonstopmode", "-output-directory", tmp, "main.tex"]}[engine]]
        env = {**os.environ, "SOURCE_DATE_EPOCH": source_date_epoch(), "FORCE_SOURCE_DATE": "1"}
        for cmd in cmds:
            r = subprocess.run(cmd, cwd=TEX_DIR, capture_output=True, text=True, env=env)
            if r.returncode != 0:
                return False
        built = Path(tmp) / "main.pdf"
        if not built.exists():
            return False
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(built, out)
    return True


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
