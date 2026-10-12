"""Replay of a BPI 2019-shaped log: frame, predicates, verdict, outcome, evidence set."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Iterable, Iterator

from .config import W_DAYS, W_SENSITIVITY_DAYS, P2PPatterns
from .category import requires_receipt
from .contract import applicable, decide
from .evidence import EvidenceSet, source_hash
from .frame import FrameResult, classify, cleared_value, line_value
from .model import Case, Event, count
from .outcome import corrective_within, first_receipt_after, lag_band, receipt_class
from .predicates import Value, evaluate, last_approval, uncancelled_receipts


def log_end(cases: Iterable[Case]) -> datetime:
    """T_end: the latest timestamp of any event in the log."""
    latest = None
    for case in cases:
        for e in case.events:
            if latest is None or e.ts > latest:
                latest = e.ts
    if latest is None:
        raise ValueError("log has no events")
    return latest


def inputs_at(case: Case, clearing: Event, p: P2PPatterns) -> dict:
    events = case.upto(clearing.ts)
    approved = last_approval(events, p)
    return {
        "uncancelled_receipts": uncancelled_receipts(events, p),
        "invoice_receipts": count(events, p.invoice_receipt),
        "last_approval": approved.isoformat() if approved else None,
        "changes_since_approval": sum(
            1 for e in events if approved is not None and e.activity in p.changes and e.ts > approved
        ),
        "open_payment_blocks": count(events, p.payment_block_set) - count(events, p.payment_block_remove),
        "line_closed_balance": count(events, p.line_closed) - count(events, p.line_reopened),
    }


def strata_of(case: Case) -> dict:
    return {
        "company": case.attr("company"),
        "spend_area": case.attr("spend_area"),
        "vendor": case.attr("vendor"),
    }


def replay_clearing(case: Case, frame: FrameResult, clearing: Event, p: P2PPatterns, t_end: datetime) -> EvidenceSet:
    values = evaluate(case, clearing, p)
    verdict = decide(values, frame.category)
    receipt_failed = requires_receipt(frame.category) and values["D1"] is Value.FAIL
    later = first_receipt_after(case, clearing.ts, t_end, p) if receipt_failed else None
    amount, source = cleared_value(case, clearing, p)
    return EvidenceSet(
        case_id=case.case_id,
        purchase_document=case.attr("purchase_document"),
        category=frame.category.value,
        t_c=clearing.ts.isoformat(),
        clearing_actor=clearing.actor,
        inputs=inputs_at(case, clearing, p),
        predicates={k: v.value for k, v in values.items()},
        applicable=list(applicable(frame.category)),
        verdict="allow" if verdict.allow else "hold",
        defective=verdict.defective,
        failed=list(verdict.failed),
        unknown=list(verdict.unknown),
        receipt_class=receipt_class(later) if receipt_failed else None,
        lag_band=lag_band(clearing.ts, later) if receipt_failed else None,
        outcome_w=corrective_within(case, clearing.ts, W_DAYS, p),
        outcome_w_sensitivity=corrective_within(case, clearing.ts, W_SENSITIVITY_DAYS, p),
        cleared_value=amount,
        cleared_value_source=source,
        line_value=line_value(case, p),
        strata=strata_of(case),
        source_sha256=source_hash(case, clearing.ts),
    )


@dataclass
class CaseResult:
    case_id: str
    frame: FrameResult
    records: list[EvidenceSet] = field(default_factory=list)


def replay_case(case: Case, p: P2PPatterns, flag_true, t_end: datetime) -> CaseResult:
    frame = classify(case, p, flag_true, t_end, W_DAYS)
    records = [replay_clearing(case, frame, c, p, t_end) for c in frame.analysed] if frame.framed else []
    return CaseResult(case.case_id, frame, records)


def replay_log(open_cases: Callable[[], Iterable[Case]], p: P2PPatterns, flag_true) -> Iterator[CaseResult]:
    """Two passes over the log: T_end first, then every case."""
    t_end = log_end(open_cases())
    for case in open_cases():
        yield replay_case(case, p, flag_true, t_end)
