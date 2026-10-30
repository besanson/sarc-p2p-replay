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

import json
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
    out.write_text(_layout(out.read_text(encoding="utf-8")), encoding="utf-8")


# Layout only (D-E-0): no word of the paper changes. Tables are set smaller with narrower column gaps;
# long unbroken strings in table cells (hashes, DOIs, file names, identifiers) may break anywhere;
# bare URLs become \url, which xurl (loaded by pandoc's template) breaks anywhere.
TABLE_SETUP = ("\\usepackage{seqsplit}\n"
               "\\AtBeginEnvironment{longtable}{\\footnotesize\\setlength{\\tabcolsep}{3pt}}\n")
LONG_TOKEN = re.compile(r"(?<!\S)([A-Za-z0-9][^\s\\{}&]{17,}[^\s\\{}&.,;)])")
TEXTTT = re.compile(r"(\\texttt\{[^{}]*\})")


def _cells(body: str) -> str:
    parts = TEXTTT.split(body)
    for i, part in enumerate(parts):
        if i % 2:  # a \texttt{...} group: its content may break anywhere when long
            parts[i] = re.sub(r"\\texttt\{([^{}\s]{12,})\}", r"\\texttt{\\seqsplit{\1}}", part)
        else:
            parts[i] = LONG_TOKEN.sub(r"\\seqsplit{\1}", part)
    return "".join(parts)


def _layout(tex: str) -> str:
    tex = tex.replace("\\begin{document}", TABLE_SETUP + "\\begin{document}", 1)
    # The affiliation as a footnote on the author's name, not beside it; the PDF metadata carries the name only.
    tex = re.sub(r"\\author\{([^,{}]+), ([^{}]+)\}", r"\\author{\1\\thanks{\2}}", tex, count=1)
    tex = re.sub(r"pdfauthor=\{([^,{}]+), [^{}]+\}", r"pdfauthor={\1}", tex, count=1)
    tex = re.sub(r"(\\begin\{longtable\}.*?\\endlastfoot)(.*?)(\\end\{longtable\})",
                 lambda m: m.group(1) + _cells(m.group(2)) + m.group(3), tex, flags=re.DOTALL)
    return re.sub(r"(?<![{\w])(https?://[^\s}]+)", r"\\url{\1}", tex)


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


OVERFULL = ROOT / "out" / "paper-tex" / "overfull.json"


def _record_overfull(log: str) -> None:
    widths = [float(w) for w in re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)", log)]
    OVERFULL.parent.mkdir(parents=True, exist_ok=True)
    OVERFULL.write_text(json.dumps({"overfull_hboxes": len(widths),
                                    "overfull_hboxes_over_10pt": sum(w > 10 for w in widths),
                                    "widest_pt": max(widths, default=0.0)}, indent=2) + "\n", encoding="utf-8")


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
        _record_overfull((Path(tmp) / "main.log").read_text(encoding="latin-1"))
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
