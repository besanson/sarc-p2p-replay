"""Registered configuration (prereg/p7-v1.1.md and its companion files).

The numbers below are the registered values of p7-v1.1 (which supersedes p7-v1);
tests/test_pipeline.py checks each one against the registration text. The activity lists and the
column mapping are read from the YAML companion files, never restated here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
PREREG = ROOT / "prereg"
PATTERNS_PATH = PREREG / "outcome-patterns.yaml"
MAPPING_PATH = PREREG / "column-mapping.yaml"
TEMPLATE_PATH = PREREG / "erp-view-template.txt"

REGISTRATION = "p7-v1.1"
REGISTRATION_PATH = PREREG / "p7-v1.1.md"

# prereg/p7-v1.1.md section 2 and section 9
WINDOW_START = datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
WINDOW_END = datetime(2018, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
K_MAX_CLEARINGS = 12
W_DAYS = 60
W_SENSITIVITY_DAYS = 30
SEED = 20261201
T_END_LIMIT = datetime(2019, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
# v1.1 observation end: the last calendar month (UTC) carrying at least this many events
T_END_MONTH_MIN_EVENTS = 1000


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@dataclass(frozen=True)
class P2PPatterns:
    """BPI 2019 activity lists (outcome-patterns.yaml, key bpi2019)."""

    clearing: str
    creation: str
    goods_receipt: str
    goods_receipt_cancel: str
    invoice_receipt: str
    changes: frozenset[str]
    approval_bearing: frozenset[str]
    payment_block_set: str
    payment_block_remove: str
    line_closed: frozenset[str]
    line_reopened: frozenset[str]
    outcome: frozenset[str]
    window_days: int
    sensitivity_window_days: int
    actor_missing: frozenset[str]
    batch_actor_prefix: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "P2PPatterns":
        return cls(
            clearing=d["clearing"],
            creation=d["creation"],
            goods_receipt=d["goods_receipt"],
            goods_receipt_cancel=d["goods_receipt_cancel"],
            invoice_receipt=d["invoice_receipt"],
            changes=frozenset(d["changes"]),
            approval_bearing=frozenset(d["approval_bearing"]),
            payment_block_set=d["payment_block_set"],
            payment_block_remove=d["payment_block_remove"],
            line_closed=frozenset(d["line_closed"]),
            line_reopened=frozenset(d["line_reopened"]),
            outcome=frozenset(d["outcome"]),
            window_days=int(d["window_days"]),
            sensitivity_window_days=int(d["sensitivity_window_days"]),
            actor_missing=frozenset(d["actor_missing"]),
            batch_actor_prefix=d["batch_actor_prefix"],
        )


@dataclass(frozen=True)
class DeclarationPatterns:
    """BPI 2020 activity lists (outcome-patterns.yaml, key bpi2020)."""

    payment: frozenset[str]
    approval: frozenset[str]
    final_approval_required_role: frozenset[str]
    resubmission: frozenset[str]
    outcome_prime: frozenset[str]
    window_days: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DeclarationPatterns":
        return cls(
            payment=frozenset(d["payment"]),
            approval=frozenset(d["approval"]),
            final_approval_required_role=frozenset(d["final_approval_required_role"]),
            resubmission=frozenset(d["resubmission"]),
            outcome_prime=frozenset(d["outcome_prime"]),
            window_days=int(d["window_days"]),
        )


def load_patterns(path: Path = PATTERNS_PATH) -> tuple[P2PPatterns, DeclarationPatterns]:
    raw = load_yaml(path)
    return P2PPatterns.from_dict(raw["bpi2019"]), DeclarationPatterns.from_dict(raw["bpi2020"])


def load_mapping(dataset: str, path: Path = MAPPING_PATH) -> dict[str, Any]:
    raw = load_yaml(path)
    if dataset not in raw:
        raise KeyError(f"column mapping has no dataset {dataset!r}")
    return raw[dataset]
