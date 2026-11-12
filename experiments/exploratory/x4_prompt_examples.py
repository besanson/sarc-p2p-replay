"""X4, exploratory: what the model families were shown and asked, on a synthetic line (DECISIONS.md D-G-1 d).

The registered ERP view template (prereg/erp-view-template.txt) verbatim, with its SHA-256; one synthetic
line from the test fixtures (tests/fixtures/mini2019.xes) rendered at its decision point t* as the ERP view
and as the exploratory timeline view, by the code E4 used (p2p_replay.view.render,
experiments.e4_sample.timeline_view, corrected in 1.1.1, DECISIONS.md D-G-3); the Haiku request body and the Jev request, built for that line by
the E4 request code (experiments.e4_run.haiku_params, jev_wire), the Jev one with the template's
reply-format sentence replaced by a typed choice (the deviation "E4 Jev request format"); and the fields
each view exposes and omits. Nothing from a real line. No model is called.

Writes results/exploratory/prompt-examples.json and paper/appendix-prompts.md (generated from it).

Usage: python -m experiments.exploratory.x4_prompt_examples
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from experiments.common import write_json
from experiments.e4_run import haiku_params, jev_wire
from experiments.e4_sample import timeline_view
from p2p_replay.category import category_of
from p2p_replay.config import REGISTRATION, ROOT, TEMPLATE_PATH, W_DAYS, load_mapping, load_patterns
from p2p_replay.reader import read_log
from p2p_replay.replay import observation_end, verdict_at_decision_point
from p2p_replay.view import render, view_fields

FIXTURE = ROOT / "tests" / "fixtures" / "mini2019.xes"
LINE = "B_stale_receipt_3way_before"
OUT = ROOT / "results" / "exploratory" / "prompt-examples.json"
APPENDIX = ROOT / "paper" / "appendix-prompts.md"
OMITTED = ["the event timeline", "actor names", "line, document, company and vendor identifiers"]


def build(fixture: Path = FIXTURE, line: str = LINE) -> dict[str, Any]:
    mapping = load_mapping("bpi2019")
    p, _ = load_patterns()
    flag_true = mapping.get("flag_true", ["true"])
    end = observation_end(read_log(fixture, mapping), 1)  # the fixture's months are small, as in the tests
    case = next(c for c in read_log(fixture, mapping) if c.case_id == line).truncated(end.t_end)
    category = category_of(case, flag_true)
    t_star, verdict = verdict_at_decision_point(case, category, p, W_DAYS, amended=True)
    erp, timeline = render(case, t_star, p, flag_true), timeline_view(case, t_star)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    return {
        "exploratory": True, "label": "exploratory, not registered; a synthetic fixture line, no real line",
        "registration": REGISTRATION, "decision": "DECISIONS.md D-G-1 d",
        "template": {"path": "prereg/erp-view-template.txt", "sha256": hashlib.sha256(template.encode("utf-8")).hexdigest(),
                     "text": template},
        "synthetic_line": {"source": "tests/fixtures/mini2019.xes", "case_id": line, "category": category.value,
                           "t_star": t_star.isoformat(), "gate_verdict": "allow" if verdict.allow else "hold",
                           "failed_predicates": list(verdict.failed)},
        "views": {"erp_view": erp, "timeline_view_exploratory": timeline},
        "renders": {"erp_view": bool(erp.strip()) and "{" + "category}" not in erp,
                    "timeline_view": bool(timeline.strip())},
        "requests": {
            "haiku": haiku_params(erp),
            "jev": json.loads(jev_wire(erp)),
            "jev_deviation": "the template's closing reply-format sentence (a JSON decision and hold probability) is "
                             "omitted from the Jev context and replaced by a typed choice with the labels clear and hold "
                             "(prereg/DEVIATIONS.md, E4 Jev request format)",
        },
        "fields": {
            "erp_view_exposes": sorted(view_fields(case, t_star, p, flag_true)),
            "erp_view_omits": OMITTED,
            "timeline_view_exposes": ["the template's task paragraph", "event date", "activity", "value in EUR"],
            "timeline_view_rule": "events at or before t*, without the decision's own clearing when t* is a clearing "
                                  "(DECISIONS.md D-G-3; the 1.1.0 view showed it)",
            "timeline_view_omits": ["the ERP record's derived fields (approved price, invoice and receipt status, "
                                    "changes since approval, payment block)", "actor names",
                                    "line, document, company and vendor identifiers"],
        },
        "not_separated": "the design does not separate wording, structure and information content: the two views "
                         "differ in all three at once",
    }


def appendix(doc: dict[str, Any]) -> str:
    line, req = doc["synthetic_line"], doc["requests"]
    fence = lambda text, lang="": f"```{lang}\n{text.rstrip()}\n```"  # noqa: E731
    f = doc["fields"]
    return "\n".join([
        "<!-- paper/appendix-prompts.md: generated by experiments/exploratory/x4_prompt_examples.py from "
        "results/exploratory/prompt-examples.json; do not edit. -->",
        "## Appendix: What the models were shown (exploratory)", "",
        "Exploratory and illustrative. A synthetic line from the test fixtures, never a real line, rendered by the "
        "code the agent replay used. The design does not separate wording, structure and information content: the "
        "two views differ in all three at once.", "",
        f"The registered template, `{doc['template']['path']}`, verbatim (SHA-256 `{doc['template']['sha256']}`):", "",
        fence(doc["template"]["text"]), "",
        f"The synthetic line `{line['case_id']}` ({line['category']}) at its decision point {line['t_star']}, "
        f"gate verdict {line['gate_verdict']}, failed predicates {', '.join(line['failed_predicates']) or 'none'}.", "",
        "The ERP view (registered):", "", fence(doc["views"]["erp_view"]), "",
        "The timeline view (exploratory), as corrected in 1.1.1: the events up to the decision point without the "
        "decision's own clearing; the opening paragraph is the template's, unchanged:", "",
        fence(doc["views"]["timeline_view_exploratory"]), "",
        "The Haiku request body:", "", fence(json.dumps(req["haiku"], indent=2, ensure_ascii=False), "json"), "",
        f"The Jev request ({req['jev_deviation']}):", "", fence(json.dumps(req["jev"], indent=2, ensure_ascii=False), "json"), "",
        "| view | exposes | omits |", "|---|---|---|",
        f"| ERP view | {', '.join(f['erp_view_exposes'])} | {'; '.join(f['erp_view_omits'])} |",
        f"| timeline view | {', '.join(f['timeline_view_exposes'])} | {'; '.join(f['timeline_view_omits'])} |", "",
    ])


def run(out: Path = OUT, appendix_path: Path = APPENDIX) -> dict[str, Any]:
    doc = build()
    write_json(out, doc)
    appendix_path.write_text(appendix(doc), encoding="utf-8")
    return doc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.exploratory.x4_prompt_examples")
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--appendix", type=Path, default=APPENDIX)
    args = parser.parse_args(argv)
    doc = run(args.out, args.appendix)
    print(f"X4: {doc['synthetic_line']['case_id']} renders: {doc['renders']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
