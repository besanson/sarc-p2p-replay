# results/

Slot files. Every figure in the paper comes from a file here, written by code
in `experiments/`; nothing in this directory is edited by hand. Company and
vendor appear only as hashed stratum labels inside the JSON files. Sections
refer to `prereg/p7-v1.1.md`.

## e0/ (E0 pilot, Phase C0)

| file | holds | section |
|---|---|---|
| `e0/run-1/` | E0 run 1 under p7-v1, stopped; superseded by run 2 | 2.2, 6 (E0) |
| `e0/run-2/e0-lines.txt` | the E0 lines, removed from every estimate | 2, 6 (E0) |
| `e0/run-2/e0-report.json` | stop conditions, attribute and activity inventory, frame counts, pilot predicate counts | 2.2, 6 (E0) |
| `e0/run-2/e0-timing.json` | wall time of the E0 passes | 6 (E0) |

## e1/ (E1, exposure: `experiments/e1.py`)

| file | holds | section |
|---|---|---|
| `e1/exclusions.json` | exclusion counts in registered order, T_end, events after T_end, E0 removal, analysed clearings | 2, 2.1 |
| `e1/exposure.json` | per defect class and overall: share of clearings (Wilson and clustered bootstrap) and of cleared value (clustered bootstrap); held-unknown share | 3.5, 5, 6 (E1) |
| `e1/exposure-by-stratum.json` | the same per stratum, with the quartile cutpoints | 2.3, 5, 6 (E1) |
| `e1/value-fallback.json` | cleared-value source counts | 3.4 |
| `e1/category-crosscheck.json` | lines whose Item Category string disagrees with the flag-derived category | 3.1 |
| `e1/coverage-check.json` | each detected row of `COVERAGE.md` (BPI 2019) and whether its predicate failed at least once | 6 (E1) |
| `e1/evidence-set.jsonl.gz` | the full evidence set, one record per analysed clearing, identifiers hashed | 3.9 |
| `e1/lines.jsonl.gz` | one record per framed line: category, value, strata, human hold, gate status at t* (literal reading) | 2, 3.6, 7 |
| `e1/lines-t-star-amended.jsonl.gz` | gate status at t* per framed line under D-C-2 B (D5 not applicable at a t* that is not a clearing) | 7; DEVIATIONS |
| `e1/evidence-sample.jsonl` | the seeded sample export of the evidence set | 3.9 |

## e2/ (E2, consequence: `experiments/e2.py`)

| file | holds | section |
|---|---|---|
| `e2/hypotheses.json` | H1, H2, H3 at W = 60: O rates, difference, bootstrap SE, z, raw one-sided p; the H1 all-category comparison and W = 30, descriptive; Holm deferred to after E4 | 3.7, 4, 5 |
| `e2/confounders.json` | O rates of each comparison's groups per stratum | 2.3, 6 |

## e3/ (E3, gate effect: `experiments/e3.py`)

| file | holds | section |
|---|---|---|
| `e3/gate-held.json` | share of analysed clearings the gate would have held, in count and cleared value | 3.5, 5, 6 (E3) |
| `e3/verdict-by-outcome.json` | the verdict by O table in count and cleared value, at both windows | 3.7, 6 (E3) |
| `e3/lag-bands.json` | D1/D2 failures by lag band in count and cleared value | 3.3, 3.8 |
| `e3/human-hold.json` | human-hold classification of every framed line, unclassified count, human hold rate on defective and on clean lines, under the literal reading and under D-C-2 B | 3.6, 7; DEVIATIONS |
| `e3/confounders.json` | the E3 quantities per stratum | 2.3, 6 |

## e4/ (E4, agent replay: `experiments/e4_sample.py`, `experiments/e4.py`)

| file | holds | section |
|---|---|---|
| `e4/sample.json` | the drawn lines in registered order: hashed id, stratum, status at t* (D-C-2 B), failed predicates, t*, value, the human arm from the log | 7; DEVIATIONS |
| `e4/sample-frame.json` | eligible lines per status and stratum, the allocation, the drawn counts | 7 |
| `e4/views.jsonl` | the ERP view of each sampled line, keyed by order | 7 |
| `e4/views-timeline.jsonl` | the exploratory timeline view of each sampled line, keyed by order (exploratory) | 7 |

## e6/ (E6, timing: `experiments/e6.py`)

| file | holds | section |
|---|---|---|
| `e6/timing-e1.json` | wall time of the full E1 replay over three runs, median, seconds per decision, hardware; the cost column waits for E4 | 6 (E6) |

## Checks

| file | holds | section |
|---|---|---|
| `mutation.json` | mutation gate result on `src/` (kill score, counts, threshold) | 10 |
| `checks-d-c-2.json` | D-C-2 B applied: E1 re-run from the log against the committed files, E2 re-run, E3 double run | DEVIATIONS |

## Reproducibility (`experiments/repro.py`)

| file | holds | section |
|---|---|---|
| `reproducibility.json` | E1, E2 and E3 run twice from the log: run times and the per-file byte comparison | 6 |
