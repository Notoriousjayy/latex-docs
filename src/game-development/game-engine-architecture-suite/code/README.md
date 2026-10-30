# Code

Reference implementation exercises, not a reusable production engine; compilers/tests are run independently of the documentation build.

## Files

See the child directories and source README files.

## Validation

All .tex documents in this suite are standalone pdfLaTeX roots; use `latexmk -pdf -halt-on-error <file>.tex` from their own directory. The suite validator also checks matching Template–Blank pairs.
