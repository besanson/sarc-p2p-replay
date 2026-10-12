"""ERP view for E4, serialised by the registered template (prereg/erp-view-template.txt).

Only events at or before the decision point t* are read. The view carries no
event timeline, company, vendor, actor or line id.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .category import Category, category_of, parse_flag
from .config import TEMPLATE_PATH, P2PPatterns
from .frame import line_value
from .model import Case, count
from .predicates import last_approval, uncancelled_receipts

BEGIN, END = "=== REQUEST ===", "=== END ==="
CATEGORY_LABELS = {
    Category.THREE_WAY_AFTER: "3-way match, invoice after goods receipt",
    Category.THREE_WAY_BEFORE: "3-way match, invoice before goods receipt",
    Category.TWO_WAY: "2-way match",
}
NO_QUANTITY = "not recorded in this system"


def load_request_template(path: Path = TEMPLATE_PATH) -> str:
    """The request block: the lines strictly between the marker lines (the header mentions them in prose)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = lines.index(BEGIN) + 1
    return "\n".join(lines[start : lines.index(END, start)])


def _yes(flag: bool | None) -> str:
    return "yes" if flag else "no"


def _day(ts: datetime | None) -> str:
    return ts.date().isoformat() if ts is not None else "none"


def _eur(value: float | None) -> str:
    return f"{value:.2f}" if value is not None else "none"


def view_fields(case: Case, t_star: datetime, p: P2PPatterns, flag_true) -> dict[str, str]:
    category = category_of(case, flag_true)
    if category not in CATEGORY_LABELS:
        raise ValueError(f"no ERP view for category {category.value!r}")
    events = case.upto(t_star)
    approved_at = last_approval(events, p)
    approval_values = [e.value for e in events if e.activity in p.approval_bearing and e.ts == approved_at]
    approved_price = next((v for v in approval_values if v is not None), None)
    if approved_price is None:
        approved_price = line_value(case, p)
    invoices = [e for e in events if e.activity == p.invoice_receipt]
    receipts = [e for e in events if e.activity == p.goods_receipt]
    has_receipt = uncancelled_receipts(events, p) > 0
    changes = [
        f"{'price' if 'price' in e.activity.lower() else 'quantity'} changed on {_day(e.ts)}"
        for e in events
        if approved_at is not None and e.activity in p.changes and e.ts > approved_at
    ]
    blocked = count(events, p.payment_block_set) - count(events, p.payment_block_remove) > 0
    return {
        "category": CATEGORY_LABELS[category],
        "gr_based_iv": _yes(parse_flag(case.attr("gr_based_iv"), flag_true)),
        "gr_required": _yes(parse_flag(case.attr("goods_receipt_required"), flag_true)),
        "approved_price": _eur(approved_price),
        "approved_quantity": NO_QUANTITY,
        "invoice_received": _yes(bool(invoices)),
        "invoice_date": _day(invoices[-1].ts) if invoices else "none",
        "invoice_value": _eur(invoices[-1].value) if invoices else "none",
        "gr_recorded": _yes(has_receipt),
        "gr_date": _day(receipts[-1].ts) if has_receipt else "none",
        "changes": ", ".join(changes) if changes else "none",
        "payment_block": "set" if blocked else "not set",
        "decision_date": _day(t_star),
    }


def render(case: Case, t_star: datetime, p: P2PPatterns, flag_true, template: str | None = None) -> str:
    """Placeholders are replaced by name; the JSON braces in the instruction are left alone."""
    text = load_request_template() if template is None else template
    for name, value in view_fields(case, t_star, p, flag_true).items():
        text = text.replace("{" + name + "}", value)
    return text
