# Algorithm Engineering & Computer Science Documentation Suite

**Edition:** 1.0 · **Updated:** 2026-10-29 · **Source format:** LaTeX / Python 3 / C11 / C++20

A repository-ready, original educational documentation suite anchored to Donald E. Knuth's *The Art of Computer Programming*, Volumes 1, 2, 3, 4A, and 4B. It is an independently authored learning and engineering package, not an authorized adaptation or substitute for the books. **The source books are not redistributed.**

## Contents

Under this repository directory, `src/programming/algorithms/algorithm-engineering/`, the suite contains **33 standalone `.tex` documents** and one shared style file:

| Family | Files | Purpose |
|---|---:|---|
| `technical-references/` | 3 | Engineering handbook, proof field guide, source crosswalk |
| `study-guides/` | 5 | One guide for each supplied physical volume; seven source chapters covered |
| `curricula/` | 2 | 24-week prerequisite path and evidence-based competency matrix |
| `laboratories/` | 3 | Eight projects per language, with validation requirements |
| `workbooks/` | 4 | Mathematical reasoning and original exercises with writing space |
| `procedures/` | 2 | Controlled benchmarking and formal verification/review SOPs |
| `templates/` | 5 | Instructional forms with rating and completion guidance |
| `blank/` | 9 | Five print-ready assessment forms and four blank math-workbook companions |
| `shared/` | 1 style file | Typography, page furniture, boxed notes and reusable form macros |

Also included: original Python, C11 and C++20 reference implementations, correctness tests, example benchmark harnesses, a CMake build, shell build/test scripts, and a manifest.

## Repository integration

This collection belongs to the existing `src/programming/algorithms/` domain. The suite is source-only in Git: no compiled PDFs, no copyrighted books, and no temporary build files. Keep the nine leaf-directory READMEs and the paired `templates/`, `workbooks/`, and `blank/` directories together. The `code/` directory contains original reference implementations that belong to this teaching suite.

## Quick start

**Build all LaTeX documents** (requires a reasonably complete TeX Live installation):

```bash
./scripts/build-algorithm-suite.sh
```

Compiled PDFs appear in `build/pdf/<family>/`. Build a single file from **its own leaf directory**; for example:

```bash
cd src/programming/algorithms/algorithm-engineering/technical-references
pdflatex -interaction=nonstopmode -halt-on-error algorithm-engineering-technical-reference.tex
pdflatex -interaction=nonstopmode -halt-on-error algorithm-engineering-technical-reference.tex
```

**Run reference implementation tests**:

```bash
./scripts/test-algorithm-code.sh
```

Or independently:

```bash
cd code/python && python3 -m unittest -v
cd ../c && make test
cd ../../
cmake -S code/cpp -B /tmp/algorithm-suite-build -DCMAKE_BUILD_TYPE=Debug
cmake --build /tmp/algorithm-suite-build
ctest --test-dir /tmp/algorithm-suite-build --output-on-failure
```

**Collect actual performance measurements** (benchmark output is not pre-populated):

```bash
cd code/python && python3 benchmark.py --max-power 12 --repeats 15 --batch 20 --csv python-results.csv
# separately, from package root after compiling C++:
/tmp/algorithm-suite-build/alg_bench 4096 15 20 > cpp-results.csv
```

Each lab requires correctness results before measurement. Do not compare Python and C++ timing as though language runtimes alone were a test of algorithm complexity.

## Source alignment

| Volume | Content | Chapter numbering |
|---|---|---|
| 1, Fundamental Algorithms (3rd ed., 1997) | Algorithms, analysis, MIX, structures | Chapters 1–2 |
| 2, Seminumerical Algorithms (3rd ed., 1998) | Random numbers, arithmetic | Chapters 3–4 |
| 3, Sorting and Searching (2nd ed., 1998) | Sorting, searching, indexing | Chapters 5–6 |
| 4A, Combinatorial Algorithms, Part 1 (2011) | Boolean algorithms, basic enumeration | Chapter 7 §§7.1–7.2.1 |
| 4B, Combinatorial Algorithms, Part 2 (2022) | Backtracking, exact cover, SAT | Chapter 7 §7.2.2 and subsections |

Source references are volume/section identifiers grounded in the supplied editions. Independent exercises, procedures, experiments and sample code are **new authorial material**. This package does not copy the books' exercise text, complete worked answers, figures or implementation code. Historical machines and storage technologies are discussed as historic contexts, not modern deployment instructions.

## Repository integration

The canonical import location is `src/programming/algorithms/algorithm-engineering/` under an existing `latex-docs` repository. This package is designed to coexist with domain -> artifact family taxonomies, without modifying existing files or assuming other paths. Merge `src/`, `code/`, and the specifically named scripts; do not blindly overwrite a repository's root README, build system or workflows. Review `integration/INTEGRATION.md` before committing.

Blank forms contain **no bracketed instructional placeholders**. The `*-template.tex` files have the completion guidance; `*-blank.tex` files have only form titles, labels and empty writing space.

## Editorial and validation rules

1. Check the source-volume/section locator before adding a source-derived claim.
2. Use authored demonstrations and new practice problems; do not paste book pages, figures or answers.
3. For every algorithm specify semantics, correctness, complexity, measurements and limitations.
4. All new forms that require handwritten completion need a true blank companion.
5. Keep files independently compilable; update the family README and manifest on addition.
6. Keep raw benchmark samples and environment metadata if results are published.

## Status

This is a standalone import-ready package. It has **not** been pushed to or merged with a remote GitHub repository. Import paths may require minor adjustment if the destination `latex-docs` repository uses different taxonomy or LaTeX conventions.

## Repository catalog governance

The canonical semantic source inventory registers the 24 non-Blank standalone documents and the one shared LaTeX fragment. The nine printable Blank variants are deliberately excluded from the canonical source count and governed by the separate Template–Blank pairing manifest. All 33 standalone documents remain discoverable through this suite index and are compiled as LaTeX roots by the repository build pipeline.
