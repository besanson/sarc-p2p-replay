"""`make reproduce`: regenerate every deterministic result of paper 7 and compare it with the committed files.

For an external reproducer (REPRODUCE.md). Everything is regenerated into out/reproduce/ from the three
logs in data/ (fetched by `make bootstrap`, SHA-256 checked against prereg/data.lock), the committed E4
model responses (no model is called) and paper 5's compiler at its engines.lock pin, in pipeline order:

  E0 run 2 (the pilot draw), E1 (with the regenerated E0 lines removed), E2, E3, the E4 sample draw and
  views, the E4 analyses (primary and exploratory) from the committed responses, E5, the E7 vocabulary
  check and replication, the E6 cost table (from the responses), the round-1, round-2 and round-3 slots;
  then the paper, filled from the regenerated slots: paper/paper.md, paper/filled-template.json, the
  README's generated blocks, the figures and paper-tex/main.tex.

Each regenerated file is compared by SHA-256 with the committed one. Every committed file under results/
is accounted for: compared, excluded as machine-dependent (MACHINE), or a verification record of an
earlier run that this reproduction replaces (RECORDS). paper-tex/main.pdf is built when a LaTeX engine is
installed and reported for information only: its bytes depend on the TeX installation.

Writes out/reproduce/report.md (the table and the verdict, for a GitHub issue) and prints the same.
Exit 0 when every compared file matches.

Usage: python scripts/reproduce.py
"""

from __future__ import annotations

import hashlib
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
OUT = ROOT / "out" / "reproduce"

# Machine-dependent records: excluded by name, never compared.
MACHINE = {
    "results/e0/run-2/e0-timing.json": "wall time of the E0 passes",
    "results/e6/timing-e1.json": "wall time and hardware of the E1 replay",
    "results/reproducibility.json": "run times of the internal double run",
    "results/ci-runs.json": "GitHub Actions runs",
    "results/package-smoke.json": "Python version of the smoke test",
    "results/gates-report.json": "gate report of the release machine",
    "results/data-check.json": "check of the data files on the release machine",
    "results/mutation.json": "mutation run (Phase B/C)",
    "results/mutation-release.json": "mutation run (release)",
}
# Verification records of earlier runs (byte comparisons, superseded runs): not regenerated; this
# reproduction replaces them.
RECORDS = {
    "results/README.md": "index of the slot files",
    "results/checks-d-c-2.json": "D-C-2 re-run record",
    "results/round1-double-run.json": "double-run record",
    "results/round2-double-run.json": "double-run record",
    "results/round3-double-run.json": "double-run record",
    "results/e4/double-run.json": "double-run record",
    "results/e4-exploratory/double-run.json": "double-run record",
    "results/e5/double-run.json": "double-run record",
    "results/e7/double-run.json": "double-run record",
    "results/e0/run-1/": "E0 run 1 under p7-v1, stopped and superseded by run 2",
}


def sha(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def regenerate_results(res: Path, root: Path) -> None:
    from experiments import (e0, e1, e2, e3, e4, e4_sample, e5, e6_cost, e7, e7_check, round1_slots,  # noqa: PLC0415
                             round2_slots, round3_slots)

    log = ROOT / "data" / "BPI_Challenge_2019.xes"
    e0_dir = res / "e0" / "run-2"
    step = lambda name: print(f"reproduce: {name}", flush=True)  # noqa: E731
    step("E0 run 2"); e0.run(log, e0_dir)
    e0_lines = e0_dir / "e0-lines.txt"
    step("E1"); e1.run(log, res / "e1", e0_lines)
    step("E2"); e2.run(res / "e1", res / "e2")
    step("E3"); e3.run(res / "e1", res / "e3")
    step("E4 sample draw"); e4_sample.run(log, res / "e1", res / "e4", e0_lines)
    step("E4 analysis"); e4.run("e4", root=root); e4.run("e4-exploratory", root=root)
    step("E5"); e5.run(res / "e1", res / "e5")
    step("E7"); e7_check.run(res / "e7"); e7.run(res / "e7")
    step("E6 cost"); e6_cost.run(root=root, out=res / "e6")
    step("round-1 slots"); round1_slots.run(log, root=root, e1_dir=res / "e1", e0_path=e0_lines, out=res)
    step("round-2 slots"); round2_slots.run(log, e1_dir=res / "e1", e5_dir=res / "e5", e7_dir=res / "e7",
                                            e0_path=e0_lines, out=res)
    step("round-3 slots"); round3_slots.run(e1_dir=res / "e1", out=res)


def regenerate_paper(res: Path, paper_dir: Path) -> None:
    import build_tex  # noqa: PLC0415
    import figures  # noqa: PLC0415
    import fill_paper  # noqa: PLC0415

    # The paper also cites machine-dependent records (E6 timing); they are copied from the commit.
    for rel in MACHINE:
        src, dst = ROOT / rel, res / rel.removeprefix("results/")
        if src.is_file() and not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
    fill_paper.RESULTS = figures.RESULTS = res
    paper_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "README.md", paper_dir / "README.md")
    print("reproduce: paper", flush=True)
    fill_paper.run(out_paper=paper_dir / "paper.md", out_filled=paper_dir / "filled-template.json",
                   readme=paper_dir / "README.md")
    figures.run(paper_dir / "figures")
    if shutil.which("pandoc"):
        build_tex.write_tex(paper_dir / "paper.md", paper_dir / "main.tex")


def compare(res: Path, paper_dir: Path) -> tuple[list[dict], list[str], dict | None]:
    rows, uncovered = [], []
    for committed in sorted((ROOT / "results").rglob("*")):
        if not committed.is_file():
            continue
        rel = committed.relative_to(ROOT).as_posix()
        if rel in MACHINE or rel in RECORDS or any(rel.startswith(k) for k in RECORDS if k.endswith("/")):
            continue
        regen = res / committed.relative_to(ROOT / "results")
        if not regen.exists():
            uncovered.append(rel)
            continue
        rows.append({"file": rel, "committed": sha(committed), "regenerated": sha(regen)})
    pairs = [("paper/paper.md", "paper.md"), ("paper/filled-template.json", "filled-template.json"),
             ("README.md", "README.md"), ("paper-tex/main.tex", "main.tex")]
    pairs += [(f"paper/figures/{p.name}", f"figures/{p.name}") for p in sorted((ROOT / "paper" / "figures").iterdir())]
    for committed, regen in pairs:
        if not (paper_dir / regen).exists():
            uncovered.append(committed + (" (pandoc not installed)" if regen == "main.tex" else ""))
            continue
        rows.append({"file": committed, "committed": sha(ROOT / committed), "regenerated": sha(paper_dir / regen)})
    for r in rows:
        r["match"] = r["committed"] is not None and r["committed"] == r["regenerated"]
    pdf = None
    import build_tex  # noqa: PLC0415

    engine = build_tex.latex_engine()
    tex = paper_dir / "main.tex"
    if engine and tex.exists() and tex.read_bytes() == (ROOT / "paper-tex" / "main.tex").read_bytes():
        print("reproduce: PDF (information only)", flush=True)
        built = paper_dir / "main.pdf"
        if build_tex.build_pdf(engine, built):
            pdf = {"engine": engine, "committed": sha(ROOT / "paper-tex" / "main.pdf"), "built": sha(built)}
    return rows, uncovered, pdf


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True).stdout.strip()


def report(rows: list[dict], uncovered: list[str], pdf: dict | None) -> tuple[str, bool]:
    bad = [r for r in rows if not r["match"]]
    ok = not bad and not uncovered
    verdict = (f"REPRODUCED: all {len(rows)} compared files match." if ok else
               f"NOT REPRODUCED: {len(bad)} of {len(rows)} compared files differ"
               + (f"; {len(uncovered)} committed files were not regenerated" if uncovered else "") + ".")
    short = lambda h: h[:16] if h else "missing"  # noqa: E731
    lines = ["# Reproduction of v1.0.0", "",
             f"Commit `{git('rev-parse', 'HEAD')}` ({git('describe', '--tags', '--always')}); "
             f"Python {platform.python_version()}; {platform.platform()}.", "",
             "| file | committed SHA-256 | regenerated SHA-256 | match |", "|---|---|---|---|"]
    lines += [f"| `{r['file']}` | `{short(r['committed'])}` | `{short(r['regenerated'])}` | {'yes' if r['match'] else 'NO'} |"
              for r in rows]
    if uncovered:
        lines += ["", "Committed files not regenerated:", ""] + [f"- `{u}`" for u in uncovered]
    lines += ["", "Excluded as machine-dependent (not compared):", ""]
    lines += [f"- `{k}`: {v}" for k, v in MACHINE.items()]
    lines += ["", "Verification records of earlier runs (not regenerated; this reproduction replaces them):", ""]
    lines += [f"- `{k}`: {v}" for k, v in RECORDS.items()]
    if pdf:
        lines += ["", f"For information: `paper-tex/main.pdf` built with {pdf['engine']}: "
                      f"{'identical to' if pdf['committed'] == pdf['built'] else 'differs from'} the committed PDF "
                      "(its bytes depend on the TeX installation; the committed one used TeX Live 2023, pdfTeX 1.40.25)."]
    else:
        lines += ["", "For information: `paper-tex/main.pdf` was not built (no LaTeX engine, or main.tex differs)."]
    lines += ["", f"**{verdict}**", ""]
    return "\n".join(lines), ok


def main() -> int:
    shutil.rmtree(OUT, ignore_errors=True)
    root = OUT / "root"
    res = root / "results"
    res.mkdir(parents=True)
    os.symlink(ROOT / "responses", root / "responses")
    regenerate_results(res, root)
    regenerate_paper(res, OUT / "paper")
    rows, uncovered, pdf = compare(res, OUT / "paper")
    text, ok = report(rows, uncovered, pdf)
    (OUT / "report.md").write_text(text, encoding="utf-8")
    print(text)
    print(f"reproduce: report in {(OUT / 'report.md').relative_to(ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
