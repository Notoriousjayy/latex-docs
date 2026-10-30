# Scorecards

Scored, evidence-based review instruments. Each has a guided form and printable blank. A release blocker overrides the numeric score.

## Files

- [`documentation-and-capstone-assessment-scorecard-blank.tex`](./documentation-and-capstone-assessment-scorecard-blank.tex)
- [`documentation-and-capstone-assessment-scorecard-template.tex`](./documentation-and-capstone-assessment-scorecard-template.tex)
- [`gameplay-integration-readiness-scorecard-blank.tex`](./gameplay-integration-readiness-scorecard-blank.tex)
- [`gameplay-integration-readiness-scorecard-template.tex`](./gameplay-integration-readiness-scorecard-template.tex)
- [`performance-and-memory-scorecard-blank.tex`](./performance-and-memory-scorecard-blank.tex)
- [`performance-and-memory-scorecard-template.tex`](./performance-and-memory-scorecard-template.tex)
- [`runtime-architecture-quality-scorecard-blank.tex`](./runtime-architecture-quality-scorecard-blank.tex)
- [`runtime-architecture-quality-scorecard-template.tex`](./runtime-architecture-quality-scorecard-template.tex)

## Validation

All .tex documents in this suite are standalone pdfLaTeX roots; use `latexmk -pdf -halt-on-error <file>.tex` from their own directory. The suite validator also checks matching Template–Blank pairs.
