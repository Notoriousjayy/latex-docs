# Makefile - Optimized LaTeX build system
# Supports parallel builds, category filtering, and incremental compilation
SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

# Configuration
LATEXMK ?= latexmk
LATEX_ENGINE ?= lualatex
LATEXMK_OPTS ?= -$(LATEX_ENGINE) -interaction=nonstopmode -halt-on-error -file-line-error -shell-escape -synctex=1

# Parallelism: Use available cores minus 1 (or 4 if nproc not available)
JOBS ?= $(shell nproc 2>/dev/null | awk '{print $$1-1}' || echo 4)

# Source directories (categories)
CATEGORIES := $(shell find src -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort)

# All root documents (files with \documentclass)
ROOT_TEX := $(shell grep -rl --include='*.tex' '^\s*\\documentclass' src 2>/dev/null || true)
ROOT_PDF := $(patsubst %.tex,%.pdf,$(ROOT_TEX))

# ============================================================================
# Help
# ============================================================================
.PHONY: help
help:
	@echo "LaTeX Document Build System"
	@echo ""
	@echo "Targets:"
	@echo "  make build-all         Build all documents (sequential)"
	@echo "  make build-parallel    Build all documents (parallel, uses $(JOBS) jobs)"
	@echo "  make build-category-X  Build documents in category X"
	@echo "  make list-roots        List all buildable documents"
	@echo "  make list-categories   List available categories"
	@echo "  make clean             Remove auxiliary files (keep PDFs)"
	@echo "  make distclean         Remove all generated files including PDFs"
	@echo ""
	@echo "Available categories: $(CATEGORIES)"
	@echo ""
	@echo "Examples:"
	@echo "  make build-category-security    # Build only security docs"
	@echo "  make build-parallel JOBS=8      # Build all with 8 parallel jobs"

# ============================================================================
# Discovery
# ============================================================================
.PHONY: list-roots
list-roots:
	@echo "Detected LaTeX roots ($(words $(ROOT_TEX)) documents):"
	@if [[ -z "$(ROOT_TEX)" ]]; then \
	  echo "  (none found under src/)"; \
	else \
	  printf "  %s\n" $(ROOT_TEX); \
	fi

.PHONY: list-categories
list-categories:
	@echo "Available categories:"
	@for cat in $(CATEGORIES); do \
	  count=$$(grep -rl --include='*.tex' '^\s*\\documentclass' "src/$$cat" 2>/dev/null | wc -l); \
	  echo "  $$cat ($$count documents)"; \
	done

# ============================================================================
# Sequential Build
# ============================================================================
.PHONY: build-all
build-all:
	@if [[ -z "$(ROOT_TEX)" ]]; then \
	  echo "ERROR: No LaTeX roots found."; \
	  exit 2; \
	fi
	@echo "Building $(words $(ROOT_TEX)) documents sequentially..."
	@for f in $(ROOT_TEX); do \
	  echo "==> $$f"; \
	  d="$$(dirname "$$f")"; \
	  b="$$(basename "$$f")"; \
	  (cd "$$d" && $(LATEXMK) $(LATEXMK_OPTS) "$$b") || echo "    ⚠ Build warning for $$f"; \
	done
	@echo "Build complete."

# ============================================================================
# Parallel Build
# ============================================================================
.PHONY: build-parallel
build-parallel:
	@if [[ -z "$(ROOT_TEX)" ]]; then \
	  echo "ERROR: No LaTeX roots found."; \
	  exit 2; \
	fi
	@echo "Building $(words $(ROOT_TEX)) documents in parallel ($(JOBS) jobs)..."
	@printf '%s\n' $(ROOT_TEX) | xargs -P $(JOBS) -I {} bash -c '\
	  f="{}"; \
	  d="$$(dirname "$$f")"; \
	  b="$$(basename "$$f")"; \
	  echo "==> $$f"; \
	  (cd "$$d" && $(LATEXMK) $(LATEXMK_OPTS) "$$b" >/dev/null 2>&1) && echo "    ✓ $$f" || echo "    ✗ $$f"'
	@echo "Parallel build complete."

# ============================================================================
# Category-specific builds
# ============================================================================
define category_rule
.PHONY: build-category-$(1)
build-category-$(1):
	@ROOTS=$$$$(grep -rl --include='*.tex' '^\s*\\documentclass' src/$(1) 2>/dev/null || true); \
	if [[ -z "$$$$ROOTS" ]]; then \
	  echo "No documents found in src/$(1)"; \
	  exit 0; \
	fi; \
	COUNT=$$$$(echo "$$$$ROOTS" | wc -w); \
	echo "Building $$$$COUNT documents in category: $(1)"; \
	for f in $$$$ROOTS; do \
	  echo "==> $$$$f"; \
	  d="$$$$(dirname "$$$$f")"; \
	  b="$$$$(basename "$$$$f")"; \
	  (cd "$$$$d" && $(LATEXMK) $(LATEXMK_OPTS) "$$$$b") || echo "    ⚠ Build warning"; \
	done; \
	echo "Category $(1) complete."
endef

$(foreach cat,$(CATEGORIES),$(eval $(call category_rule,$(cat))))

# ============================================================================
# Cleaning
# ============================================================================
.PHONY: clean
clean:
	@if [[ -z "$(ROOT_TEX)" ]]; then \
	  echo "Nothing to clean."; \
	  exit 0; \
	fi
	@echo "Cleaning auxiliary files..."
	@for f in $(ROOT_TEX); do \
	  d="$$(dirname "$$f")"; \
	  b="$$(basename "$$f")"; \
	  (cd "$$d" && $(LATEXMK) -c "$$b" 2>/dev/null) || true; \
	done
	@echo "Clean complete."

.PHONY: distclean
distclean:
	@if [[ -z "$(ROOT_TEX)" ]]; then \
	  echo "Nothing to distclean."; \
	  exit 0; \
	fi
	@echo "Removing all generated files..."
	@for f in $(ROOT_TEX); do \
	  d="$$(dirname "$$f")"; \
	  b="$$(basename "$$f")"; \
	  (cd "$$d" && $(LATEXMK) -C "$$b" 2>/dev/null) || true; \
	done
	@find src -name "*.pdf" -type f -delete 2>/dev/null || true
	@echo "Distclean complete."

# ============================================================================
# Incremental build (only changed files)
# ============================================================================
.PHONY: build-changed
build-changed:
	@echo "Building only changed documents..."
	@CHANGED=$$(git diff --name-only HEAD~1 HEAD 2>/dev/null | grep '\.tex$$' || echo ""); \
	if [[ -z "$$CHANGED" ]]; then \
	  echo "No .tex files changed since last commit."; \
	  exit 0; \
	fi; \
	for tex in $$CHANGED; do \
	  if grep -q '^\s*\\documentclass' "$$tex" 2>/dev/null; then \
	    echo "==> $$tex"; \
	    d="$$(dirname "$$tex")"; \
	    b="$$(basename "$$tex")"; \
	    (cd "$$d" && $(LATEXMK) $(LATEXMK_OPTS) "$$b") || echo "    ⚠ Build warning"; \
	  fi; \
	done
	@echo "Incremental build complete."
