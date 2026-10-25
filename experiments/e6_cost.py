"""E6, cost part (prereg/p7-v1.1.md section 6, E6): USD per decision per family, from the responses.

Reads every responses file under responses/e4/ and responses/e4-exploratory/ and the manifest,
and writes results/e6/cost.json: per arm and family the decisions made (lines with a final call
record), attempts, tokens, spend and USD per decision; the total against the cap.

Usage: python -m experiments.e6_cost
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from experiments.common import write_json
from experiments.e4_run import ARMS, CAP_USD, FAMILIES, Log
from p2p_replay.config import REGISTRATION, ROOT


def run(root: Path = ROOT, out: Path | None = None) -> dict[str, Any]:
    arms: dict[str, Any] = {}
    total = 0.0
    for arm, (directory, _) in ARMS.items():
        for family in FAMILIES:
            path = root / directory / family / "responses.jsonl"
            if not path.exists():
                continue
            recs = Log(path).records()
            attempts = [r for r in recs if r.get("kind") == "attempt"]
            calls = [r for r in recs if r.get("kind") == "call"]
            events = [r for r in recs if r.get("kind") == "run_event"]
            spend = sum(float(r["charged_usd"]) for r in attempts)
            total += spend
            arms.setdefault(arm, {})[family] = {
                "label": "exploratory" if arm != "e4" else "primary",
                "status": events[-1]["status"] if events else "NOT_RUN",
                "decisions": len(calls), "attempts": len(attempts),
                "input_tokens": sum(r.get("usage_input_tokens") or 0 for r in attempts),
                "output_tokens": sum(r.get("usage_output_tokens") or 0 for r in attempts),
                "spend_usd": spend,
                "usd_per_decision": spend / len(calls) if calls else None,
            }
    doc = {"registration": REGISTRATION, "section": "6, E6 (cost)",
           "rule": "spend charged by every attempt (retries and re-requests included) / decisions made; "
                   "token prices as recorded in responses/e4/manifest-e4.json",
           "cap_usd": CAP_USD, "spend_usd_total": total, "arms": arms}
    write_json((out or root / "results" / "e6") / "cost.json", doc)
    return doc


def main(argv: list[str] | None = None) -> int:
    doc = run()
    print(f"E6 cost: USD {doc['spend_usd_total']:.4f} of {doc['cap_usd']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
