# Final audit

Twelve items, as paper 6's release audit (inherited from paper 5's
`FINAL-AUDIT.md`), adapted to a replay of a real event log. Each item is
closed only with an evidence path (a file, a CI run, a slot, an issue), never
with prose. At Phase A0 every item is open.

| # | item | evidence required | status |
|---|---|---|---|
| 1 | Latest CI on 3.11 and 3.12 green | GitHub Actions run ids on the release commit | open |
| 2 | Package builds (sdist and wheel) and installs in a fresh venv | `make package-smoke-test` log | open |
| 3 | The replay runs outside the repository root on an arbitrary XES or CSV log with `prereg/column-mapping.yaml` | smoke test on a fixture log from a temp directory | open |
| 4 | Mutation score on `src/` at least 0.85 | mutation report | open (Phase B run: 0.9389, `DECISIONS.md` D-B-2; re-run on the release commit) |
| 5 | Paper centred on the registered hypotheses H1 to H4 and exposure, every number from a slot | typed-numerals lint, slot files | open |
| 6 | README shows the replay, the exposure table and the gate column immediately | README at release commit | open |
| 7 | Negative or null results retained as registered (any H not supported is reported) | `results/` slots, `CLAIMS.md` status | open |
| 8 | Data reproduces from the committed hash: `make bootstrap` fetches, the SHA-256 matches `prereg/data.lock` | bootstrap log | open |
| 9 | Byte-identical regeneration of every result from the hash and the E4 caches | double-run diff | open |
| 10 | Release gates G1 to G9 plus terminology, typed-numeral and proof-status lints green | gate report | open |
| 11 | External reproduction from a clean clone | issue with matching result hashes | open |
| 12 | Claims never exceed evidence: no causal language, no loss figure, no company or vendor named, coverage honest | terminology lint, `COVERAGE.md`, review rounds | open |

## Summary

0 of 12 items met. Phase A0.
