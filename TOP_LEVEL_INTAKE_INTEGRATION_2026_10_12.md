# Top-Level Document Intake Integration — 2026-10-12

Integration of the repository-root document staging intake into the
categorized `src/` library. Machine-readable provenance:
[`tooling/manifests/top-level-document-intake.json`](tooling/manifests/top-level-document-intake.json).
Migration tooling: [`tooling/scripts/migrate_top_level_intake.py`](tooling/scripts/migrate_top_level_intake.py)
(`--dry-run` / `--apply` / `--cleanup`, idempotent, hash-verified).

## 1. Baseline and observed inventory

- Baseline before migration: 699 buildable roots discovered by
  `make list-roots`; `latexmk`, `pdflatex`, `xelatex`, `lualatex`,
  Pygments 2.14 and the pinned PlantUML 1.2026.7 jar all available.
- Observed intake in the live checkout: **164 standalone `.tex` files and
  1 multi-diagram `.puml` file (165 files)** at the repository root.
- **Inventory discrepancies vs. the externally described upload set
  (176 files):** the checkout contains **no** `(2)`–`(4)` duplicate-suffix
  uploads, **no** `catalog-textual-data-string-processing-vulnerabilities.log`
  diagnostic, **no** repository-snapshot text export, and the enterprise
  report is named `enterprise_oss_security.tex` (no `(1)` suffix). Those
  files were never present in this working tree, so no disposition could be
  or needed to be recorded for them.
- **CCoE suite count discrepancy:** the checkout contains planning documents
  `2.1`–`2.31` (31 documents, not `2.1`–`2.39`) and monitoring/control
  `4.1`–`4.2` (2 documents, not `4.1`–`4.6`). The full observed suite is
  **50 numbered documents + 1 master guide**, all preserved. Missing numbers
  were **not** fabricated.
- **Calculus Cornell units:** units `00`–`13` (14 documents) are present;
  `14`/`15` belong to the *cloud* Cornell numbering, not calculus.

## 2. Duplicate resolution

| Original | Resolution |
|---|---|
| `42010-ad-template-polished.tex`, `42010-vp-template-polished.tex`, `viewpoint-section.tex`, `viewpoint-template-polished.tex` | Byte-identical to the copies already integrated in `src/templates/architecture/` by commit 499cef81; verified with `cmp`, originals removed. |
| `template.tex` | Content-equivalent to `kubernetes-from-first-principles.tex` except two `$$…$$` → `$…$` typographic corrections present only in the named file; the named file is canonical. No unique content lost. |

All other 159 sources are unique and migrated. Original SHA-256 and
transformed SHA-256 are recorded per file in the intake manifest; originals
were deleted only after hash verification of every target (`--cleanup`).

## 3. Added files by family (all under `src/`)

| Family | Count | Destination |
|---|---|---|
| CCoE governance suite (master + 1.1–5.4 as present) | 51 | `src/architecture/governance/ccoe/{initiation,planning,execution,monitoring-and-control,closure}/` |
| Cloud engineering deliverables 01–07 | 7 | `src/architecture/cloud/engineering-suite/` |
| Cloud chapter companions ch01–ch18 | 18 | `src/architecture/cloud/concepts-technology-architecture/` |
| Cloud Cornell notes 01–18 | 18 | `src/cornell-notes/architecture/cloud-computing/` |
| Calculus Cornell notes 00–13 | 14 | `src/cornell-notes/mathematics/calculus/` |
| Secure coding standards (12 languages) | 12 | `src/security/application-security/secure-coding/` |
| GHAS catalog/crosswalk + Actions hardening | 3 | `src/security/github-advanced-security/references/` |
| Code auditing catalogs + string-vuln catalog | 3 | `src/security/application-security/auditing/` |
| Burp Suite guide / PentAGI handout / review template | 3 | `…/dast/burp-suite/`, `…/pentesting/`, `…/processes/` |
| **Open-Source Enterprise Security Platform report** | 1 | `src/security/enterprise-security/open-source-enterprise-security-platform.tex` |
| BABOK v3 suite | 6 | `src/business-analysis/babok/` |
| Intelligent Investor suite 01–06 | 6 | `src/personal/finance/intelligent-investor/` |
| Cleaning operations / JAN-PRO roadmap | 4 | `src/startups/cleaning-services/` |
| Mathematics (proof libraries, calculus workbooks) | 4 | `src/mathematics/{proofs,calculus}/` |
| Kubernetes guides | 2 | `src/devops/platform/kubernetes/` |
| HTTP references | 2 | `src/programming/web/` |
| Algorithms / concurrency / game patterns | 3 | `src/programming/{algorithms,concurrency}/`, `src/game-development/patterns/` |
| Gamified DevOps curriculum | 1 | `src/devops/foundations/` |
| Orange Pi engineering guide | 1 | `src/electronics/` |
| UML 2.5.1 PlantUML legend (split, see §6) | 12 `.puml` | `src/architecture/uml/uml-2-5-1-legend/` |

All filenames follow the kebab-case ≤50-character policy; stable numeric
identifiers (CCoE `N.M`, cloud `chNN`/`NN`, Cornell unit numbers, investor
`01–06`) are preserved in filenames and document metadata. A few overlong
names were shortened with meaning preserved (recorded in the manifest), e.g.
`ch10_cloud_security_and_cybersecurity_access_oriented_mechanisms.tex` →
`ch10-access-oriented-security-mechanisms.tex`.

## 4. Style-architecture changes

- **New semantic module `tooling/styles/latex/cloudsuite.sty`** (inherits
  `base.sty` → house `style.sty`). The 25 cloud documents were authored
  against a `styles/cloudsuite.sty` that was never supplied; the used API was
  inventoried from the documents and implemented as documented,
  namespace-safe commands: `\coverpage{}{}{}`, `\sourceStatement`,
  `\sourceRef{ch}{page}`, `\refs`, `\field{}`, `\DocShort`, `takeaway` and
  `workbox` environments, and the suite palette (`navy`, `petrol`, `pale`,
  `gold`). `\sourceRef` renders neutral `Source: Ch. N, p. M` pointers; no
  bibliographic entry was invented. Each cloud document now loads exactly
  `\usepackage{cloudsuite}`.
- **Cornell collections migrated onto `cornell-notes`** (32 documents):
  duplicated preambles replaced by the module plus a small per-collection
  adapter (extra packages the house style does not own, collection palette,
  collection-specific tcolorboxes, Cornell metadata). Collisions with module
  compatibility names were resolved by renaming document-local definitions
  (`summarybox`→`sectionsummarybox`, cloud `notebox`→`scopenotebox`, calculus
  `\cornellhead`/`\cornellrow`→`\cornellcuehead`/`\cornellcuerow`); module
  `C`/`N` column types are reused.
- **`cornell-notes.sty` bug fix (title page only):** `\CornellIfNonEmpty`
  and `\CornellUnitLabel` used `\ifstrempty` on field *macros*, which never
  expands its argument, so unset fields rendered artifacts such as a stray
  `:` and `Primary source: , , , .` on every Cornell cover that omitted
  metadata (385 of 394 pre-existing Cornell roots omit the source fields).
  Replaced with `\ifdefvoid` on the field macros; populated fields render
  exactly as before. Regression-built existing Cornell documents
  successfully.
- Every other migrated document keeps its self-contained preamble, matching
  the precedent of the most recent integration commit (499cef81) and the 135
  pre-existing self-contained roots.

## 5. Dependency / incompatibility resolutions

- **Missing `styles/cloudsuite.sty`:** implemented as above (not a blank stub;
  all 25 documents build with full content).
- **`fontspec` under pdfLaTeX:** 5 intake documents (`Residential_Cleaning_*`,
  `Budget_Cleaning_Supply_Catalog`, `Gamified_DevOps_Security_Learning_Guide`,
  `http_headers_reference`) declare `fontspec` with system fonts. Each now
  carries `% !TeX program = lualatex`, which the build system's engine
  detection honors. All requested fonts (Libertinus Serif, Noto Sans/Serif,
  EB Garamond, Inter, Lato, DejaVu Sans Mono, Linux Libertine O) resolve via
  luaotfload from `texlive-fonts-extra`/system fonts — already installed by
  `.github/actions/setup-latex`, so **no CI package changes were required**.
  `Orange_Pi_Zero_Engineering_Guide` already declared `xelatex` and builds.
- **Latent TikZ bug in the Burp Suite guide:** `diamond/.style={diamond,…}`
  self-references the key and overflows TeX's input stack under any engine;
  the local style was renamed `decisionnode` (shape semantics unchanged).
- **`listings` vs the minted contract:** 28 migrated documents use
  `listings` in self-contained preambles (173 blocks, many with custom
  styles and captions). The house minted contract applies to documents that
  load the shared style; 6 pre-existing self-contained roots already use
  listings, and the CI does not gate `style_migration.py --validate`.
  Decision: these documents keep `listings` (recorded as `listings-token`
  advisory findings), preserving literal code fidelity; conversion remains
  available as follow-up work. The **enterprise report's four code blocks
  were converted to `minted`** (json/yaml/json/bash) with content unchanged.

## 6. Enterprise Open-Source Security Platform report (acceptance gate)

- Source `enterprise_oss_security.tex` (SHA-256 in manifest) →
  `src/security/enterprise-security/open-source-enterprise-security-platform.tex`;
  published PDF path
  `public/pdfs/security/enterprise-security/open-source-enterprise-security-platform.pdf`.
- Engine contract: `% !TeX program = lualatex` added (the source requests
  `fontspec` with Linux Libertine O / Lato / DejaVu Sans Mono; all verified
  present). Letter geometry, Roman front-matter and Arabic main-matter
  pagination, `\pagecolor{navy}`/`\nopagecolor` cover reset, chapter accent
  rules and running headers verified visually.
- Verified in the built 45-page PDF: PDF title metadata; **13 main chapters**
  (PART 1–13) **plus the two appendix chapters**; **28 capability IDs**
  (`CAP-01`–`CAP-28`); **four complete TikZ diagrams** (context,
  logical/container, deployment, roadmap — rendered as TikZ, not routed to
  PlantUML); **eight long tables** with repeating headers; **four minted
  code blocks** (content byte-faithful to the lstlistings); **23
  bibliography entries** with clickable citations/URLs; the 2026-10-12
  research-edition date; evidence labels D/U/A/E/Q; the qualified research
  claims (337 advertised profiles / 24 upstream-reviewed projects / 116
  discovery candidates / 140 registry entries / zero exhaustive 30-field
  audits / zero production-approved deployments) retained verbatim as
  source-attributed statements. Chapter 13 custom `insight`/`caution` boxes,
  `\term`/`\data`/`\status` macros and `Y`/`P` column types remain
  document-local (no global redefinitions introduced).
- **Missing research artifacts:** the report's reproduction section refers to
  `build_report.py` and `tool_registry.json`. These files were **not**
  uploaded and were **not** fabricated; the prose reference is retained and
  their absence is recorded here and in the manifest note. The 140-entry
  registry is content *within* the report, not 140 separate files.
- The PDF is picked up by the Pages index generator (verified with
  `stage-pages` against the built corpus).

## 7. PlantUML legend

The 12-block `uml-2.5.1-legend.puml` was split into 12 single-diagram files
under `src/architecture/uml/uml-2-5-1-legend/` because the repository's
PlantUML lint contract requires exactly one leaf style include per file and
forbids local colour/typography skinparams (the render pipeline itself
supports multi-block files, but the lint gate does not). Per block: original
`@startuml` names preserved as traceability comments, one leaf
`tooling/styles/plantuml/...` include matched to the diagram type,
house-owned skinparams removed, deliberate `monochrome`/`strictuml` notation
settings kept. Three source-compatibility fixes for the pinned engine
1.2026.7 (quoted `namespace` name; body-less `package … as X` declarations;
standalone `<<stereotype>>` lines in activity diagrams folded into their
action labels as `«stereotype»`). All 12 diagrams render (png + svg) through
`make render-plantuml`; `plantuml_lint.py` is clean; every view/legend block
is accounted for.

## 8. Build and validation results

- Roots: 699 → **858** (`make list-roots`); **159/159 new roots build
  successfully** with their configured engines, verified by PDF existence
  (not exit codes alone) plus content checks on the enterprise report.
- Representative visual review (rendered pages inspected) across: enterprise
  title page/capability table/architecture decisions/minted JSON page; CCoE
  charter form (document-control header, signature lines, fill-in rules);
  cloud chapter cover and Cornell matrices; calculus and cloud Cornell
  covers and body pages (cue tables, formula boxes, TikZ flow); investor
  worksheet cover; proof-library ToC; cleaning-operations and gamified-
  curriculum fontspec covers; UML legend PNG.
- `python3 tooling/scripts/style_migration.py --validate`: baseline had 83
  findings (71 `filename-too-long`, 6 `listings-token`, 6 naming — all
  pre-existing, none in migrated files). After migration the only new
  findings are the **28 documented `listings-token` advisories** (§5); no
  new naming, Cornell-structure, or minted-helper findings.
- `make plan PLAN_MODE=full MAX_SHARDS=12`: plans 858/858 roots across 12
  shards. Dependency graph verified: editing `cloudsuite.sty` invalidates
  exactly the 25 cloud roots; `cornell-notes.sty` invalidates 394 roots.
- CI path filters (`latex-ci.yml`, `render-plantuml.yml`, `_build-latex.yml`)
  already cover `src/**` and `tooling/**`, including all new locations, the
  new module and the new manifest. No CI jobs were disabled or weakened.
- Warning triage: worst new-document overfull boxes (≤84pt) occur in wide
  CodeQL crosswalk tables with long hyperlinked query names, inherited from
  the sources; affected pages were rendered and remain legible.
- **Not executed in this environment:** an actual GitHub Actions run (no
  runner), the full 858-root `make publish` (the 159 new roots and
  representative existing roots were built locally; existing-root regression
  was spot-checked via Cornell rebuilds), and a browser-based review of the
  Pages site (index generation itself was verified).

## 9. Working-tree summary

- Pre-existing, untouched: deletion of `github-workflows-build-latex.yml`
  (was already staged in the worktree before this migration).
- Modified: `tooling/styles/latex/cornell-notes.sty` (title-page emptiness
  fix, §4).
- Added: 159 `.tex` sources, 12 `.puml` sources, rendered legend `png/`+`svg/`
  outputs, `tooling/styles/latex/cloudsuite.sty`,
  `tooling/scripts/migrate_top_level_intake.py`,
  `tooling/manifests/top-level-document-intake.json`, this report.
- Removed: all 165 root intake files (after per-file hash verification).
- No source intake remains unclassified; every uploaded file present in the
  checkout has a recorded disposition in the manifest.
