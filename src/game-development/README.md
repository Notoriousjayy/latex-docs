# Game Development

## Overview

Cross-engine game-development references for design, game AI, animation, content pipelines, graphics, patterns and physical simulation. Engine-specific implementation code belongs in the owning software project.

## Scope and boundaries

Use this domain for game-engineering principles, design documents, graphics, animation, and simulation. General-purpose algorithms belong in [Programming](../programming/README.md); underlying mathematics belongs in [Mathematics](../mathematics/README.md).

## Directory map and documentation catalog

### Document types

| Collection | Use it for | LaTeX sources |
|---|---|---:|
| [Templates](templates/README.md) | Reusable design documents, worked forms and printable blanks | 30 |
| [Study guides](study-guides/README.md) | Chapter-by-chapter guided reading | 36 |
| [Curricula](curricula/README.md) | Prerequisite-based learning path | 1 |
| [Technical references](technical-references/README.md) | Design theory, probability, metrics and lens crosswalk | 7 |
| [Workbooks](workbooks/README.md) | Engineering exercises and printable workbook pairs | 15 |
| [Laboratories](laboratories/README.md) | Python/C++ design and implementation handouts | 10 |
| [Architecture specifications](architecture-specifications/README.md) | Game runtime, economy, telemetry and content architecture | 4 |
| [Playtesting](playtesting/README.md) | Recruitment, observation and analysis procedures | 3 |
| [Assessments](assessments/README.md) | Scored quality gates and Template–Blank pairs | 8 |

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
- [Art of Game Design: 35-chapter study collection](study-guides/art-of-game-design/README.md) for reading and labs.
- [Game Design Engineering learning path](curricula/game-design-engineering-learning-path.tex) for prerequisite-ordered progression.
- [Gameplay design forms](templates/art-of-game-design/README.md) for 14 printable Template–Blank pairs.
- [Game mechanics and balancing workbooks](workbooks/README.md) for exercises and working forms.
- [Architecture and playtesting quality gates](assessments/README.md) for assessments.
- [Suite catalog and validation](game-design-engineering-suite/README.md) for source crosswalks, provenance and evidence.
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
