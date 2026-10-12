"""Predicates D1 to D7 at clearing time (prereg/p7-v1.md section 3.2).

Every predicate reads only events with timestamp at most t_c. Counts, not
event order, decide receipts, blocks and deletions, so the result does not
depend on the order of events that share a timestamp.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from .config import P2PPatterns
from .model import Case, Event, count

PREDICATES = ("D1", "D2", "D3", "D4", "D5", "D6", "D7")


class Value(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


def _pass_unless(failed: bool) -> Value:
    return Value.FAIL if failed else Value.PASS


def uncancelled_receipts(events: tuple[Event, ...], p: P2PPatterns) -> int:
    return count(events, p.goods_receipt) - count(events, p.goods_receipt_cancel)


def last_approval(events: tuple[Event, ...], p: P2PPatterns) -> datetime | None:
    stamps = [e.ts for e in events if e.activity in p.approval_bearing]
    return max(stamps) if stamps else None


def creation_actors(events: tuple[Event, ...], p: P2PPatterns) -> tuple[str | None, ...]:
    creations = [e for e in events if e.activity == p.creation]
    if not creations:
        return ()
    first = min(e.ts for e in creations)
    return tuple(e.actor for e in creations if e.ts == first)


def actor_missing(actor: str | None, p: P2PPatterns) -> bool:
    return actor is None or actor.strip() in p.actor_missing


def d1_receipt_present(events: tuple[Event, ...], p: P2PPatterns) -> Value:
    return _pass_unless(uncancelled_receipts(events, p) <= 0)


def d2_receipt_before_clearing(events: tuple[Event, ...], p: P2PPatterns) -> Value:
    # Same count as D1 at t_c (prereg 3.3); kept separate for its dimension.
    return _pass_unless(uncancelled_receipts(events, p) <= 0)


def d3_invoice_present(events: tuple[Event, ...], p: P2PPatterns) -> Value:
    return _pass_unless(count(events, p.invoice_receipt) == 0)


def d4_unchanged_since_approval(events: tuple[Event, ...], p: P2PPatterns) -> Value:
    approved = last_approval(events, p)
    if approved is None:
        return Value.UNKNOWN
    return _pass_unless(any(e.activity in p.changes and e.ts > approved for e in events))


def d5_distinct_actors(events: tuple[Event, ...], clearing_actor: str | None, p: P2PPatterns) -> Value:
    creators = [a for a in creation_actors(events, p) if not actor_missing(a, p)]
    if actor_missing(clearing_actor, p) or not creators:
        return Value.UNKNOWN
    return _pass_unless(clearing_actor in creators)


def d6_block_respected(events: tuple[Event, ...], p: P2PPatterns) -> Value:
    return _pass_unless(count(events, p.payment_block_set) - count(events, p.payment_block_remove) > 0)


def d7_not_deleted(events: tuple[Event, ...], p: P2PPatterns) -> Value:
    return _pass_unless(count(events, p.line_closed) - count(events, p.line_reopened) > 0)


def evaluate(case: Case, clearing: Event, p: P2PPatterns) -> dict[str, Value]:
    """All seven predicates for one clearing; applicability is the contract's job."""
    events = case.upto(clearing.ts)
    return {
        "D1": d1_receipt_present(events, p),
        "D2": d2_receipt_before_clearing(events, p),
        "D3": d3_invoice_present(events, p),
        "D4": d4_unchanged_since_approval(events, p),
        "D5": d5_distinct_actors(events, clearing.actor, p),
        "D6": d6_block_respected(events, p),
        "D7": d7_not_deleted(events, p),
    }
