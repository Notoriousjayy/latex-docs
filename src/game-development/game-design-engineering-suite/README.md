# Game Design and Game Development Engineering Documentation Suite

**Authoritative source domain:** [`src/game-development/`](../) in `Notoriousjayy/latex-docs`.

This is a source-first LaTeX supplement to the existing repository, aligned with *The Art of Game Design: A Book of Lenses*, **Jesse Schell, third edition** (CRC Press; copyright 2020). It does **not** include the source book and does not reproduce the author's lens questions. The book's 35-chapter progression is preserved in the study-guide series. Original software-engineering procedures, example code, measurements, acceptance criteria, threat models, and scoring rubrics are marked as supplementary rather than attributed to the source.

## Contents and navigation

| Collection | Deliverable | Role |
|---|---|---|
| `study-guides/art-of-game-design/` | 35 individual chapter study guides | Reading concepts, design labs, engineering extensions, questions, rubrics |
| `curricula/` | Seven-phase prerequisite sequence | Progression, gates, capstone |
| `technical-references/` | Seven references, including the lens index | Formal mechanics, probability, design theory, measurement, architecture and traceability |
| `workbooks/` | Five instructional workbooks plus five Template–Blank pairs | Mechanics, balance, iteration, player research, architecture |
| `laboratories/` | Ten laboratory documents | Design challenges, Python/C++ exercises, verification |
| `laboratories/examples/` | Ten Python and ten C++17 programs | Compiled/tested standalone implementations |
| `architecture-specifications/` | Four architecture specifications | Runtime, economy, telemetry, content |
| `architecture-specifications/diagrams/` | Four PlantUML diagrams | Reviewable architecture-as-code |
| `playtesting/` | Three procedures | Recruiting, execution, interpretation |
| `templates/art-of-game-design/` | Fourteen Template–Blank pairs | Working design records and writable paper copies |
| `assessments/` | Four scorecard Template–Blank pairs | Experience, balance, architecture, playtesting |
| `catalog/` | Chapter and lens crosswalk CSVs | Traceability and navigation |

## Template and blank lifecycle

Every new document intended as a repeatable form has `*-template.tex` (worked, fictional example) and `*-blank.tex` (unfilled printable writing fields). Blank forms intentionally contain **no bracketed placeholder instructions**, sample answers, or fill-in text. Standalone technical references, laboratories, and chapter study guides are not forms and therefore do not have blank companions.

Existing `game-design-document-*-template.tex` and `*-blank.tex` records already in the repository are preserved and are **not** replaced by this package. The suite provides narrower forms for the workflow around the GDD.

## Build and test

From a standalone LaTeX file's directory:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error chapter-12-some-elements-are-game-mechanics.tex
```

From `src/game-development/laboratories/examples/`:

```bash
python3 python/finite-state-rules.py
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build
ctest --test-dir build --output-on-failure
```

All `.tex` files are standalone and use commonly available TeX Live packages. PlantUML diagrams are built separately. Run the repository's `make preflight` and `make build-category-game-development` *after* adding the files.

## Design evidence standard

- Never mistake functional unit tests for evidence of player enjoyment.
- Preserve assumptions, negative findings, playable build revision, participant consent, and study limitations.
- For probabilistic results report the distribution, not just the mean.
- For telemetry collect only consented, minimal events; do not include real user data in examples.
- Maintain a trace from experience goals to requirements, implementation and validation evidence.

## License and provenance

This package contains newly authored educational source files. The cited book remains copyrighted by its publisher; obtain and use it separately. No game engine, licensed asset pack, or textbook PDF is bundled. See `SOURCES.md` and `INTEGRATION.md`.
