# Cloud Architecture Diagram Library

A source-controlled catalog of 51 PlantUML diagrams across fundamental, advanced and specialized cloud architecture patterns. These are conceptual models, not validated cloud deployments or vendor-specific implementation blueprints.

## Collections

| Collection | Diagrams | Coverage |
|---|---|---|
| [Fundamental cloud architectures](cloud-arch-plantuml) | 20 | Capacity, elasticity, failover, load balancing and resource pooling |
| [Advanced cloud architectures](advanced-cloud-architecture-plantuml) | 14 | Clustering, relocation, disaster recovery, provisioning and VPC |
| [Specialized cloud architectures](specialized-cloud-architectures-puml) | 17 | Storage, network, edge/fog and distributed architectures |

See the [manifest](cloud-architecture-diagram-library-manifest.csv) and [validation checklist](validation-checklist.md) for source inventory and integration review.

## Render and validate

```bash
make render-plantuml
python3 tooling/scripts/plantuml_lint.py
make preflight
make build-category-architecture
```

Run from the repository root. The PlantUML renderer uses the pinned, checksummed version in [its manifest](../../../../../tooling/manifests/plantuml.json). Rendered PNG, SVG and JPG files reside with each collection (and within `diagrams/` for the advanced set); the former root-level `png/` and `svg/` layout is not present.

## Using a diagram

Start with a `.puml` source, review its assumptions, render it, and reference a real relative image path from your LaTeX document. The [LaTeX index](../cloud-architecture-diagram-library-index.tex) is the collection entry point. pdfLaTeX can include PNG/JPG directly; SVG requires conversion or compatible tooling.

## Maintenance

- Keep source `.puml` files authoritative; regenerate image derivatives instead of editing them manually.
- Preserve source terminology, scope and provenance. Document provider-specific extensions as separate adaptations.
- Use [the shared PlantUML style framework](../../../../../tooling/plantuml/README.md) and review both rendered visuals and architectural semantics.
- After renames, update manifests, image paths, cross-references and validation documentation.

## Related

[Cloud architecture](../../readme.md)
