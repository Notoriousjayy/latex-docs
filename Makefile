# Makefile - Developer-facing facade for the latex-docs build system
SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

LATEXMK ?= latexmk
JOBS ?= $(shell nproc 2>/dev/null | awk '{print int($$1 * 0.75)}' || echo 4)
SRC_DIR := src
BUILD_DIR := public/pdfs
LOG_DIR := public/logs

.PHONY: help
help:
	@echo "LaTeX document build facade"
	@echo ""
	@echo "Commands:"
	@echo "  make list-roots"
	@echo "  make list-categories"
	@echo "  make build-all"
	@echo "  make build-parallel JOBS=8"
	@echo "  make build-category-<name>"
	@echo "  make build-changed"
	@echo "  make clean"
	@echo "  make distclean"

.PHONY: list-roots
list-roots:
	@python3 tooling/scripts/latex_build.py list-roots

.PHONY: list-categories
list-categories:
	@python3 tooling/scripts/latex_build.py list-categories

.PHONY: build-all
build-all:
	@python3 tooling/scripts/latex_build.py build-all

.PHONY: build-parallel
build-parallel:
	@python3 tooling/scripts/latex_build.py build-all --parallel --jobs $(JOBS)

define category_rule
.PHONY: build-category-$(1)
build-category-$(1):
	@python3 tooling/scripts/latex_build.py build-category $(1)
endef

CATEGORIES := $(shell python3 tooling/scripts/latex_build.py list-categories)
$(foreach cat,$(CATEGORIES),$(eval $(call category_rule,$(cat))))

.PHONY: build-changed
build-changed:
	@python3 tooling/scripts/latex_build.py build-changed

.PHONY: publish
publish: build-all
	@echo "Publishing PDFs to $(BUILD_DIR)"
	@mkdir -p $(BUILD_DIR) $(LOG_DIR)
	@python3 tooling/scripts/latex_build.py build-all >/dev/null

.PHONY: clean
clean:
	@python3 tooling/scripts/latex_build.py clean

.PHONY: distclean
distclean: clean
	@find $(SRC_DIR) -name '*.pdf' -type f -delete 2>/dev/null || true
	@rm -rf $(BUILD_DIR) $(LOG_DIR) 2>/dev/null || true
