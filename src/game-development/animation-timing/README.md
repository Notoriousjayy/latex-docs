# Animation Timing and Game Animation Engineering Documentation Suite

**Status:** standalone, repository-ready source package  |  **Version:** 1.0  |  **Updated:** 2026-10-30

This package is organized for `src/game-development/animation-timing/` inside the `Notoriousjayy/latex-docs` repository. The existing `game-development` domain remains authoritative; the package is a cohesive, discoverable subject collection, and the leaf directories distinguish artifacts by purpose.

## What is included

- **82 standalone LaTeX chapter study guides**, corresponding exactly to the numbered chapters in Harold Whitaker, John Halas, and Tom Sito, *Timing for Animation*, third edition (2020).
- A **16-week prerequisite-based curriculum**, competency crosswalk, four technical references, seven implementation laboratories, two architecture specifications, two SOPs and three capstone projects.
- **Fourteen paired Template and printable Blank documents** in the workbooks, templates, and scorecards families. Blanks contain field labels and empty writing areas, never bracketed completion prompts.
- Three additional graded problem sets, runnable Python 3 / C++20 reference code, unit tests and CMake/CTest tooling.

The book gives the conceptual and historical animation basis. Mathematical modeling, Python/C++ software, game-engine architecture, deterministic simulation, formal scorecards, test workflows and quantitative thresholds are **supplementary engineering work**. The source EPUB is not redistributed. See [SOURCE_PROVENANCE.md](SOURCE_PROVENANCE.md).

## Start here

1. [Prerequisite-based 16-week curriculum](curricula/prerequisite-based-16-week-curriculum.tex) and [chapter crosswalk](curricula/chapter-to-competency-and-evidence-crosswalk.tex).
2. [Time base / X-sheet reference](technical-references/timing-frame-rates-and-exposure.tex) and [spacing reference](technical-references/spacing-poses-easing-and-cycles.tex).
3. [Chapter-by-chapter library](study-guides/README.md), [workbooks](workbooks/README.md), and [practical labs](laboratories/README.md).
4. [Gameplay animation architecture](architecture/README.md) and [engine integration reference](technical-references/realtime-animation-architecture-and-integration.tex).
5. [Paired forms register](PAIR_REGISTER.json), [scorecards](scorecards/README.md), and [capstones](projects/README.md).

## Build in the repository

The `.tex` files are independent, authored with `technical-user-manual`, `technical-implementation`, `technical-design-spec`, and `technical-testing` semantic packages already in `tooling/styles/latex/`. Do not copy or override the central house style.

From the **repository root**:

```bash
make preflight
make build-category-game-development
python3 src/game-development/animation-timing/scripts/validate_suite.py
bash src/game-development/animation-timing/scripts/build-suite.sh
```

The first two commands use the repository's canonical build system. The suite-specific script compiles these documents in isolation and stores outputs under a temporary or explicitly selected folder rather than adding compiled artifacts to Git.

## Test executable examples

```bash
cd src/game-development/animation-timing/code/python
python3 -m unittest -v test_animation
python3 export_demo.py --prefix shot01

cd ../..
cmake -S code/cpp -B /tmp/animation-timing-cpp
cmake --build /tmp/animation-timing-cpp
ctest --test-dir /tmp/animation-timing-cpp --output-on-failure
```

The example CSVs are generated artifacts; review them rather than committing measurement outputs indiscriminately.

## Print-ready pair contract

- `*-template.tex` is guided: includes instructions, source crosswalk, illustrative entries, and a form.
- `*-blank.tex` is an empty printable working copy: labels, neutral criteria and empty spaces only. No completed decisions, example answers, or bracketed response placeholders.
- Forms are not proof of technical acceptance or player study completion unless filled and reviewed. Register each pair in the repository-wide catalog as part of integration.

## Repository integration checklist

1. Copy the complete package into `src/game-development/animation-timing/`.
2. Add one navigation entry to `src/game-development/README.md` and the root discoverability index as appropriate.
3. Add these 14 pairs to `catalog/template-blank-pairs.md` and its validator's machine-readable registry, following the current repository format.
4. Compile changed LaTeX roots and run the repository's existing pair validation and unit-test workflows. Do not claim a successful full corpus build from package-local tests.
5. Review asset licensing; never publish or embed the supplied third-party EPUB.

See [CATALOG.md](CATALOG.md) for the full artifact inventory and [VALIDATION_REPORT.md](VALIDATION_REPORT.md) for package checks.
