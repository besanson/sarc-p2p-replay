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
| `e2/hypotheses.json` | H1, H2, H3 at W = 60: O rates, difference, bootstrap SE, z, raw one-sided p; the H1 all-category comparison and W = 30, descriptive; the Holm table over the five-test family (`holm`, written by the E4 analysis) | 3.7, 4, 5 |
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
| `e4/h4.json` | per family: hold rates on defective and clean lines, d, TOST p-values; the Holm table over the five-test family | 4, 7; DEVIATIONS |
| `e4/arms.json` | per arm (people, each family, gate): hold rates, kappa with the gate, value released on defective lines, expected correctives, invalid counts, cost per decision | 7 |
| `e4/double-run.json` | the E4 analysis run twice from the committed responses: byte comparison | 7 |

## e4-exploratory/ (E4 exploratory timeline arm, never in Holm: `experiments/e4.py --arm e4-exploratory`)

| file | holds | section |
|---|---|---|
| `e4-exploratory/h4-exploratory.json` | exploratory: per family hold rates on defective and clean lines with the timeline view, d, TOST p-values (descriptive) | 7 (exploratory) |
| `e4-exploratory/arms-exploratory.json` | exploratory: the arm measures of `e4/arms.json` with the timeline view | 7 (exploratory) |
| `e4-exploratory/double-run.json` | the exploratory analysis run twice: byte comparison | 7 (exploratory) |

## e5/ (E5, derivation with paper 5's compiler: `experiments/e5.py`)

| file | holds | section |
|---|---|---|
| `e5/derivation.json` | per category: states, clearings per declared loss, the compiler's core, reducts and minimum-cardinality field set, the derived contract against the registered one, "reproduces" or "does not reproduce" | 3.1, 6 (E5) |
| `e5/trace-<category>.json` | the compiler's full output per category: candidate context, certificate, witnesses, every state with its losses | 6 (E5) |
| `e5/double-run.json` | E5 run twice: byte comparison | 6 (E5) |

## e6/ (E6, timing: `experiments/e6.py`)

| file | holds | section |
|---|---|---|
| `e6/timing-e1.json` | wall time of the full E1 replay over three runs, median, seconds per decision, hardware; the cost column waits for E4 | 6 (E6) |
| `e6/cost.json` | USD per decision per family and arm, from the responses (retries and re-requests included); spend total against the cap | 6 (E6) |

## e7/ (E7, BPI 2020 declarations: `experiments/e7_check.py`, `experiments/e7.py`)

| file | holds | section |
|---|---|---|
| `e7/vocabulary.json` | per log: activity names and counts, attribute keys, T_end'; per registered list, which names occur; mapped attributes present | 8 |
| `e7/units.json` | per log and pooled: cases, payments, exclusions after T_end' - W, units | 8 |
| `e7/predicates.json` | per log and pooled: D1', D2', D3' pass, fail and unknown counts | 8 |
| `e7/exposure.json` | share of payments and of paid value (case `Amount`) with at least one failed predicate | 8 |
| `e7/comparisons.json` | O' rate for D1', D2', D3' failures against all-pass, difference and case-clustered bootstrap interval; descriptive, not in Holm | 8 |
| `e7/evidence-set.jsonl.gz` | one record per payment unit, ids hashed | 8 |
| `e7/double-run.json` | E7 vocabulary check and replication run twice: byte comparison | 8 |

## Checks

| file | holds | section |
|---|---|---|
| `mutation.json` | mutation gate result on `src/` (kill score, counts, threshold) | 10 |
| `checks-d-c-2.json` | D-C-2 B applied: E1 re-run from the log against the committed files, E2 re-run, E3 double run | DEVIATIONS |

## Reproducibility (`experiments/repro.py`)

| file | holds | section |
|---|---|---|
| `reproducibility.json` | E1, E2 and E3 run twice from the log: run times and the per-file byte comparison | 6 |
