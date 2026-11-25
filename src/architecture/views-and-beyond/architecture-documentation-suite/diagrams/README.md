# Agent harness architecture diagrams

Nine source-controlled PlantUML models accompany the [proposed architecture standard](../07-agent-harness-architecture-standard.tex). These are illustrative target-design models, not observed production evidence. Rendering does not establish semantic correctness or standards conformance.

| Model | Source | PNG | SVG |
|---|---|---|---|
| System context | [PlantUML](01-context.puml) | [PNG](png/01-context.png) | [SVG](svg/01-context.svg) |
| Container architecture | [PlantUML](02-containers.puml) | [PNG](png/02-containers.png) | [SVG](svg/02-containers.svg) |
| Component architecture | [PlantUML](03-components.puml) | [PNG](png/03-components.png) | [SVG](svg/03-components.svg) |
| Module dependencies | [PlantUML](04-modules.puml) | [PNG](png/04-modules.png) | [SVG](svg/04-modules.svg) |
| Authorized tool execution | [PlantUML](05-authorized-execution.puml) | [PNG](png/05-authorized-execution.png) | [SVG](svg/05-authorized-execution.svg) |
| Run state lifecycle | [PlantUML](06-run-state.puml) | [PNG](png/06-run-state.png) | [SVG](svg/06-run-state.svg) |
| Security trust boundaries | [PlantUML](07-trust-boundaries.puml) | [PNG](png/07-trust-boundaries.png) | [SVG](svg/07-trust-boundaries.svg) |
| Deployment architecture | [PlantUML](08-deployment.puml) | [PNG](png/08-deployment.png) | [SVG](svg/08-deployment.svg) |
| Persistence data model | [PlantUML](09-data-model.puml) | [PNG](png/09-data-model.png) | [SVG](svg/09-data-model.svg) |

Browse the [PNG index](png/README.md), [SVG index](svg/README.md), or return to the [suite index](../README.md). Regenerate rendered assets from the repository root using `make render-plantuml`; preserve the PlantUML sources as authoritative.
