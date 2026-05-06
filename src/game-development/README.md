# Game Development

Game-engine and game-design documentation. Strong overlap with the
solo-authored AetherForge Engine project (C/C++, SDL3, OpenGL ES 3.0,
WebGL 2.0) — engine-internal docs live in the engine repository; this
folder hosts cross-cutting and study-plan material.

## Scope

**Belongs here:**
- Game-design documents (GDDs) and the GDD template.
- Animation and asset-pipeline notes.
- Physics-engine gap analyses and study plans.
- Cross-engine pipeline blueprints (AI-assisted asset generation, etc.).

**Does not belong here:**
- AetherForge Engine internal API documentation (lives in the engine repo).
- WebAssembly build-system docs — see `../programming/languages/c-cpp/wasm/`.

## Contents

| Child | Purpose |
|---|---|
| `animation/` | Computer animation user stories. |
| `asset-pipelines/` | AI-assisted 3D model and sprite pipelines. |
| `design-documents/` | GDD overview document and template (`templates/`). |
| `physics-engines/` | Physics-engine gap analyses. |

## Conventions

- The GDD template (`design-documents/templates/gdd-template.tex`)
  is the starting point for new GDDs; copy it before customizing.
- Asset-pipeline write-ups end with `-pipeline.tex`.

## Building

```bash
make build-category-game-development
```

## Related

- `../README.md`
- `../programming/languages/c-cpp/` for engine-language references.
