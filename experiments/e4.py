"""E4 analysis (prereg/p7-v1.1.md sections 4 and 7), from the committed responses only. No call.

Reads results/e4/sample.json, the per-family responses (responses/<arm>/<family>/responses.jsonl)
and results/e2/hypotheses.json, and writes:

  results/e4/h4.json      per family: hold rate on defective and on clean lines (invalid replies
                          count as neither), d = defective minus clean, TOST with unpooled SE
                          against -0.05 and +0.05, p_TOST = max of the two one-sided p-values;
                          then Holm over H1, H2, H3 (p = 1, D-C-2 A), H4-Jev, H4-Haiku at 0.05
  results/e4/arms.json    per arm (people from the log, each family, the gate): hold rates,
                          Cohen's kappa of each family with the gate, value released on defective
                          lines, expected correctives, invalid counts, cost per decision
  results/e2/hypotheses.json   its `holm` field (the rest of the file is unchanged)

The exploratory arm (--arm e4-exploratory) writes results/e4-exploratory/ with the same
measures, labelled exploratory, and never enters Holm.

A family stopped before the full sample is reported on its completed lines and marked truncated.

Usage: python -m experiments.e4 [--arm e4|e4-exploratory]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Sequence

from experiments.common import one_sided_p, ratio, write_json
from experiments.e4_run import ARMS, FAMILIES, Log
from p2p_replay.config import REGISTRATION, ROOT

MARGIN = 0.05
ALPHA = 0.05
FAMILY_LABEL = {"jev": "H4-Jev", "haiku": "H4-Haiku"}


def tost(k_d: int, n_d: int, k_c: int, n_c: int, m: float = MARGIN) -> dict[str, Any]:
    """Two one-sided z-tests with unpooled SE: H0 d <= -m and H0 d >= +m."""
    if n_d == 0 or n_c == 0:
        return {"d": None, "se": None, "p_lower": None, "p_upper": None, "p_tost": None}
    pd, pc = k_d / n_d, k_c / n_c
    d = pd - pc
    se = math.sqrt(pd * (1 - pd) / n_d + pc * (1 - pc) / n_c)
    if se == 0:
        inside = -m < d < m
        p_lo = p_hi = 0.0 if inside else 1.0
    else:
        p_lo = one_sided_p((d + m) / se)
        p_hi = one_sided_p((m - d) / se)
    return {"d": d, "se": se, "z_lower": (d + m) / se if se else None, "z_upper": (m - d) / se if se else None,
            "p_lower": p_lo, "p_upper": p_hi, "p_tost": max(p_lo, p_hi)}


def kappa(a: Sequence[str], b: Sequence[str]) -> float | None:
    """Cohen's kappa of two hold/clear label sequences."""
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(x == "hold" for x in a) / n, sum(x == "hold" for x in b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


def holm(pvalues: dict[str, float], alpha: float = ALPHA) -> list[dict[str, Any]]:
    order = sorted(pvalues, key=lambda k: (pvalues[k], k))
    m = len(order)
    rows, running = [], 0.0
    for i, name in enumerate(order):
        adj = min(1.0, (m - i) * pvalues[name])
        running = max(running, adj)
        rows.append({"test": name, "p_raw": pvalues[name], "rank": i + 1, "multiplier": m - i,
                     "p_holm": running})
    stop = False
    for r in rows:  # step-down: stop at the first adjusted p at or above alpha
        stop = stop or r["p_holm"] >= alpha
        r["below_alpha"] = not stop
    return rows


def defect_rate_group(failed: Sequence[str]) -> str | None:
    """The E2 defect group whose O rate a released defective line carries."""
    if "D1" in failed:
        return "H1"
    if "D4" in failed:
        return "H2"
    return None


def family_calls(arm: str, family: str, root: Path = ROOT) -> tuple[dict[int, dict], dict[str, Any]]:
    log = Log(root / ARMS[arm][0] / family / "responses.jsonl")
    recs = log.records()
    calls = {r["order"]: r for r in recs if r.get("kind") == "call"}
    attempts = [r for r in recs if r.get("kind") == "attempt"]
    events = [r for r in recs if r.get("kind") == "run_event"]
    status = events[-1]["status"] if events else "NOT_RUN"
    spend = sum(float(r["charged_usd"]) for r in attempts)
    return calls, {"status": status, "lines_done": len(calls), "attempts": len(attempts), "spend_usd": spend,
                   "invalid": sum(1 for r in calls.values() if r["status"] == "invalid"),
                   "cost_usd_per_decision": spend / len(calls) if calls else None,
                   "returned_models": sorted({r["returned_model"] for r in calls.values()
                                              if r["returned_model"] != "unreported"})}


def analyse(arm: str = "e4", root: Path = ROOT) -> dict[str, Any]:
    sample = json.loads((root / "results" / "e4" / "sample.json").read_text(encoding="utf-8"))["lines"]
    hyp_path = root / "results" / "e2" / "hypotheses.json"
    hyp = json.loads(hyp_path.read_text(encoding="utf-8"))
    o_rate = {g: hyp["estimates"][g]["W60"]["defect_group"]["O_rate"] for g in ("H1", "H2")}
    n_total = len(sample)
    defective = [r for r in sample if r["status"] == "defective"]
    no_group = sum(1 for r in defective if defect_rate_group(r["failed"]) is None)

    def released_summary(released: Sequence[dict]) -> dict[str, Any]:
        expected = sum(o_rate[g] for r in released if (g := defect_rate_group(r["failed"])) is not None)
        return {"released_defective_lines": len(released),
                "value_released_on_defective_lines_eur": round(sum(r["value_eur"] for r in released), 2),
                "expected_correctives": expected,
                "released_defective_lines_without_e2_group": sum(1 for r in released
                                                                  if defect_rate_group(r["failed"]) is None)}

    arms: dict[str, Any] = {}
    # people, from the log (3.6): unclassified lines count as neither
    human = {s: [r for r in sample if r["status"] == s and r["human_arm"] != "unclassified"] for s in ("defective", "clean")}
    arms["people"] = {
        "source": "the log (section 3.6)",
        "defective": {"lines": len(human["defective"]), "held": sum(r["human_arm"] == "hold" for r in human["defective"])},
        "clean": {"lines": len(human["clean"]), "held": sum(r["human_arm"] == "hold" for r in human["clean"])},
        "unclassified": sum(1 for r in sample if r["human_arm"] == "unclassified"),
    } | released_summary([r for r in human["defective"] if r["human_arm"] == "release"])
    arms["gate"] = {"source": "gate verdict at t* (D-C-2 B): holds every defective line, allows every clean line",
                    "defective": {"lines": len(defective), "held": len(defective)},
                    "clean": {"lines": n_total - len(defective), "held": 0}} | released_summary([])

    h4: dict[str, Any] = {}
    for family in FAMILIES:
        calls, meta = family_calls(arm, family, root)
        rows = [(r, calls[r["order"]]) for r in sample if r["order"] in calls]
        valid = [(r, c) for r, c in rows if c["status"] == "ok"]
        k = {s: sum(1 for r, c in valid if r["status"] == s and c["decision"] == "hold") for s in ("defective", "clean")}
        n = {s: sum(1 for r, _ in valid if r["status"] == s) for s in ("defective", "clean")}
        truncated = meta["status"] != "COMPLETE"
        test = tost(k["defective"], n["defective"], k["clean"], n["clean"])
        gate_labels = ["hold" if r["status"] == "defective" else "clear" for r, _ in valid]
        model_labels = [c["decision"] for _, c in valid]
        released = [r for r, c in valid if r["status"] == "defective" and c["decision"] == "clear"]
        arms[family] = {
            "source": f"responses/{ARMS[arm][0].split('/', 1)[1]}/{family}/responses.jsonl",
            "status": meta["status"], "truncated": truncated,
            "lines_called": len(rows), "invalid": meta["invalid"],
            "invalid_by_status": {s: sum(1 for r, c in rows if r["status"] == s and c["status"] == "invalid")
                                  for s in ("defective", "clean")},
            "defective": {"lines": n["defective"], "held": k["defective"]},
            "clean": {"lines": n["clean"], "held": k["clean"]},
            "kappa_with_gate": kappa(model_labels, gate_labels),
            "agreement_with_gate": ratio(sum(a == b for a, b in zip(model_labels, gate_labels)), len(valid)),
            "spend_usd": meta["spend_usd"], "attempts": meta["attempts"],
            "cost_usd_per_decision": meta["cost_usd_per_decision"], "returned_models": meta["returned_models"],
        } | released_summary(released)
        h4[FAMILY_LABEL[family]] = {
            "family": family, "status": meta["status"], "truncated": truncated,
            "hold_rate_defective": ratio(k["defective"], n["defective"]),
            "hold_rate_clean": ratio(k["clean"], n["clean"]),
            "defective": {"lines": n["defective"], "held": k["defective"]},
            "clean": {"lines": n["clean"], "held": k["clean"]},
            "margin": MARGIN, **test,
        }
    for name in ("people", "gate"):
        a = arms[name]
        a["hold_rate_defective"] = ratio(a["defective"]["held"], a["defective"]["lines"])
        a["hold_rate_clean"] = ratio(a["clean"]["held"], a["clean"]["lines"])
    for family in FAMILIES:
        a = arms[family]
        a["hold_rate_defective"] = ratio(a["defective"]["held"], a["defective"]["lines"])
        a["hold_rate_clean"] = ratio(a["clean"]["held"], a["clean"]["lines"])

    label = "exploratory" if arm != "e4" else "primary"
    arms_doc = {"registration": REGISTRATION, "section": "7 (E4)", "arm": arm, "label": label,
                "amendment": "DECISIONS.md D-C-2 B", "sample_lines": n_total,
                "expected_correctives_rule": "released defective lines x the E2 O rate at W = 60 of their defect "
                                             "group: the H1 defect group if D1/D2 fails, else the H2 defect group "
                                             "if D4 fails; lines failing neither have no E2 group and are counted",
                "e2_o_rate_w60": o_rate, "defective_lines_without_e2_group": no_group,
                "arms": arms}
    h4_doc: dict[str, Any] = {"registration": REGISTRATION, "section": "4 (H4)", "arm": arm, "label": label,
                              "test": "TOST, two one-sided z-tests with unpooled SE against -m and +m; "
                                      "p_TOST = max of the two",
                              "margin": MARGIN, "families": h4}
    holm_doc = None
    if arm == "e4":
        p = {"H1": hyp["estimates"]["H1"]["W60"]["p_one_sided_raw"],
             "H2": hyp["estimates"]["H2"]["W60"]["p_one_sided_raw"],
             "H3": 1.0}
        notes = {"H3": "not computable (0 D5 failures); enters with p = 1 (DECISIONS.md D-C-2 A)"}
        for fam_label, entry in h4.items():
            p[fam_label] = entry["p_tost"] if entry["p_tost"] is not None else 1.0
            if entry["p_tost"] is None:
                notes[fam_label] = "not computable; enters with p = 1"
            elif entry["truncated"]:
                notes[fam_label] = f"family stopped {entry['status']}; p on the completed lines"
        holm_doc = {"family": ["H1", "H2", "H3", "H4-Jev", "H4-Haiku"], "alpha": ALPHA, "applied": True,
                    "method": "Holm step-down over the five-test family",
                    "notes": notes, "table": holm(p)}
        h4_doc["holm"] = holm_doc
    return {"arms": arms_doc, "h4": h4_doc, "holm": holm_doc}


def run(arm: str = "e4", root: Path = ROOT, out: Path | None = None, hypotheses: Path | None = None) -> dict[str, Any]:
    result = analyse(arm, root)
    out = out or (root / "results" / ("e4" if arm == "e4" else "e4-exploratory"))
    suffix = "" if arm == "e4" else "-exploratory"
    write_json(out / f"arms{suffix}.json", result["arms"])
    write_json(out / f"h4{suffix}.json", result["h4"])
    if result["holm"] is not None:
        hyp_path = hypotheses or (root / "results" / "e2" / "hypotheses.json")
        hyp = json.loads((root / "results" / "e2" / "hypotheses.json").read_text(encoding="utf-8"))
        hyp["holm"] = result["holm"]
        write_json(hyp_path, hyp)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.e4")
    parser.add_argument("--arm", choices=tuple(ARMS), default="e4")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--hypotheses", type=Path, default=None, help="where to write hypotheses.json (default results/e2)")
    args = parser.parse_args(argv)
    result = run(args.arm, out=args.out, hypotheses=args.hypotheses)
    for name, e in result["h4"]["families"].items():
        print(f"{name}: hold defective {e['hold_rate_defective']}, clean {e['hold_rate_clean']}, p_TOST {e['p_tost']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
