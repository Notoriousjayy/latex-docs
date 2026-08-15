# Cornell Notes Collections

Centralized Cornell Notes sources live under `src/cornell-notes/` and use the shared `cornell-notes` semantic style.

## Collections

- Computer Science
  - String Algorithms
- Electronics
  - Electronic Circuits
- Mathematics
  - Numerical Methods
- Security
  - CISSP

## Numerical Methods

The Numerical Methods collection provides chapter-by-chapter Cornell notes for foundational numerical computing topics. The collection is organized by topic directory for maintainability while preserving a chapter-ordered learning sequence.

### Topic groups

1. foundations
2. linear-algebra
3. interpolation-integration-and-functions
4. randomization-and-ordering
5. root-finding-and-optimization
6. fourier-and-spectral-methods
7. statistics-modeling-and-inference
8. differential-and-integral-equations
9. computational-geometry
10. general-algorithms

### Chapter index (1-22)

1. Chapter 1: Preliminaries  
   Source: `src/cornell-notes/mathematics/numerical-methods/foundations/ch01-preliminaries-notes.tex`
2. Chapter 2: Solution of Linear Algebraic Equations  
   Source: `src/cornell-notes/mathematics/numerical-methods/linear-algebra/ch02-linear-equations-notes.tex`
3. Chapter 3: Interpolation and Extrapolation  
   Source: `src/cornell-notes/mathematics/numerical-methods/interpolation-integration-and-functions/ch03-interpolation-notes.tex`
4. Chapter 4: Integration of Functions  
   Source: `src/cornell-notes/mathematics/numerical-methods/interpolation-integration-and-functions/ch04-integration-notes.tex`
5. Chapter 5: Evaluation of Functions  
   Source: `src/cornell-notes/mathematics/numerical-methods/interpolation-integration-and-functions/ch05-function-evaluation-notes.tex`
6. Chapter 6: Special Functions  
   Source: `src/cornell-notes/mathematics/numerical-methods/interpolation-integration-and-functions/ch06-special-functions-notes.tex`
7. Chapter 7: Random Numbers  
   Source: `src/cornell-notes/mathematics/numerical-methods/randomization-and-ordering/ch07-random-numbers-notes.tex`
8. Chapter 8: Sorting and Selection  
   Source: `src/cornell-notes/mathematics/numerical-methods/randomization-and-ordering/ch08-sorting-selection-notes.tex`
9. Chapter 9: Root Finding and Nonlinear Sets of Equations  
   Source: `src/cornell-notes/mathematics/numerical-methods/root-finding-and-optimization/ch09-root-finding-notes.tex`
10. Chapter 10: Minimization or Maximization of Functions  
    Source: `src/cornell-notes/mathematics/numerical-methods/root-finding-and-optimization/ch10-optimization-notes.tex`
11. Chapter 11: Eigensystems  
    Source: `src/cornell-notes/mathematics/numerical-methods/linear-algebra/ch11-eigensystems-notes.tex`
12. Chapter 12: Fast Fourier Transform  
    Source: `src/cornell-notes/mathematics/numerical-methods/fourier-and-spectral-methods/ch12-fft-notes.tex`
13. Chapter 13: Fourier and Spectral Applications  
    Source: `src/cornell-notes/mathematics/numerical-methods/fourier-and-spectral-methods/ch13-spectral-applications-notes.tex`
14. Chapter 14: Statistical Description of Data  
    Source: `src/cornell-notes/mathematics/numerical-methods/statistics-modeling-and-inference/ch14-statistical-description-notes.tex`
15. Chapter 15: Modeling of Data  
    Source: `src/cornell-notes/mathematics/numerical-methods/statistics-modeling-and-inference/ch15-data-modeling-notes.tex`
16. Chapter 16: Classification and Inference  
    Source: `src/cornell-notes/mathematics/numerical-methods/statistics-modeling-and-inference/ch16-classification-inference-notes.tex`
17. Chapter 17: Integration of Ordinary Differential Equations  
    Source: `src/cornell-notes/mathematics/numerical-methods/differential-and-integral-equations/ch17-ordinary-differential-equations-notes.tex`
18. Chapter 18: Two-Point Boundary Value Problems  
    Source: `src/cornell-notes/mathematics/numerical-methods/differential-and-integral-equations/ch18-boundary-value-problems-notes.tex`
19. Chapter 19: Integral Equations and Inverse Theory  
    Source: `src/cornell-notes/mathematics/numerical-methods/differential-and-integral-equations/ch19-integral-equations-notes.tex`
20. Chapter 20: Partial Differential Equations  
    Source: `src/cornell-notes/mathematics/numerical-methods/differential-and-integral-equations/ch20-partial-differential-equations-notes.tex`
21. Chapter 21: Computational Geometry  
  Source: `src/cornell-notes/mathematics/numerical-methods/computational-geometry/ch21-computational-geometry-notes.tex`
22. Chapter 22: General Algorithms  
  Source: `src/cornell-notes/mathematics/numerical-methods/general-algorithms/ch22-general-algorithms-notes.tex`

## Electronic Circuits

The Electronic Circuits collection provides 15 chapter-ordered Cornell notes under `src/cornell-notes/electronics/electronic-circuits/`.

### Topic groups

1. foundations
2. semiconductor-devices
3. analog-circuits
4. power-electronics
5. digital-logic-and-interfaces
6. mixed-signal-systems
7. embedded-systems

The chapter sequence is complete only for chapters 1--15; no placeholder chapters 16--20 are included. Each source compiles to `public/pdfs/cornell-notes/electronics/electronic-circuits/<topic>/<filename>.pdf`.

### Expected PDF output path

Each chapter compiles to:

`public/pdfs/cornell-notes/mathematics/numerical-methods/<topic>/<filename>.pdf`

Example:

`public/pdfs/cornell-notes/mathematics/numerical-methods/fourier-and-spectral-methods/ch12-fft-notes.pdf`

### Build commands

- Build one chapter:
  - `cd src/cornell-notes/mathematics/numerical-methods/foundations`
  - `TEXINPUTS="$(pwd)/../../../../../tooling/latex//:$(pwd)/../../../../../tooling/styles/latex//:$TEXINPUTS" latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error -file-line-error ch01-preliminaries-notes.tex`
- Build one collection:
  - `python3 tooling/scripts/latex_build.py build-category cornell-notes --output-dir public/pdfs --log-dir public/logs --clean-output`
- Build all Cornell Notes (or all changed roots in Cornell Notes):
  - `make build-changed BASE_REF=HEAD~1 HEAD_REF=HEAD`
  - `make publish-parallel JOBS=8`

### Filename policy note

Upload-attachment suffixes such as `(1)` are not valid repository names. Cornell source paths, manifests, generated PDFs, logs, and Pages URLs must use canonical kebab-case basenames without upload suffixes.
