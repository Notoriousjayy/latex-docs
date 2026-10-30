# Game Engine Architecture and Development Engineering Suite

**Source and target:** Jason Gregory, *Game Engine Architecture*, 3rd edition (CRC Press, 2018); `src/game-development/game-engine-architecture-suite/` in `latex-docs`.

This is a self-contained **learning and engineering documentation package**, not a copy of the textbook or a production-ready engine. The **17 chapter study guides** follow the book's five-part organization and section numbers. All technical commentary, labs, examples, assessment forms and implementation exercises are independently authored. The textbook is required for its full arguments, diagrams and case studies.

## Start here

1. [Prerequisite-based curriculum](curriculum/prerequisite-based-curriculum.tex) — 24-week dependency-based syllabus with exit gates.
2. [Study guides](study-guides/README.md) — all 17 chapter-aligned guides, including reading prompts, implementation activities and validation criteria.
3. [Technical references](technical-references/README.md) — eight original subsystem references.
4. [Labs](labs/README.md) — eleven graded instructions using C++20 and standard-library Python 3 examples.
5. [Architecture specifications](architecture-specifications/README.md) — four architecture descriptions/specifications, distinct from single-decision ADRs.
6. [Benchmark procedures](benchmarking/README.md) — timing, memory and parallel-job evidence protocols.
7. [Templates](templates/README.md), [Workbooks](workbooks/README.md), [Scorecards](scorecards/README.md) — every paper form has a guided template and printable blank.
8. [Code](code/README.md) — small runnable lab exercises and tests.

## Provenance

- **Book-aligned:** chapter titles, numbering, and high-level subject areas (chapters 1–17, five parts); see `study-guides/` and each document's reading crosswalk.
- **Supplemental engineering content:** C++20 and Python 3 implementation choices, simple ECS prototype, integer accumulator, example test/benchmark harnesses, safe ownership conventions and CI workflows. These are not claimed to be Gregory's code or prescriptions.
- **Out of scope:** complete commercial-grade game engine, production graphics API implementation, network replication, shipped asset libraries or cross-platform bitwise determinism.

## Run and validate

From this suite root:

```sh
python3 scripts/validate_suite.py
python3 -m unittest discover -s code/python/tests -v
cmake -S code/cpp -B /tmp/gea-cpp-build -DCMAKE_BUILD_TYPE=Debug
cmake --build /tmp/gea-cpp-build -j 4
ctest --test-dir /tmp/gea-cpp-build --output-on-failure
cd curriculum && latexmk -pdf -halt-on-error prerequisite-based-curriculum.tex
```

For an individual LaTeX document, enter its directory and run `latexmk -pdf -interaction=nonstopmode -halt-on-error filename.tex`. Each file declares its own `\documentclass`, compatible with the repository's root-discovery approach. All document styles use pdfLaTeX-compatible packages and intentionally avoid network-required assets and fragile relative-style imports.

## Suggested repository taxonomy

```text
src/game-development/game-engine-architecture-suite/
  study-guides/              17 chapter files
  curriculum/                 prerequisite curriculum
  technical-references/      8 references
  labs/                      11 printable lab instructions
  architecture-specifications/ 4 architecture design records
  benchmarking/              3 benchmark protocols
  templates/                 6 Template–Blank pairs
  workbooks/                 5 Template–Blank pairs
  scorecards/                4 Template–Blank pairs
  code/cpp/                  C++ examples and CMake
  code/python/               Python examples and unittests
  scripts/                   validators
  shared/                    provenance policy
```

This is a subject-specific preserved suite inside the existing `game-development` domain. Existing `graphics/`, `physics-engines/`, `patterns/` and generic `templates/` content should remain untouched; use cross-links, not relocation or duplication. The parent `src/game-development/README.md` and discovery catalog may be updated by a subsequent repository-integration change after reviewing repository-wide catalog-generation policies.

## Known instructional limits

C++ examples assert key invariants and are intentionally not multithread-safe resource managers. The worker-batch example uses independent output cells and joins threads, not a full dependency-aware job scheduler. The Python rasterizer does not implement a complete GPU pipeline. The audio code writes an offline WAV, not a realtime OS callback. The capstone lab is an integration *specification*, not a fully delivered commercial engine.
