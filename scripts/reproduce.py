"""`make reproduce`: regenerate every deterministic result of paper 7 and compare it with the committed files.

For an external reproducer (REPRODUCE.md). Everything is regenerated into out/reproduce/ from the three
logs in data/ (fetched by `make bootstrap`, SHA-256 checked against prereg/data.lock), the committed E4
model responses (no model is called) and paper 5's compiler at its engines.lock pin, in pipeline order:

  E0 run 2 (the pilot draw), E1 (with the regenerated E0 lines removed), E2, E3, the E4 sample draw and
  views, the E4 analyses (primary and exploratory) from the committed responses, E5, the E7 vocabulary
  check and replication, the E6 cost table (from the responses), the round-1, round-2 and round-3 slots;
  then the paper, filled from the regenerated slots: paper/paper.md, paper/filled-template.json, the
  README's generated blocks, the figures and paper-tex/main.tex.

Each regenerated file is compared with the committed one by SHA-256 and, for JSON and JSON lines, also
within tolerance (scripts/tolerance.py: structures and strings equal, numbers within 1e-12 relative):
floating-point last digits can differ across machines and architectures (D-F-1). Text files (the
paper, its TeX, the README) are compared by bytes. The figures' SVG and PDF bytes depend on font
embedding and are listed, not compared; the numbers they plot (paper/figures/figure-data.json) are.
Every committed file under results/ is accounted for: compared, excluded as machine-dependent
(MACHINE), or a verification record that this reproduction replaces (RECORDS). paper-tex/main.pdf is
built when a LaTeX engine is installed and reported for information only; that optional step never
stops the run.

Writes out/reproduce/report.md (the table and the verdict, for a GitHub issue), always, and prints the
same. Exit 0 when every compared file is equal (byte-identical or within tolerance).

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
from tolerance import REL  # noqa: E402

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
    "results/reproduction/": "records of external reproduction attempts and the comparison rule",
}
# The paper's generated files: text compared by bytes, JSON within tolerance. The figures' SVG and PDF
# bytes depend on font embedding across machines (D-F-1): listed, not compared; figure-data.json, the
# numbers they plot, is compared within tolerance.
FIGURE_FILES = sorted(f"paper/figures/{p.name}" for p in (ROOT / "paper" / "figures").iterdir()
                      if p.suffix in (".svg", ".pdf"))
PAPER_FILES = [("paper/paper.md", "paper.md"), ("paper/filled-template.json", "filled-template.json"),
               ("README.md", "README.md"), ("paper-tex/main.tex", "main.tex"),
               ("paper/figures/figure-data.json", "figures/figure-data.json")]


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


def reason(rel: str) -> str:
    """Why a committed file under results/ is not regenerated."""
    if rel in MACHINE:
        return f"machine-dependent record ({MACHINE[rel]})"
    for key, why in RECORDS.items():
        if rel == key or (key.endswith("/") and rel.startswith(key)):
            kind = ("record of an external attempt" if rel.startswith("results/reproduction/attempt-")
                    else "verification record")
            return f"{kind} ({why})"
    return "not produced by any regeneration step"


def committed_results() -> list[str]:
    return sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "results").rglob("*") if p.is_file())


def missing(regenerated: set[str]) -> dict[str, str]:
    """Every committed file under results/ that the regeneration did not produce, with its reason (D-F-3)."""
    return {rel: reason(rel) for rel in committed_results() if rel not in regenerated}


def copy_committed(res: Path) -> dict[str, str]:
    """Copy from the commit every file under results/ absent from the regenerated tree, so that the paper,
    which also cites records (E6 timing, the external attempts), can be filled. A copied file is never
    counted as reproduced."""
    present = {"results/" + p.relative_to(res).as_posix() for p in res.rglob("*") if p.is_file()}
    copied = missing(present)
    for rel in copied:
        dst = res / rel.removeprefix("results/")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, dst)
    return copied


def regenerate_paper(res: Path, paper_dir: Path) -> dict[str, str]:
    """Fill the paper, the README's blocks, the figures and main.tex from the regenerated tree; returns the
    files copied from the commit into it (D-F-3)."""
    import build_tex  # noqa: PLC0415
    import figures  # noqa: PLC0415
    import fill_paper  # noqa: PLC0415

    copied = copy_committed(res)
    fill_paper.RESULTS = figures.RESULTS = res
    paper_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "README.md", paper_dir / "README.md")
    print(f"reproduce: paper ({len(copied)} committed records copied, not regenerated)", flush=True)
    fill_paper.run(out_paper=paper_dir / "paper.md", out_filled=paper_dir / "filled-template.json",
                   readme=paper_dir / "README.md")
    figures.run(paper_dir / "figures")
    if shutil.which("pandoc"):
        build_tex.write_tex(paper_dir / "paper.md", paper_dir / "main.tex")
    return copied


def compare(res: Path, paper_dir: Path, copied: dict[str, str] | None = None) -> tuple[list[dict], list[str]]:
    """Every compared file: byte identity, and for JSON and JSON lines equality within tolerance (scripts/tolerance.py).
    A file copied from the commit is never compared: if it should have been regenerated, it is uncovered."""
    import tolerance  # noqa: PLC0415

    copied = copied or {}
    rows, uncovered = [], []
    for committed in sorted((ROOT / "results").rglob("*")):
        if not committed.is_file():
            continue
        rel = committed.relative_to(ROOT).as_posix()
        if rel in MACHINE or rel in RECORDS or any(rel.startswith(k) for k in RECORDS if k.endswith("/")):
            continue
        regen = res / committed.relative_to(ROOT / "results")
        if rel in copied or not regen.exists():
            uncovered.append(rel)
            continue
        rows.append({"file": rel, **tolerance.compare(committed, regen)})
    for committed, regen in PAPER_FILES:
        if not (paper_dir / regen).exists():
            uncovered.append(committed + (" (pandoc not installed)" if regen == "main.tex" else ""))
            continue
        rows.append({"file": committed, **tolerance.compare(ROOT / committed, paper_dir / regen)})
    return rows, uncovered


def pdf_step(paper_dir: Path) -> str:
    """The optional PDF build, for information only. Never raises: any failure is reported as a reason."""
    try:
        import build_tex  # noqa: PLC0415

        engine = build_tex.latex_engine()
        tex = paper_dir / "main.tex"
        if engine is None:
            return "PDF not built: no LaTeX engine (tectonic, latexmk, pdflatex, xelatex) installed"
        if not tex.exists() or tex.read_bytes() != (ROOT / "paper-tex" / "main.tex").read_bytes():
            return "PDF not built: the regenerated main.tex differs from the committed one, or was not written"
        print("reproduce: PDF (information only)", flush=True)
        built = paper_dir / "main.pdf"
        if not build_tex.build_pdf(engine, built):
            return f"PDF not built: {engine} did not produce main.pdf"
        same = sha(built) == sha(ROOT / "paper-tex" / "main.pdf")
        return (f"`paper-tex/main.pdf` built with {engine}: {'identical to' if same else 'differs from'} the committed "
                "PDF (its bytes depend on the TeX installation and engine; the committed one used pdflatex, TeX Live "
                "2023, pdfTeX 1.40.25)")
    except Exception as exc:  # noqa: BLE001 - the optional step must never stop the run
        return f"PDF not built: {type(exc).__name__}: {exc}"


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True).stdout.strip()


def _version() -> str:
    import tomllib  # noqa: PLC0415

    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


def report(rows: list[dict], uncovered: list[str], pdf: str | None,
           copied: dict[str, str] | None = None) -> tuple[str, bool]:
    bad = [r for r in rows if not r["equal"]]
    ok = not bad and not uncovered
    byte = sum(r["byte_identical"] for r in rows)
    diffs = [r["max_abs_difference"] for r in rows if r["max_abs_difference"] is not None]
    worst = max(diffs, default=0.0)
    if ok:
        verdict = (f"REPRODUCED: {len(rows)} files equal ({byte} byte-identical, {len(rows) - byte} within tolerance, "
                   f"max difference {worst:.3g})")
    else:
        verdict = ("NOT REPRODUCED: " + "; ".join(
            [f"{len(bad)} of {len(rows)} compared files not equal: " + ", ".join(r["file"] for r in bad)] if bad else [])
            + ("; " if bad and uncovered else "")
            + (f"{len(uncovered)} committed files not regenerated: " + ", ".join(uncovered) if uncovered else ""))
    fmt = lambda r: "n/a" if r["max_abs_difference"] is None else f"{r['max_abs_difference']:.3g}"  # noqa: E731
    lines = [f"# Reproduction of v{_version()}", "",
             f"Commit `{git('rev-parse', 'HEAD')}` ({git('describe', '--tags', '--always')}); "
             f"Python {platform.python_version()}; {platform.platform()}.", "",
             "Byte-identical: the SHA-256 of the regenerated file equals the committed one. Within tolerance (JSON "
             "and JSON lines only): the parsed structures and strings are equal and every number pair satisfies "
             f"|a - b| <= {REL:g} x max(1, |a|, |b|); text files are compared by bytes only.", "",
             "| file | byte-identical | within tolerance | max absolute difference |", "|---|---|---|---|"]
    lines += [f"| `{r['file']}` | {'yes' if r['byte_identical'] else 'no'} | {'yes' if r['within_tolerance'] else 'NO'} | "
              f"{fmt(r)} |" for r in rows]
    if uncovered:
        lines += ["", "Committed files not regenerated:", ""] + [f"- `{u}`" for u in uncovered]
    if copied:
        lines += ["", "Copied from the commit, not regenerated (never counted as reproduced; the paper cites some of "
                      "them):", ""] + [f"- `{k}`: {v}" for k, v in copied.items()]
    lines += ["", "Excluded as machine-dependent (not compared):", ""]
    lines += [f"- `{k}`: {v}" for k, v in MACHINE.items()]
    lines += [f"- `{k}`: figure bytes (font embedding); its numbers are compared in `paper/figures/figure-data.json`"
              for k in FIGURE_FILES]
    lines += ["", "Verification records of earlier runs (not regenerated; this reproduction replaces them):", ""]
    lines += [f"- `{k}`: {v}" for k, v in RECORDS.items()]
    lines += ["", f"For information: {pdf or 'PDF step not reached'}.", "", f"**{verdict}**", ""]
    return "\n".join(lines), ok


def finish(res: Path, paper_dir: Path, out: Path = OUT, copied: dict[str, str] | None = None) -> bool:
    """Compare, run the optional PDF step and always write the report."""
    rows, uncovered = compare(res, paper_dir, copied)
    text, ok = report(rows, uncovered, pdf_step(paper_dir), copied)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.md").write_text(text, encoding="utf-8")
    print(text)
    print(f"reproduce: report in {(out / 'report.md')}")
    return ok


def main() -> int:
    shutil.rmtree(OUT, ignore_errors=True)
    root = OUT / "root"
    res = root / "results"
    res.mkdir(parents=True)
    os.symlink(ROOT / "responses", root / "responses")
    regenerate_results(res, root)
    copied = regenerate_paper(res, OUT / "paper")
    return 0 if finish(res, OUT / "paper", copied=copied) else 1


if __name__ == "__main__":
    sys.exit(main())
