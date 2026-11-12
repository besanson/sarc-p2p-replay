"""The exploratory analyses (DECISIONS.md D-G-1) as steps, run in order by `make reproduce`, gate G4 and
the exploratory double run. Each step reads the e1/ to e3/ slots of `results_dir` (the committed ones or a
reproduction's regenerated ones) and writes under `out`/exploratory/; X4 also writes the paper's
generated appendix into `paper_dir`. Returns the paths written, relative to `out` (results files) or as
`paper/...` (the appendix)."""

from __future__ import annotations

from pathlib import Path

from experiments.common import BOOTSTRAP_B, E0_LINES
from p2p_replay.config import T_END_MONTH_MIN_EVENTS


def x1(log: Path, results_dir: Path, out: Path, paper_dir: Path, e0_path: Path, min_month_events: int, b: int) -> list[str]:
    from experiments.exploratory import x1_d4_sensitivity  # noqa: PLC0415

    x1_d4_sensitivity.run(log, results_dir, out / "exploratory" / "d4-sensitivity.json", e0_path, min_month_events, b)
    return ["exploratory/d4-sensitivity.json"]


def x2(log: Path, results_dir: Path, out: Path, paper_dir: Path, e0_path: Path, min_month_events: int, b: int) -> list[str]:
    from experiments.exploratory import x2_adjusted_h1_h2  # noqa: PLC0415

    x2_adjusted_h1_h2.run(results_dir, out / "exploratory" / "adjusted-h1-h2.json", b)
    return ["exploratory/adjusted-h1-h2.json"]


def x3(log: Path, results_dir: Path, out: Path, paper_dir: Path, e0_path: Path, min_month_events: int, b: int) -> list[str]:
    from experiments.exploratory import x3_hold_friction  # noqa: PLC0415

    x3_hold_friction.run(results_dir, out / "exploratory" / "hold-friction.json", b)
    return ["exploratory/hold-friction.json"]


def x4(log: Path, results_dir: Path, out: Path, paper_dir: Path, e0_path: Path, min_month_events: int, b: int) -> list[str]:
    from experiments.exploratory import x4_prompt_examples  # noqa: PLC0415

    paper_dir.mkdir(parents=True, exist_ok=True)
    x4_prompt_examples.run(out / "exploratory" / "prompt-examples.json", paper_dir / "appendix-prompts.md")
    return ["exploratory/prompt-examples.json", "paper/appendix-prompts.md"]


STEPS = {"X1": x1, "X2": x2, "X3": x3, "X4": x4}


def run_all(log: Path, results_dir: Path, out: Path, paper_dir: Path, e0_path: Path = E0_LINES,
            min_month_events: int = T_END_MONTH_MIN_EVENTS, b: int = BOOTSTRAP_B) -> list[str]:
    written: list[str] = []
    for step in STEPS.values():
        written += step(log, results_dir, out, paper_dir, e0_path, min_month_events, b)
    return written
