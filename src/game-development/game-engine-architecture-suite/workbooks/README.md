# Workbooks

Every workbook has both guided -template.tex and print-ready -blank.tex versions. Use blanks for handwriting and evidence capture.

## Files

- [`memory-allocator-benchmark-workbook-blank.tex`](./memory-allocator-benchmark-workbook-blank.tex)
- [`memory-allocator-benchmark-workbook-template.tex`](./memory-allocator-benchmark-workbook-template.tex)
- [`parallel-jobs-and-race-analysis-workbook-blank.tex`](./parallel-jobs-and-race-analysis-workbook-blank.tex)
- [`parallel-jobs-and-race-analysis-workbook-template.tex`](./parallel-jobs-and-race-analysis-workbook-template.tex)
- [`physics-audio-integration-workbook-blank.tex`](./physics-audio-integration-workbook-blank.tex)
- [`physics-audio-integration-workbook-template.tex`](./physics-audio-integration-workbook-template.tex)
- [`render-and-animation-workbook-blank.tex`](./render-and-animation-workbook-blank.tex)
- [`render-and-animation-workbook-template.tex`](./render-and-animation-workbook-template.tex)
- [`simulation-timestep-workbook-blank.tex`](./simulation-timestep-workbook-blank.tex)
- [`simulation-timestep-workbook-template.tex`](./simulation-timestep-workbook-template.tex)

## Validation

All .tex documents in this suite are standalone pdfLaTeX roots; use `latexmk -pdf -halt-on-error <file>.tex` from their own directory. The suite validator also checks matching Template–Blank pairs.
