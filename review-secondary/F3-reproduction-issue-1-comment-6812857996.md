Gastón, the rerun at `V1.0.2` completed successfully: `make reproduce` exited with code 0. The generated report is pasted unchanged below.

- Run: 2026-11-12, 02:32:51–02:44:50 UTC, as reported by the machine clock (about 12 minutes).
- Same clone, existing data and environment retained; Pandoc 3.1.3 on PATH, Python 3.13.16, macOS 26.7.2 arm64.
- No repository source code, tests, registered hashes, or expected results were edited. The tracked checkout was clean before and after the run; prior failed-run output was preserved.
- Only the requested reproduction command was run for this tag; tests and gates were not rerun.
- Copilot helped execute the commands and inspect the output; I had no role in developing the repository.

---

# Reproduction of v1.0.2

Commit `50aeeb8de5db82ab60379ec63dc766d29f328809` (V1.0.2); Python 3.13.16; macOS-26.7.2-arm64-arm-64bit-Mach-O.

Byte-identical: the SHA-256 of the regenerated file equals the committed one. Within tolerance (JSON and JSON lines only): the parsed structures and strings are equal and every number pair satisfies |a - b| <= 1e-12 x max(1, |a|, |b|); text files are compared by bytes only.

| file | byte-identical | within tolerance | max absolute difference |
|---|---|---|---|
| `results/e0/run-2/e0-lines.txt` | yes | yes | n/a |
| `results/e0/run-2/e0-report.json` | yes | yes | 0 |
| `results/e1/actors.json` | yes | yes | 0 |
| `results/e1/analysed-clearing-actors.json` | yes | yes | 0 |
| `results/e1/category-crosscheck.json` | yes | yes | 0 |
| `results/e1/coverage-check.json` | yes | yes | 0 |
| `results/e1/evidence-sample.jsonl` | yes | yes | 0 |
| `results/e1/evidence-set.jsonl.gz` | yes | yes | 0 |
| `results/e1/exclusions.json` | yes | yes | 0 |
| `results/e1/exposure-by-stratum.json` | no | yes | 1.11e-16 |
| `results/e1/exposure.json` | no | yes | 2.71e-20 |
| `results/e1/lines-t-star-amended.jsonl.gz` | yes | yes | 0 |
| `results/e1/lines.jsonl.gz` | yes | yes | 0 |
| `results/e1/predicate-unknowns.json` | yes | yes | 0 |
| `results/e1/value-fallback.json` | yes | yes | 0 |
| `results/e2/confounders.json` | yes | yes | 0 |
| `results/e2/hypotheses.json` | no | yes | 5.42e-20 |
| `results/e3/confounders.json` | yes | yes | 0 |
| `results/e3/gate-held.json` | yes | yes | 0 |
| `results/e3/human-hold-composition.json` | yes | yes | 0 |
| `results/e3/human-hold.json` | yes | yes | 0 |
| `results/e3/lag-bands.json` | yes | yes | 0 |
| `results/e3/verdict-by-outcome.json` | yes | yes | 0 |
| `results/e4/arms-classified-lines.json` | yes | yes | 0 |
| `results/e4/arms.json` | yes | yes | 0 |
| `results/e4/h4.json` | no | yes | 5.42e-20 |
| `results/e4/sample-frame.json` | yes | yes | 0 |
| `results/e4/sample.json` | yes | yes | 0 |
| `results/e4/timeline.json` | yes | yes | 0 |
| `results/e4/views-timeline.jsonl` | yes | yes | 0 |
| `results/e4/views.jsonl` | yes | yes | 0 |
| `results/e4-exploratory/arms-exploratory.json` | yes | yes | 0 |
| `results/e4-exploratory/h4-exploratory.json` | yes | yes | 0 |
| `results/e5/derivation.json` | yes | yes | 0 |
| `results/e5/sufficiency.json` | yes | yes | 0 |
| `results/e5/trace-2-way.json` | yes | yes | 0 |
| `results/e5/trace-3-way-invoice-after-receipt.json` | yes | yes | 0 |
| `results/e5/trace-3-way-invoice-before-receipt.json` | yes | yes | 0 |
| `results/e6/cost.json` | yes | yes | 0 |
| `results/e7/comparisons.json` | yes | yes | 0 |
| `results/e7/evidence-set.jsonl.gz` | yes | yes | 0 |
| `results/e7/exposure.json` | yes | yes | 0 |
| `results/e7/predicates.json` | yes | yes | 0 |
| `results/e7/units.json` | yes | yes | 0 |
| `results/e7/unknown-overlap.json` | yes | yes | 0 |
| `results/e7/vocabulary.json` | yes | yes | 0 |
| `paper/paper.md` | yes | yes | n/a |
| `paper/filled-template.json` | no | yes | 5.42e-20 |
| `README.md` | yes | yes | n/a |
| `paper-tex/main.tex` | yes | yes | n/a |
| `paper/figures/figure-data.json` | yes | yes | 0 |

Copied from the commit, not regenerated (never counted as reproduced; the paper cites some of them):

- `results/README.md`: verification record (index of the slot files)
- `results/checks-d-c-2.json`: verification record (D-C-2 re-run record)
- `results/ci-runs.json`: machine-dependent record (GitHub Actions runs)
- `results/data-check.json`: machine-dependent record (check of the data files on the release machine)
- `results/e0/run-1/e0-lines.txt`: verification record (E0 run 1 under p7-v1, stopped and superseded by run 2)
- `results/e0/run-1/e0-report.json`: verification record (E0 run 1 under p7-v1, stopped and superseded by run 2)
- `results/e0/run-1/e0-timestamp-tail.json`: verification record (E0 run 1 under p7-v1, stopped and superseded by run 2)
- `results/e0/run-1/e0-timing.json`: verification record (E0 run 1 under p7-v1, stopped and superseded by run 2)
- `results/e4-exploratory/double-run.json`: verification record (double-run record)
- `results/e4/double-run.json`: verification record (double-run record)
- `results/e5/double-run.json`: verification record (double-run record)
- `results/e6/timing-e1.json`: machine-dependent record (wall time and hardware of the E1 replay)
- `results/e7/double-run.json`: verification record (double-run record)
- `results/gates-report.json`: machine-dependent record (gate report of the release machine)
- `results/mutation-release.json`: machine-dependent record (mutation run (release))
- `results/mutation.json`: machine-dependent record (mutation run (Phase B/C))
- `results/package-smoke.json`: machine-dependent record (Python version of the smoke test)
- `results/reproducibility.json`: machine-dependent record (run times of the internal double run)
- `results/reproduction/attempt-1.json`: record of an external attempt (records of external reproduction attempts and the comparison rule)
- `results/reproduction/attempt-2.json`: record of an external attempt (records of external reproduction attempts and the comparison rule)
- `results/reproduction/comparison-rule.json`: verification record (records of external reproduction attempts and the comparison rule)
- `results/round1-double-run.json`: verification record (double-run record)
- `results/round2-double-run.json`: verification record (double-run record)
- `results/round3-double-run.json`: verification record (double-run record)

Excluded as machine-dependent (not compared):

- `results/e0/run-2/e0-timing.json`: wall time of the E0 passes
- `results/e6/timing-e1.json`: wall time and hardware of the E1 replay
- `results/reproducibility.json`: run times of the internal double run
- `results/ci-runs.json`: GitHub Actions runs
- `results/package-smoke.json`: Python version of the smoke test
- `results/gates-report.json`: gate report of the release machine
- `results/data-check.json`: check of the data files on the release machine
- `results/mutation.json`: mutation run (Phase B/C)
- `results/mutation-release.json`: mutation run (release)
- `paper/figures/fig1-exposure.pdf`: figure bytes (font embedding); its numbers are compared in `paper/figures/figure-data.json`
- `paper/figures/fig1-exposure.svg`: figure bytes (font embedding); its numbers are compared in `paper/figures/figure-data.json`
- `paper/figures/fig2-hold-rates.pdf`: figure bytes (font embedding); its numbers are compared in `paper/figures/figure-data.json`
- `paper/figures/fig2-hold-rates.svg`: figure bytes (font embedding); its numbers are compared in `paper/figures/figure-data.json`
- `paper/figures/fig3-lag-bands.pdf`: figure bytes (font embedding); its numbers are compared in `paper/figures/figure-data.json`
- `paper/figures/fig3-lag-bands.svg`: figure bytes (font embedding); its numbers are compared in `paper/figures/figure-data.json`
- `paper/figures/fig4-verdict-outcome.pdf`: figure bytes (font embedding); its numbers are compared in `paper/figures/figure-data.json`
- `paper/figures/fig4-verdict-outcome.svg`: figure bytes (font embedding); its numbers are compared in `paper/figures/figure-data.json`

Verification records of earlier runs (not regenerated; this reproduction replaces them):

- `results/README.md`: index of the slot files
- `results/checks-d-c-2.json`: D-C-2 re-run record
- `results/round1-double-run.json`: double-run record
- `results/round2-double-run.json`: double-run record
- `results/round3-double-run.json`: double-run record
- `results/e4/double-run.json`: double-run record
- `results/e4-exploratory/double-run.json`: double-run record
- `results/e5/double-run.json`: double-run record
- `results/e7/double-run.json`: double-run record
- `results/e0/run-1/`: E0 run 1 under p7-v1, stopped and superseded by run 2
- `results/reproduction/`: records of external reproduction attempts and the comparison rule

For information: `paper-tex/main.pdf` built with tectonic: differs from the committed PDF (its bytes depend on the TeX installation and engine; the committed one used pdflatex, TeX Live 2023, pdfTeX 1.40.25).

**REPRODUCED: 51 files equal (46 byte-identical, 5 within tolerance, max difference 1.11e-16)**
