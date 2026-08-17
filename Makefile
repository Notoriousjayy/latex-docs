# Makefile - Developer-facing facade for the latex-docs build system
SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

LATEXMK ?= latexmk
JOBS ?= $(shell nproc 2>/dev/null | awk '{print int($$1 * 0.75)}' || echo 4)
SRC_DIR := src
BUILD_DIR := public/pdfs
LOG_DIR := public/logs
SITE_DIR ?= public/site
BASE_REF ?=
HEAD_REF ?=
OUTPUT_DIR ?=
MODE_NAME ?=
BASE_REVISION ?=
HEAD_REVISION ?=
CLEAN_OUTPUT ?=

# Planning / sharding knobs. MAX_SHARDS bounds GitHub Actions runner fan-out;
# JOBS bounds concurrent latexmk processes inside a single runner. Tune them
# independently: total concurrency is MAX_SHARDS x JOBS.
BUILD ?= python3 tooling/scripts/latex_build.py
PLAN ?= public/logs/build-plan.json
PLAN_MODE ?= changed
MAX_SHARDS ?= 12
MIN_ROOTS_PER_SHARD ?= 25
SHARD_INDEX ?= 0

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
	@echo "  make plan PLAN_MODE=changed|full MAX_SHARDS=N"
	@echo "  make build-shard PLAN=<plan.json> SHARD_INDEX=N"
	@echo "  make verify-corpus PLAN=<plan.json>"
	@echo "  make render-plantuml"
	@echo "  make publish"
	@echo "  make publish-parallel"
	@echo "  make clean"
	@echo "  make distclean"

.PHONY: list-roots
list-roots:
	@$(BUILD) list-roots

.PHONY: list-categories
list-categories:
	@$(BUILD) list-categories

.PHONY: build-all
build-all:
	@$(BUILD) build-all $(BUILD_ARGS)

.PHONY: build-parallel
build-parallel:
	@$(BUILD) build-all --parallel --jobs $(JOBS) $(BUILD_ARGS)

define category_rule
.PHONY: build-category-$(1)
build-category-$(1):
	@$(BUILD) build-category $(1) $(BUILD_ARGS)
endef

CATEGORIES := $(shell $(BUILD) list-categories)
$(foreach cat,$(CATEGORIES),$(eval $(call category_rule,$(cat))))

.PHONY: build-changed
build-changed:
	@$(BUILD) build-changed --jobs $(JOBS) $(BUILD_ARGS)

.PHONY: render-plantuml
render-plantuml:
	@$(BUILD) render-plantuml

.PHONY: publish
publish:
	@echo "Publishing PDFs to $(BUILD_DIR)"
	@$(BUILD) build-all --output-dir $(BUILD_DIR) --log-dir $(LOG_DIR) --clean-output --mode-name publish

.PHONY: publish-parallel
publish-parallel:
	@echo "Publishing PDFs in parallel to $(BUILD_DIR)"
	@$(BUILD) build-all --parallel --jobs $(JOBS) --output-dir $(BUILD_DIR) --log-dir $(LOG_DIR) --clean-output --mode-name publish

.PHONY: plan
plan:
	@$(BUILD) plan --mode $(PLAN_MODE) --base "$(BASE_REF)" --head "$(HEAD_REF)" \
		--max-shards $(MAX_SHARDS) --min-roots-per-shard $(MIN_ROOTS_PER_SHARD) \
		--output $(PLAN) --emit summary

.PHONY: build-shard
build-shard:
	@$(BUILD) build-selection --plan $(PLAN) --shard-index $(SHARD_INDEX) --jobs $(JOBS) $(BUILD_ARGS)

.PHONY: verify-corpus
verify-corpus:
	@$(BUILD) verify-corpus --pdf-dir $(BUILD_DIR) --plan $(PLAN)

.PHONY: stage-pages
stage-pages:
	@$(BUILD) stage-pages --pdf-dir $(BUILD_DIR) --site-dir $(SITE_DIR)

.PHONY: clean
clean:
	@$(BUILD) clean

.PHONY: distclean
distclean: clean
	@find $(SRC_DIR) -name '*.pdf' -type f -delete 2>/dev/null || true
	@rm -rf $(BUILD_DIR) $(LOG_DIR) 2>/dev/null || true
