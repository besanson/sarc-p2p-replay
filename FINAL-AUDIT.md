# Final audit

Twelve items, as paper 6's release audit (inherited from paper 5's
`FINAL-AUDIT.md`), adapted to a replay of a real event log. Each item is
closed only with an evidence path (a file, a CI run, a slot, an issue), never
with prose.

| # | item | evidence required | status |
|---|---|---|---|
| 1 | Latest CI on 3.11 and 3.12 green | GitHub Actions run ids on the release commit | closed: `results/ci-runs.json` (runs on 3.11 and 3.12, green); the release commit's runs are added at release |
| 2 | Package builds (sdist and wheel) and installs in a fresh venv | `make package-smoke-test` log | closed: `results/package-smoke.json` |
| 3 | The replay runs outside the repository root on an arbitrary XES or CSV log with `prereg/column-mapping.yaml` | smoke test on a fixture log from a temp directory | closed: `results/package-smoke.json` (checks `xes: replay runs outside the repository`, `csv: replay runs outside the repository`) |
| 4 | Mutation score on `src/` at least 0.85 | mutation report | open (Phase B run: 0.9389, `DECISIONS.md` D-B-2, `results/mutation.json`; re-run on the release commit) |
| 5 | Paper centred on the registered hypotheses H1 to H4 and exposure, every number from a slot | typed-numerals lint, slot files | closed: `lint/typed_numerals.py`, `paper/filled-template.json` |
| 6 | README shows the replay, the exposure table and the gate column immediately | README at release commit | closed: `README.md` headline block, generated from `paper/readme-headline.md` (`paper/filled-template.json`, `readme_headline`) |
| 7 | Negative or null results retained as registered (any H not supported is reported) | `results/` slots, `CLAIMS.md` status | closed: `CLAIMS.md` (C6 not supported, C5 and C11 inconclusive, C9 not supported, all retained); `results/e4/h4.json`, `results/e2/hypotheses.json`, `results/e7/comparisons.json`, `results/e5/derivation.json` |
| 8 | Data reproduces from the committed hash: `make bootstrap` fetches, the SHA-256 matches `prereg/data.lock` | bootstrap log | closed: `results/data-check.json` (`make check-data`: the three files at their registered SHA-256); fetch URLs in `prereg/data.lock`, used at A0 (`DECISIONS.md` D-A0-1) |
| 9 | Byte-identical regeneration of every result from the hash and the E4 caches | double-run diff | closed: `results/round1-double-run.json`, `results/round2-double-run.json`, `results/round3-double-run.json`, `results/e4/double-run.json`, `results/e4-exploratory/double-run.json`, `results/e5/double-run.json`, `results/e7/double-run.json`, `results/reproducibility.json` |
| 10 | Release gates G1 to G9 plus terminology, typed-numeral and proof-status lints green | gate report | closed: `results/gates-report.json` (G1 to G9: no gate fails; G4 waits only on item 11), `lint/terminology.py`, `lint/typed_numerals.py`, `lint/proof_status.py` |
| 11 | External reproduction from a clean clone | issue with matching result hashes | open (Phase F) |
| 12 | Claims never exceed evidence: no causal language, no loss figure, no company or vendor named, coverage honest | terminology lint, `COVERAGE.md`, review rounds | closed: `lint/terminology.py`, `COVERAGE.md`, `review-secondary/D1-review-*.md`, `review-secondary/D2-review-*.md`, `review-secondary/D3-review-*.md` |

## Summary

10 of 12 items met. Open: 4 (mutation re-run on the release commit) and 11 (external reproduction, Phase F).
