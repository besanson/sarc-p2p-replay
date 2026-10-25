"""E7 vocabulary check (prereg/p7-v1.1.md section 8; prereg/outcome-patterns.yaml bpi2020).

Over data/InternationalDeclarations.xes.gz and data/DomesticDeclarations.xes.gz (SHA-256 checked
against prereg/data.lock): every activity name with its count per log; for each registered
bpi2020 list, which names occur and which do not (an absent name is reported with a zero count
and is not replaced); every case and event attribute key with its count; the latest timestamp
per log (T_end', section 8, unchanged by v1.1); and whether every attribute the registered
column mapping names for bpi2020 occurs in each log. A mapped attribute absent from a log is a
stop: the runner exits 3 and E7 does not run.

Writes results/e7/vocabulary.json.

Usage: python -m experiments.e7_check
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import tomllib
from pathlib import Path
from typing import Any

import yaml

from experiments.common import write_json
from experiments.e0 import mapped_keys, raw_inventory
from p2p_replay.config import MAPPING_PATH, PATTERNS_PATH, REGISTRATION, ROOT, load_mapping

LOGS = {"international": "bpi2020_international", "domestic": "bpi2020_domestic"}
LISTS = ("payment", "approval", "final_approval_required_role", "resubmission", "outcome_prime")
DEFAULT_OUT = ROOT / "results" / "e7"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def run(out: Path = DEFAULT_OUT, root: Path = ROOT, data: Path | None = None,
        lock: dict[str, Any] | None = None) -> dict[str, Any]:
    lock = lock if lock is not None else tomllib.loads((root / "prereg" / "data.lock").read_text(encoding="utf-8"))
    patterns = yaml.safe_load(PATTERNS_PATH.read_text(encoding="utf-8"))["bpi2020"]
    mapping = load_mapping("bpi2020", MAPPING_PATH)
    keys = mapped_keys(mapping)
    logs: dict[str, Any] = {}
    stop = False
    for name, lock_key in LOGS.items():
        entry = lock[lock_key]
        path = (data or root / "data") / entry["file"]
        sha = file_sha256(path)
        if sha != entry["sha256"]:
            raise RuntimeError(f"{entry['file']}: SHA-256 differs from prereg/data.lock")
        inv = raw_inventory(path, creation="")
        missing_case = [k for k in keys["case"] if k not in inv["trace_keys"]]
        missing_event = [k for k in keys["event"] if k not in inv["event_keys"]]
        stop = stop or bool(missing_case or missing_event)
        logs[name] = {
            "file": entry["file"], "sha256": sha, "traces": inv["traces"], "events": inv["events"],
            "t_end_prime": inv["latest_timestamp"].isoformat() if inv["latest_timestamp"] else None,
            "activities": inv["activities"],
            "case_attribute_keys": inv["trace_keys"], "event_attribute_keys": inv["event_keys"],
            "mapped_attributes_missing": {"case": missing_case, "event": missing_event},
        }
    registered = {}
    for lst in LISTS:
        names = patterns[lst]
        registered[lst] = {
            n: {log: logs[log]["activities"].get(n, 0) for log in LOGS} for n in names}
    absent = sorted({n for lst in registered.values() for n, c in lst.items() if not any(c.values())})
    absent_per_log = {log: sorted({n for lst in registered.values() for n, c in lst.items() if c[log] == 0})
                      for log in LOGS}
    doc = {
        "registration": REGISTRATION, "section": "8", "patterns": str(PATTERNS_PATH.relative_to(ROOT)),
        "mapping_keys": keys, "logs": logs, "registered_lists": registered,
        "registered_names_absent_from_both_logs": absent,
        "registered_names_absent_per_log": absent_per_log,
        "rule": "an absent registered name is reported with a zero count and stays in its list (not replaced)",
        "stop": stop,
        "stop_rule": "a mapped attribute absent from a log stops E7",
    }
    write_json(out / "vocabulary.json", doc)
    return doc


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(prog="experiments.e7_check").parse_args(argv)
    doc = run()
    print(f"E7 vocabulary: absent from both logs {doc['registered_names_absent_from_both_logs']}; "
          f"stop: {doc['stop']}")
    return 3 if doc["stop"] else 0


if __name__ == "__main__":
    sys.exit(main())
