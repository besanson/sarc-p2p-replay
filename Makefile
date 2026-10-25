.PHONY: help bootstrap siblings venv fetch-data check-data preflight bootstrap-paper test lint mutate gates gates-quick fill figures paper clean

# Paper 7: sarc-p2p-replay. Apache License 2.0.
# Target layout as paper 6 (gigo-jev-probe) and paper 5 (sarc-authority-derivation):
# `bootstrap` prepares the replay; `bootstrap-paper` prepares the paper toolchain
# and is deliberately separate.

PYTHON ?= python3
VENV   ?= .venv
# test and lint run in the venv once `make venv` has made it
RUN    := $(if $(wildcard $(VENV)/bin/python),$(VENV)/bin/python,$(PYTHON))

help:
	@echo "bootstrap        siblings at pin, venv, data fetch with SHA-256 check, preflight"
	@echo "siblings         clone ../dqSarc ../sarc-authority-derivation ../gigo-jev-probe and check out the engines.lock pins"
	@echo "venv             create $(VENV) and install the package with [dev]"
	@echo "fetch-data       download the registered logs into data/ and check SHA-256 against prereg/data.lock"
	@echo "check-data       check the files already in data/ (no download)"
	@echo "preflight        report keys, data and sibling pins (never prints a key)"
	@echo "bootstrap-paper  check the LaTeX toolchain for paper-tex/ (separate from bootstrap)"
	@echo "test             pytest"
	@echo "lint             terminology and proof-status lints"
	@echo "mutate           mutation gate on src/ (kill score >= 0.85, no uncovered mutant)"
	@echo "gates            release gates G1 to G9 (out/gates/report.json); gates-quick skips the log replays"
	@echo "fill             paper/paper.md and results/filled-template.json from paper/template.md and the slots"
	@echo "figures          paper/figures/ (SVG and PDF) from the slots"
	@echo "paper            fill, figures, paper-tex/main.tex; the PDF when a LaTeX engine is installed"

bootstrap: siblings venv fetch-data preflight
	@echo "bootstrap: done"

siblings:
	$(PYTHON) -I scripts/siblings.py

venv:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -q -e '.[dev]'

fetch-data:
	$(PYTHON) -I scripts/fetch_data.py

check-data:
	$(PYTHON) -I scripts/fetch_data.py --check

preflight:
	$(PYTHON) preflight.py

bootstrap-paper:
	@for t in pandoc tectonic latexmk pdflatex xelatex; do \
		if command -v $$t >/dev/null 2>&1; then echo "$$t: found"; else echo "$$t: absent"; fi; done
	@$(RUN) -c "import matplotlib; print('matplotlib:', matplotlib.__version__)" 2>/dev/null || echo "matplotlib: absent"

test:
	$(RUN) -m pytest

lint:
	$(RUN) -m lint.terminology
	$(RUN) -m lint.proof_status
	$(RUN) -m lint.typed_numerals

gates:
	$(RUN) scripts/gates.py

gates-quick:
	$(RUN) scripts/gates.py --quick

fill:
	$(RUN) scripts/fill_paper.py

figures:
	$(RUN) scripts/figures.py

paper: figures fill
	$(RUN) scripts/build_tex.py

mutate:
	rm -rf mutants
	$(VENV)/bin/mutmut run
	$(VENV)/bin/mutmut export-cicd-stats
	$(RUN) scripts/mutation_check.py

clean:
	rm -rf out mutants .pytest_cache build dist *.egg-info
