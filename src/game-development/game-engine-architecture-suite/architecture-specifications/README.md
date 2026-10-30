# Architecture Specifications

Original architecture specifications for lifecycle, subsystem integration, streaming and capstone documentation.

## Files

- [`asset-pipeline-and-world-streaming.tex`](./asset-pipeline-and-world-streaming.tex)
- [`capstone-engine-architecture-description.tex`](./capstone-engine-architecture-description.tex)
- [`render-animation-physics-audio-integration.tex`](./render-animation-physics-audio-integration.tex)
- [`subsystem-and-lifecycle-specification.tex`](./subsystem-and-lifecycle-specification.tex)

## Validation

All .tex documents in this suite are standalone pdfLaTeX roots; use `latexmk -pdf -halt-on-error <file>.tex` from their own directory. The suite validator also checks matching Template–Blank pairs.
