# Shared

Shared authoring policy and provenance guidance. LaTeX roots intentionally embed their own portable style header to avoid relative-include failures.

## Files

See the child directories and source README files.

## Validation

All .tex documents in this suite are standalone pdfLaTeX roots; use `latexmk -pdf -halt-on-error <file>.tex` from their own directory. The suite validator also checks matching Template–Blank pairs.
