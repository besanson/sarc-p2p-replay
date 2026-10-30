"""Package smoke test (FINAL-AUDIT items 2 and 3; gate G8): `make package-smoke-test`.

1. Build the sdist and the wheel (`python -m build`, in a build venv, so the repository's own venv
   is not touched).
2. Create a fresh venv in a temporary directory and install the wheel there (its one dependency,
   pyyaml, from the index).
3. From a different temporary directory, outside the repository, run the installed package
   (`python -I -m p2p_replay replay`, so nothing is imported from the checkout):
   - on tests/fixtures/mini2019.xes, with prereg/column-mapping.yaml and prereg/outcome-patterns.yaml
     copied beside it;
   - on tests/fixtures/mini2019.csv, with its own mapping (the registered BPI 2019 mapping with the
     CSV's case-id column and no actor fallback, as tests/test_pipeline.py builds it).
4. Compare: each evidence output with the fixture's expected verdicts (tests/fixtures/make_fixtures.py
   EXPECTED: verdict, failed and unknown predicates, receipt class, lag band, outcome) and byte for
   byte with the replay run from the source tree on the same inputs; the CSV output with the XES
   output.

Logs go to out/package-smoke/; `--record` also writes results/package-smoke.json. Exit 1 on any
failed check.

Usage: python scripts/package_smoke.py [--record]
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
OUT = ROOT / "out" / "package-smoke"
RECORD = ROOT / "results" / "package-smoke.json"
FIXTURES = ROOT / "tests" / "fixtures"
MIN_MONTH_EVENTS = "1"  # the fixture's months are small; the tests use the same value


def _run(cmd: list[str], log: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    log += [f"$ {' '.join(cmd)}" + (f"   (cwd {cwd})" if cwd else ""), r.stdout.rstrip(), r.stderr.rstrip(),
            f"exit {r.returncode}", ""]
    return r


def csv_mapping() -> dict[str, Any]:
    reg = yaml.safe_load((ROOT / "prereg" / "column-mapping.yaml").read_text(encoding="utf-8"))["bpi2019"]
    return {"bpi2019": {**reg, "case": dict(reg["case"], case_id="case:concept:name"),
                        "event": dict(reg["event"], actor_fallback=None)}}


def expected_rows() -> dict[str, list[tuple]]:
    from fixtures import make_fixtures  # noqa: PLC0415

    return {cid: [tuple(x) for x in recs] for cid, (_, recs) in make_fixtures.EXPECTED.items() if recs}


def observed_rows(path: Path) -> dict[str, list[tuple]]:
    out: dict[str, list[tuple]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        out.setdefault(r["case_id"], []).append((r["verdict"], r["failed"], r["unknown"], r["receipt_class"],
                                                 r["lag_band"], r["outcome_w"]))
    return out


def source_tree_replay(log: Path, mapping: Path, patterns: Path, out: Path) -> None:
    from p2p_replay import cli  # noqa: PLC0415

    cli.main(["replay", str(log), "--mapping", str(mapping), "--patterns", str(patterns), "--out", str(out),
              "--min-month-events", MIN_MONTH_EVENTS])


def run(record: bool = False) -> dict[str, Any]:
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True)
    log: list[str] = []
    checks: dict[str, bool] = {}
    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)
        dist, buildenv, venv, work = tmp / "dist", tmp / "buildenv", tmp / "venv", tmp / "work"
        work.mkdir()
        # 1. build
        _run([sys.executable, "-m", "venv", str(buildenv)], log)
        _run([str(buildenv / "bin" / "python"), "-m", "pip", "install", "-q", "build"], log)
        r = _run([str(buildenv / "bin" / "python"), "-m", "build", "--sdist", "--wheel", "--outdir", str(dist), str(ROOT)],
                 log)
        sdists, wheels = sorted(dist.glob("*.tar.gz")), sorted(dist.glob("*.whl"))
        checks["sdist and wheel built"] = r.returncode == 0 and len(sdists) == 1 and len(wheels) == 1
        # 2. fresh venv, install the wheel
        _run([sys.executable, "-m", "venv", str(venv)], log)
        py = str(venv / "bin" / "python")
        r = _run([py, "-m", "pip", "install", "-q", str(wheels[0])], log) if wheels else None
        checks["wheel installs in a fresh venv"] = r is not None and r.returncode == 0
        where = _run([py, "-I", "-c", "import p2p_replay, sys; print(p2p_replay.__file__)"], log, cwd=work)
        checks["package imported from the fresh venv, not the checkout"] = (
            where.returncode == 0 and str(venv) in where.stdout and str(ROOT) not in where.stdout)
        # 3. run outside the repository: XES with the registered files beside it, CSV with its own mapping
        for name in ("column-mapping.yaml", "outcome-patterns.yaml"):
            shutil.copy(ROOT / "prereg" / name, work / name)
        shutil.copy(FIXTURES / "mini2019.xes", work / "mini2019.xes")
        shutil.copy(FIXTURES / "mini2019.csv", work / "mini2019.csv")
        (work / "csv-mapping.yaml").write_text(yaml.safe_dump(csv_mapping(), sort_keys=True), encoding="utf-8")
        runs = {"xes": ("mini2019.xes", "column-mapping.yaml"), "csv": ("mini2019.csv", "csv-mapping.yaml")}
        expected = expected_rows()
        outputs = {}
        for kind, (logname, mapping) in runs.items():
            out = work / f"evidence-{kind}.jsonl"
            r = _run([py, "-I", "-m", "p2p_replay", "replay", logname, "--mapping", mapping, "--patterns",
                      "outcome-patterns.yaml", "--out", out.name, "--min-month-events", MIN_MONTH_EVENTS], log, cwd=work)
            ok = r.returncode == 0 and out.exists()
            checks[f"{kind}: replay runs outside the repository"] = ok
            checks[f"{kind}: evidence equals the fixture's expected verdicts"] = ok and observed_rows(out) == expected
            reference = tmp / f"source-{kind}.jsonl"
            source_tree_replay(work / logname, work / mapping, work / "outcome-patterns.yaml", reference)
            checks[f"{kind}: evidence byte-identical to the source-tree replay"] = (
                ok and out.read_bytes() == reference.read_bytes())
            if ok:
                outputs[kind] = out.read_bytes()
                shutil.copy(out, OUT / out.name)
        checks["csv and xes evidence identical"] = len(outputs) == 2 and outputs["csv"] == outputs["xes"]
        artefacts = {"sdist": sdists[0].name if sdists else None, "wheel": wheels[0].name if wheels else None}
    (OUT / "log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    doc = {
        "audit_items": [2, 3], "gate": "G8",
        "python": platform.python_version(),
        "artefacts": artefacts,
        "fixture_records": sum(len(v) for v in expected_rows().values()),
        "checks": checks,
        "passed": all(checks.values()),
        "log": "out/package-smoke/log.txt (not committed)",
    }
    (OUT / "result.json").write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if record:
        RECORD.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return doc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="package_smoke")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args(argv)
    doc = run(args.record)
    for name, ok in doc["checks"].items():
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
    print(f"package smoke test: {'passed' if doc['passed'] else 'FAILED'}")
    return 0 if doc["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
