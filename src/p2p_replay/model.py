"""Events and cases in canonical form.

A case's events are kept in one canonical order: timestamp, then activity,
actor and value. The source order of events that share a timestamp is
therefore never visible to the replay, which is what makes the verdict
invariant under reordering within equal timestamps (prereg/p7-v1.1.md 3.3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, Mapping


def parse_timestamp(text: str) -> datetime:
    """ISO 8601 to an aware UTC datetime; a naive timestamp is taken as UTC."""
    value = text.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    ts = datetime.fromisoformat(value)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class Event:
    activity: str
    ts: datetime
    actor: str | None = None
    value: float | None = None

    def sort_key(self) -> tuple:
        return (
            self.ts,
            self.activity,
            self.actor if self.actor is not None else "",
            self.value is None,
            self.value if self.value is not None else 0.0,
        )

    def to_dict(self) -> dict:
        return {
            "activity": self.activity,
            "ts": self.ts.isoformat(),
            "actor": self.actor,
            "value": self.value,
        }


@dataclass(frozen=True)
class Case:
    case_id: str
    attrs: Mapping[str, str | None] = field(default_factory=dict)
    events: tuple[Event, ...] = ()

    @classmethod
    def build(cls, case_id: str, attrs: Mapping[str, str | None], events: Iterable[Event]) -> "Case":
        return cls(case_id, dict(attrs), tuple(sorted(events, key=Event.sort_key)))

    def attr(self, name: str) -> str | None:
        return self.attrs.get(name)

    def upto(self, t: datetime) -> tuple[Event, ...]:
        """Events with timestamp at most t (the evidence available at t)."""
        return tuple(e for e in self.events if e.ts <= t)

    def truncated(self, t: datetime) -> "Case":
        """The same case without events after t (v1.1: events after T_end are excluded)."""
        return Case(self.case_id, self.attrs, self.upto(t))

    def of(self, activities: str | Iterable[str]) -> tuple[Event, ...]:
        wanted = {activities} if isinstance(activities, str) else set(activities)
        return tuple(e for e in self.events if e.activity in wanted)


def count(events: Iterable[Event], activities: str | Iterable[str]) -> int:
    wanted = {activities} if isinstance(activities, str) else set(activities)
    return sum(1 for e in events if e.activity in wanted)
