# Algorithm Analysis and Analytic Combinatorics Documentation Suite

**Status:** original, source-aligned educational companion; not official material from the textbook authors or publisher. **Repository destination:** `src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/` in `latex-docs`.

## Primary source and attribution

Robert Sedgewick and Philippe Flajolet, *An Introduction to the Analysis of Algorithms*, second edition, Addison--Wesley, 2013, ISBN 978-0-321-90575-8. The chapter ordering, topic names and printed page ranges are mapped in `technical-documents/chapter-to-operations-crosswalk.tex`. Exposition, experiments, worksheets, assessments and implementations are independently created companion content. No original textbook PDFs, scanned pages, figures or long passages are included in this distribution.

## Find a document by intent

| What you need | Location |
|---|---|
| Rigorous cost models, derivations, formulas | [Technical documents](technical-documents/README.md) |
| Chapter-specific learning and dependency order | [Study guides](study-guides/README.md) |
| Guided math derivations + print forms | [Workbooks](workbooks/README.md) |
| Runnable Python, C11 and C++17 laboratories | [Laboratories](laboratories/README.md) |
| Template/Blank reusable record lifecycle | [Templates](templates/README.md) |
| Diagnostics, capstone and grading | [Assessments](assessments/README.md) |

## Intended study sequence

Start with the diagnostic, then Chapters 1--5 in order; apply Chapters 6--9 with the appropriate workbooks and labs. Use the technical reference as a cross-chapter index, not a substitute for mathematical derivation. The sixteen-week curriculum provides outcomes and evidence gates.

## Integration and compilation

Copy this suite directory to the matching path in the repository. The source roots select the canonical `technical-*` semantic packages if available and use `support/aaoa-standalone.sty` only for independent compilation. The authoritative repository stylesheet continues to own the visual house style. Do not add the fallback stylesheet to repository `tooling/styles/latex/` or override the house style.

```bash
# Repository root
make preflight
make build-category-programming
python3 -m unittest discover -s src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/laboratories/code -p 'test_models.py'
```

For independent LaTeX preview, `cd` into a document directory and run `pdflatex -halt-on-error <file>.tex` twice. The fallback stylesheet exists at `../support/`.

**Repository maintenance:** update `src/programming/algorithms/README.md` and any generated discovery catalog using the repository's catalog regeneration procedure after integration. Do not manually assert a catalog has been regenerated. Update nearest README on file additions and ensure Template/Blank pairs remain synchronized.

## Template--Blank lifecycle

`*-template.tex` has completion guidance, explicitly including bracketed hints where useful. `*-blank.tex` contains print-ready section headings, ruled response areas, and **no prompt placeholders**. Workbooks have corresponding `*-workbook-blank.tex` copies with exercise text retained but responses empty. Blank copies are for actual completion; templates are instructions, not filled evidence.

## Laboratory integrity

Source code is original and depends only on Python's standard library, a C11 compiler and a C++17 compiler (CMake optional but provided). Claims involving average case are model-dependent. Run the bundled tests before relying on empirical results; archive raw samples and report the environment rather than publishing bare performance rankings.
