# sarc-p2p-replay

Paper 7 of the SARC programme. Working title: **Silent Evidence Defects in the
Wild: A Registered Replay of a Real Purchase-to-Pay Process**. Author: Gaston
Besanson, Universidad Torcuato Di Tella. Sole author; AI tools are support,
disclosed in the acknowledgements only.

**Status: Phase A0.** Skeleton, documents and the draft preregistration
`prereg/p7-v1.md`. No analysis, no model call and no result exist in this
tree. Nothing is binding until the author tags `prereg-p7-v1`.

## What the paper does

Papers 1 to 6 showed the mechanism on constructed domains and made no
prevalence claim. Paper 7 replays every invoice clearing in the BPI Challenge
2019 purchase-to-pay log through a deterministic min() gate built from the
programme's own predicates (D1 to D7, `prereg/p7-v1.md` section 3). For each
clearing it reconstructs the evidence held at clearing time, records what the
gate would have held, and reads what followed in the log. It reports exposure
in count and euros, the corrective events that follow a defect, the gate's
reach and hold cost, and, on a registered sample, what two model families
decide on the same ERP view beside the human decision in the log and the gate
verdict. It replicates the consequence shape on the BPI Challenge 2020
declaration logs. No new mechanism.

What it does not claim: see `CLAIMS.md` (non-claims) and `COVERAGE.md`
(defect classes the log cannot expose).

## Layout

| path | content |
|---|---|
| `prereg/` | registration `p7-v1.md`, `data.lock` (DOIs, URLs, SHA-256), outcome patterns, ERP view template, column mapping, `DEVIATIONS.md` |
| `CLAIMS.md` `NOVELTY.md` `COVERAGE.md` | claims C1 to C13 and non-claims; prior-art fence; coverage matrix |
| `DECISIONS.md` `FINAL-AUDIT.md` | decision log; release audit (all items open) |
| `engines.lock` | pinned siblings: dqSarc, sarc-authority-derivation, gigo-jev-probe |
| `preflight.py` | reports keys, data and sibling pins; never prints a key |
| `lint/` | terminology lint |
| `src/p2p_replay/` | replay engine (Phase B; empty at A0) |
| `experiments/` `responses/` `results/` | E0 to E7 runners, E4 caches, slots (Phases C and later) |
| `paper/` `paper-tex/` `review-secondary/` | draft, gates, external reviews (Phases D and later) |
| `data/` | gitignored; fetched by `make bootstrap` |

## Reproduce

```
make bootstrap        # siblings at pin, .venv, data fetch with SHA-256 check, preflight
make test             # pytest
make lint             # terminology lint
make bootstrap-paper  # LaTeX toolchain for the paper (separate; not needed for the replay)
```

Keys, when Phase C needs them, live only in `.env` (see `.env.example`). They
are never committed, printed or copied.

## Data

BPI Challenge 2019 (CC BY 4.0) and BPI Challenge 2020 International and
Domestic Declarations (CC BY-NC 4.0), from 4TU.ResearchData, by Boudewijn van
Dongen. DOIs and SHA-256 in `prereg/p7-v1.md` section Data. The logs are not
redistributed here.

## Licence

Code and documents: Apache License 2.0 (`LICENSE`). The event logs keep their
own licences.
