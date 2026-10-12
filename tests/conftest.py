from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import dataclasses

import pytest
import yaml

from p2p_replay.config import DeclarationPatterns, P2PPatterns
from p2p_replay.model import Case, Event

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
BASE = datetime(2018, 3, 1, 12, 0, tzinfo=timezone.utc)


def _patterns(cls, raw: dict):
    # Built here without calling the code under test, so that module import never
    # runs a mutant (mutmut); tests/test_pipeline.py checks load_patterns() equals these.
    kwargs = {}
    for f in dataclasses.fields(cls):
        value = raw[f.name]
        kwargs[f.name] = frozenset(value) if isinstance(value, list) else value
    return cls(**kwargs)


_RAW_PATTERNS = yaml.safe_load((ROOT / "prereg" / "outcome-patterns.yaml").read_text(encoding="utf-8"))
P2P = _patterns(P2PPatterns, _RAW_PATTERNS["bpi2019"])
DECL = _patterns(DeclarationPatterns, _RAW_PATTERNS["bpi2020"])
MAPPING = yaml.safe_load((ROOT / "prereg" / "column-mapping.yaml").read_text(encoding="utf-8"))["bpi2019"]
FLAG_TRUE = MAPPING["flag_true"]

THREE_WAY_AFTER = {"gr_based_iv": "true", "goods_receipt_required": "true", "item_type": "Standard"}
THREE_WAY_BEFORE = {"gr_based_iv": "false", "goods_receipt_required": "true", "item_type": "Standard"}
TWO_WAY = {"gr_based_iv": "false", "goods_receipt_required": "false", "item_type": "Standard"}


def at(days: float) -> datetime:
    return BASE + timedelta(days=days)


def ev(activity: str, days: float, actor: str | None = "user_1", value: float | None = None) -> Event:
    return Event(activity, at(days), actor, value)


def make_case(events, attrs=None, case_id="L1") -> Case:
    base = {"purchase_document": "P1", "company": "c", "spend_area": "s", "vendor": "v"}
    base.update(THREE_WAY_AFTER if attrs is None else attrs)
    return Case.build(case_id, base, events)


@pytest.fixture
def p2p():
    return P2P


@pytest.fixture
def decl():
    return DECL
