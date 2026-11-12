"""External reproduction attempts (FINAL-AUDIT item 11), recorded as found, from their GitHub issues.

For an attempt N reported in issue I: the issue is read with `gh api`, its body is kept unedited as
review-secondary/FN-reproduction-issue-I.md (with its SHA-256 in the record), and every figure of the record
results/reproduction/attempt-N.json is parsed from that body: reproducer, environment, dates, the data
files as verified, the command results, the counts of matching and differing files, the JSON files with
their differing-value counts and maximum absolute differences, the figure files, the timestamp format
difference, the test and gate failures, the class of the exception in the PDF step, and the first
download's mismatch and retry. Nothing is typed by hand; a figure the body does not state is null.

Usage: python scripts/reproduction_attempts.py --issue 1 --attempt 1 [--from-file BODY.md]
       python scripts/reproduction_attempts.py --issue 1 --attempt 2 --comment ID   (a re-run reported in a comment)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "reproduction"
REPO = "besanson/sarc-p2p-replay"


def fetch(issue: int) -> dict[str, Any]:
    r = subprocess.run(["gh", "api", f"repos/{REPO}/issues/{issue}"], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def _section(body: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", body, re.M | re.S)
    return m.group(1) if m else ""


def _table(text: str) -> list[list[str]]:
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in text.splitlines()
            if line.startswith("|")]
    return [r for r in rows[2:]] if len(rows) > 2 else []


def _bullets(text: str) -> dict[str, str]:
    return {m.group(1).strip(): m.group(2).strip() for m in re.finditer(r"^- ([^:\n]+): (.+)$", text, re.M)}


def _num(s: str) -> float:
    return float(s.replace(",", ""))


def parse(body: str) -> dict[str, Any]:
    body = body.replace("\r\n", "\n")
    env = _bullets(_section(body, "Environment"))
    commands = {r[0].strip("`"): r[1] for r in _table(_section(body, "Command Results"))}
    data = [{"file": r[0], "bytes": int(_num(r[1])), "sha256": r[2]} for r in _table(_section(body, "Dataset Verification"))]
    first = re.search(r"data: (\S+) SHA-256 ([0-9a-f]{64}) != registered ([0-9a-f]{64})", body)
    test_sec = _section(body, "Test Failure")
    failed_test = re.search(r"FAILED (\S+)", test_sec)
    counts = re.search(r"(\d+) failed, (\d+) passed", test_sec)
    ts = re.search(r"committed:\s+(\S+)\s*\nregenerated:\s+(\S+)", test_sec)
    ts_fields = re.search(r"showed (\w+) differing fields", test_sec)
    gate_sec = _section(body, "Gate Results")
    gates = {m.group(1): m.group(2) for m in re.finditer(r"^(G\d [^:]+): (\w+)", gate_sec, re.M)}
    g4 = re.search(r"lists (\w+) differing result JSON files \(([^)]*)\) and all (\w+) figure files", gate_sec)
    g9 = re.search(r"^(\w+Error): ", gate_sec, re.M)
    rep_sec = _section(body, "Reproduction Command Failure")
    rep_exc = re.findall(r"^(\w+Error): ", rep_sec, re.M)
    frames = re.findall(r'File "<checkout>/(\S+)", line (\d+), in (\w+)', rep_sec)
    sup_sec = _section(body, "Supplemental Hash Comparison")
    sup = re.search(r"(\d+) of (\d+) files matched; (\d+) differed", sup_sec)
    rows = _table(sup_sec)
    files = [{"file": r[0], "committed_sha256_prefix": r[1], "regenerated_sha256_prefix": r[2],
              "match": r[3].lower() == "yes"} for r in rows]
    diffs = []
    for r in _table(_section(body, "What The JSON Differences Show")):
        maxd = None if r[2].lower().startswith("not") else float(r[2])
        diffs.append({"file": r[0], "differing_values": int(_num(r[1])), "max_abs_difference": maxd, "kind": r[3]})
    word = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
    as_int = lambda w: int(w) if w.isdigit() else word.get(w.lower())  # noqa: E731
    reproducer = re.search(r"Reproduction attempted by ([^.\n]+?)\.\s*$", body, re.M)
    return {
        "reproducer": reproducer.group(1).strip() if reproducer else None,
        "environment": {
            "release": env.get("Release"), "commit": env.get("Commit", "").strip("`") or None,
            "operating_system": env.get("Operating system"),
            "architecture": (re.search(r"\b(arm64|x86_64|x86-64|aarch64)\b", env.get("Operating system", "")) or [None])[0],
            "python": env.get("Python"), "git": env.get("Git"), "pandoc": env.get("Pandoc"),
            "tex_engine": env.get("Tectonic") and f"Tectonic {env.get('Tectonic').split(',')[0]}",
        },
        "dates": {"initial_run_and_dataset_verification": env.get("Initial run started"),
                  "supplemental_checks": env.get("Supplemental checks")},
        "commands": commands,
        "data_as_verified": data,
        "first_download": ({"file": first.group(1), "sha256_got": first.group(2), "sha256_registered": first.group(3),
                            "deleted": "deleted" in body, "retried_and_passed": "Retried once" in commands.get("make bootstrap", "")}
                           if first else None),
        "tests": {"passed": int(counts.group(2)) if counts else None, "failed": int(counts.group(1)) if counts else None,
                  "failing_test": failed_test.group(1) if failed_test else None},
        "timeline_timestamps": {"differing_fields": as_int(ts_fields.group(1)) if ts_fields else None,
                                "committed_form": ts.group(1) if ts else None,
                                "regenerated_form": ts.group(2) if ts else None},
        "gates": gates,
        "g4_differing": ({"result_json_files": as_int(g4.group(1)),
                          "result_json_names": [x.strip(" `") for x in g4.group(2).split(",")],
                          "figure_files": as_int(g4.group(3))} if g4 else None),
        "g9_exception": g9.group(1) if g9 else None,
        "reproduce_exception": rep_exc[0] if rep_exc else None,
        "reproduce_traceback": [{"file": f, "line": int(n), "function": fn} for f, n, fn in frames],
        "report_written": not ("prevented" in rep_sec and "report.md" in rep_sec),
        "supplemental_comparison": {
            "matched": int(sup.group(1)) if sup else None, "compared": int(sup.group(2)) if sup else None,
            "differed": int(sup.group(3)) if sup else None,
            "files": files,
            "differing_figure_files": [f["file"] for f in files if not f["match"] and f["file"].startswith("paper/figures/")],
            "differing_other_files": [f["file"] for f in files if not f["match"] and not f["file"].startswith("paper/figures/")],
        },
        "json_differences": diffs,
        "max_abs_numeric_difference": max((d["max_abs_difference"] for d in diffs if d["max_abs_difference"] is not None),
                                          default=None),
        "reproducer_request": "keep the reproduction status pending" if "pending" in body.splitlines()[-1] else None,
    }


def fetch_comment(comment: int) -> dict[str, Any]:
    r = subprocess.run(["gh", "api", f"repos/{REPO}/issues/comments/{comment}"], capture_output=True, text=True,
                       check=True)
    return json.loads(r.stdout)


def parse_comment(body: str) -> dict[str, Any]:
    """A re-run reported in an issue comment (attempt 2 on, D-F-3): what was run, where it stopped, why."""
    body = body.replace("\r\n", "\n")
    tag = re.search(r"^## Reproduction attempt: (v[\d.]+)", body, re.M)
    commit = re.search(r"tag resolved to `([0-9a-f]{40})`", body)
    command = re.search(r"```sh\n(.+?)\n```", body, re.S)
    env = re.search(r"- Environment: ([^;]+), (arm64|x86_64|x86-64|aarch64); Python ([\d.]+)\.", body)
    date = re.search(r"- Run date: (\S+ UTC)", body)
    reproducer = re.search(r"- Reproduction attempted by ([^.\n]+?)\.\s*$", body, re.M)
    steps = re.findall(r"^reproduce: (.+)$", body, re.M)
    exc = re.findall(r"^(\w+Error): (?:\[Errno \d+\] [^:]+: )?'?([^'\n]*)'?$", body, re.M)
    frames = re.findall(r'File "<checkout>/(\S+)", line (\d+), in (\w+)', body)
    code = re.search(r"exited with code (\d+)", body)
    return {
        "reproducer": reproducer.group(1).strip() if reproducer else None,
        "tag": tag.group(1) if tag else None,
        "commit": commit.group(1) if commit else None,
        "command": command.group(1).strip() if command else None,
        "environment": {"operating_system": env.group(1) if env else None,
                        "architecture": env.group(2) if env else None, "python": env.group(3) if env else None},
        "run_date": date.group(1) if date else None,
        "steps_completed": steps[:-1] if steps else [],
        "stopped_in_step": steps[-1] if steps else None,
        "exception": exc[-1][0] if exc else None,
        "missing_path": exc[-1][1] if exc else None,
        "traceback": [{"file": f, "line": int(n), "function": fn} for f, n, fn in frames],
        "exit_code": int(code.group(1)) if code else None,
        "report_written": not bool(re.search(r"No `out/reproduce/report\.md` was written", body)),
        "comparison_reached": "comparison stage was not reached" not in body,
    }


def parse_report_comment(body: str) -> dict[str, Any]:
    """A completed re-run whose comment carries `make reproduce`'s report unchanged (attempt 3 on, D-F-5)."""
    body = body.replace("\r\n", "\n")
    head = re.search(r"^Commit `([0-9a-f]{40})` \(([^)]+)\); Python ([\d.]+); (\S+)\.$", body, re.M)
    title = re.search(r"^# Reproduction of (v[\d.]+)$", body, re.M)
    run = re.search(r"- Run: (\d{4}-\d{2}-\d{2}), (\d{2}:\d{2}:\d{2})\D+(\d{2}:\d{2}:\d{2}) UTC", body)
    env = re.search(r"Pandoc ([\d.]+) on PATH, Python ([\d.]+), (macOS [\d.]+) (arm64|x86_64|x86-64)", body)
    verdict = re.search(r"\*\*((?:NOT )?REPRODUCED[^*]*)\*\*", body)
    counts = re.search(r"(\d+) files equal \((\d+) byte-identical, (\d+) within tolerance, max difference ([\d.e+-]+)\)",
                       verdict.group(1)) if verdict else None
    rows = re.findall(r"^\| `([^`]+)` \| (yes|no) \| (yes|NO) \| ([^|]+) \|$", body, re.M)
    code = re.search(r"exited with code (\d+)", body)
    pdf = re.search(r"^For information: (.+)$", body, re.M)
    copied = body.split("Copied from the commit", 1)[1].split("Excluded as", 1)[0] if "Copied from the commit" in body else ""
    return {
        "tag": head.group(2) if head else None,
        "report_title_version": title.group(1) if title else None,
        "commit": head.group(1) if head else None,
        "command": "make reproduce",
        "environment": {"platform": head.group(4) if head else None,
                        "operating_system": env.group(3) if env else None,
                        "architecture": env.group(4) if env else None,
                        "python": env.group(2) if env else (head.group(3) if head else None),
                        "pandoc": env.group(1) if env else None},
        "run_utc": {"date": run.group(1), "start": run.group(2), "end": run.group(3)} if run else None,
        "exit_code": int(code.group(1)) if code else None,
        "report_written": verdict is not None,
        "comparison_reached": bool(rows),
        "verdict": verdict.group(1) if verdict else None,
        "files_equal": int(counts.group(1)) if counts else None,
        "byte_identical": int(counts.group(2)) if counts else None,
        "within_tolerance": int(counts.group(3)) if counts else None,
        "max_abs_difference": float(counts.group(4)) if counts else None,
        "files_compared": len(rows),
        "within_tolerance_files": [{"file": f, "max_abs_difference": float(d)} for f, b, w, d in rows
                                   if b == "no" and w == "yes"],
        "not_equal_files": [f for f, b, w, d in rows if w == "NO"],
        "copied_records": len(re.findall(r"^- `results/", copied, re.M)),
        "pdf": pdf.group(1) if pdf else None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="reproduction_attempts")
    parser.add_argument("--issue", type=int, required=True)
    parser.add_argument("--attempt", type=int, required=True)
    parser.add_argument("--from-file", type=Path, default=None, help="parse a saved body instead of fetching")
    parser.add_argument("--comment", type=int, default=None, help="the attempt is reported in this issue comment")
    args = parser.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    if args.comment is not None:
        c = fetch_comment(args.comment)
        path = ROOT / "review-secondary" / f"F{args.attempt}-reproduction-issue-{args.issue}-comment-{args.comment}.md"
        path.write_text(c["body"], encoding="utf-8")
        record = {"attempt": args.attempt, "issue": args.issue, "comment": args.comment,
                  "commented_by": c["user"]["login"], "created_at": c["created_at"], "url": c["html_url"],
                  "body": str(path.relative_to(ROOT)),
                  "body_sha256": hashlib.sha256(c["body"].encode("utf-8")).hexdigest()}
        if "# Reproduction of v" in c["body"]:
            record.update(parse_report_comment(c["body"]))
            # The report names no person; the reproducer is the one attempt 1 names, when the same account posts.
            first = json.loads((OUT / "attempt-1.json").read_text(encoding="utf-8"))
            record["reproducer"] = first["reproducer"] if first.get("opened_by") == record["commented_by"] else None
            record["reproducer_source"] = "results/reproduction/attempt-1.json (same GitHub account)"
            summary = f"{record['tag']}: {record['verdict']}"
        else:
            record.update(parse_comment(c["body"]))
            summary = (f"{record['tag']} stopped in {record['stopped_in_step']!r} on {record['exception']}; "
                       f"report written: {record['report_written']}")
        out = OUT / f"attempt-{args.attempt}.json"
        out.write_text(json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"attempt {args.attempt}: {summary}")
        return 0
    # The body is an unedited external text, kept with the other unedited reports.
    body_path = ROOT / "review-secondary" / f"F{args.attempt}-reproduction-issue-{args.issue}.md"
    if args.from_file:
        body, meta = args.from_file.read_text(encoding="utf-8"), {}
    else:
        issue = fetch(args.issue)
        body = issue["body"]
        meta = {"title": issue["title"], "opened_by": issue["user"]["login"], "created_at": issue["created_at"],
                "state": issue["state"], "url": issue["html_url"]}
        body_path.write_text(body, encoding="utf-8")
    record = {"attempt": args.attempt, "issue": args.issue, **meta,
              "body": str(body_path.relative_to(ROOT)),
              "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(), **parse(body)}
    out = OUT / f"attempt-{args.attempt}.json"
    out.write_text(json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    s = record["supplemental_comparison"]
    print(f"attempt {args.attempt}: {s['matched']} of {s['compared']} matched, {s['differed']} differed; "
          f"max numeric difference {record['max_abs_numeric_difference']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
