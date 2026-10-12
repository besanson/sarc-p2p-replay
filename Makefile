.PHONY: help bootstrap siblings venv fetch-data check-data preflight bootstrap-paper test lint clean

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
	@echo "lint             terminology lint over live prose"

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
	@command -v latexmk >/dev/null 2>&1 && echo "latexmk: found" || echo "latexmk: absent"
	@command -v pdflatex >/dev/null 2>&1 && echo "pdflatex: found" || echo "pdflatex: absent"
	@echo "bootstrap-paper: paper-tex/ has no sources before Phase D; nothing to build"

test:
	$(RUN) -m pytest

lint:
	$(RUN) -m lint.terminology

clean:
	rm -rf out .pytest_cache build dist *.egg-info
