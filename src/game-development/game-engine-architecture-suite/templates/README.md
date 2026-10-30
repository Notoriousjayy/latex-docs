# Templates

Controlled record templates and paired clean blanks. These are game-engine-specific records, distinct from repository-wide ADR/AD forms.

## Files

- [`asset-pipeline-design-record-blank.tex`](./asset-pipeline-design-record-blank.tex)
- [`asset-pipeline-design-record-template.tex`](./asset-pipeline-design-record-template.tex)
- [`engine-architecture-decision-record-blank.tex`](./engine-architecture-decision-record-blank.tex)
- [`engine-architecture-decision-record-template.tex`](./engine-architecture-decision-record-template.tex)
- [`engine-subsystem-interface-record-blank.tex`](./engine-subsystem-interface-record-blank.tex)
- [`engine-subsystem-interface-record-template.tex`](./engine-subsystem-interface-record-template.tex)
- [`game-loop-design-record-blank.tex`](./game-loop-design-record-blank.tex)
- [`game-loop-design-record-template.tex`](./game-loop-design-record-template.tex)
- [`gameplay-object-model-design-record-blank.tex`](./gameplay-object-model-design-record-blank.tex)
- [`gameplay-object-model-design-record-template.tex`](./gameplay-object-model-design-record-template.tex)
- [`performance-experiment-plan-blank.tex`](./performance-experiment-plan-blank.tex)
- [`performance-experiment-plan-template.tex`](./performance-experiment-plan-template.tex)

## Validation

All .tex documents in this suite are standalone pdfLaTeX roots; use `latexmk -pdf -halt-on-error <file>.tex` from their own directory. The suite validator also checks matching Template–Blank pairs.
