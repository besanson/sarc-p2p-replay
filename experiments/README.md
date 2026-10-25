# experiments/

E0 to E7 runners, the seeded sample draw, analysis and slot writers. Phase C.
Outputs and what each holds: `results/README.md`.

| runner | what it does |
|---|---|
| `e0.py` | E0 pilot and the stop conditions of prereg section 2.2 (`results/e0/`) |
| `e1.py` | E1 exposure: replays every analysed clearing, writes the evidence set, line table and exposure slots (`results/e1/`) |
| `e2.py` | E2 consequence on the E1 evidence set: H1 to H3, raw p-values, confounder tables (`results/e2/`) |
| `e3.py` | E3 gate effect and human hold on the E1 evidence set (`results/e3/`) |
| `e4_sample.py` | E4 sample draw and ERP and timeline views, before any call (`results/e4/`) |
| `e4_run.py` | E4 calls per family and arm, append-only responses, cap and health rule (`responses/`) |
| `e4.py` | E4 analysis from the committed responses: H4, kappa, arms, Holm (`results/e4/`, `results/e4-exploratory/`) |
| `e5.py` | E5 derivation with paper 5's compiler, unmodified, through an adapter (`results/e5/`) |
| `e6.py` | E6 timing of three full E1 runs, with hardware (`results/e6/`) |
| `e6_cost.py` | E6 cost per decision per family from the responses (`results/e6/cost.json`) |
| `e7_check.py` | E7 vocabulary check on the BPI 2020 logs (`results/e7/vocabulary.json`) |
| `e7.py` | E7 replication on the BPI 2020 declarations (`results/e7/`) |
| `repro.py` | E1, E2 and E3 twice from the log, byte comparison (`results/reproducibility.json`) |
| `common.py` | slot files, Wilson interval, clustered bootstrap, strata |

Each runner has a fixture test in `tests/` and runs only on the registered log
otherwise. `--bootstrap-b` exists for the fixture tests; the registered value
(B = 10,000) is the default.
