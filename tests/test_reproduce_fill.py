"""The reproduction fills the paper from the regenerated tree plus the committed records it copies (D-F-3).

Attempt 2 (issue #1, v1.0.1) stopped because the paper cites records under results/reproduction/ that the
regenerated tree did not contain. Both tests use only what v1.0.1's scripts/reproduce.py also had
(MACHINE, RECORDS, regenerate_paper, compare), so they fail there on the defect itself and pass on 1.0.2."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_tex  # noqa: E402
import figures  # noqa: E402
import fill_paper  # noqa: E402
import reproduce  # noqa: E402


def _regenerated() -> set[str]:
    """What the regeneration steps produce: the checkout's results/ minus MACHINE minus RECORDS."""
    def recorded(rel: str) -> bool:
        return rel in reproduce.MACHINE or any(rel == k or (k.endswith("/") and rel.startswith(k))
                                               for k in reproduce.RECORDS)
    files = (p.relative_to(ROOT).as_posix() for p in (ROOT / "results").rglob("*") if p.is_file())
    return {rel for rel in files if not recorded(rel)}


def _tree(base: Path) -> Path:
    """A results tree holding only the regenerated files (linked from the commit; no experiment is run)."""
    res = base / "root" / "results"
    for rel in _regenerated():
        dst = res / rel.removeprefix("results/")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.symlink_to(ROOT / rel)
    return res


def _sources(monkeypatch, tmp_path) -> set[str]:
    """Every slot file the paper, the README's blocks and the figures read, traced while filling them."""
    seen: set[str] = set()
    load, fig_load = fill_paper.load, figures._load
    monkeypatch.setattr(fill_paper, "load", lambda s: (s.startswith("@") or seen.add(f"results/{s}"), load(s))[1])
    monkeypatch.setattr(figures, "_load", lambda n: (seen.add(f"results/{n}"), fig_load(n))[1])
    tmp_path.mkdir(parents=True, exist_ok=True)
    readme = tmp_path / "README.md"
    shutil.copyfile(ROOT / "README.md", readme)
    fill_paper.run(out_paper=tmp_path / "p.md", out_filled=tmp_path / "f.json", readme=readme)
    figures.run(tmp_path / "figures")
    return seen


def test_every_paper_source_is_regenerated_or_copied(monkeypatch, tmp_path):
    sources = _sources(monkeypatch, tmp_path / "trace")
    # What regenerate_paper puts in the tree before filling, with the filling itself stubbed out.
    res = _tree(tmp_path)
    monkeypatch.setattr(fill_paper, "RESULTS", fill_paper.RESULTS)
    monkeypatch.setattr(figures, "RESULTS", figures.RESULTS)
    for mod, name in ((fill_paper, "run"), (figures, "run"), (build_tex, "write_tex")):
        monkeypatch.setattr(mod, name, lambda *a, **k: None)
    reproduce.regenerate_paper(res, tmp_path / "paper")
    in_tree = {"results/" + p.relative_to(res).as_posix() for p in res.rglob("*") if p.is_file()}
    assert sources and sources <= in_tree, sorted(sources - in_tree)


def test_paper_fills_from_regenerated_files_plus_copied_records(monkeypatch, tmp_path):
    res = _tree(tmp_path)
    monkeypatch.setattr(fill_paper, "RESULTS", fill_paper.RESULTS)
    monkeypatch.setattr(figures, "RESULTS", figures.RESULTS)
    paper_dir = tmp_path / "paper"
    copied = reproduce.regenerate_paper(res, paper_dir) or {}
    assert (paper_dir / "paper.md").read_bytes() == (ROOT / "paper" / "paper.md").read_bytes()
    assert "results/reproduction/attempt-1.json" in copied and "results/e6/timing-e1.json" in copied
    rows, uncovered = reproduce.compare(res, paper_dir, copied)
    # main.tex needs pandoc; the exploratory appendix is written by the X4 step of regenerate_results, not here.
    assert all("pandoc not installed" in u or u == "paper/appendix-prompts.md" for u in uncovered)
    assert all(r["equal"] for r in rows)
    assert not {r["file"] for r in rows} & set(copied)  # a copied record is never counted as reproduced
