"""`make fresh-clone-check`: REPRODUCE.md's commands, in order, in a fresh clone of this checkout at HEAD
(D-F-3, D-F-4; FINAL-AUDIT item 9). No release is pushed before it passes.

In a new temporary directory: `git clone` the local checkout (file:// URL) at HEAD; link the three data
files of data/ into the clone's data/ (bootstrap then verifies them by size and SHA-256 and downloads
nothing); then `make bootstrap`, `make test`, `make gates`, `make reproduce`, as REPRODUCE.md lists them.
It passes when every command exits 0, `make gates` leaves the clone's tracked files unchanged, and
`make reproduce` writes out/reproduce/report.md with the verdict REPRODUCED. Uncommitted changes in this
checkout are not in the clone: commit first.

Writes out/fresh-clone-check/summary.json (the commit, each command's exit code and time, the gates'
cleanliness, the report's verdict line and counts) and the clone's report.md beside it.

Usage: python scripts/fresh_clone_check.py [--keep]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "fresh-clone-check"
COMMANDS = ("make bootstrap", "make test", "make gates", "make reproduce")


def run(cmd: str, cwd: Path, log) -> tuple[int, float, str]:
    start = time.time()
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    out = r.stdout + r.stderr
    log.write(f"$ {cmd}   (cwd {cwd})\n{out}\nexit {r.returncode}\n\n")
    log.flush()
    return r.returncode, round(time.time() - start, 1), out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fresh_clone_check")
    parser.add_argument("--keep", action="store_true", help="keep the temporary clone")
    args = parser.parse_args(argv)
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"],
                           capture_output=True, text=True).stdout.strip()
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True)
    base = Path(tempfile.mkdtemp(prefix="fresh-clone-"))
    clone = base / ROOT.name  # siblings land beside it, at the engines.lock paths
    summary: dict = {"commit": head, "uncommitted_changes_in_checkout": bool(dirty), "clone": str(clone),
                     "commands": [], "passed": False}
    with (OUT / "log.txt").open("w", encoding="utf-8") as log:
        code, _, _ = run(f"git clone -q file://{ROOT} {clone} && git -C {clone} checkout -q {head}", base, log)
        summary["clone_exit"] = code
        if code == 0:
            lock = tomllib.loads((ROOT / "prereg" / "data.lock").read_text(encoding="utf-8"))
            (clone / "data").mkdir(exist_ok=True)
            for entry in lock.values():
                (clone / "data" / entry["file"]).symlink_to(ROOT / "data" / entry["file"])
            for cmd in COMMANDS:
                code, seconds, out = run(cmd, clone, log)
                row = {"command": cmd, "exit": code, "seconds": seconds}
                if cmd == "make test":
                    m = re.search(r"(\d+) passed(?:, (\d+) skipped)?", out)
                    row["tests_passed"] = int(m.group(1)) if m else None
                    row["tests_skipped"] = int(m.group(2)) if m and m.group(2) else 0
                if cmd == "make gates":
                    m = re.search(r"^gates: (.+)$", out, re.M)
                    row["gates_summary"] = m.group(1) if m else None
                    status = subprocess.run(["git", "-C", str(clone), "status", "--porcelain", "--untracked-files=no"],
                                            capture_output=True, text=True).stdout.strip()
                    row["tracked_files_unchanged"] = status == ""
                    summary["tracked_files_unchanged_after_gates"] = status == ""
                summary["commands"].append(row)
                if code != 0:
                    break
    report = clone / "out" / "reproduce" / "report.md"
    if report.exists():
        text = report.read_text(encoding="utf-8")
        shutil.copyfile(report, OUT / "report.md")
        verdict = re.search(r"\*\*(.+?)\*\*", text)
        summary["verdict"] = verdict.group(1) if verdict else None
        summary["rows"] = len(re.findall(r"^\| `", text, re.M))
        summary["rows_not_equal"] = len(re.findall(r"\| (?:yes|no) \| NO \|", text))
        summary["copied_records"] = len(re.findall(r"^- `results/", text.split("Copied from the commit", 1)[1].split(
            "Excluded as", 1)[0], re.M)) if "Copied from the commit" in text else 0
    summary["passed"] = (summary.get("clone_exit") == 0 and len(summary["commands"]) == len(COMMANDS)
                         and all(c["exit"] == 0 for c in summary["commands"])
                         and summary.get("tracked_files_unchanged_after_gates") is True
                         and str(summary.get("verdict", "")).startswith("REPRODUCED"))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not args.keep:
        shutil.rmtree(base, ignore_errors=True)
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
