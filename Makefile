SHELL := /bin/bash

# Build a single document:
#   make build DOC=docs/<category>/<document>
build:
	@test -n "$(DOC)" || (echo "Set DOC=docs/<category>/<document>"; exit 1)
	latexmk -pdf -cd "$(DOC)/src/main.tex"

# Clean a single document:
#   make clean DOC=docs/<category>/<document>
clean:
	@test -n "$(DOC)" || (echo "Set DOC=docs/<category>/<document>"; exit 1)
	latexmk -C -cd "$(DOC)/src/main.tex"
	rm -rf "$(DOC)"/_minted* 2>/dev/null || true

# Build all documents in docs/**/src/main.tex
build-all:
	@set -euo pipefail; \
	while IFS= read -r f; do \
	  echo "==> Building $$f"; \
	  latexmk -pdf -cd "$$f"; \
	done < <(find docs -type f -path '*/src/main.tex' -print0 | xargs -0 -n1 dirname)
