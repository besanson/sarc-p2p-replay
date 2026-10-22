"""Shared pieces of the E1 to E3 runners (prereg/p7-v1.1.md sections 2.3, 3.9 and 5).

Slot files, the hashed evidence set and line table, Wilson intervals, the
purchase-document clustered bootstrap and the strata. Nothing here reads the
log; E1 writes the evidence set and E2 and E3 read it.

Bootstrap (section 5). Clusters are the purchase documents of the analysed
clearings, in sorted order of their id as the evidence set carries it (the
first 16 hex digits of its SHA-256, section 3.9), so that every interval can be
recomputed from the committed evidence set. Each bootstrap starts one
`numpy.random.Generator(PCG64(20261201))` and draws B = 10,000 resamples of the
clusters with replacement, `integers(0, n, size=n)` per resample in order; every
statistic of a runner is computed on the same B resamples. Values enter as
integer cents and counts as integers, so every resampled total is exact and the
slot files are byte-identical between runs.
"""

from __future__ import annotations

import gzip
import json
import math
from collections import Counter
from pathlib import Path
from statistics import NormalDist
from typing import Any, Iterable, Sequence

import numpy as np

from p2p_replay.config import ROOT, SEED

BOOTSTRAP_B = 10_000
Z95 = NormalDist().inv_cdf(0.975)
E0_LINES = ROOT / "results" / "e0" / "run-2" / "e0-lines.txt"
STRATA = ("category", "spend_area", "company", "month", "line_value_quartile", "vendor_activity_quartile")
MISSING = "missing"


# ---------------------------------------------------------------- files

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _line(row: dict) -> str:
    return json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n"


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(_line(r) for r in rows), encoding="utf-8")


def write_jsonl_gz(path: Path, rows: Iterable[dict]) -> None:
    """Gzip with a fixed header (no name, mtime 0), so equal rows give equal bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
        for r in rows:
            gz.write(_line(r).encode("utf-8"))


def read_jsonl_gz(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def read_e0_lines(path: Path = E0_LINES) -> set[str]:
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


# ---------------------------------------------------------------- numbers

def cents(value: float) -> int:
    """Anonymised EUR to integer cents; the log's values carry at most two decimals."""
    c = round(value * 100)
    if abs(value * 100 - c) > 1e-6:
        raise ValueError(f"value {value!r} has more than two decimals")
    return int(c)


def eur(c: int | float) -> float:
    return round(c / 100, 2)


def wilson(k: int, n: int, z: float = Z95) -> list[float] | None:
    if n == 0:
        return None
    phat = k / n
    denom = 1 + z * z / n
    centre = (phat + z * z / (2 * n)) / denom
    half = z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n)) / denom
    # The bounds are exactly 0 at k = 0 and exactly 1 at k = n.
    return [0.0 if k == 0 else max(0.0, centre - half), 1.0 if k == n else min(1.0, centre + half)]


def one_sided_p(z: float) -> float:
    """1 - Phi(z)."""
    return 0.5 * math.erfc(z / math.sqrt(2))


def ratio(num: int, den: int) -> float | None:
    return num / den if den else None


# ---------------------------------------------------------------- bootstrap

class ClusterBootstrap:
    """Resampled column totals over purchase-document clusters (section 5)."""

    def __init__(self, record_clusters: Sequence[str], b: int = BOOTSTRAP_B, seed: int = SEED, chunk: int = 200):
        self.clusters = sorted(set(record_clusters))
        position = {c: i for i, c in enumerate(self.clusters)}
        self.record_cluster = np.fromiter((position[c] for c in record_clusters), dtype=np.int64,
                                          count=len(record_clusters))
        self.b, self.seed, self.chunk = b, seed, chunk

    @property
    def n(self) -> int:
        return len(self.clusters)

    def totals(self, columns: Sequence[np.ndarray]) -> np.ndarray:
        """B x k matrix: per resample, the total of each record-level column."""
        x = np.empty((self.n, len(columns)), dtype=np.float64)
        for j, col in enumerate(columns):
            x[:, j] = np.bincount(self.record_cluster, weights=np.asarray(col, dtype=np.float64), minlength=self.n)
        if np.abs(x).max(initial=0.0) * max(self.n, 1) >= 2.0 ** 53:
            raise ValueError("cluster totals too large for exact float arithmetic")
        rng = np.random.Generator(np.random.PCG64(self.seed))
        out = np.empty((self.b, len(columns)), dtype=np.float64)
        for start in range(0, self.b, self.chunk):
            m = min(self.chunk, self.b - start)
            counts = np.empty((m, self.n), dtype=np.float64)
            for i in range(m):
                counts[i] = np.bincount(rng.integers(0, self.n, size=self.n), minlength=self.n)
            out[start:start + m] = counts @ x
        return out


def percentile95(num: np.ndarray, den: np.ndarray) -> dict[str, Any]:
    """Percentile interval of num/den over the resamples with den > 0."""
    ok = den > 0
    if not ok.any():
        return {"interval": None, "resamples_used": 0}
    lo, hi = np.percentile(num[ok] / den[ok], [2.5, 97.5])
    return {"interval": [float(lo), float(hi)], "resamples_used": int(ok.sum())}


# ---------------------------------------------------------------- strata

def quartile_cutpoints(values: Sequence[float]) -> list[float]:
    """Quartiles over the given values (numpy linear interpolation)."""
    return [float(q) for q in np.quantile(np.asarray(values, dtype=np.float64), [0.25, 0.5, 0.75])]


def quartile_of(value: float | None, cut: Sequence[float]) -> str:
    if value is None:
        return MISSING
    if value <= cut[0]:
        return "Q1"
    if value <= cut[1]:
        return "Q2"
    if value <= cut[2]:
        return "Q3"
    return "Q4"


class Strata:
    """Section 2.3 strata. Quartiles of line value over framed lines; vendor activity is the number of
    framed lines of the line's vendor, with quartiles over framed lines (E0 lines removed)."""

    def __init__(self, lines: Sequence[dict]):
        self.vendor_lines = Counter(l["strata"]["vendor"] for l in lines if l["strata"]["vendor"] is not None)
        self.value_cut = quartile_cutpoints([l["line_value"] for l in lines]) if lines else [0.0, 0.0, 0.0]
        activity = [self.vendor_lines[l["strata"]["vendor"]] for l in lines if l["strata"]["vendor"] is not None]
        self.vendor_cut = quartile_cutpoints(activity) if activity else [0.0, 0.0, 0.0]
        self.by_line = {l["case_id"]: l for l in lines}

    def cutpoints(self) -> dict[str, Any]:
        return {"line_value_quartile_cutpoints_eur": self.value_cut,
                "vendor_activity_quartile_cutpoints_lines": self.vendor_cut,
                "rule": "Q1 <= first cutpoint < Q2 <= second < Q3 <= third < Q4; numpy linear quantiles over framed lines"}

    def of_line(self, line: dict, month: str | None) -> dict[str, str]:
        vendor = line["strata"]["vendor"]
        return {
            "category": line["category"],
            "spend_area": line["strata"]["spend_area"] or MISSING,
            "company": line["strata"]["company"] or MISSING,
            "month": month or MISSING,
            "line_value_quartile": quartile_of(line["line_value"], self.value_cut),
            "vendor_activity_quartile": quartile_of(self.vendor_lines[vendor], self.vendor_cut) if vendor else MISSING,
        }

    def of_record(self, rec: dict) -> dict[str, str]:
        return self.of_line(self.by_line[rec["case_id"]], rec["t_c"][:7])


def cells(labels: Sequence[dict[str, str]]) -> dict[str, dict[str, np.ndarray]]:
    """Per stratum variable and value, a boolean mask over the records."""
    out: dict[str, dict[str, np.ndarray]] = {}
    for var in STRATA:
        column = [lab[var] for lab in labels]
        out[var] = {v: np.fromiter((c == v for c in column), dtype=bool, count=len(column)) for v in sorted(set(column))}
    return out
