# Repository integration procedure

1. Import the entire folder to `src/programming/compilers/parsing-techniques/` without changing unrelated paths.
2. Add `src/programming/compilers/README.md` and update `src/programming/README.md` with a compiler-subject collection link. Suggested blurb: "Compiler Engineering: parser and grammar formalism, 18 chapter study guides, practical implementations, benchmarking, and secure parser assessments."
3. Append the provided Template–Blank registration rows to `catalog/template-blank-pairs.md`; do not regenerate existing entries.
4. Update `catalog/README.md` and the metadata discovery catalog using the repository's existing generation scripts where available; avoid claiming a tested catalog rebuild without running it.
5. Run `python3 .../scripts/validate_suite.py`, Python unit tests, C++ CTest, then `make preflight` and the repository's changed-root LaTeX build. Fix all errors before PR.
6. Submit a reviewable pull request with original source only; do not commit generated PDFs, logs or uploaded copyrighted text.
7. Existing source `src/programming/technical-documents/parsing-techniques-algorithms-pseudocode.tex` is retained untouched; cross-link instead of duplicating or renaming it.
