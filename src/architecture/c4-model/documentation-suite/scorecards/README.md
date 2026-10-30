# Scorecards

Three weighted engineering scorecards, each with Template and printable Blank variants; numeric results never override hard release gates.

## Files

- [`architecture-traceability-scorecard-blank.tex`](architecture-traceability-scorecard-blank.tex)
- [`architecture-traceability-scorecard-template.tex`](architecture-traceability-scorecard-template.tex)
- [`diagram-quality-scorecard-blank.tex`](diagram-quality-scorecard-blank.tex)
- [`diagram-quality-scorecard-template.tex`](diagram-quality-scorecard-template.tex)
- [`release-readiness-scorecard-blank.tex`](release-readiness-scorecard-blank.tex)
- [`release-readiness-scorecard-template.tex`](release-readiness-scorecard-template.tex)

## Build and ownership

Files are standalone pdfLaTeX roots. Compile from this directory with `pdflatex -interaction=nonstopmode -halt-on-error FILE.tex`, or use the suite validator. Keep source provenance and independently authored extensions distinct.
