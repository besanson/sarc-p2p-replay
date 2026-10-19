"""Values, exclusions, frame, human hold and the E4 decision point.

prereg/p7-v1.1.md sections 2, 3.4, 3.6 and 7. The E0 pilot lines are removed by
the experiment layer, not here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .category import Category, category_of
from .config import K_MAX_CLEARINGS, WINDOW_END, WINDOW_START, P2PPatterns
from .model import Case, Event

# Exclusion codes in registered order (section 2.1), then the frame code.
NO_CREATION = "no_creation"
CONSIGNMENT = "consignment"
UNDEFINED_CATEGORY = "undefined_category"
ZERO_OR_MISSING_VALUE = "zero_or_missing_value"
FRAMEWORK = "more_than_k_clearings"
OUTSIDE_WINDOW = "outside_window"
INCOMPLETE_WINDOW = "incomplete_outcome_window"
FRAMED = "framed"
STATUSES = (
    NO_CREATION, CONSIGNMENT, UNDEFINED_CATEGORY, ZERO_OR_MISSING_VALUE,
    FRAMEWORK, OUTSIDE_WINDOW, INCOMPLETE_WINDOW, FRAMED,
)

# Cleared-value sources (section 3.4), each count a slot.
FROM_CLEARING = "clearing"
FROM_INVOICE = "invoice_receipt"
FROM_LINE = "line_value"


def creation_events(case: Case, p: P2PPatterns) -> tuple[Event, ...]:
    return case.of(p.creation)


def creation_time(case: Case, p: P2PPatterns) -> datetime | None:
    created = creation_events(case, p)
    return min(e.ts for e in created) if created else None


def line_value(case: Case, p: P2PPatterns) -> float | None:
    """Value on the earliest creation event (first in canonical order)."""
    first = creation_time(case, p)
    if first is None:
        return None
    for e in creation_events(case, p):
        if e.ts == first:
            return e.value
    return None  # pragma: no cover - unreachable: first is a creation timestamp


def positive(value: float | None) -> bool:
    return value is not None and value > 0


def cleared_value(case: Case, clearing: Event, p: P2PPatterns) -> tuple[float | None, str]:
    if positive(clearing.value):
        return clearing.value, FROM_CLEARING
    invoices = [e for e in case.upto(clearing.ts) if e.activity == p.invoice_receipt]
    if invoices and positive(invoices[-1].value):
        return invoices[-1].value, FROM_INVOICE
    return line_value(case, p), FROM_LINE


def clearings(case: Case, p: P2PPatterns) -> tuple[Event, ...]:
    return case.of(p.clearing)


@dataclass(frozen=True)
class FrameResult:
    status: str
    category: Category | None
    analysed: tuple[Event, ...] = ()

    @property
    def framed(self) -> bool:
        return self.status == FRAMED


def classify(case: Case, p: P2PPatterns, flag_true, t_end: datetime, window_days: int) -> FrameResult:
    """Apply the exclusions in registered order; return the analysed clearings of a framed line."""
    created = creation_time(case, p)
    if created is None:
        return FrameResult(NO_CREATION, None)
    category = category_of(case, flag_true)
    if category is Category.CONSIGNMENT:
        return FrameResult(CONSIGNMENT, category)
    if category is Category.UNDEFINED:
        return FrameResult(UNDEFINED_CATEGORY, category)
    if not positive(line_value(case, p)):
        return FrameResult(ZERO_OR_MISSING_VALUE, category)
    cleared = clearings(case, p)
    if len(cleared) > K_MAX_CLEARINGS:
        return FrameResult(FRAMEWORK, category)
    if not (WINDOW_START <= created <= WINDOW_END):
        return FrameResult(OUTSIDE_WINDOW, category)
    horizon = t_end - timedelta(days=window_days)
    anchor = cleared[0].ts if cleared else created
    if anchor > horizon:
        return FrameResult(INCOMPLETE_WINDOW, category)
    return FrameResult(FRAMED, category, tuple(c for c in cleared if c.ts <= horizon))


def first_invoice(case: Case, p: P2PPatterns) -> datetime | None:
    invoices = case.of(p.invoice_receipt)
    return invoices[0].ts if invoices else None


def human_hold(case: Case, p: P2PPatterns, t_end: datetime, window_days: int) -> bool | None:
    """Section 3.6. None: not classified (no invoice receipt by T_end - W).

    "Cleared within the window" counts any clearing at most W days after the
    first invoice receipt, including one recorded before that receipt.
    """
    invoiced = first_invoice(case, p)
    if invoiced is None or invoiced > t_end - timedelta(days=window_days):
        return None
    cleared = clearings(case, p)
    first_clearing = cleared[0].ts if cleared else None
    blocks = case.of(p.payment_block_set)
    if blocks and (first_clearing is None or blocks[0].ts <= first_clearing):
        return True
    return first_clearing is None or first_clearing > invoiced + timedelta(days=window_days)


def decision_point(case: Case, p: P2PPatterns, window_days: int) -> datetime | None:
    """E4 t*: first clearing if within W of the first invoice receipt, else that receipt + W."""
    invoiced = first_invoice(case, p)
    if invoiced is None:
        return None
    limit = invoiced + timedelta(days=window_days)
    cleared = clearings(case, p)
    if cleared and cleared[0].ts <= limit:
        return cleared[0].ts
    return limit
