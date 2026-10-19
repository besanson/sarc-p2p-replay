"""Contract per category and the min() verdict (prereg/p7-v1.1.md sections 3.1 and 3.5)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .category import Category
from .predicates import Value

ALL = ("D1", "D2", "D3", "D4", "D5", "D6", "D7")
CONTRACTS: dict[Category, tuple[str, ...]] = {
    Category.THREE_WAY_AFTER: ALL,
    Category.THREE_WAY_BEFORE: ALL,
    Category.TWO_WAY: ("D3", "D4", "D5", "D6", "D7"),
}


@dataclass(frozen=True)
class Verdict:
    allow: bool
    defective: bool
    failed: tuple[str, ...]
    unknown: tuple[str, ...]

    @property
    def held_unknown(self) -> bool:
        """Held, with no failed predicate: only unknowns kept it from passing."""
        return not self.allow and not self.defective


def applicable(category: Category) -> tuple[str, ...]:
    if category not in CONTRACTS:
        raise ValueError(f"no contract for category {category.value!r}")
    return CONTRACTS[category]


def score(value: Value) -> int:
    return 1 if value is Value.PASS else 0


def decide(values: Mapping[str, Value], category: Category) -> Verdict:
    ids = applicable(category)
    allow = min(score(values[i]) for i in ids) == 1
    failed = tuple(i for i in ids if values[i] is Value.FAIL)
    unknown = tuple(i for i in ids if values[i] is Value.UNKNOWN)
    return Verdict(allow=allow, defective=bool(failed), failed=failed, unknown=unknown)
