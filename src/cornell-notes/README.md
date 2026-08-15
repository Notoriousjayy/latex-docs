# Cornell Notes Collections

Centralized Cornell Notes sources live under `src/cornell-notes/` and use the shared `cornell-notes` semantic style.

## Collections

- Computer Science
  - Combinatorial Algorithms
  - Computer Networks
  - Operating Systems
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

## Combinatorial Algorithms

The Combinatorial Algorithms collection contains Chapters 1--30 under `src/cornell-notes/computer-science/combinatorial-algorithms/`. Topic groups are `subset-generation`, `compositions`, `permutations`, `integer-partitions`, `set-partitions`, `general-frameworks`, `young-tableaux`, `sorting`, `array-reindexing`, `graph-algorithms`, `polynomial-algorithms`, `matrix-and-array-algorithms`, `partially-ordered-sets`, `backtracking`, and `tree-algorithms`.

### Chapter index (1-30)

1. `subset-generation/ch01-next-subset-of-an-n-set-notes.tex`
2. `subset-generation/ch02-random-subset-of-an-n-set-notes.tex`
3. `subset-generation/ch03-next-k-subset-of-an-n-set-notes.tex`
4. `subset-generation/ch04-random-k-subset-of-an-n-set-notes.tex`
5. `compositions/ch05-next-composition-of-n-into-k-parts-notes.tex`
6. `compositions/ch06-random-composition-of-n-into-k-parts-notes.tex`
7. `permutations/ch07-next-permutation-of-n-letters-notes.tex`
8. `permutations/ch08-random-permutation-of-n-letters-notes.tex`
9. `integer-partitions/ch09-next-partition-of-integer-n-notes.tex`
10. `integer-partitions/ch10-random-partition-of-an-integer-n-notes.tex`
11. `set-partitions/ch11-next-partition-of-an-n-set-notes.tex`
12. `set-partitions/ch12-random-partition-of-an-n-set-notes.tex`
13. `general-frameworks/ch13-general-combinatorial-family-algorithms-notes.tex`
14. `young-tableaux/ch14-young-tableaux-notes.tex`
15. `sorting/ch15-sorting-notes.tex`
16. `permutations/ch16-cycle-structure-of-a-permutation-notes.tex`
17. `array-reindexing/ch17-renumbering-rows-and-columns-of-an-array-notes.tex`
18. `graph-algorithms/ch18-spanning-forest-of-a-graph-notes.tex`
19. `polynomial-algorithms/ch19-newton-forms-of-a-polynomial-notes.tex`
20. `graph-algorithms/ch20-chromatic-polynomial-of-a-graph-notes.tex`
21. `polynomial-algorithms/ch21-composition-of-power-series-notes.tex`
22. `graph-algorithms/ch22-network-flows-notes.tex`
23. `matrix-and-array-algorithms/ch23-permanent-function-notes.tex`
24. `matrix-and-array-algorithms/ch24-invert-a-triangular-array-notes.tex`
25. `partially-ordered-sets/ch25-triangular-numbering-in-partially-ordered-sets-notes.tex`
26. `partially-ordered-sets/ch26-mobius-function-notes.tex`
27. `backtracking/ch27-backtrack-method-notes.tex`
28. `tree-algorithms/ch28-labeled-trees-notes.tex`
29. `tree-algorithms/ch29-random-unlabeled-rooted-trees-notes.tex`
30. `tree-algorithms/ch30-tree-of-minimal-length-notes.tex`

## Computer Networks

The Computer Networks collection contains Chapters 1--9 under `src/cornell-notes/computer-science/computer-networks/`: `foundations/ch01-introduction-cornell-notes.tex`, `physical-layer/ch02-physical-layer-cornell-notes.tex`, `data-link-layer/ch03-data-link-layer-cornell-notes.tex`, `medium-access-control/ch04-medium-access-control-sublayer-cornell-notes.tex`, `network-layer/ch05-network-layer-cornell-notes.tex`, `transport-layer/ch06-transport-layer-cornell-notes.tex`, `application-layer/ch07-application-layer-cornell-notes.tex`, `network-security/ch08-network-security-cornell-notes.tex`, and `reference-material/ch09-reading-list-and-bibliography-cornell-notes.tex`.

## Operating Systems

The Operating Systems collection contains Chapters 1--13 under `src/cornell-notes/computer-science/operating-systems/`: `foundations/ch01-introduction-cornell-notes.tex`, `processes-and-threads/ch02-processes-and-threads-cornell-notes.tex`, `memory-management/ch03-memory-management-cornell-notes.tex`, `file-systems/ch04-file-systems-cornell-notes.tex`, `input-output/ch05-input-output-cornell-notes.tex`, `deadlocks/ch06-deadlocks-cornell-notes.tex`, `virtualization-and-cloud/ch07-virtualization-and-the-cloud-cornell-notes.tex`, `multiple-processor-systems/ch08-multiple-processor-systems-cornell-notes.tex`, `security/ch09-security-cornell-notes.tex`, `case-studies/ch10-case-study-1-unix-linux-and-android-cornell-notes.tex`, `case-studies/ch11-case-study-2-windows-8-cornell-notes.tex`, `operating-system-design/ch12-operating-system-design-cornell-notes.tex`, and `reference-material/ch13-reading-list-and-bibliography-cornell-notes.tex`.

### Shared publication contract

All three collections use `cornell-notes` and publish source-relative PDFs under `public/pdfs/cornell-notes/computer-science/<collection>/<topic>/<filename>.pdf`. Build them through `python3 tooling/scripts/latex_build.py build-category cornell-notes --output-dir public/pdfs --log-dir public/logs --clean-output`. Upload-copy suffixes are prohibited from source, PDF, log, and Pages paths.

The supplied import is complete at 52 traceable documents: 30 Combinatorial Algorithms, 9 Computer Networks, and 13 Operating Systems. The earlier 56-file estimate is reconciled as a four-document discrepancy; no additional related source files were found or invented.

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
