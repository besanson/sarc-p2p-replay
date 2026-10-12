# Decisions

One entry per decision, append-only. A decision that changes a registered item
after the tag `prereg-p7-v1` is a deviation and also goes in
`prereg/DEVIATIONS.md`.

## D-A0-1 Datasets, licences and hashes (2026-10-12)

Verified from the 4TU.ResearchData record pages and the 4TU v2 API, not from
memory:

- **BPI Challenge 2019.** DOI `10.4121/uuid:d06aff4b-79f0-45e6-8ec8-e19730c248f1`.
  Licence as the page states it: CC BY 4.0. One file, `BPI_Challenge_2019.xes`,
  728,558,522 bytes, SHA-256
  `af63bc687fc4152f2123b05c3af7772b37ef3fce2d3f67f812666c9e356baae7`. Published
  counts 251,734 cases and 1,595,923 events, confirmed by tag count.
- **BPI Challenge 2020**, collection DOI
  `10.4121/uuid:52fb97d4-4588-43c9-9d04-3604d4613b51` (no collection-level
  licence; each member states its own). E7 uses the two declaration logs:
  - International Declarations, DOI `10.4121/uuid:2bbf8f6a-fc50-48eb-aa9e-c4ea5ef7e8c5`,
    CC BY-NC 4.0, `InternationalDeclarations.xes.gz`, 1,581,144 bytes, SHA-256
    `b527c8d06255f4312c6ce8f36f7f4110243d84fd6ca48583cd9b80896c601494`, 6,449
    cases and 72,151 events, confirmed.
  - Domestic Declarations, DOI `10.4121/uuid:3f422315-ed9d-4882-891f-e180b5b4feb5`,
    CC BY-NC 4.0, `DomesticDeclarations.xes.gz`, 933,930 bytes, SHA-256
    `0bc3312acf0b9ee5ae6f4ebe9df204005ef11665d62f2d21dd04995161d7532b`, 10,500
    cases and 56,437 events, confirmed.

Neither licence forbids redistribution. The logs are still not committed: the
2019 file is 728 MB, and the 2020 files carry a non-commercial term that the
repository's Apache 2.0 licence should not appear to cover. `data/` is
gitignored; `make bootstrap` fetches by URL and checks SHA-256 against
`prereg/data.lock`. The paper cites both licences and attributes 4TU and the
challenge organisers. The non-commercial term binds use of the BPI 2020 logs, not
the replay code.

"Travel declarations" in the brief is read as the two declaration datasets. The
other three BPI 2020 members are not used.

## D-A0-2 Sibling pins (2026-10-12)

`engines.lock` pins the three siblings at their `main` heads on 2026-10-12:
dqSarc `db6c396128a4df7fe12d13be163b1e7d32087177`, sarc-authority-derivation
`cfb321ec220e83e81a771a048276571f6edf08fb`, gigo-jev-probe
`e1fc75b6686beecd3f4abdd57241ffc46c96e019`. The first two equal paper 6's own
pins. Each is cloned at `../<name>`.

## D-A0-3 Where "as paper 6" resolves (2026-10-12)

gigo-jev-probe (paper 6) carries the preflight shape, `engines.lock`, the
`.env.example` discipline, `prereg/DEVIATIONS.md`, the arm health rule and the
two model families. It carries no Makefile, no lint modules, no gate layout and
no `FINAL-AUDIT.md`; those live in sarc-authority-derivation (paper 5), which
paper 6 pins. "As paper 6" is therefore read as paper 6 where paper 6 has the
item and paper 5 otherwise: the 12-item audit, the G1 to G9 gate names, and the
lint conventions (local negation, fenced and inline code stripped) come from
paper 5.

At A0 only the terminology lint is written (`lint/terminology.py`). The
typed-numeral and proof-status lints need paper prose and property tests to
act on; they are ported from paper 5 in Phases B and D, before any number is in
the draft.

## D-A0-4 Preflight reports, it does not gate, at A0 (2026-10-12)

Paper 6's preflight exits non-zero when a key is missing, because it ran before
model calls. At A0 the brief requires preflight to pass with keys and data
absent. `preflight.py` therefore reports each item (keys, data, siblings) as
present or absent and exits 0; `--require keys,data,siblings` turns any named
item into a hard failure for Phases C and later. It never prints a key and never
raises.
