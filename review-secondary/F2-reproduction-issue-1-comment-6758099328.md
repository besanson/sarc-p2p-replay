## Reproduction attempt: v1.0.1

Gastón, I reran this in the same clone with the existing data and environment, as requested:

```sh
git fetch --tags && git checkout v1.0.1 && make reproduce
```

The tag resolved to `5be6cd6dc3a332e1fe4cd808541a9b31af50c107`. I kept Pandoc 3.1.3 on PATH, as in the previous attempt.

The run failed during paper generation with a `FileNotFoundError` for `out/reproduce/root/results/reproduction/attempt-1.json`. The file exists in the checkout at `results/reproduction/attempt-1.json`, but was absent from the regenerated results tree.

`make reproduce` exited with code 2. **No `out/reproduce/report.md` was written**, so there is no generated report to paste. The comparison stage was not reached; this is not a successful reproduction.

- Reproduction attempted by Eduardo Arana, Independent Researcher.
- Environment: macOS 26.7.2 (build 25G332), arm64; Python 3.13.16.
- Run date: 2026-11-10 UTC, as reported by the machine clock.
- No repository code, tests, registered hashes, or expected results were edited. The tracked checkout was clean before and after the run. The generated v1.0.0 gate report was preserved in a stash before switching tags.
- Only the requested reproduction command was run for v1.0.1; I did not rerun tests or gates or patch the failure.
- Copilot helped execute the commands and inspect the output; I had no role in developing the repository.

Full command output follows, with the checkout's absolute path replaced by `<checkout>`:

```text
.venv/bin/python scripts/reproduce.py
reproduce: E0 run 2
reproduce: E1
reproduce: E2
reproduce: E3
reproduce: E4 sample draw
reproduce: E4 analysis
reproduce: E5
reproduce: E7
reproduce: E6 cost
reproduce: round-1 slots
reproduce: round-2 slots
reproduce: round-3 slots
reproduce: paper
Traceback (most recent call last):
  File "<checkout>/scripts/reproduce.py", line 247, in <module>
    sys.exit(main())
             ~~~~^^
  File "<checkout>/scripts/reproduce.py", line 242, in main
    regenerate_paper(res, OUT / "paper")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "<checkout>/scripts/reproduce.py", line 124, in regenerate_paper
    fill_paper.run(out_paper=paper_dir / "paper.md", out_filled=paper_dir / "filled-template.json",
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                   readme=paper_dir / "README.md")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<checkout>/scripts/fill_paper.py", line 645, in run
    paper, filled = fill(template.read_text(encoding="utf-8"))
                    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<checkout>/scripts/fill_paper.py", line 565, in fill
    value = walk(load(source), keys)
                 ~~~~^^^^^^^^
  File "<checkout>/scripts/fill_paper.py", line 77, in load
    _cache[source] = json.loads((RESULTS / source).read_text(encoding="utf-8"))
                                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.13/3.13.16/Frameworks/Python.framework/Versions/3.13/lib/python3.13/pathlib/_local.py", line 546, in read_text
    return PathBase.read_text(self, encoding, errors, newline)
           ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.13/3.13.16/Frameworks/Python.framework/Versions/3.13/lib/python3.13/pathlib/_abc.py", line 632, in read_text
    with self.open(mode='r', encoding=encoding, errors=errors, newline=newline) as f:
         ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.13/3.13.16/Frameworks/Python.framework/Versions/3.13/lib/python3.13/pathlib/_local.py", line 537, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '<checkout>/out/reproduce/root/results/reproduction/attempt-1.json'
make: *** [reproduce] Error 1
```
