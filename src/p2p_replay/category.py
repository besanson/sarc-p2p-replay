"""Item category from the case flags (prereg/p7-v1.md section 3.1)."""

from __future__ import annotations

from enum import Enum
from typing import Iterable

from .model import Case

FLAG_FALSE = frozenset({"false", "False", "FALSE", "0"})


class Category(str, Enum):
    THREE_WAY_AFTER = "3-way, invoice after receipt"
    THREE_WAY_BEFORE = "3-way, invoice before receipt"
    TWO_WAY = "2-way"
    CONSIGNMENT = "consignment"
    UNDEFINED = "undefined"


def parse_flag(value: str | None, flag_true: Iterable[str]) -> bool | None:
    if value is None:
        return None
    if value in set(flag_true):
        return True
    if value in FLAG_FALSE:
        return False
    return None


def is_consignment(case: Case) -> bool:
    for field in ("item_type", "item_category"):
        value = case.attr(field)
        if value is not None and "consignment" in value.lower():
            return True
    return False


def category_of(case: Case, flag_true: Iterable[str]) -> Category:
    if is_consignment(case):
        return Category.CONSIGNMENT
    gr_iv = parse_flag(case.attr("gr_based_iv"), flag_true)
    gr = parse_flag(case.attr("goods_receipt_required"), flag_true)
    if gr is True and gr_iv is True:
        return Category.THREE_WAY_AFTER
    if gr is True and gr_iv is False:
        return Category.THREE_WAY_BEFORE
    if gr is False and gr_iv is False:
        return Category.TWO_WAY
    return Category.UNDEFINED


def requires_receipt(category: Category) -> bool:
    return category in (Category.THREE_WAY_AFTER, Category.THREE_WAY_BEFORE)
