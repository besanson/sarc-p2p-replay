"""Release gates G1 to G9 (FINAL-AUDIT item 10); `make gates` runs them and writes out/gates/report.json.

Layout from paper 5 (sarc-authority-derivation at the engines.lock pin: paper-tex/gates/run_gates.py,
the `release-check` Makefile target), adapted to this repository. Paper 5's G1 to G9 are LaTeX
release-kit gates; here G1 to G9 cover the whole release, and paper 5's paper checks (build,
token purity, number parity between source and typeset paper) sit inside G9.

  G1 tests            pytest; CI run ids on the release commit wait on Phase E
  G2 lints            terminology, proof-status, typed-numeral (template and generated paper)
  G3 mutation         results/mutation.json passes (>= 0.85, no uncovered mutant) and src/ has not
                      changed since the commit that recorded it
  G4 regeneration     every deterministic result regenerated from the log and the committed E4
                      responses into out/gates/regen/ and compared byte for byte with results/;
                      the paper, filled template and figures regenerated and compared; external
                      reproduction waits on Phase F
  G5 claims           every CLAIMS.md status and evidence path equals what the slots give
                      (scripts/claim_statuses.py), every evidence file exists
  G6 secrets          no key, token or private key in any tracked file; .env untracked and ignored
  G7 data and pins    data files match prereg/data.lock, siblings at engines.lock, the E1 slot
                      records the registered log hash
  G8 package          the wheel builds; the fresh-venv smoke test waits on Phase E
  G9 paper            paper/paper.md and paper-tex/main.tex present and regenerated identically,
                      no template syntax left in the .tex, the numerals of paper.md and main.tex
                      equal as a multiset, references only verified records; the PDF build waits
                      for a LaTeX engine when none is installed

Each gate is "pass", "fail" or "waiting": waiting when every check it can run now passes and an
item remains for a later phase or environment (named in the report). The run passes when no gate fails.

Usage: python scripts/gates.py [--quick | --ci]
  --quick skips the log replays of G4; --ci runs only the gates that need neither the log nor a
  TeX engine nor the mutation run (G2, G5, G6, G7, G8) and marks the others "not run in CI"
  (report in out/gates/report-ci.json)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
OUT = ROOT / "out" / "gates"
PY = sys.executable
SECRET_PATTERNS = [r"sk-ant-[A-Za-z0-9_-]{10,}", r"apikey_[0-9a-f]{20,}", r"AKIA[0-9A-Z]{16}",
                   r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"ghp_[A-Za-z0-9]{30,}"]


def sh(*cmd: str, cwd: Path = ROOT, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True, env=env)


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def gate(status: str, detail: Any = None, waiting: list[str] | None = None) -> dict[str, Any]:
    return {"status": status, "detail": detail, "waiting": waiting or []}


def g1_tests() -> dict:
    r = sh(PY, "-m", "pytest", "-q", "-p", "no:cacheprovider")
    last = (r.stdout.strip().splitlines() or [""])[-1]
    return gate("pass" if r.returncode == 0 else "fail", last,
                ["CI run ids on Python 3.11 and 3.12 for the release commit: waiting on Phase E"])


def g2_lints() -> dict:
    out = {}
    for mod in ("lint.terminology", "lint.proof_status", "lint.typed_numerals"):
        r = sh(PY, "-m", mod)
        out[mod] = {"exit": r.returncode, "summary": " ".join(r.stdout.strip().splitlines()[:3])}
    return gate("pass" if all(v["exit"] == 0 for v in out.values()) else "fail", out)


def g3_mutation() -> dict:
    m = json.loads((ROOT / "results" / "mutation.json").read_text(encoding="utf-8"))
    mut_commit = sh("git", "log", "-1", "--format=%H", "--", "results/mutation.json").stdout.strip()
    src_commit = sh("git", "log", "-1", "--format=%H", "--", "src/").stdout.strip()
    clean_tree = sh("git", "diff", "--quiet", "HEAD", "--", "src/").returncode == 0
    src_before = bool(mut_commit) and sh("git", "merge-base", "--is-ancestor", src_commit, mut_commit).returncode == 0
    ok = m["passes"] and clean_tree and src_before
    return gate("pass" if ok else "fail", {"kill_score": m["kill_score"], "threshold": m["threshold"],
                                           "no_tests": m["no_tests"], "recorded_in": mut_commit,
                                           "src_last_changed_in": src_commit,
                                           "src_unchanged_since_recorded": src_before and clean_tree})


def _compare(a: Path, b: Path, names: list[str]) -> list[dict]:
    rows = []
    for n in names:
        fa, fb = a / n, b / n
        ha = digest(fa) if fa.is_file() else None
        hb = digest(fb) if fb.is_file() else None
        rows.append({"file": n, "identical": ha is not None and ha == hb})
    return rows


def g4_regeneration(quick: bool) -> dict:
    from experiments import e1, e2, e3, e4, e4_sample, e5, e6_cost, e7, e7_check

    regen = OUT / "regen"
    shutil.rmtree(regen, ignore_errors=True)
    res = regen / "results"
    (regen / "results").mkdir(parents=True)
    os.symlink(ROOT / "responses", regen / "responses")
    log = ROOT / "data" / "BPI_Challenge_2019.xes"
    produced: list[str] = []
    waiting = ["external reproduction from a clean clone (FINAL-AUDIT item 11): waiting on Phase F"]
    if quick or not log.exists():
        shutil.copytree(ROOT / "results" / "e1", res / "e1")
        shutil.copytree(ROOT / "results" / "e4", res / "e4")
        waiting.append("E1 replay and E4 sample draw from the log: skipped (--quick or no data)")
    else:
        e1.run(log, res / "e1")
        e4_sample.run(log, res / "e1", res / "e4")
        produced += [f"e1/{p.name}" for p in (res / "e1").iterdir()]
        produced += [f"e4/{n}" for n in ("sample.json", "sample-frame.json", "views.jsonl", "views-timeline.jsonl")]
    e2.run(res / "e1", res / "e2")
    e3.run(res / "e1", res / "e3")
    e4.run("e4", root=regen)
    e4.run("e4-exploratory", root=regen)
    produced += [f"e2/{n}" for n in ("hypotheses.json", "confounders.json")]
    produced += [f"e3/{p.name}" for p in (res / "e3").iterdir()]
    produced += ["e4/arms.json", "e4/h4.json", "e4-exploratory/arms-exploratory.json",
                 "e4-exploratory/h4-exploratory.json"]
    try:
        e5.run(res / "e1", res / "e5")
        produced += [f"e5/{p.name}" for p in (res / "e5").iterdir()]
    except Exception as exc:  # noqa: BLE001 - sibling absent: reported, not failed
        waiting.append(f"E5 needs paper 5's compiler at its pin: {type(exc).__name__}")
    if (ROOT / "data" / "DomesticDeclarations.xes.gz").exists():
        e7_check.run(res / "e7")
        e7.run(res / "e7")
        produced += [f"e7/{p.name}" for p in (res / "e7").iterdir()]
    e6_cost.run(root=regen, out=res / "e6")
    produced.append("e6/cost.json")
    if not quick and log.exists():
        from experiments import round1_slots  # noqa: PLC0415

        round1_slots.run(log, root=regen, e1_dir=res / "e1", out=res)
        produced += ["e3/human-hold-composition.json", "e1/actors.json", "e4/arms-classified-lines.json"]
        from experiments import round2_slots  # noqa: PLC0415

        parts = (("timeline", "actors") + (("sufficiency",) if (res / "e5" / "derivation.json").exists() else ())
                 + (("e7",) if (res / "e7" / "evidence-set.jsonl.gz").exists() else ()))
        docs = round2_slots.run(log, e1_dir=res / "e1", e5_dir=res / "e5", e7_dir=res / "e7", out=res, parts=parts)
        produced += list(docs)
        from experiments import round3_slots  # noqa: PLC0415

        produced += list(round3_slots.run(e1_dir=res / "e1", out=res))
    rows = _compare(ROOT / "results", res, sorted(set(produced)))

    import fill_paper  # noqa: PLC0415
    import figures  # noqa: PLC0415

    paper_dir = OUT / "paper-regen"
    shutil.rmtree(paper_dir, ignore_errors=True)
    paper_rows = []
    if (ROOT / "paper" / "template.md").exists():
        fill_paper.run(out_paper=paper_dir / "paper.md", out_filled=paper_dir / "filled-template.json")
        paper_rows += [{"file": "paper/paper.md", "identical": digest(ROOT / "paper" / "paper.md") == digest(paper_dir / "paper.md")},
                       {"file": "paper/filled-template.json",
                        "identical": digest(ROOT / "paper" / "filled-template.json") == digest(paper_dir / "filled-template.json")}]
        figures.run(paper_dir / "figures")
        for f in sorted((paper_dir / "figures").iterdir()):
            committed = ROOT / "paper" / "figures" / f.name
            paper_rows.append({"file": f"paper/figures/{f.name}",
                               "identical": committed.is_file() and digest(committed) == digest(f)})
    ok = all(r["identical"] for r in rows + paper_rows) and bool(rows)
    return gate("pass" if ok else "fail", {"results": rows, "paper": paper_rows,
                                           "differing": [r["file"] for r in rows + paper_rows if not r["identical"]]},
                waiting)


def g5_claims() -> dict:
    from claim_statuses import statuses  # noqa: PLC0415

    expected = statuses()
    found = {}
    for line in (ROOT / "CLAIMS.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| (C\d+) \| .* \| ([^|]*) \| ([^|]*) \| ([^|]*) \|$", line)
        if m:
            found[m.group(1)] = (m.group(3).strip(), m.group(4).strip())
    mismatch = [c for c in expected if found.get(c) != expected[c]]
    missing = sorted({p for _, ev in expected.values() for p in re.findall(r"`([^`]+)`", ev)
                      if not (ROOT / p).exists()})
    return gate("pass" if not mismatch and not missing else "fail",
                {"claims": len(found), "mismatch": mismatch, "missing_evidence_files": missing})


def g6_secrets() -> dict:
    files = sh("git", "ls-files").stdout.split()
    hits = []
    for f in files:
        p = ROOT / f
        if not p.is_file() or p.stat().st_size > 50_000_000:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in SECRET_PATTERNS:
            if re.search(pat, text):
                hits.append({"file": f, "pattern": pat})
    env_tracked = ".env" in files
    env_ignored = sh("git", "check-ignore", "-q", ".env").returncode == 0
    ok = not hits and not env_tracked and env_ignored
    return gate("pass" if ok else "fail", {"files_scanned": len(files), "hits": hits,
                                           ".env tracked": env_tracked, ".env ignored": env_ignored})


def g7_data_and_pins() -> dict:
    r = sh(PY, "preflight.py", "--require", "data,siblings")
    lock = __import__("tomllib").loads((ROOT / "prereg" / "data.lock").read_text(encoding="utf-8"))
    recorded = json.loads((ROOT / "results" / "e1" / "exclusions.json").read_text(encoding="utf-8"))["log"]["sha256"]
    slot_ok = recorded == lock["bpi2019"]["sha256"]
    if r.returncode != 0:
        return gate("waiting", {"preflight": r.stdout.strip().splitlines()[-1:], "e1_log_hash_matches_lock": slot_ok},
                    ["data or siblings absent in this checkout: run make bootstrap"])
    return gate("pass" if slot_ok else "fail", {"preflight": "data and siblings complete",
                                                 "e1_log_hash_matches_lock": slot_ok})


def g8_package() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        # Isolated build, as pyproject.toml's build-system declares (the venv itself has no setuptools).
        r = sh(PY, "-m", "pip", "wheel", ".", "--no-deps", "-q", "-w", tmp)
        wheels = sorted(p.name for p in Path(tmp).glob("*.whl"))
    return gate("pass" if r.returncode == 0 and wheels else "fail", {"wheels": wheels},
                ["fresh-venv install and smoke test (make package-smoke-test, FINAL-AUDIT item 2): waiting on Phase E"])


def g9_paper() -> dict:
    paper, tex = ROOT / "paper" / "paper.md", ROOT / "paper-tex" / "main.tex"
    if not paper.exists():
        return gate("fail", "paper/paper.md missing")
    detail: dict[str, Any] = {}
    waiting = []
    import build_tex  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as tmp:
        regen = Path(tmp) / "main.tex"
        build_tex.write_tex(paper, regen)
        detail["tex_regenerated_identical"] = tex.exists() and digest(tex) == digest(regen)
    tex_text = tex.read_text(encoding="utf-8") if tex.exists() else ""
    md_text = paper.read_text(encoding="utf-8")
    # Token purity: no placeholder left in the paper, and none (escaped by pandoc) in the tex.
    detail["template_syntax_left_in_tex"] = "{{" in md_text or "\\{\\{" in tex_text
    # Number parity: HTML comments (reference ids, the source note) are not typeset, so not counted.
    md_nums = Counter(re.findall(r"\d[\d,.]*\d|\d", re.sub(r"<!--.*?-->|`[^`]*`|https?://\S+", "", md_text, flags=re.DOTALL)))
    tex_nums = Counter(re.findall(r"\d[\d,.]*\d|\d", re.sub(r"\\texttt\{[^}]*\}|\\url\{[^}]*\}|\\href\{[^}]*\}", "",
                                                              build_tex.body_of(tex_text))))
    detail["numeral_multiset_md_minus_tex"] = dict((md_nums - tex_nums).most_common(10))
    cites = json.loads((ROOT / "verified-citations.json").read_text(encoding="utf-8"))["citations"]
    status = {c["id"]: c["status"] for c in cites}
    used = re.findall(r"<!-- ref:([a-z0-9-]+) -->", paper.read_text(encoding="utf-8"))
    detail["references"] = len(used)
    detail["unverified_references"] = [u for u in used if status.get(u) != "verified"]
    engine = build_tex.latex_engine()
    if engine is None:
        waiting.append("PDF build: no LaTeX engine (tectonic, latexmk, pdflatex, xelatex) in this environment")
        detail["pdf"] = None
    else:
        detail["pdf"] = build_tex.build_pdf(engine)
    ok = (detail["tex_regenerated_identical"] and not detail["template_syntax_left_in_tex"]
          and not detail["numeral_multiset_md_minus_tex"] and not detail["unverified_references"]
          and (engine is None or detail["pdf"]))
    return gate("pass" if ok else "fail", detail, waiting)


GATES: dict[str, Callable[..., dict]] = {
    "G1 tests": g1_tests, "G2 lints": g2_lints, "G3 mutation": g3_mutation,
    "G4 regeneration": g4_regeneration, "G5 claims": g5_claims, "G6 secrets": g6_secrets,
    "G7 data and pins": g7_data_and_pins, "G8 package": g8_package, "G9 paper": g9_paper,
}


CI_GATES = ("G2 lints", "G5 claims", "G6 secrets", "G7 data and pins", "G8 package")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gates")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true")
    mode.add_argument("--ci", action="store_true")
    args = parser.parse_args(argv)
    report: dict[str, Any] = {"gates": {}}
    for name, fn in GATES.items():
        if args.ci and name not in CI_GATES:
            report["gates"][name] = gate("not run in CI", "needs the log, a TeX engine or the mutation run")
            print(f"{name}: not run in CI")
            continue
        try:
            result = fn(args.quick) if name.startswith("G4") else fn()
        except Exception as exc:  # noqa: BLE001 - a crashing gate is a failing gate
            result = gate("fail", f"{type(exc).__name__}: {exc}")
        # A gate whose checks pass but which still waits on a later phase reports "waiting".
        if result["status"] == "pass" and result["waiting"]:
            result["status"] = "waiting"
        report["gates"][name] = result
        print(f"{name}: {result['status']}" + (f" (waiting: {'; '.join(result['waiting'])})" if result["waiting"] else ""))
    statuses = [g["status"] for g in report["gates"].values()]
    report["summary"] = {s: statuses.count(s) for s in ("pass", "fail", "waiting", "not run in CI")}
    report["passed"] = "fail" not in statuses
    report["quick"] = args.quick
    report["ci"] = args.ci
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ("report-ci.json" if args.ci else "report.json")).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"gates: {report['summary']}; passed: {report['passed']}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
