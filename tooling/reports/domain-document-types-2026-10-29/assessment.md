# Domain-first document types and leaf README architecture

**Date:** 2026-10-29  
**Repository:** Notoriousjayy/latex-docs  
**Base commit:** `25940cc0d75278b3d7c79cc21b1820a7b1398e8d`  
**Status:** implementation and static inspection complete; GitHub CI is the final acceptance gate.

## Architectural principle

Navigation follows **domain → artifact type → document** where the classification is confident. Directories such as `technical-documents/`, `templates/`, `workbooks/`, `study-guides/`, and `study-notes/` provide intuitive second-level entry points without introducing extra single-file nesting.

**Exceptions:** keep tightly coupled standards clauses, textbook chapters, diagram/source-asset folders, governance suites and mixed-purpose source collections intact. In particular, the cross-disciplinary `cornell-notes/` tree retains its historical chapter/standards structure until a separately validated cross-domain migration is justified. This is intentionally not a forced universal two-level taxonomy.

## Results

| Measure | Before | After |
|---|---:|---:|
| Tracked `src/` files | 2169 | 2579 |
| Source directories | 530 | 532 |
| Leaf directories | 409 | 412 |
| Leaf directories with README | 2 (before this follow-up) | 412/412 |
| LaTeX files | 1054 | 1054 |
| Rendered image assets | 798 | 798 |
| LaTeX relocations | 0 | 40 |
| Added leaf README files | — | 410 |

The file moves are **byte-identical**: every relocated `.tex` file retains the same Git blob SHA. The document root count remains 1054, and no source documents or image assets were dropped.

## Catalog and leaf indexing

Every immediate domain README now has a document-type section followed by a preserved subject-collection section where needed. All 412 leaf directories have README coverage, including the 92 diagram-output leaf folders. Generated indexes list their actual files and provide a nearest-available parent navigation link. Image-asset leaf READMEs identify the assets as generated output that should be regenerated from owning diagram sources rather than edited in place.

**Scope:** The new leaf indexes are filename-derived navigational aids; they do not imply that every included document was editorially reviewed or that its technical contents were independently validated. No new LaTeX styling systems or rewritten document bodies were introduced.

## Moves and verification

The [migration crosswalk](migration-crosswalk.csv) contains all 40 source relocations; [migrations.json](migrations.json) provides the machine-readable authoritative map. All 40 moved LaTeX documents were inspected for local `\\input`, `\\include`, `\\includegraphics`, and bibliography directives; none contained these move-sensitive dependencies. Existing source Markdown files were link-checked against the proposed repository tree; 394 local links in the initial 42-file Markdown set resolved without errors. Top-domain and representative leaf-index links were checked separately (194 links; no missing targets).

**Remaining gate:** run `python3 -m unittest -v tests.test_src_information_architecture tests.test_domain_document_type_layout`, `make preflight`, and the GitHub Actions LaTeX shard build. The workflow has been wired to run the regression tests before provisioning TeX runners. A successful source-tree inspection is not a substitute for a passing full compilation.

## Maintenance and placement policy

1. Choose the **primary domain** first: e.g., `security/`, `programming/`, `mathematics/` or `architecture/`.
2. Choose a document type only when it helps readers: technical documents explain; templates provide blank structures; workbooks require practice; study guides plan; study notes summarize.
3. Keep inseparable chapter sets, diagrams and their assets together. Do not create an empty directory solely to make categories look uniform.
4. Give every new **leaf directory** a dedicated `README.md`, with actual files, scope and a route to its owning collection; do not create generic nested directory chains.
5. Move files without changing their body when possible. Update every path-sensitive link, manifest, test, citation and build reference; preserve Git history and labels for migration traceability.
6. Treat generated images as build artifacts, not independently authored documents, even though they now carry concise leaf indexes.

## Risks and follow-up

- Canonical source paths changed: external links and previously published paths might require redirect/crosswalk support.
- The historical Cornell Notes library is organized by document method, not by a single subject-domain. Moving it under subject domains is a major follow-up requiring the collection manifest, chapter crosswalk and citation repair.
- A full content-level classification of all 1054 LaTeX sources was outside the verified scope. Mixed-purpose suites remain in stable positions rather than being split on filenames alone.
- The additional 410 Markdown indexes are lightweight but create maintenance overhead; update the index when adding or removing leaf files.
- The PR should not be merged before the CI job completes successfully.
