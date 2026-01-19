# LaTeX Docs Makefile
# ===================

LATEX      ?= pdflatex
LATEXFLAGS ?= -interaction=nonstopmode -halt-on-error
SRC_DIR    ?= src
BUILD_DIR  ?= build

TEX_FILES := $(shell find $(SRC_DIR) -name '*.tex' -type f)
PDF_FILES := $(patsubst $(SRC_DIR)/%.tex,$(BUILD_DIR)/%.pdf,$(TEX_FILES))

.PHONY: all clean list

all: $(PDF_FILES)

$(BUILD_DIR)/%.pdf: $(SRC_DIR)/%.tex
	@mkdir -p $(dir $@)
	@echo "Building: $<"
	@cd $(dir $<) && $(LATEX) $(LATEXFLAGS) -output-directory=$(abspath $(dir $@)) $(notdir $<) > /dev/null 2>&1 || (echo "Error building $<"; exit 1)
	@cd $(dir $<) && $(LATEX) $(LATEXFLAGS) -output-directory=$(abspath $(dir $@)) $(notdir $<) > /dev/null 2>&1

clean:
	rm -rf $(BUILD_DIR)
	find . -name '*.aux' -delete
	find . -name '*.log' -delete
	find . -name '*.out' -delete
	find . -name '*.toc' -delete

list:
	@echo "Source files:"
	@find $(SRC_DIR) -name '*.tex' -type f | sort
