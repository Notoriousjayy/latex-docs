# Original PlantUML C4 model examples

All example systems are **fictional**, designed for teaching, and do not assert any real deployment or security posture.

Diagrams refer to the repository's existing house styles via a relative `!include` path. They are intended to be copied into `src/architecture/c4-model/documentation-suite/examples/` and processed with the root tooling renderer and linter.

Run from repository root: `make render-plantuml` followed by `python3 tooling/scripts/plantuml_lint.py`.

C4's four core abstractions and seven diagram types are notation-independent; these `.puml` files provide only representative illustrative models. Review macro compatibility with the repository's **pinned PlantUML version**, especially deployment instance references. The suite generator does not independently render these examples without that toolchain. No local palette or `skinparam` overrides are used.
