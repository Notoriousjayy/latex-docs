# Labs

Printable laboratory instructions aligned with executable source files under ../code; the tests form the evidence baseline.

## Files

- [`lab-01-fixed-step-game-loop.tex`](./lab-01-fixed-step-game-loop.tex)
- [`lab-02-arena-allocator.tex`](./lab-02-arena-allocator.tex)
- [`lab-03-parallel-batch.tex`](./lab-03-parallel-batch.tex)
- [`lab-04-generation-handles.tex`](./lab-04-generation-handles.tex)
- [`lab-05-math-and-pose-blending.tex`](./lab-05-math-and-pose-blending.tex)
- [`lab-06-triangle-rasterizer.tex`](./lab-06-triangle-rasterizer.tex)
- [`lab-07-bouncing-body.tex`](./lab-07-bouncing-body.tex)
- [`lab-08-audio-mixer.tex`](./lab-08-audio-mixer.tex)
- [`lab-09-entity-events.tex`](./lab-09-entity-events.tex)
- [`lab-10-frame-metrics.tex`](./lab-10-frame-metrics.tex)
- [`lab-11-integrated-engine-capstone.tex`](./lab-11-integrated-engine-capstone.tex)

## Validation

All .tex documents in this suite are standalone pdfLaTeX roots; use `latexmk -pdf -halt-on-error <file>.tex` from their own directory. The suite validator also checks matching Template–Blank pairs.
