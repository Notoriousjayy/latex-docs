PYTHON ?= python3
.PHONY: validate pdfs clean list
validate:
	$(PYTHON) scripts/validate_suite.py
list:
	find . -name '*.tex' ! -path '*/shared/*' | sort
pdfs: validate
	$(PYTHON) scripts/build_pdfs.py
clean:
	rm -rf build
