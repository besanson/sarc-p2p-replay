"""E7 replication on BPI 2020 declarations: D1' to D3' and O' (prereg/p7-v1.md section 8)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Callable, Iterable, Iterator

from .config import DeclarationPatterns
from .evidence import canonical_json, source_hash
from .model import Case, Event
from .predicates import Value

PREDICATES_PRIME = ("D1'", "D2'", "D3'")


def evaluate_payment(case: Case, payment: Event, p: DeclarationPatterns) -> dict[str, Value]:
    events = case.upto(payment.ts)
    approvals = [e.ts for e in events if e.activity in p.approval]
    required = any(e.activity in p.final_approval_required_role for e in events)
    if approvals:
        last = max(approvals)
        changed = any(e.activity in p.resubmission and e.ts > last for e in events)
        d3 = Value.FAIL if changed else Value.PASS
    else:
        d3 = Value.UNKNOWN
    return {
        "D1'": Value.PASS if approvals else Value.FAIL,
        "D2'": Value.PASS if required else Value.FAIL,
        "D3'": d3,
    }


def outcome_prime(case: Case, t_pay: datetime, p: DeclarationPatterns) -> bool:
    end = t_pay + timedelta(days=p.window_days)
    return any(e.activity in p.outcome_prime and t_pay < e.ts <= end for e in case.events)


@dataclass(frozen=True)
class PaymentRecord:
    case_id: str
    t_pay: str
    predicates: dict
    verdict: str
    defective: bool
    outcome_prime: bool
    source_sha256: str

    def to_json(self) -> str:
        return canonical_json(asdict(self))


def replay_declaration(case: Case, p: DeclarationPatterns, t_end: datetime) -> list[PaymentRecord]:
    horizon = t_end - timedelta(days=p.window_days)
    out = []
    for payment in case.of(p.payment):
        if payment.ts > horizon:
            continue
        values = evaluate_payment(case, payment, p)
        out.append(PaymentRecord(
            case_id=case.case_id,
            t_pay=payment.ts.isoformat(),
            predicates={k: v.value for k, v in values.items()},
            verdict="allow" if all(v is Value.PASS for v in values.values()) else "hold",
            defective=any(v is Value.FAIL for v in values.values()),
            outcome_prime=outcome_prime(case, payment.ts, p),
            source_sha256=source_hash(case, payment.ts),
        ))
    return out


def replay_declarations(open_cases: Callable[[], Iterable[Case]], p: DeclarationPatterns) -> Iterator[PaymentRecord]:
    from .replay import log_end

    t_end = log_end(open_cases())
    for case in open_cases():
        yield from replay_declaration(case, p, t_end)
