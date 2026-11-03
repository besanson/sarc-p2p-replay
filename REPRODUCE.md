# Reproducing paper 7 (v1.0.0)

For an external reproducer. You need Python 3.11 or later, git, network access to github.com,
pypi.org and data.4tu.nl, and about 2 GB of free disk. pandoc is needed to regenerate
`paper-tex/main.tex` (the committed file was written by pandoc 3.1.3; another version may write
different bytes). A LaTeX engine is optional: the PDF is built and compared for information only.
No API key is needed: the model responses are committed and no model is called.

```
git clone --branch v1.0.0 https://github.com/besanson/sarc-p2p-replay.git
```
Clones the repository at the release tag.

```
cd sarc-p2p-replay
```
Every command below runs from the repository root.

```
make bootstrap
```
Clones the sibling repositories at their `engines.lock` pins next to this one, creates `.venv`
with the package and its pinned dependencies, downloads the three event logs by the URLs in
`prereg/data.lock` and checks each SHA-256 (a file with another hash is deleted), then runs preflight.

```
make test
```
Runs the test suite; every test should pass (none is skipped once the siblings are present).

```
make gates
```
Runs the release gates G1 to G9 (about 25 minutes; G4 replays the whole log); none should fail.

```
make reproduce
```
Regenerates every deterministic result into `out/reproduce/` (about 30 minutes): E0 run 2, E1,
E2, E3, the E4 sample draw and both E4 analyses from the committed responses, E5, E7, the E6 cost
table, the round-1 to round-3 slots, then the paper, its figures, the README's generated blocks and
`paper-tex/main.tex` from the regenerated slots. It compares each file's SHA-256 with the committed
one, prints the table and a verdict line, and writes both to `out/reproduce/report.md`.

The machine-dependent records (wall times, hardware, CI runs, the package smoke test, the gate and
data-check reports, the mutation runs) and the verification records of earlier runs (double-run
comparisons, the superseded E0 run 1) are listed in the report by name and not compared.

Open an issue titled 'Reproduction of v1.0.0' with the contents of out/reproduce/report.md, your operating system, Python version and the date.
