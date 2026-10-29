# Mathematics

## Overview

Formal and applied mathematics references, workbooks and study plans spanning algebra, calculus, differential equations, computational geometry and mathematical proofs.

## Scope and boundaries

Mathematical theory, proofs, methods, and applied workbooks belong here. Language-specific algorithms belong in [Programming](../programming/README.md), with applied game simulations in [Game Development](../game-development/README.md).

## Directory map and documentation catalog

### Document types

| Collection | Use it for | LaTeX sources |
|---|---|---:|
| [Workbooks and exercises](workbooks/README.md) | Practice, exercises, checklists and worked activities | 3 |
| [Study guides](study-guides/README.md) | Study plans, curricula and guided reading | 4 |

### Subject collections and preserved suites

These collections retain topic, standard, chapter, governance or diagram boundaries where splitting would increase navigation cost or disrupt related sources.

| Collection | Contents | LaTeX sources |
|---|---|---:|
| [algebra](algebra/README.md) | Matrices, polynomials and C/C++ representations. | 2 |
| [differential equations](differential-equations/README.md) | ODEs, PDEs, dynamics, scientific computing and exercises. | 7 |
| [geometry](geometry/README.md) | Computational geometry algorithms, polygons and study plans. | 4 |
| [proofs](proofs/README.md) | Proof techniques and structured mathematical reasoning. | 2 |


## Recommended navigation

- **Engineering models:** calculus → differential equations → numerical methods and applications.
- **Algorithmic geometry:** algebra → proof techniques → geometry and data structures.
- **Proof-based study:** definitions → propositions → examples and counterexamples.

## Build and validate

```bash
make preflight
make build-category-mathematics
```

Building the PDF sources does not constitute executable verification of every included algorithm or numerical method.

## Maintenance conventions

State assumptions, definitions, mathematical domains, physical units where applicable, convergence conditions and any implementation limitations. Attribute textbook material precisely and separate derivations from illustrative pseudocode.

## Related domains

[Programming](../programming/README.md) · [Source catalog](../README.md)
