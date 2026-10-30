# Parsing Techniques and Compiler Engineering Documentation Suite

**Edition:** 1.0 (2026-10-30) | **Canonical format:** original LaTeX and executable source code.

Repository destination: `src/programming/compilers/parsing-techniques/`. This collection follows the existing domain-first taxonomy and the artifact-family arrangement used for other algorithm suites; the `compilers/` subject collection is new and fits the programming-domain scope stated in `src/programming/README.md`.

Source anchor: Dick Grune and Ceriel J. H. Jacobs, *Parsing Techniques: A Practical Guide*, second edition (Springer, 2008), 18 chapters. Chapter pages and titles are used as navigational locators. Modern compiler pipeline, security and benchmarking procedures are independent authored engineering extensions, **not textbook assertions**. The copyrighted PDF and its illustrations, code and problem statements are not redistributed.

## Document families

| Folder | Purpose |
|---|---|
| `technical-references/` | Formal methods, parser selection and pipeline design |
| `study-guides/` | 18 standalone guides, one per source chapter |
| `curricula/` | 24-week dependency path, competency portfolio matrix |
| `laboratories/` | 8 controlled implementation laboratories |
| `workbooks/` | 4 instructional printable workbooks paired with Blanks |
| `procedures/` | Benchmarking, verification and research review SOPs |
| `assessments/` | Parser security threat model and assessment guidance |
| `templates/` | Guided specification, report, triage and scorecard forms |
| `blank/` | Print-ready unfilled companions, no bracketed prompts |
| `code/python/` | Reference CYK, Earley, predictive grammar analysis, expression parser, test suite and bench |
| `code/cpp/` | C++20 CYK and Earley recognizers with CMake/CTest, CMake build |
| `shared/` | Presentation helpers compatible with repository semantic style module |
| `integration/` | Import notes and Template–Blank pair registration |

## Recommended entry sequence

Read `technical-references/parsing-engineering-technical-reference.tex` and `curricula/prerequisite-based-curriculum.tex`. Work Ch. 1--5 fundamentals; implement CYK/Earley and compare results; progress through LL and LR; finish with compiler and security/benchmark evidence. Source-only Git policy: keep generated PDF/log/build files out of commits.

## Build

Build with the parent repository's `make build-category-programming` or `make build-changed` and `tooling/latex` + `tooling/styles/latex` on `TEXINPUTS`. Individual roots load exactly one semantic `technical-*` style and include `../shared/parsing-macros.tex`.

```sh
python3 src/programming/compilers/parsing-techniques/scripts/validate_suite.py
python3 -m unittest discover -s src/programming/compilers/parsing-techniques/code/python -p 'test_*.py' -v
cmake -S src/programming/compilers/parsing-techniques/code/cpp -B /tmp/parsing-suite-cpp
cmake --build /tmp/parsing-suite-cpp && ctest --test-dir /tmp/parsing-suite-cpp --output-on-failure
```

## Governance

Forms designated `*-template.tex` contain guidance. Their `*-blank.tex` pairs have visible labels, empty lines and no bracketed instructional placeholder text. Blank forms are not evidence of a completed review. Update the repository's central `catalog/template-blank-pairs.md` on integration using `integration/template-blank-catalog-additions.md`; do not replace the existing catalog. All leaf folders contain a README and `integration/` has explicit import steps.

## Limitations

The executable modules are pedagogical reference implementations for selected algorithms, **not** complete LR, GLL, or GLR parser generators. The higher-level advanced chapters use design/tracing laboratories rather than asserting unimplemented general parser support. Security assessment documentation does not certify the example code for production.
