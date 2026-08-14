# Makefile - Developer-facing facade for the latex-docs build system
SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

LATEXMK ?= latexmk
JOBS ?= $(shell nproc 2>/dev/null | awk '{print int($$1 * 0.75)}' || echo 4)
SRC_DIR := src
BUILD_DIR := public/pdfs
LOG_DIR := public/logs
BASE_REF ?=
HEAD_REF ?=
OUTPUT_DIR ?=
MODE_NAME ?=
BASE_REVISION ?=
HEAD_REVISION ?=
CLEAN_OUTPUT ?=

BUILD_ARGS :=
ifneq ($(strip $(OUTPUT_DIR)),)
BUILD_ARGS += --output-dir $(OUTPUT_DIR)
endif
ifneq ($(strip $(LOG_DIR)),)
BUILD_ARGS += --log-dir $(LOG_DIR)
endif
ifneq ($(strip $(MODE_NAME)),)
BUILD_ARGS += --mode-name $(MODE_NAME)
endif
ifneq ($(strip $(BASE_REF)),)
BUILD_ARGS += --base $(BASE_REF)
else ifneq ($(strip $(BASE_REVISION)),)
BUILD_ARGS += --base $(BASE_REVISION)
endif
ifneq ($(strip $(HEAD_REF)),)
BUILD_ARGS += --head $(HEAD_REF)
else ifneq ($(strip $(HEAD_REVISION)),)
BUILD_ARGS += --head $(HEAD_REVISION)
endif
ifeq ($(strip $(CLEAN_OUTPUT)),true)
BUILD_ARGS += --clean-output
endif

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
	@echo "  make build-changed BASE_REF=<sha> HEAD_REF=<sha>"
	@echo "  make render-plantuml"
	@echo "  make publish"
	@echo "  make publish-parallel"
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
	@python3 tooling/scripts/latex_build.py build-all $(BUILD_ARGS)

.PHONY: build-parallel
build-parallel:
	@python3 tooling/scripts/latex_build.py build-all --parallel --jobs $(JOBS) $(BUILD_ARGS)

define category_rule
.PHONY: build-category-$(1)
build-category-$(1):
	@python3 tooling/scripts/latex_build.py build-category $(1) $(BUILD_ARGS)
endef

CATEGORIES := $(shell python3 tooling/scripts/latex_build.py list-categories)
$(foreach cat,$(CATEGORIES),$(eval $(call category_rule,$(cat))))

.PHONY: build-changed
build-changed:
	@python3 tooling/scripts/latex_build.py build-changed --jobs $(JOBS) $(BUILD_ARGS)

.PHONY: render-plantuml
render-plantuml:
	@python3 tooling/scripts/latex_build.py render-plantuml

.PHONY: publish
publish:
	@echo "Publishing PDFs to $(BUILD_DIR)"
	@python3 tooling/scripts/latex_build.py build-all --output-dir $(BUILD_DIR) --log-dir $(LOG_DIR) --clean-output --mode-name publish

.PHONY: publish-parallel
publish-parallel:
	@echo "Publishing PDFs in parallel to $(BUILD_DIR)"
	@python3 tooling/scripts/latex_build.py build-all --parallel --jobs $(JOBS) --output-dir $(BUILD_DIR) --log-dir $(LOG_DIR) --clean-output --mode-name publish

.PHONY: clean
clean:
	@python3 tooling/scripts/latex_build.py clean

.PHONY: distclean
distclean: clean
	@find $(SRC_DIR) -name '*.pdf' -type f -delete 2>/dev/null || true
	@rm -rf $(BUILD_DIR) $(LOG_DIR) 2>/dev/null || true
