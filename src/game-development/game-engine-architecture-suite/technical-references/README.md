# Technical References

Substantial engineering references for subsystem contracts, timing, memory, rendering, animation, physics, audio and gameplay.

## Files

- [`animation-and-state-machines.tex`](./animation-and-state-machines.tex)
- [`audio-and-input.tex`](./audio-and-input.tex)
- [`engine-system-boundaries.tex`](./engine-system-boundaries.tex)
- [`gameplay-object-model.tex`](./gameplay-object-model.tex)
- [`math-rendering-and-visibility.tex`](./math-rendering-and-visibility.tex)
- [`memory-and-resource-lifetimes.tex`](./memory-and-resource-lifetimes.tex)
- [`physics-and-collision.tex`](./physics-and-collision.tex)
- [`simulation-and-concurrency.tex`](./simulation-and-concurrency.tex)

## Validation

All .tex documents in this suite are standalone pdfLaTeX roots; use `latexmk -pdf -halt-on-error <file>.tex` from their own directory. The suite validator also checks matching Template–Blank pairs.
