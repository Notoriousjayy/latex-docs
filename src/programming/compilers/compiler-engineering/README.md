# Compiler Engineering Documentation Suite

**Edition:** 1.0 | **Updated:** 2026-10-30 | **Source:** LaTeX / Python 3 / C11 / C++20

A source-only, independently authored engineering curriculum and reference suite grounded in Keith D. Cooper and Linda Torczon's *Engineering a Compiler*, Third Edition (Morgan Kaufmann/Elsevier, 2023). This package follows the book's **14 actual chapters**, plus Appendix A (ILOC) and Appendix B (Data Structures). It does **not** include or reproduce the copyrighted book, figures, answer key or extended text.

## Authoritative taxonomy

**Destination:** `src/programming/compilers/compiler-engineering/`

The existing `src/programming/technical-documents/engineering-compiler-algorithms-pseudocode.tex` remains authoritative at its current location; this package does not replace, move or duplicate it. General SAST and security governance stay under security; language-specific secure-coding standards stay under programming/languages. This is a cohesive compiler engineering subject collection, subdivided by artifact type. Every leaf has its own README.

## Inventory

| Artifact family | Standalone `.tex` roots | Contents |
|---|---:|---|
| Technical references | 3 | Compiler architecture, formal-methods field reference, source crosswalk |
| Chapter study guides | 14 | One independently authored guide for each chapter |
| Curricula | 2 | Prerequisite-based 18-week plan and competency gates |
| Laboratories | 4 | Four Python and C/C++ lab manuals, with staged assignments |
| Workbooks | 4 | Four guided workbook templates (and paired blanks) |
| Procedures | 3 | Benchmark, correctness and optimization SOPs |
| Security assessments | 3 | Threat model, security test plan, scorecard |
| Reusable templates | 7 | Pass, decision, testing, benchmark, security, capstone and security-scorecard forms |
| Printable blanks | 11 | Seven form blanks and four workbook blanks, with no bracketed instructions |
| **Total independent LaTeX roots** | **51** | Plus shared style preamble |

Each form and each workbook has a consistent **Template–Blank** lifecycle: the template describes how to complete the artifact; the blank is ready for handwriting, with labels and genuinely empty writing space. Unlike the templates, blank sheets do not include completion guidance or bracketed placeholders.

## Reading order

1. Foundation: Chapter 1; scanner Chapter 2; parser Chapter 3.
2. Front end and IR: Chapters 4, 5, 6, 7 (the ordering of IR before syntax-driven translation is important in the third edition).
3. Optimization theory: Chapters 8, 9, 10.
4. Back end: Chapters 11, 12, 13.
5. Runtime: Chapter 14; implement after back-end foundations. Appendices A and B support IR code and data structures.

The curriculum introduces backend architecture before advanced global analysis in some weeks; consult the [curriculum](curricula/compiler-engineering-18-week-curriculum.tex) for the explicit prerequisite DAG.

## Implemented and specified code

**Runnable teaching kernels (tested locally):**

- `code/python/lexer.py`, `parser.py`, `ir.py`, `dataflow.py`, `optimizer.py`, `test_compiler.py`, `benchmark.py`.
- `code/c/scanner.c`, `scanner.h`, `test_scanner.c`, C11 Makefile.
- `code/cpp/dataflow.cpp`, `scheduler.cpp`, `allocator.cpp`, CMake/CTest configuration.

These are deliberately small, original implementations. **Not** a complete compiler, full SSA constructor, LLVM plugin, production-grade optimizer, ABI-compliant code generator or production JIT. Some lab tasks are extensions to be implemented; the lab manuals distinguish these from runnable source files. The C++ colorer reports spill candidates rather than rewriting spilled uses. The C++ scheduler is a bounded toy model for a single-issue machine.

## How to build and test

Requires a TeX Live distribution with `pdflatex`, `latexmk`, `tikz`, `fancyvrb`, `amsmath`, `lmodern`, and other widely available packages in the shared preamble; Python 3; a C11 compiler; a C++20 compiler; CMake and CTest.

```bash
cd src/programming/compilers/compiler-engineering
python3 scripts/check-suite.py
bash scripts/test-code.sh
bash scripts/build-latex.sh
```

Generated PDFs appear in untracked `build/pdf/`. To compile a single document, run `pdflatex -halt-on-error <filename>.tex` **from the file's own artifact family directory**, so that the relative `../shared/` preamble resolves. Root repository build automation should preserve this working-directory convention. Use `make build-category-programming` only after validating against the repository's build harness.

For local reproducible timing (no pre-filled result data):

```bash
cd code/python
python3 benchmark.py --repeats 15 --batch 3000 --csv benchmark-results.csv
```

## Evidence, test and assurance conventions

Each laboratory requires syntax/semantic acceptance criteria, boundary and negative cases, source-level invariants, exact test commands and review evidence. Any performance claim must first pass equivalence tests and include raw measurements. Blank forms have no suggested answers; workbooks are exercises, not reproductions of copyrighted end-of-chapter problems.

The source text supplies theoretical compiler and implementation foundations; threat modeling, bounded fuzzing, sanitizers, source provenance, CI controls and contemporary AppSec scorecards are explicitly **suite-authored extensions**, not claims about the textbook's coverage.

## Attribution and reuse

Cooper, Keith D., and Linda Torczon. *Engineering a Compiler*. 3rd ed., Morgan Kaufmann/Elsevier, 2023. ISBN 978-0-12-815412-0. The technical references include a source crosswalk. The uploaded book itself remains outside the Git tree and downloadable package.

## Integrating with latex-docs

See `integration/INTEGRATION.md` for a minimal domain README snippet and catalog-regeneration notes. No existing repository files need to be overwritten to adopt this source-only tree.
