"""E5, derivation (prereg/p7-v1.1.md section 6, E5; claim C9) with paper 5's compiler, unmodified.

Paper 5's `authority_compiler.derive_authority_contract` (sarc-authority-derivation at the
engines.lock pin, imported from the sibling checkout; no fork, no patch) receives, per item
category:

- reachable states: the E1 verdict relation of that category (results/e1/evidence-set.jsonl.gz),
  one state per distinct combination of the evidence-set observations below (repeated
  clearings with identical observations are one state; the count of clearings is reported);
- candidate context: those observations, each with the values it takes in the category;
- the loss model: exactly the three registered declared losses, as predicates over the state.

Observations (one per registered predicate input in the evidence set, plus the clearing's
position on its line):

  receipts          inputs.uncancelled_receipts    read by D1 and D2
  invoices          inputs.invoice_receipts        read by D3
  changes           inputs.changes_since_approval  read by D4
  distinct_actors   predicates.D5 (pass/fail/unknown; the evidence set records D5's value,
                    not the creator's actor)        read by D5
  blocks            inputs.open_payment_blocks     read by D6
  closed            inputs.line_closed_balance     read by D7
  clearing_ordinal  the clearing's position among the line's analysed clearings, from the
                    evidence set's own case_id and t_c   read by no predicate

Losses (registration section 6, E5):

  L1 pay for goods not received: the category requires a goods receipt and receipts <= 0
  L2 pay twice:                  clearing_ordinal > invoices (more clearings than invoices)
  L3 pay a changed amount:       changes > 0

The derived contract is the set of registered predicates whose observation is in the
compiler's minimum-cardinality reduct; it is compared with the category's registered
contract (section 3.1). Writes results/e5/derivation.json and, per category, the compiler's
full output and witnesses as results/e5/trace-<category>.json.

Usage: python -m experiments.e5 [--e1 results/e1] [--out results/e5]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from collections import Counter, defaultdict
from dataclasses import asdict, make_dataclass
from pathlib import Path
from typing import Any, Callable

from experiments.common import read_jsonl_gz, write_json
from p2p_replay.config import REGISTRATION, ROOT

DEFAULT_E1 = ROOT / "results" / "e1"
DEFAULT_OUT = ROOT / "results" / "e5"
SIBLING = "sarc-authority-derivation"

FIELDS = ("receipts", "invoices", "changes", "distinct_actors", "blocks", "closed", "clearing_ordinal")
FIELD_PREDICATES = {
    "receipts": ("D1", "D2"), "invoices": ("D3",), "changes": ("D4",), "distinct_actors": ("D5",),
    "blocks": ("D6",), "closed": ("D7",), "clearing_ordinal": (),
}
REGISTERED_CONTRACT = {
    "3-way, invoice after receipt": ("D1", "D2", "D3", "D4", "D5", "D6", "D7"),
    "3-way, invoice before receipt": ("D1", "D2", "D3", "D4", "D5", "D6", "D7"),
    "2-way": ("D3", "D4", "D5", "D6", "D7"),
}
REQUIRES_RECEIPT = {"3-way, invoice after receipt", "3-way, invoice before receipt"}
# Paper 5's compiler reads states as dataclasses (participation._fingerprint uses dataclasses.fields).
State = make_dataclass("State", [(f, Any) for f in FIELDS], frozen=True, order=True)
LOSSES = {
    "L1": "pay for goods not received: the category requires a goods receipt and receipts <= 0",
    "L2": "pay twice: clearing_ordinal > invoices",
    "L3": "pay a changed amount: changes > 0",
}


def sibling_path(root: Path = ROOT) -> tuple[Path, str]:
    lock = tomllib.loads((root / "engines.lock").read_text(encoding="utf-8"))[SIBLING]
    path = (root / lock["path"]).resolve()
    head = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()
    if head != lock["commit"]:
        raise RuntimeError(f"{SIBLING} is at {head}, not at its engines.lock pin {lock['commit']}")
    return path, head


def import_compiler(path: Path):
    for p in (str(path / "src"), str(path)):
        if p not in sys.path:
            sys.path.insert(0, p)
    from authority_compiler import derive_authority_contract  # noqa: PLC0415
    from reduct import compute_core  # noqa: PLC0415

    return derive_authority_contract, compute_core


def loss_model(category: str) -> dict[str, Callable[[State], bool]]:
    requires = category in REQUIRES_RECEIPT
    return {
        "L1": lambda s: requires and s.receipts <= 0,
        "L2": lambda s: s.clearing_ordinal > s.invoices,
        "L3": lambda s: s.changes > 0,
    }


def states(records: list[dict]) -> dict[str, Counter]:
    """Per category, the distinct states with the number of analysed clearings each stands for."""
    by_line: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_line[r["case_id"]].append(r)
    out: dict[str, Counter] = defaultdict(Counter)
    for rows in by_line.values():
        for i, r in enumerate(sorted(rows, key=lambda r: r["t_c"]), start=1):
            inp = r["inputs"]
            out[r["category"]][State(inp["uncancelled_receipts"], inp["invoice_receipts"],
                                     inp["changes_since_approval"], r["predicates"]["D5"],
                                     inp["open_payment_blocks"], inp["line_closed_balance"], i)] += 1
    return out


def predicates_of(fields) -> list[str]:
    return sorted({p for f in fields for p in FIELD_PREDICATES[f]})


def derive(category: str, counts: Counter, derive_contract, compute_core) -> tuple[dict, dict]:
    reachable = sorted(counts, key=lambda s: tuple(str(getattr(s, f)) for f in FIELDS))
    model = loss_model(category)
    context = {f: sorted({getattr(s, f) for s in reachable}, key=str) for f in FIELDS}
    contract = derive_contract(model, reachable, context)
    _, _, witnesses = compute_core(reachable, model, FIELDS)
    min_card = sorted(contract.minimum_cardinality_reduct)
    derived = predicates_of(min_card)
    registered = list(REGISTERED_CONTRACT[category])
    equal = derived == registered
    reducts = sorted(sorted(r) for r in contract.minimal_reducts) if contract.minimal_reducts is not None else None
    loss_states = {name: sum(counts[s] for s in reachable if fn(s)) for name, fn in model.items()}
    summary = {
        "analysed_clearings": sum(counts.values()),
        "distinct_states": len(reachable),
        "clearings_per_loss": loss_states,
        "clearings_with_any_loss": sum(counts[s] for s in reachable if any(fn(s) for fn in model.values())),
        "core_fields": sorted(contract.core_attributes),
        "minimal_reducts": reducts,
        "contracts_of_minimal_reducts": [predicates_of(r) for r in reducts] if reducts is not None else None,
        "minimum_cardinality_field_set": min_card,
        "derived_contract": derived,
        "registered_contract": registered,
        "equal": equal,
        "registered_not_derived": [p for p in registered if p not in derived],
        "derived_not_registered": [p for p in derived if p not in registered],
        "fields_outside_every_predicate": [f for f in min_card if not FIELD_PREDICATES[f]],
        "result": "reproduces" if equal else "does not reproduce",
    }
    trace = {
        "registration": REGISTRATION, "category": category, "compiler": "authority_compiler.derive_authority_contract",
        "losses": LOSSES, "candidate_context": context,
        "core_attributes": sorted(contract.core_attributes),
        "redundant_attributes": sorted(contract.redundant_attributes),
        "minimal_reducts": reducts, "minimal_reducts_note": contract.minimal_reducts_note,
        "minimum_cardinality_reduct": min_card,
        "minimum_cost_reduct": None,
        "sufficiency_certificate": contract.sufficiency_certificate,
        "counterexamples": contract.counterexamples,
        "reachability_dependencies": sorted(contract.reachability_dependencies),
        "candidate_property_count": contract.candidate_property_count,
        "reachable_tuple_count": contract.reachable_tuple_count,
        "core_witnesses": witnesses,
        "states": [{"state": asdict(s), "clearings": counts[s],
                    "losses": [n for n, fn in model.items() if fn(s)]} for s in reachable],
    }
    return summary, trace


def slug(category: str) -> str:
    return category.replace(",", "").replace(" ", "-")


def run(e1_dir: Path = DEFAULT_E1, out: Path = DEFAULT_OUT, root: Path = ROOT) -> dict[str, Any]:
    path, head = sibling_path(root)
    derive_contract, compute_core = import_compiler(path)
    import authority_compiler  # noqa: PLC0415

    per = states(read_jsonl_gz(e1_dir / "evidence-set.jsonl.gz"))
    categories: dict[str, Any] = {}
    for category in sorted(per):
        summary, trace = derive(category, per[category], derive_contract, compute_core)
        categories[category] = summary
        write_json(out / f"trace-{slug(category)}.json", trace)
    doc = {
        "registration": REGISTRATION, "section": "6, E5", "claim": "C9",
        "compiler": {"repository": SIBLING, "commit": head, "entry_point": "authority_compiler.derive_authority_contract",
                     "version": getattr(authority_compiler, "__version__", None), "modified": False},
        "losses": LOSSES,
        "fields": {f: list(FIELD_PREDICATES[f]) for f in FIELDS},
        "derived_contract_rule": "registered predicates whose observation is in the minimum-cardinality reduct",
        "categories": categories,
    }
    write_json(out / "derivation.json", doc)
    return doc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.e5")
    parser.add_argument("--e1", type=Path, default=DEFAULT_E1)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    doc = run(args.e1, args.out)
    for category, s in doc["categories"].items():
        print(f"E5 {category}: {s['result']}; minimum-cardinality field set {s['minimum_cardinality_field_set']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
