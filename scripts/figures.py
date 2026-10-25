"""Figures for the paper, from the slot files only; deterministic SVG and PDF in paper/figures/.

  fig1-exposure       share of analysed clearings and of cleared value per defect class, with the
                      clustered bootstrap 95% intervals (results/e1/exposure.json)
  fig2-hold-rates     hold rate on defective and on clean lines for people (from the log), Jev,
                      Haiku and the gate (results/e4/arms.json); the exploratory timeline arm in a
                      separate, labelled panel (results/e4-exploratory/arms-exploratory.json)
  fig3-lag-bands      D1/D2 failures by lag band, in count and cleared value (results/e3/lag-bands.json)
  fig4-verdict-outcome the 2 x 2 gate verdict x corrective table at W = 60, in count and cleared value
                      (results/e3/verdict-by-outcome.json)

Determinism: the SVG hash salt is fixed, no date or creator metadata is written, and fonts are
embedded as paths (svg.fonttype none is not used), so regeneration is byte-identical.

Usage: python scripts/figures.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SOURCE_DATE_EPOCH", "0")

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
OUT = ROOT / "paper" / "figures"
CLASSES = ("D1 class (absent receipt)", "D2 class (stale receipt)", "D3", "D4", "D5", "D6", "D7",
           "at least one defect")
SHORT = {"D1 class (absent receipt)": "D1 class", "D2 class (stale receipt)": "D2 class",
         "at least one defect": "any"}
INK, MUTED, ACCENT, SECOND = "#1f2937", "#9ca3af", "#2563eb", "#d97706"


def _load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def _style() -> None:
    plt.rcParams.update({
        "svg.hashsalt": "sarc-p2p-replay", "svg.fonttype": "path", "pdf.fonttype": 42,
        "font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    })


def _save(fig, out: Path, name: str) -> list[str]:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.svg", format="svg", metadata={"Date": None, "Creator": None})
    fig.savefig(out / f"{name}.pdf", format="pdf", metadata={"CreationDate": None, "ModDate": None,
                                                             "Creator": None, "Producer": None})
    plt.close(fig)
    return [f"{name}.svg", f"{name}.pdf"]


def fig_exposure(out: Path) -> list[str]:
    e = _load("e1/exposure.json")["classes"]
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    xs = range(len(CLASSES))
    for offset, key, iv, color, label in ((-0.18, "share_of_clearings", "bootstrap95", ACCENT, "share of clearings"),
                                          (0.18, "share_of_value", "value_bootstrap95", SECOND, "share of cleared value")):
        vals = [100 * e[c][key] for c in CLASSES]
        lo = [100 * (e[c][key] - e[c][iv][0]) for c in CLASSES]
        hi = [100 * (e[c][iv][1] - e[c][key]) for c in CLASSES]
        ax.bar([x + offset for x in xs], vals, width=0.36, color=color, label=label)
        ax.errorbar([x + offset for x in xs], vals, yerr=[lo, hi], fmt="none", ecolor=INK, elinewidth=0.8, capsize=2)
    ax.set_xticks(list(xs), [SHORT.get(c, c) for c in CLASSES])
    ax.set_ylabel("% of analysed clearings / cleared value")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    return _save(fig, out, "fig1-exposure")


def fig_hold_rates(out: Path) -> list[str]:
    a = _load("e4/arms.json")["arms"]
    x = _load("e4-exploratory/arms-exploratory.json")["arms"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.4, 2.8), gridspec_kw={"width_ratios": [4, 2]}, sharey=True)
    arms = (("people", "people\n(log)"), ("jev", "Jev"), ("haiku", "Haiku"), ("gate", "gate"))
    for ax, data, keys, title in ((ax1, a, arms, "ERP view (registered)"),
                                  (ax2, x, arms[1:3], "timeline view (exploratory)")):
        xs = range(len(keys))
        ax.bar([i - 0.18 for i in xs], [100 * data[k]["hold_rate_defective"] for k, _ in keys], width=0.36,
               color=ACCENT, label="defective lines")
        ax.bar([i + 0.18 for i in xs], [100 * data[k]["hold_rate_clean"] for k, _ in keys], width=0.36,
               color=MUTED, label="clean lines")
        ax.set_xticks(list(xs), [lab for _, lab in keys])
        ax.set_title(title, fontsize=9)
    ax1.set_ylabel("hold rate, %")
    ax1.set_ylim(0, 105)
    ax2.legend(*ax1.get_legend_handles_labels(), frameon=False, loc="upper right", fontsize=8)
    fig.tight_layout()
    return _save(fig, out, "fig2-hold-rates")


def fig_lag_bands(out: Path) -> list[str]:
    lag = _load("e3/lag-bands.json")["bands"]
    keys = ("0-1", "1-7", "7-30", "over 30", "never")
    labels = ("[0, 1]", "(1, 7]", "(7, 30]", "> 30", "never")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.4, 2.6))
    ax1.bar(labels, [lag[k]["clearings"] for k in keys], color=ACCENT)
    ax1.set_title("clearings", fontsize=9)
    ax2.bar(labels, [lag[k]["cleared_value_eur"] for k in keys], color=SECOND)
    ax2.set_title("cleared value, anonymised EUR", fontsize=9)
    for ax in (ax1, ax2):
        ax.set_xlabel("days from clearing to receipt")
    fig.tight_layout()
    return _save(fig, out, "fig3-lag-bands")


def fig_verdict_outcome(out: Path) -> list[str]:
    t = _load("e3/verdict-by-outcome.json")["table"]["W60"]
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.4))
    rows = ("hold", "allow")
    cols = ("with", "without")
    for ax, key, title in ((axes[0], "clearings", "clearings"), (axes[1], "cleared_value_eur", "cleared value, anonymised EUR")):
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.set_axis_off()
        ax.set_title(title, fontsize=9, pad=20)
        for i, r in enumerate(rows):
            for j, c in enumerate(cols):
                v = t[f"{r}_{c}_corrective"][key]
                ax.add_patch(plt.Rectangle((j, 1 - i), 1, 1, fill=False, edgecolor=INK, linewidth=0.8))
                ax.text(j + 0.5, 1.5 - i, f"{v:,.0f}", ha="center", va="center", fontsize=9)
        ax.text(0.5, 2.05, "corrective", ha="center", va="bottom", fontsize=8)
        ax.text(1.5, 2.05, "no corrective", ha="center", va="bottom", fontsize=8)
        ax.text(-0.05, 1.5, "gate: hold", ha="right", va="center", fontsize=8)
        ax.text(-0.05, 0.5, "gate: allow", ha="right", va="center", fontsize=8)
    fig.tight_layout()
    return _save(fig, out, "fig4-verdict-outcome")


def run(out: Path = OUT) -> list[str]:
    _style()
    files = []
    for fn in (fig_exposure, fig_hold_rates, fig_lag_bands, fig_verdict_outcome):
        files += fn(out)
    return files


def main() -> int:
    files = run()
    print(f"figures: {len(files)} files in {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
