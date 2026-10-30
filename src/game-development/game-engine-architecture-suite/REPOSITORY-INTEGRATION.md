# Merge checklist for `latex-docs`

The bundle is already positioned under `src/game-development/game-engine-architecture-suite/`.

1. Copy the archive contents into the repository root, preserving paths.
2. Add to the `src/game-development/README.md` navigation list:

   `- [Game Engine Architecture & Engineering Suite](game-engine-architecture-suite/README.md) — 17 source-aligned guides, curriculum, labs, engineering references and paired printable forms.`

3. Run the repository's catalog-generation process (if present). Do not edit generated indexes by hand unless documentation states they are manually maintained.
4. From the suite root run `make validate`, `make test-python`, `make test-cpp`.
5. From the repository root run `make preflight` and `make build-category-game-development`.
6. Inspect at least one rendered Template and one Blank form and verify blank print pages contain no prefilled responses or bracketed placeholders.
7. Commit on a feature branch, review the build impact and merge after CI passes.

The package does **not** replace root/readme, other game-development collections, style-system files or existing Template–Blank pairs.
