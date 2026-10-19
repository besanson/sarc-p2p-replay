"""Evidence set: one record per analysed clearing (prereg/p7-v1.1.md section 3.9)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime

from .model import Case


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_hash(case: Case, t_c: datetime) -> str:
    """SHA-256 of the canonical serialisation of the line's events up to t_c."""
    payload = {"case_id": case.case_id, "events": [e.to_dict() for e in case.upto(t_c)]}
    return sha256_text(canonical_json(payload))


@dataclass(frozen=True)
class EvidenceSet:
    case_id: str
    purchase_document: str | None
    category: str
    t_c: str
    clearing_actor: str | None
    inputs: dict
    predicates: dict
    applicable: list
    verdict: str
    defective: bool
    failed: list
    unknown: list
    receipt_class: str | None
    lag_band: str | None
    outcome_w: bool
    outcome_w_sensitivity: bool
    cleared_value: float | None
    cleared_value_source: str
    line_value: float | None
    strata: dict
    source_sha256: str

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return canonical_json(self.to_dict())


def export_record(record: EvidenceSet) -> dict:
    """Record for a public export: line, document, actor and stratum ids hashed."""
    out = record.to_dict()
    for key in ("case_id", "purchase_document", "clearing_actor"):
        if out[key] is not None:
            out[key] = sha256_text(out[key])[:16]
    out["strata"] = {
        k: (sha256_text(v)[:16] if k in ("company", "vendor") and v is not None else v)
        for k, v in out["strata"].items()
    }
    return out
