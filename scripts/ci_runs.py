"""results/ci-runs.json: the GitHub Actions runs of the CI workflow on given commits (FINAL-AUDIT item 1).

Read from the GitHub API with `gh api` (never typed): for each commit, every run of
.github/workflows/ci.yml with its id, URL, status and conclusion, and each matrix job (Python 3.11
and 3.12) with its id, URL and conclusion. A commit is green when its latest completed run succeeded
on both versions.

Usage: python scripts/ci_runs.py SHA [SHA ...]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REPO = "besanson/sarc-p2p-replay"
WORKFLOW = ".github/workflows/ci.yml"
VERSIONS = ("3.11", "3.12")
OUT = ROOT / "results" / "ci-runs.json"


def gh(path: str) -> Any:
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def commit_runs(sha: str) -> dict[str, Any]:
    full = subprocess.run(["git", "-C", str(ROOT), "rev-parse", sha], capture_output=True, text=True,
                          check=True).stdout.strip()
    runs = [r for r in gh(f"repos/{REPO}/actions/runs?head_sha={full}&per_page=100")["workflow_runs"]
            if r["path"] == WORKFLOW]
    out = []
    for r in sorted(runs, key=lambda r: r["id"]):
        jobs = gh(f"repos/{REPO}/actions/runs/{r['id']}/jobs")["jobs"]
        out.append({"run_id": r["id"], "url": r["html_url"], "event": r["event"], "status": r["status"],
                    "conclusion": r["conclusion"],
                    "jobs": [{"name": j["name"], "job_id": j["id"], "url": j["html_url"], "conclusion": j["conclusion"]}
                             for j in sorted(jobs, key=lambda j: j["name"])]})
    done = [r for r in out if r["status"] == "completed"]
    latest = done[-1] if done else None
    green = bool(latest) and latest["conclusion"] == "success" and all(
        any(j["name"] == f"test ({v})" and j["conclusion"] == "success" for j in latest["jobs"]) for v in VERSIONS)
    return {"commit": full, "runs": out, "green_on": list(VERSIONS) if green else [], "green": green}


def main(argv: list[str] | None = None) -> int:
    shas = (argv if argv is not None else sys.argv[1:])
    if not shas:
        raise SystemExit("usage: python scripts/ci_runs.py SHA [SHA ...]")
    doc = {"audit_item": 1, "gate": "G1", "workflow": WORKFLOW, "repository": REPO,
           "source": "GitHub REST API via gh api", "commits": [commit_runs(s) for s in shas]}
    doc["all_green"] = all(c["green"] for c in doc["commits"])
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for c in doc["commits"]:
        print(f"{c['commit'][:7]}: {'green on ' + ', '.join(c['green_on']) if c['green'] else 'not green'}")
    return 0 if doc["all_green"] else 1


if __name__ == "__main__":
    sys.exit(main())
