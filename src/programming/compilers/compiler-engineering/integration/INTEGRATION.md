# Repository integration plan (non-destructive)

1. Copy this subtree to `src/programming/compilers/compiler-engineering/` on a feature branch.
2. Add a **single new row** to the subject-collection table of `src/programming/README.md`:

   `| [compiler-engineering](compiler-engineering/README.md) | Compiler construction, 14 chapter guides, curricula, labs, workbooks, templates and print-ready blanks. | 51 |`

3. Optionally link the suite from `src/README.md` as a subject under programming, rather than creating an artificial extra top-level domain.
4. If the existing semantic manifest uses curated metadata, register all standalone `.tex` files with primary type and authoritative subject. Run `python3 tooling/scripts/build_semantic_catalogs.py --write` in the target repo and review changes to `catalog/`; avoid hand-editing generated catalog counts.
5. Preserve `src/programming/technical-documents/engineering-compiler-algorithms-pseudocode.tex`. Cross-link it; do not migrate or duplicate it in this merge.
6. From the repository root run `make preflight`, `make build-category-programming`; check any custom minted or PlantUML restrictions and adjust only if necessary.
7. Commit source, code, READMEs and manifest. Do not commit generated PDF, build cache, secret, or the original copyrighted textbook.
8. Open a PR and require reviewer confirmation of generated catalog consistency and leaf READMEs before merge.

This package was produced as files for integration; no GitHub branch, commit or PR is created merely by downloading it.
