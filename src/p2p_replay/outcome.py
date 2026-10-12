"""Outcome proxy O, receipt defect class and lag bands (prereg/p7-v1.md 3.3, 3.7, 3.8)."""

from __future__ import annotations

from datetime import datetime, timedelta

from .config import P2PPatterns
from .model import Case
from .predicates import uncancelled_receipts

LAG_BANDS = ("0-1", "1-7", "7-30", "over 30", "never")
STALE = "stale receipt"
ABSENT = "absent receipt"


def corrective_within(case: Case, t_c: datetime, days: int, p: P2PPatterns) -> bool:
    """O: an outcome activity on the line in (t_c, t_c + days]."""
    end = t_c + timedelta(days=days)
    return any(e.activity in p.outcome and t_c < e.ts <= end for e in case.events)


def first_receipt_after(case: Case, t_c: datetime, t_end: datetime, p: P2PPatterns) -> datetime | None:
    """Earliest timestamp in (t_c, t_end] at which an uncancelled receipt exists.

    Evaluated once per distinct timestamp on cumulative counts, so events
    sharing a timestamp are taken together.
    """
    stamps = sorted({e.ts for e in case.events if t_c < e.ts <= t_end})
    for ts in stamps:
        if uncancelled_receipts(case.upto(ts), p) > 0:
            return ts
    return None


def lag_band(t_c: datetime, receipt: datetime | None) -> str:
    if receipt is None:
        return "never"
    days = (receipt - t_c).total_seconds() / 86400
    if days <= 1:
        return "0-1"
    if days <= 7:
        return "1-7"
    if days <= 30:
        return "7-30"
    return "over 30"


def receipt_class(receipt: datetime | None) -> str:
    """Reporting class of a D1/D2 failure; never an input to the gate."""
    return ABSENT if receipt is None else STALE
