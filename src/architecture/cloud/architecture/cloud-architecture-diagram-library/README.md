
# Cloud Architecture Diagram Library

## Purpose

This directory contains the imported `cloud-architecture-diagram-library` as a reusable PlantUML diagram library for the `latex-docs` repository. The LaTeX repository remains the system of record for documents; this directory is scoped to reusable cloud architecture diagrams and supporting metadata.

## Source Collections

| Collection | Purpose |
|---|---|
| `advanced-cloud-architecture-plantuml/` | Advanced cloud architecture diagrams, manifest metadata, and validation notes. |
| `cloud-arch-plantuml/` | Core cloud architecture pattern diagrams. |
| `specialized_cloud_architectures_puml/` | Specialized cloud architecture diagrams. |

## Directory Layout

```text
cloud-architecture-diagram-library/
├── README.md
├── cloud-architecture-diagram-library-manifest.csv
├── validation-checklist.md
├── advanced-cloud-architecture-plantuml/
├── cloud-arch-plantuml/
├── specialized_cloud_architectures_puml/
├── svg/
└── png/
```

## Rendering

Render all PlantUML diagrams recursively from the `latex-docs` repository root:

```bash
python3 tools/integrate_cloud_architecture_diagram_library.py   --source-repo ../cloud-architecture-diagram-library   --target-repo .   --render --plantuml-cmd plantuml --update-generated
```

Alternatively, render directly with PlantUML after the library has been imported:

```bash
find src/architecture/cloud/architecture/cloud-architecture-diagram-library   -name '*.puml' -print0 | xargs -0 plantuml -tsvg
```

The preferred generated output locations are:

- `cloud-architecture-diagram-library/svg/<collection>/...`
- `cloud-architecture-diagram-library/png/<collection>/...`

## LaTeX Usage

From a document located under `src/architecture/cloud/architecture/`, reference rendered PNG output with a relative path:

```latex
\begin{figure}[H]
  \centering
  \includegraphics[width=0.95\linewidth]{cloud-architecture-diagram-library/png/cloud-arch-plantuml/03a_dynamic_scalability_sequence.png}
  \caption{Dynamic Scalability Architecture}
\end{figure}
```

For `pdflatex`, PNG is the least fragile default. Use SVG only when the repository build already converts SVG to PDF or supports SVG inclusion safely.

## Maintenance Rules

1. Preserve the source collection layout; do not flatten the imported library.
2. Keep `.puml` files version-controlled.
3. Keep generated images in `svg/` and `png/` rather than beside unrelated `.tex` files.
4. Do not introduce vendor-specific cloud services unless already present in a source diagram.
5. Do not rewrite diagram semantics except for compile-correctness fixes.
6. Preserve `advanced-cloud-architecture-plantuml/manifest.csv` and regenerate the consolidated manifest when diagrams change.
7. Do not move existing LaTeX documents to accommodate this library.

## Validation

Run the generated validation checklist in `validation-checklist.md` after migration and after any diagram update.



