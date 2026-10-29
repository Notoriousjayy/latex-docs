# Game Development

## Overview

Cross-engine game-development references for design, game AI, animation, content pipelines, graphics, patterns and physical simulation. Engine-specific implementation code belongs in the owning software project.

## Scope and boundaries

Use this domain for game-engineering principles, design documents, graphics, animation, and simulation. General-purpose algorithms belong in [Programming](../programming/README.md); underlying mathematics belongs in [Mathematics](../mathematics/README.md).

## Directory map and documentation catalog

### Document types

| Collection | Use it for | LaTeX sources |
|---|---|---:|
| [Templates](templates/README.md) | Reusable structured starting points and document forms | 2 |
| [Study guides](study-guides/README.md) | Study plans, curricula and guided reading | 1 |

### Subject collections and preserved suites

These collections retain topic, standard, chapter, governance or diagram boundaries where splitting would increase navigation cost or disrupt related sources.

| Collection | Contents | LaTeX sources |
|---|---|---:|
| [ai](ai/README.md) | Game AI algorithms and pseudocode. | 1 |
| [asset pipelines](asset-pipelines/README.md) | Sprite and 3D model generation workflows. | 2 |
| [graphics](graphics/README.md) | Computer graphics principles. | 1 |
| [patterns](patterns/README.md) | Game programming pattern catalogs. | 2 |
| [physics engines](physics-engines/README.md) | Collision, fluid simulation and engineering gap analysis. | 4 |


## Recommended navigation

- [Game Design Document template](templates/game-design-document-gdd-template.tex) for design scope, mechanics and requirements.
- [Game programming pattern catalog](patterns/game-programming-pattern-catalog.tex) for implementation trade-offs.
- [Real-time collision detection](physics-engines/real-time-collision-detection-algorithms.tex) for math, numerical assumptions and example algorithms.

## Build and validate

```bash
make preflight
make build-category-game-development
```

These targets compile the documentation, not a game runtime or asset-pipeline executable.

## Maintenance conventions

- Specify tool versions and asset licenses in pipeline documents.
- Differentiate pseudocode from measured or tested algorithms.
- Record reproducibility conditions and failure cases for physics and simulation models.

## Related domains

[Programming](../programming/README.md) · [Mathematics](../mathematics/README.md)
