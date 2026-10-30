# Repository integration and validation guide

Target repository: `https://github.com/Notoriousjayy/latex-docs` (default branch `main`). The original distribution archive includes only new files and does not overwrite the existing `src/game-development/README.md` or existing template pairs.

1. When working from the standalone archive, extract at the repository root, keeping `src/game-development/` paths unchanged. The new `study-guides/art-of-game-design/` directory complements the existing `study-guides` collection.
2. Add a navigation entry to `src/game-development/README.md` pointing to the new guides, curriculum, references, workbooks, laboratories, architecture specifications, playtesting procedures, assessments, and form pairs. Do not replace the existing game-development index.
3. Run `make preflight` then `make build-category-game-development`; fix any global repository style/lint requirements that differ from standalone `latexmk`.
4. Run `python3` scripts under `laboratories/examples/python`, then CMake/CTest in `laboratories/examples/`.
5. Render the `.puml` diagrams using PlantUML as optional architecture assets and keep them alongside their specifications.
6. Verify all blank forms have no printed placeholder instructions and every template and blank pair has matched section titles. Inspect at least one rendered example/blank per form family.
7. Submit changes through the repository's normal review/PR process, then update the domain README counts from the resulting tracked files.

### Recommended index additions

- Study guides: `study-guides/art-of-game-design/README.md`.
- Curriculum: `curricula/README.md`.
- References: `technical-references/README.md`.
- Laboratories: `laboratories/README.md`.
- Printable forms: `templates/art-of-game-design/README.md`.
- Evaluations: `assessments/README.md`.

### Boundary with existing materials

Keep general algorithm theory in `programming/` or `mathematics/`; these examples remain here because they demonstrate game-specific mechanics and player experience questions. Retain general game design documents in the existing `src/game-development/templates` family. Do not create a second top-level `game-development` domain or reclassify existing documents without separate repository review.
