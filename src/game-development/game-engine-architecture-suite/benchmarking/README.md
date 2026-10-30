# Benchmarking

Repeatable frame-time, memory and concurrency measurement procedures with raw data requirements.

## Files

- [`allocator-and-data-layout.tex`](./allocator-and-data-layout.tex)
- [`frame-pacing-and-real-time-budget.tex`](./frame-pacing-and-real-time-budget.tex)
- [`job-scheduler-scaling.tex`](./job-scheduler-scaling.tex)

## Validation

All .tex documents in this suite are standalone pdfLaTeX roots; use `latexmk -pdf -halt-on-error <file>.tex` from their own directory. The suite validator also checks matching Template–Blank pairs.
