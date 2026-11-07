# Reproduction of v1.0.0

Reproduction attempted by Eduardo Arana, Independent Researcher.

I ran the release instructions on a separate clone of v1.0.0. I could not complete a successful reproduction: one test failed, three gates failed, and `make reproduce` stopped with an exception before writing `out/reproduce/report.md`.

No repository source code, tests, registered hashes, or expected results were edited. `make gates` itself overwrote its machine-dependent `results/gates-report.json`, as its documented `--record` option does. No model was called and no API key was supplied. Copilot helped execute the commands on my machine and inspect the output; I had no role in developing the repository.

## Environment

- Release: v1.0.0
- Commit: `eb5ce3dd4a5c33a80a52320657ea74d3b982de6f`
- Operating system: macOS 26.7.2, build 25G332, arm64
- Python: 3.13.16
- Git: 2.54.0 (Apple Git-157)
- Pandoc: 3.1.3, downloaded from its official release and used locally
- Tectonic: 0.17.0, already installed and automatically selected by the release script
- Initial run started: 2026-11-04 UTC; successful dataset verification: 2026-11-05 UTC
- Supplemental checks: machine clock reported 2026-11-07 UTC. Dates are recorded from the machine clock, not independently verified.

Python was selected with `make bootstrap PYTHON=/opt/homebrew/bin/python3.13`. The matching Pandoc directory was added to PATH for the gates and reproduction commands. No release code was patched. Gates and reproduction used their separate output directories and overlapped in execution.

## Command Results

| Step | Result |
| --- | --- |
| Clone at v1.0.0 | Completed; exact commit above |
| `make bootstrap` | Initial primary-log SHA-256 mismatch; downloaded file deleted automatically. Retried once with the same command, URL and registered hashes; all three logs then passed |
| `make test` | 157 passed, 1 failed; make exit code 2 |
| `make gates` | 6 passed, 3 failed: G1 tests, G4 regeneration, G9 paper; make exit code 2 |
| `make reproduce` | Regenerated results and paper, then raised FileNotFoundError during the optional PDF step; make exit code 2. No standard report or verdict line was written |

## Dataset Verification

After the retry, file sizes and full SHA-256 values were also checked independently with `wc -c` and `shasum -a 256`. All matched the registration.

| File | Bytes | SHA-256 |
| --- | --- | --- |
| BPI_Challenge_2019.xes | 728558522 | af63bc687fc4152f2123b05c3af7772b37ef3fce2d3f67f812666c9e356baae7 |
| InternationalDeclarations.xes.gz | 1581144 | b527c8d06255f4312c6ce8f36f7f4110243d84fd6ca48583cd9b80896c601494 |
| DomesticDeclarations.xes.gz | 933930 | 0bc3312acf0b9ee5ae6f4ebe9df204005ef11665d62f2d21dd04995161d7532b |

Initial download error, retained even though the retry succeeded:

```text
data: BPI_Challenge_2019.xes SHA-256 d4b8ce105ae360a650fa6526e4d4a63205c72f20b11d61a0b69d432ba774edff != registered af63bc687fc4152f2123b05c3af7772b37ef3fce2d3f67f812666c9e356baae7
data: BPI_Challenge_2019.xes deleted
make: *** [fetch-data] Error 1
```

## Test Failure

```text
____________________ test_timeline_from_the_committed_logs _____________________

tests/test_round2_slots.py:85:
    assert json.loads(committed.read_text(encoding="utf-8")) == doc
E   AssertionError

FAILED tests/test_round2_slots.py::test_timeline_from_the_committed_logs
1 failed, 157 passed in 11.51s
make: *** [test] Error 1
```

Inspecting the parsed JSON against the committed file showed ten differing fields, all commit author/committer UTC timestamps. For example:

```text
committed:   2026-10-25T18:21:56+00:00
regenerated: 2026-10-25T18:21:56Z
```

The instants are equivalent, but the exact-string test and byte comparison fail. No other values differed in the timeline JSON. I did not normalize either file to make the check pass.

## Gate Results

```text
G1 tests: fail
G2 lints: pass
G3 mutation: pass
G4 regeneration: fail (waiting: external reproduction from a clean clone (FINAL-AUDIT item 11): waiting on Phase F)
G5 claims: pass
G6 secrets: pass
G7 data and pins: pass
G8 package: pass
G9 paper: fail
gates: {'pass': 6, 'fail': 3, 'waiting': 0, 'not run in CI': 0}; passed: False
make: *** [gates] Error 1
```

G4's detailed report lists five differing result JSON files (`e1/exposure-by-stratum.json`, `e1/exposure.json`, `e2/hypotheses.json`, `e4/h4.json`, `e4/timeline.json`) and all eight figure files (four SVG/PDF pairs). Its paper text, filled-template manifest and README comparison passed. The G4 manifest differs from the separate full-reproduction manifest check below: G4 fills the paper using the checkout's result files, while the full reproduction fills it from the regenerated files.

G9's recorded error:

```text
FileNotFoundError: [Errno 2] No such file or directory: '/var/folders/md/jb890gbs4dxb2r7zcm16k2c40000gn/T/tmpjzbpzeld/main.log'
```

## Reproduction Command Failure

The command reached `reproduce: PDF (information only)` and then stopped. Relevant traceback excerpt, with the checkout's absolute path abbreviated to `<checkout>`:

```text
Traceback (most recent call last):
  File "<checkout>/scripts/reproduce.py", line 202, in <module>
    sys.exit(main())
  File "<checkout>/scripts/reproduce.py", line 193, in main
    rows, uncovered, pdf = compare(res, OUT / "paper")
  File "<checkout>/scripts/reproduce.py", line 147, in compare
    if build_tex.build_pdf(engine, built):
  File "<checkout>/scripts/build_tex.py", line 133, in build_pdf
    _record_overfull((Path(tmp) / "main.log").read_text(encoding="latin-1"))
FileNotFoundError: [Errno 2] No such file or directory: '/var/folders/md/jb890gbs4dxb2r7zcm16k2c40000gn/T/tmpuiihofjo/main.log'
make: *** [reproduce] Error 1
```

The optional PDF failure prevented the standard `out/reproduce/report.md` from being written. I did not change the code or hide Tectonic to get a different result.

## Supplemental Hash Comparison

Since the command failed before printing its table, I separately hashed the files it had already generated, using the release script's file list, exclusions and SHA-256 comparison rules. This did not rerun any experiment. It is supplemental evidence, not a successful `make reproduce` run or its missing report.

**Supplemental result: 44 of 58 files matched; 14 differed; no required comparison file was missing.** The optional PDF was not evaluated in this supplemental comparison.

The table uses 16-character prefixes for readability, as the release report does. Comparisons used the complete SHA-256 values.

| File | Committed SHA-256 Prefix | Regenerated SHA-256 Prefix | Match |
| --- | --- | --- | --- |
| results/e0/run-2/e0-lines.txt | 04d93ca4e249cd21 | 04d93ca4e249cd21 | yes |
| results/e0/run-2/e0-report.json | a7738f0ceb8458ec | a7738f0ceb8458ec | yes |
| results/e1/actors.json | 14688b2c9b1e61ad | 14688b2c9b1e61ad | yes |
| results/e1/analysed-clearing-actors.json | fbb5e153b6bb530f | fbb5e153b6bb530f | yes |
| results/e1/category-crosscheck.json | eb5de0194d80d7ae | eb5de0194d80d7ae | yes |
| results/e1/coverage-check.json | d413839bdbd9079b | d413839bdbd9079b | yes |
| results/e1/evidence-sample.jsonl | dad7d9ecbee9af14 | dad7d9ecbee9af14 | yes |
| results/e1/evidence-set.jsonl.gz | 98b55e8024238f6a | 98b55e8024238f6a | yes |
| results/e1/exclusions.json | e77ba0a504e36d5f | e77ba0a504e36d5f | yes |
| results/e1/exposure-by-stratum.json | 69e40a99b444e8f2 | 2fea6793afadf7d8 | NO |
| results/e1/exposure.json | 25594ef8804c3508 | f0cf909bb7124e8d | NO |
| results/e1/lines-t-star-amended.jsonl.gz | 5ee75c46632418de | 5ee75c46632418de | yes |
| results/e1/lines.jsonl.gz | d19d1717db9e7d19 | d19d1717db9e7d19 | yes |
| results/e1/predicate-unknowns.json | 99ec4a5fabcdc4af | 99ec4a5fabcdc4af | yes |
| results/e1/value-fallback.json | 12a5ba137b63dd65 | 12a5ba137b63dd65 | yes |
| results/e2/confounders.json | 99afde938fd681fe | 99afde938fd681fe | yes |
| results/e2/hypotheses.json | eb43d763e5ee882f | 94ecc3631ca37812 | NO |
| results/e3/confounders.json | a17d465c04962c1b | a17d465c04962c1b | yes |
| results/e3/gate-held.json | 67daeeca5d8a5453 | 67daeeca5d8a5453 | yes |
| results/e3/human-hold-composition.json | 5823edd3b29a1691 | 5823edd3b29a1691 | yes |
| results/e3/human-hold.json | 9524d1d4544471d7 | 9524d1d4544471d7 | yes |
| results/e3/lag-bands.json | 561b9f8fe62e64ae | 561b9f8fe62e64ae | yes |
| results/e3/verdict-by-outcome.json | 1a6a50ed6a649937 | 1a6a50ed6a649937 | yes |
| results/e4/arms-classified-lines.json | 287a2d1951c1df6b | 287a2d1951c1df6b | yes |
| results/e4/arms.json | c24c34aa5dc2ebd4 | c24c34aa5dc2ebd4 | yes |
| results/e4/h4.json | 1c3e0400258cae6e | 4760effd6807ed01 | NO |
| results/e4/sample-frame.json | 95a410a21d867552 | 95a410a21d867552 | yes |
| results/e4/sample.json | def21c85339f8a26 | def21c85339f8a26 | yes |
| results/e4/timeline.json | d8f39eb8f902bf7e | 453c69c8487b69e5 | NO |
| results/e4/views-timeline.jsonl | dc92705897db922c | dc92705897db922c | yes |
| results/e4/views.jsonl | 74c51af5febe1e06 | 74c51af5febe1e06 | yes |
| results/e4-exploratory/arms-exploratory.json | 18489fdad1523161 | 18489fdad1523161 | yes |
| results/e4-exploratory/h4-exploratory.json | aeb62b2a9197d225 | aeb62b2a9197d225 | yes |
| results/e5/derivation.json | 3cbf9d9b0adc76cf | 3cbf9d9b0adc76cf | yes |
| results/e5/sufficiency.json | 2bc621ab99434259 | 2bc621ab99434259 | yes |
| results/e5/trace-2-way.json | 5affb9165555f897 | 5affb9165555f897 | yes |
| results/e5/trace-3-way-invoice-after-receipt.json | b526262dba4228b2 | b526262dba4228b2 | yes |
| results/e5/trace-3-way-invoice-before-receipt.json | adc1fc3880e0f933 | adc1fc3880e0f933 | yes |
| results/e6/cost.json | 473e71f251d67e09 | 473e71f251d67e09 | yes |
| results/e7/comparisons.json | 3eb78536a1aea74e | 3eb78536a1aea74e | yes |
| results/e7/evidence-set.jsonl.gz | 0d0b09caceebd1c8 | 0d0b09caceebd1c8 | yes |
| results/e7/exposure.json | d81ee233499642fa | d81ee233499642fa | yes |
| results/e7/predicates.json | 4a5239dfc1022152 | 4a5239dfc1022152 | yes |
| results/e7/units.json | 69703a41567fe00c | 69703a41567fe00c | yes |
| results/e7/unknown-overlap.json | fefbaee64501d20f | fefbaee64501d20f | yes |
| results/e7/vocabulary.json | e85cc2204600d2ed | e85cc2204600d2ed | yes |
| paper/paper.md | 58c3e7e173568ea2 | 58c3e7e173568ea2 | yes |
| paper/filled-template.json | 317df03a12925a39 | 08fb355f738ac7aa | NO |
| README.md | f53a38c0b81f5e66 | f53a38c0b81f5e66 | yes |
| paper-tex/main.tex | 9b15b0a5e1d26719 | 9b15b0a5e1d26719 | yes |
| paper/figures/fig1-exposure.pdf | 682bee99c4d210a1 | 32edfeba5d2e3583 | NO |
| paper/figures/fig1-exposure.svg | 9f8af9656ec4bc35 | 740df62d35d19b8f | NO |
| paper/figures/fig2-hold-rates.pdf | 9ab743e26726f1c6 | 2a47aa85a0eb39d2 | NO |
| paper/figures/fig2-hold-rates.svg | c64ee1d1aa701986 | a95c5ced82e18d32 | NO |
| paper/figures/fig3-lag-bands.pdf | c94a270fde1231b7 | 4aa81894dd046a9a | NO |
| paper/figures/fig3-lag-bands.svg | 06d6c08af9ef1622 | 6c6c31ea58184a61 | NO |
| paper/figures/fig4-verdict-outcome.pdf | cde97e311a1b72d3 | 90e7d43ec09b50dc | NO |
| paper/figures/fig4-verdict-outcome.svg | 6017bf321f2f4935 | 5992315bd669d363 | NO |

The machine-dependent records and earlier verification records were excluded exactly as listed in `scripts/reproduce.py`: E0 timings, E6 timing/hardware, internal reproducibility timing, CI runs, package smoke records, gate/data-check reports, mutation records, the results index, double-run/check records, and the superseded E0 run 1. These are not claims of externally reproduced timings or independently rerun mutation tests.

## What The JSON Differences Show

Parsed comparison with the committed JSON found:

| Result File | Differing Values | Maximum Absolute Numeric Difference | Kind |
| --- | --- | --- | --- |
| results/e1/exposure-by-stratum.json | 309 | 1.1102230246251565e-16 | Numeric values only |
| results/e1/exposure.json | 5 | 2.710505431213761e-20 | Numeric values only |
| results/e2/hypotheses.json | 6 | 5.421010862427522e-20 | Numeric values only |
| results/e4/h4.json | 6 | 5.421010862427522e-20 | Numeric values only |
| results/e4/timeline.json | 10 | not applicable | UTC timestamp strings only |

These observations do not establish the platform-level cause of the numerical differences, and they do not override the strict byte-for-byte failures. I have not classified the figure or filled-template differences further. The generated paper text and TeX are byte-identical to the release.

Please keep the reproduction status pending rather than describing this attempt as a successful external reproduction.
