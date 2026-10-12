"""Event log readers: XES (plain or gzip) and CSV (plain or gzip).

Both map source attribute names to engine field names through the registered
column mapping (prereg/column-mapping.yaml). Only the fields in the mapping
are kept; every other attribute is dropped at read time, so free text and
vendor names never reach the replay.

XES: case attributes are the direct attribute children of <trace>; event
attributes are the direct attribute children of <event>. Nested attributes
(lists, containers) and log-level globals are ignored.

CSV: one row per event; the columns named by the mapping's `case` section are
read from the first row of each case.
"""

from __future__ import annotations

import csv
import gzip
import io
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterator, Mapping

from .model import Case, Event, parse_timestamp

ATTRIBUTE_TAGS = frozenset({"string", "date", "int", "float", "boolean", "id"})


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _open_binary(path: Path):
    return gzip.open(path, "rb") if path.suffix == ".gz" else path.open("rb")


def _float(text: str | None) -> float | None:
    if text is None or text.strip() == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _actor(raw: Mapping[str, str], event_map: Mapping[str, str]) -> str | None:
    for key in ("actor", "actor_fallback"):
        name = event_map.get(key)
        if name and raw.get(name) is not None:
            return raw[name]
    return None


def make_event(raw: Mapping[str, str], mapping: Mapping[str, Any]) -> Event:
    event_map = mapping["event"]
    activity = raw.get(event_map["activity"])
    stamp = raw.get(event_map["timestamp"])
    if activity is None or stamp is None:
        raise ValueError(f"event without activity or timestamp: {sorted(raw)}")
    value_key = event_map.get("value_eur")
    return Event(
        activity=activity,
        ts=parse_timestamp(stamp),
        actor=_actor(raw, event_map),
        value=_float(raw.get(value_key)) if value_key else None,
    )


def make_case(raw_attrs: Mapping[str, str], raw_events: list[Mapping[str, str]], mapping: Mapping[str, Any]) -> Case:
    case_map = mapping["case"]
    case_id = raw_attrs.get(case_map["case_id"])
    if case_id is None:
        raise ValueError("case without case id")
    attrs = {field: raw_attrs.get(source) for field, source in case_map.items() if field != "case_id"}
    return Case.build(case_id, attrs, (make_event(e, mapping) for e in raw_events))


def read_xes(path: Path, mapping: Mapping[str, Any]) -> Iterator[Case]:
    with _open_binary(Path(path)) as fh:
        stack: list[str] = []
        root = None
        trace_attrs: dict[str, str] = {}
        events: list[dict[str, str]] = []
        event_attrs: dict[str, str] = {}
        for kind, el in ET.iterparse(fh, events=("start", "end")):
            tag = _local(el.tag)
            if kind == "start":
                if root is None:
                    root = el
                stack.append(tag)
                if tag == "trace":
                    trace_attrs, events = {}, []
                elif tag == "event":
                    event_attrs = {}
                continue
            stack.pop()
            if tag in ATTRIBUTE_TAGS and stack:
                parent = stack[-1]
                if parent == "event":
                    event_attrs[el.get("key")] = el.get("value")
                elif parent == "trace":
                    trace_attrs[el.get("key")] = el.get("value")
            elif tag == "event":
                events.append(event_attrs)
            elif tag == "trace":
                yield make_case(trace_attrs, events, mapping)
                el.clear()
                if root is not None:
                    root.clear()


def read_csv(path: Path, mapping: Mapping[str, Any]) -> Iterator[Case]:
    """Rows of one case need not be adjacent; cases are yielded in first-seen order."""
    case_key = mapping["case"]["case_id"]
    with _open_binary(Path(path)) as fh:
        text = io.TextIOWrapper(fh, encoding="utf-8", newline="")
        order: list[str] = []
        attrs: dict[str, dict[str, str]] = {}
        rows: dict[str, list[dict[str, str]]] = {}
        for row in csv.DictReader(text):
            cid = row.get(case_key)
            if cid is None:
                raise ValueError(f"CSV row without column {case_key!r}")
            if cid not in rows:
                order.append(cid)
                attrs[cid] = row
                rows[cid] = []
            rows[cid].append(row)
    for cid in order:
        yield make_case(attrs[cid], rows[cid], mapping)


def read_log(path: Path, mapping: Mapping[str, Any]) -> Iterator[Case]:
    name = Path(path).name.lower()
    if name.endswith((".xes", ".xes.gz")):
        return read_xes(path, mapping)
    if name.endswith((".csv", ".csv.gz")):
        return read_csv(path, mapping)
    raise ValueError(f"unsupported log format: {path}")
