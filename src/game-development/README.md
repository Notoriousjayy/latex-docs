# Game Development

## Overview

Cross-engine game-development references for design, game AI, animation, content pipelines, graphics, patterns and physical simulation. Engine-specific implementation code belongs in the owning software project.

## Scope and boundaries

Use this domain for game-engineering principles, design documents, graphics, animation, and simulation. General-purpose algorithms belong in [Programming](../programming/README.md); underlying mathematics belongs in [Mathematics](../mathematics/README.md).

## Directory map and documentation catalog

| Area | Material |
|---|---|
| [AI](ai/) | Game AI algorithms and pseudocode. |
| [Animation](animation/) | Animation study plan. |
| [Asset pipelines](asset-pipelines/) | Sprite and 3D model generation workflows. |
| [Design documents](design-documents/) | GDD source templates and examples. |
| [Graphics](graphics/) | Computer graphics principles. |
| [Patterns](patterns/) | Game programming pattern catalogs. |
| [Physics engines](physics-engines/) | Collision, fluid simulation and engineering gap analysis. |

## Recommended navigation

- [Game Design Document template](design-documents/templates/game-design-document-gdd-template.tex) for design scope, mechanics and requirements.
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
