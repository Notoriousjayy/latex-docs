# ADR: Retain the Existing LaTeX and PlantUML Rendering Architecture

Status: proposed for code review.

## Context

Five stand-alone source repositories contain grammar definitions and React/TypeScript railroad visualizations. The destination is a source-first LaTeX documentation library with a pinned PlantUML renderer, PNG rendering, pdfLaTeX builds and a single GitHub Pages publisher. The owner explicitly required no React application migration and PNG images when using PlantUML.

## Decision

Preserve grammar texts as pinned JSON and original factory modules as inert provenance. Render printable references through the existing pdfLaTeX toolchain. Author and render railroad diagrams as native PlantUML EBNF sources. The existing PlantUML output discovery must recognize the EBNF start marker; it continues to manage PNG and SVG outputs without an alternative engine.

Display **PNG** in the PDFs and in the published Pages gallery. The gallery is a static HTML view of raster assets from the verified existing pipeline; it is staged inside the authoritative Pages job. Do not add React, npm, Webpack, a backend or a competing publisher.

## Trade-offs

This approach avoids redundant frontend infrastructure, preserves reproducible documentation builds and provides one consistent published site. Five hand-authored EBNF diagrams remain in the document references. The build-time Python converter now emits a PNG for every one of the 1,166 imported textual productions on the Pages gallery. Unsupported factories are marked as text-only schematics rather than asserting a false grammar equivalence. Complete graphical or semantic parity remains a separate verification problem.

No standards compliance or source completeness certification is implied.
