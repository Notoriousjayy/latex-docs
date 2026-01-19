SHELL := /usr/bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

LATEXMK ?= latexmk
LATEXMK_OPTS ?= -pdf -interaction=nonstopmode -halt-on-error -file-line-error

# Standalone build roots = any .tex containing \documentclass under src/
ROOT_TEX := $(shell grep -rl --include='*.tex' '^[[:space:]]*\\documentclass' src || true)
ROOT_PDF := $(patsubst %.tex,%.pdf,$(ROOT_TEX))

.PHONY: help list-roots build-all clean distclean

help:
	@echo "Targets:"
	@echo "  make build-all     Build all standalone LaTeX roots under src/ (\\documentclass...)"
	@echo "  make list-roots    Print detected build roots"
	@echo "  make clean         Clean aux files for all roots (keeps PDFs)"
	@echo "  make distclean     Clean aux files and PDFs for all roots"

list-roots:
	@echo "Detected LaTeX roots:"
	@if [[ -z "$(ROOT_TEX)" ]]; then \
	  echo "  (none found under src/)"; \
	else \
	  printf "  %s\n" $(ROOT_TEX); \
	fi

build-all:
	@if [[ -z "$(ROOT_TEX)" ]]; then \
	  echo "ERROR: No LaTeX roots found (no src/**/*.tex with \\documentclass)."; \
	  exit 2; \
	fi
	@echo "Building $$(echo $(ROOT_TEX) | wc -w | tr -d ' ') documents..."
	@for f in $(ROOT_TEX); do \
	  echo "==> $$f"; \
	  d="$$(dirname "$$f")"; \
	  b="$$(basename "$$f")"; \
	  (cd "$$d" && $(LATEXMK) $(LATEXMK_OPTS) "$$b"); \
	done
	@echo "Build complete."

clean:
	@if [[ -z "$(ROOT_TEX)" ]]; then \
	  echo "Nothing to clean."; \
	  exit 0; \
	fi
	@for f in $(ROOT_TEX); do \
	  d="$$(dirname "$$f")"; \
	  b="$$(basename "$$f")"; \
	  (cd "$$d" && $(LATEXMK) -c "$$b"); \
	done

distclean:
	@if [[ -z "$(ROOT_TEX)" ]]; then \
	  echo "Nothing to distclean."; \
	  exit 0; \
	fi
	@for f in $(ROOT_TEX); do \
	  d="$$(dirname "$$f")"; \
	  b="$$(basename "$$f")"; \
	  (cd "$$d" && $(LATEXMK) -C "$$b"); \
	done
	@rm -f $(ROOT_PDF)
