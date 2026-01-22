# Makefile - Optimized LaTeX build system for latex-docs
# Supports parallel builds, category filtering, and incremental compilation
SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

# =============================================================================
# Configuration
# =============================================================================
LATEXMK      ?= latexmk
LATEX_ENGINE ?= pdf
LATEXMK_OPTS ?= -$(LATEX_ENGINE) -interaction=nonstopmode -halt-on-error \
                -file-line-error -shell-escape -synctex=1

# Parallelism: default to nproc-1 or 4
JOBS ?= $(shell nproc 2>/dev/null | awk '{print int($$1 * 0.75)}' || echo 4)

# Directories
SRC_DIR   := src
BUILD_DIR := public/pdfs
LOG_DIR   := public/logs

# Source discovery
CATEGORIES := $(shell find $(SRC_DIR) -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort)
ROOT_TEX   := $(shell find $(SRC_DIR) -name '*.tex' -type f -exec grep -l '^\s*\\documentclass' {} \; 2>/dev/null | sort)
ROOT_COUNT := $(words $(ROOT_TEX))

# =============================================================================
# Default target
# =============================================================================
.PHONY: help
help:
	@echo "╔══════════════════════════════════════════════════════════════════╗"
	@echo "║              LaTeX Document Build System                         ║"
	@echo "╠══════════════════════════════════════════════════════════════════╣"
	@echo "║ Documents: $(ROOT_COUNT) roots across $(words $(CATEGORIES)) categories"
	@echo "╚══════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Build Commands:"
	@echo "  make build-all          Build all documents sequentially"
	@echo "  make build-parallel     Build all documents in parallel ($(JOBS) jobs)"
	@echo "  make build-category-X   Build only category X"
	@echo "  make build-changed      Build only files changed since last commit"
	@echo ""
	@echo "Publishing:"
	@echo "  make publish            Build all + organize PDFs for GitHub Pages"
	@echo "  make publish-parallel   Same as publish, but parallel build"
	@echo ""
	@echo "Utilities:"
	@echo "  make list-roots         List all buildable documents"
	@echo "  make list-categories    List categories with document counts"
	@echo "  make clean              Remove auxiliary files (keep PDFs)"
	@echo "  make distclean          Remove all generated files"
	@echo ""
	@echo "Categories: $(CATEGORIES)"
	@echo ""
	@echo "Examples:"
	@echo "  make build-category-security"
	@echo "  make build-parallel JOBS=8"
	@echo "  make publish"

# =============================================================================
# Discovery targets
# =============================================================================
.PHONY: list-roots
list-roots:
	@echo "LaTeX root documents ($(ROOT_COUNT) total):"
	@echo ""
	@for f in $(ROOT_TEX); do echo "  $$f"; done

.PHONY: list-categories
list-categories:
	@echo "Categories with document counts:"
	@echo ""
	@for cat in $(CATEGORIES); do \
	  count=$$(find "$(SRC_DIR)/$$cat" -name '*.tex' -type f -exec grep -l '^\s*\\documentclass' {} \; 2>/dev/null | wc -l); \
	  printf "  %-25s %3d documents\n" "$$cat" "$$count"; \
	done

# =============================================================================
# Build single document (internal helper)
# =============================================================================
define build_one
	@tex_file="$(1)"; \
	dir="$$(dirname "$$tex_file")"; \
	base="$$(basename "$$tex_file")"; \
	name="$${base%.tex}"; \
	echo ""; \
	echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
	echo "Building: $$tex_file"; \
	echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
	mkdir -p "$${dir}/_minted-$${name}"; \
	if (cd "$$dir" && $(LATEXMK) $(LATEXMK_OPTS) "$$base"); then \
	  echo "  ✓ SUCCESS: $${dir}/$${name}.pdf"; \
	else \
	  echo "  ✗ FAILED: $$tex_file"; \
	fi
endef

# =============================================================================
# Sequential build
# =============================================================================
.PHONY: build-all
build-all:
	@if [[ -z "$(ROOT_TEX)" ]]; then \
	  echo "ERROR: No LaTeX roots found in $(SRC_DIR)/"; \
	  exit 2; \
	fi
	@echo "Building $(ROOT_COUNT) documents sequentially..."
	@for f in $(ROOT_TEX); do \
	  $(call build_one,$$f); \
	done
	@echo ""
	@echo "Build complete."

# =============================================================================
# Parallel build
# =============================================================================
.PHONY: build-parallel
build-parallel:
	@if [[ -z "$(ROOT_TEX)" ]]; then \
	  echo "ERROR: No LaTeX roots found in $(SRC_DIR)/"; \
	  exit 2; \
	fi
	@echo "Building $(ROOT_COUNT) documents in parallel ($(JOBS) jobs)..."
	@echo ""
	@printf '%s\n' $(ROOT_TEX) | xargs -P $(JOBS) -I {} bash -c ' \
	  tex_file="{}"; \
	  dir="$$(dirname "$$tex_file")"; \
	  base="$$(basename "$$tex_file")"; \
	  name="$${base%.tex}"; \
	  mkdir -p "$${dir}/_minted-$${name}"; \
	  if (cd "$$dir" && $(LATEXMK) $(LATEXMK_OPTS) "$$base" >/dev/null 2>&1); then \
	    echo "✓ $${dir}/$${name}.pdf"; \
	  else \
	    echo "✗ $$tex_file"; \
	  fi \
	'
	@echo ""
	@echo "Parallel build complete."

# =============================================================================
# Category-specific builds
# =============================================================================
define category_rule
.PHONY: build-category-$(1)
build-category-$(1):
	@ROOTS=$$$$(find $(SRC_DIR)/$(1) -name '*.tex' -type f -exec grep -l '^\s*\\documentclass' {} \; 2>/dev/null | sort); \
	if [[ -z "$$$$ROOTS" ]]; then \
	  echo "No documents found in $(SRC_DIR)/$(1)"; \
	  exit 0; \
	fi; \
	COUNT=$$$$(echo "$$$$ROOTS" | wc -l); \
	echo "Building $$$$COUNT documents in category: $(1)"; \
	for f in $$$$ROOTS; do \
	  dir="$$$$(dirname "$$$$f")"; \
	  base="$$$$(basename "$$$$f")"; \
	  name="$$$${base%.tex}"; \
	  echo ""; \
	  echo "━━━ Building: $$$$f"; \
	  mkdir -p "$$$${dir}/_minted-$$$${name}"; \
	  if (cd "$$$$dir" && $(LATEXMK) $(LATEXMK_OPTS) "$$$$base"); then \
	    echo "  ✓ SUCCESS"; \
	  else \
	    echo "  ✗ FAILED"; \
	  fi; \
	done; \
	echo ""; \
	echo "Category $(1) complete."
endef

$(foreach cat,$(CATEGORIES),$(eval $(call category_rule,$(cat))))

# =============================================================================
# Incremental build (only changed files)
# =============================================================================
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
	    $(call build_one,$$tex); \
	  fi; \
	done
	@echo ""
	@echo "Incremental build complete."

# =============================================================================
# Publish: Build and organize for GitHub Pages
# =============================================================================
.PHONY: publish
publish: build-all organize-pdfs
	@echo "Publish complete. PDFs in $(BUILD_DIR)/"

.PHONY: publish-parallel
publish-parallel: build-parallel organize-pdfs
	@echo "Publish complete. PDFs in $(BUILD_DIR)/"

.PHONY: organize-pdfs
organize-pdfs:
	@echo "Organizing PDFs for publishing..."
	@mkdir -p $(BUILD_DIR) $(LOG_DIR)
	@for tex in $(ROOT_TEX); do \
	  dir="$$(dirname "$$tex")"; \
	  base="$$(basename "$$tex" .tex)"; \
	  rel_dir="$${dir#$(SRC_DIR)/}"; \
	  pdf="$${dir}/$${base}.pdf"; \
	  log="$${dir}/$${base}.log"; \
	  if [[ -f "$$pdf" ]]; then \
	    mkdir -p "$(BUILD_DIR)/$$rel_dir"; \
	    cp "$$pdf" "$(BUILD_DIR)/$$rel_dir/"; \
	  fi; \
	  if [[ -f "$$log" ]]; then \
	    mkdir -p "$(LOG_DIR)/$$rel_dir"; \
	    cp "$$log" "$(LOG_DIR)/$$rel_dir/$${base}.log.txt"; \
	  fi; \
	done
	@echo "Organized $$(find $(BUILD_DIR) -name '*.pdf' | wc -l) PDFs"

# =============================================================================
# Cleaning
# =============================================================================
.PHONY: clean
clean:
	@echo "Cleaning auxiliary files..."
	@for f in $(ROOT_TEX); do \
	  dir="$$(dirname "$$f")"; \
	  base="$$(basename "$$f")"; \
	  (cd "$$dir" && $(LATEXMK) -c "$$base" 2>/dev/null) || true; \
	done
	@find $(SRC_DIR) -name "*.aux" -delete 2>/dev/null || true
	@find $(SRC_DIR) -name "*.fls" -delete 2>/dev/null || true
	@find $(SRC_DIR) -name "*.fdb_latexmk" -delete 2>/dev/null || true
	@echo "Clean complete."

.PHONY: distclean
distclean: clean
	@echo "Removing all generated files..."
	@for f in $(ROOT_TEX); do \
	  dir="$$(dirname "$$f")"; \
	  base="$$(basename "$$f")"; \
	  (cd "$$dir" && $(LATEXMK) -C "$$base" 2>/dev/null) || true; \
	done
	@find $(SRC_DIR) -name "*.pdf" -type f -delete 2>/dev/null || true
	@rm -rf $(BUILD_DIR) $(LOG_DIR) 2>/dev/null || true
	@echo "Distclean complete."

# =============================================================================
# PlantUML rendering
# =============================================================================
.PHONY: render-plantuml
render-plantuml:
	@echo "Rendering PlantUML diagrams..."
	@find $(SRC_DIR) -name "*.puml" ! -name "*config*" | while read puml; do \
	  dir="$$(dirname "$$puml")"; \
	  base="$$(basename "$$puml" .puml)"; \
	  echo "  $$puml"; \
	  mkdir -p "$${dir}/png" "$${dir}/svg"; \
	  plantuml -tpng -o png "$$puml" 2>/dev/null || true; \
	  plantuml -tsvg -o svg "$$puml" 2>/dev/null || true; \
	done
	@echo "PlantUML rendering complete."
