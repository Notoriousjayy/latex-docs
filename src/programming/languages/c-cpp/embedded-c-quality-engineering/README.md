# Embedded C Programming, Coding Standards & Software Quality Engineering Suite

**Edition:** 1.0 (2026-11-01). **Status:** Original educational and proposed engineering materials; not an approved safety or MISRA compliance claim.

This collection lives in `src/programming/languages/c-cpp/embedded-c-quality-engineering/`. All `.tex` roots use the repository's existing semantic LaTeX style modules; generated PDFs are build outputs.

## Source boundaries and intellectual property

The eight source chapter headings, only, are used to navigate Michael Barr's **BARR-C:2018 Embedded C Coding Standard**. The publisher's license restricts public redistribution of the original document and its derivatives. This public suite does **not** contain the uploaded PDF, copied BARR-C rule text, source figures, author examples or a proprietary MISRA rule crosswalk. All explanations, implementation exercises, control IDs, policies and forms are original. Exact BARR-C and licensed MISRA requirements must be consulted in authorized copies before assessing formal conformance. BARR-C:2018 relates to MISRA C:2012; MISRA C:2023 is a later separate reference.

## Contents

| Artifact family | Content |
| --- | --- |
| `study-guides/` | Eight individually compilable chapter guides |
| `curriculum/` | Twelve-week prerequisite path and assessment gates |
| `laboratories/` | Six C99 laboratories plus original secure-coding exercises |
| `technical-references/` | C99 engineering, BARR-C/MISRA comparison, static analysis and CI/CD reference |
| `governance/` | Original EC-Q01..EC-Q08 compliance matrix and review decision matrix |
| `procedures/` | Code review, deviation and release-readiness procedures |
| `templates/` + `blank-forms/` | Eight independently maintained, printable Template–Blank pairs |
| `examples/c99/` | C99 frame decoder, host tests and Makefile |
| `examples/workflows/` | **Inactive** CI demonstration requiring review and pinned actions |
| `references/` | Attribution, current source register and licensing boundary |

## Working sequence

1. Start with `curriculum/prerequisite-based-curriculum.tex`; read the relevant chapter guide.
2. Complete laboratories 01 to 06; run the frame codec project with `make -C examples/c99 test` **from this suite root**.
3. Run static checks and record findings, then use the review SOP and original EC-Q compliance matrix.
4. Produce assessment evidence using annotated Templates; print the corresponding Blank for unfilled paper use.
5. Before release, collect an approved deviation record and product-specific target/HIL evidence.

## Build

From repository root:

```sh
make preflight
make build-category-programming
python3 tooling/scripts/validate_artifact_pairs.py
```

These are repository interfaces; adding sources does not imply CI has passed. The source is authoritative and individual roots are discovered by `\\documentclass`. Standalone build example:

```sh
export TEXINPUTS="$(pwd)/tooling/latex//:$(pwd)/tooling/styles/latex//:${TEXINPUTS:-}"
cd src/programming/languages/c-cpp/embedded-c-quality-engineering/study-guides
latexmk -pdf -interaction=nonstopmode -halt-on-error chapter-01-general-rules.tex
```

Host demonstration (no MCU needed):

```sh
cd src/programming/languages/c-cpp/embedded-c-quality-engineering/examples/c99
make clean test
```

## Quality and limitations

The pair governance manifest registers all eight complete pairs. Each Blank includes labels, lines, an empty working grid and sign-off space, but no prefilled evidence. A clean compiler or analyzer report is insufficient for correctness; validate ISR behavior, peripheral sequencing, latency and synchronization on target hardware. Any MISRA C compliance claim requires licensed normative materials, an edition-specific plan, supported rule coverage and approved deviations.

[Primary BARR-C source](https://barrgroup.com/embedded-c-coding-standard) | [MISRA](https://misra.org.uk/) | [GCC](https://gcc.gnu.org/onlinedocs/) | [Cppcheck](https://cppcheck.sourceforge.io/)
