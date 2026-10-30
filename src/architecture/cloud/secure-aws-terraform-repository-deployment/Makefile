MAIN := aws-terraform-repository-deployment-standard.tex

.PHONY: pdf check clean
pdf:
	cd standard && pdflatex -shell-escape -interaction=nonstopmode -halt-on-error $(MAIN) && pdflatex -shell-escape -interaction=nonstopmode -halt-on-error $(MAIN)

check:
	python3 tests/verify_package.py

clean:
	cd standard && latexmk -c $(MAIN)
