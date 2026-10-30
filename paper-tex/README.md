# paper-tex/

The typeset paper, generated, never edited by hand: `make paper` writes `main.tex` from
`paper/paper.md` with pandoc and builds `main.pdf` with the first LaTeX engine installed
(tectonic, latexmk, pdflatex, xelatex; `make bootstrap-paper` lists what is present).

| file | holds |
|---|---|
| `main.tex` | pandoc's standalone LaTeX of `paper/paper.md`; figures are the PDF twins in `paper/figures/` |
| `main.pdf` | the PDF, built with pdflatex (two runs) |

The build is deterministic: pdfTeX writes no creation or modification date, no trailer id and no
pdfTeX info entry (`\pdfinfoomitdate=1\pdftrailerid{}\pdfsuppressptexinfo=-1`), and
`SOURCE_DATE_EPOCH` is the commit date of the last change to `paper/paper.md`. Two builds give the
same bytes; gate G9 rebuilds twice and compares both with the committed `main.pdf`. The bytes
depend on the TeX installation; the committed PDF was built with TeX Live 2023 (Debian packages
below, pdfTeX 1.40.25).

To build on another machine (Debian or Ubuntu):

```
sudo apt-get install --no-install-recommends texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended lmodern pandoc
make paper
```
