SHELL := /usr/bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

# Ensure common binary locations are available to TeX shell-escape (e.g., inkscape)
export PATH := /usr/local/bin:/usr/bin:/bin:$(PATH)

LATEXMK ?= latexmk

# Force LuaLaTeX for native Unicode support (required by fontspec).
# Use 'override' to prevent CI/container environment variables from
# unintentionally switching latexmk back to pdflatex.
override LATEX_ENGINE := lualatex
override LATEXMK_OPTS := -lualatex -shell-escape -interaction=nonstopmode -halt-on-error -file-line-error

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
	  echo "    $$d: $(LATEXMK) $(LATEXMK_OPTS) $$b"; \
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
