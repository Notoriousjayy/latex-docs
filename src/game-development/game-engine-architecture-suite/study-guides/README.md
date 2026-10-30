# Study Guides

Seventeen original chapter-aligned guides. Start at the prerequisite curriculum and follow chapter dependencies; each guide ends with an evidence gate.

## Files

- [`01-introduction.tex`](./01-introduction.tex)
- [`02-tools-of-the-trade.tex`](./02-tools-of-the-trade.tex)
- [`03-fundamentals-of-software-engineering-for-games.tex`](./03-fundamentals-of-software-engineering-for-games.tex)
- [`04-parallelism-and-concurrent-programming.tex`](./04-parallelism-and-concurrent-programming.tex)
- [`05-3d-math-for-games.tex`](./05-3d-math-for-games.tex)
- [`06-engine-support-systems.tex`](./06-engine-support-systems.tex)
- [`07-resources-and-the-file-system.tex`](./07-resources-and-the-file-system.tex)
- [`08-the-game-loop-and-real-time-simulation.tex`](./08-the-game-loop-and-real-time-simulation.tex)
- [`09-human-interface-devices.tex`](./09-human-interface-devices.tex)
- [`10-tools-for-debugging-and-development.tex`](./10-tools-for-debugging-and-development.tex)
- [`11-the-rendering-engine.tex`](./11-the-rendering-engine.tex)
- [`12-animation-systems.tex`](./12-animation-systems.tex)
- [`13-collision-and-rigid-body-dynamics.tex`](./13-collision-and-rigid-body-dynamics.tex)
- [`14-audio.tex`](./14-audio.tex)
- [`15-introduction-to-gameplay-systems.tex`](./15-introduction-to-gameplay-systems.tex)
- [`16-runtime-gameplay-foundation-systems.tex`](./16-runtime-gameplay-foundation-systems.tex)
- [`17-you-mean-there-s-more.tex`](./17-you-mean-there-s-more.tex)

## Validation

All .tex documents in this suite are standalone pdfLaTeX roots; use `latexmk -pdf -halt-on-error <file>.tex` from their own directory. The suite validator also checks matching Template–Blank pairs.
