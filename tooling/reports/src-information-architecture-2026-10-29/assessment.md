# Source Information Architecture Assessment — 2026-10-29

**Repository:** `Notoriousjayy/latex-docs`  
**Baseline:** `main` at `f41770db49bbe8f0e51afcf20ddb301ab822a532`  
**Scope:** tracked `src/` files and directories; related Markdown indexes, historical migration mappings, PlantUML source references, and CI regression gates.

## Executive assessment

The repository is primarily a **source-first documentation corpus** with intact topic domains, architecture governance suites, and chapter/standards-based Cornell Notes. Its major information-architecture problem is **not that every deep directory is wrong**: the depth distribution is dominated by diagrams and book/standard clause hierarchies where grouping preserves provenance. The immediate actionable problems are one artificial top-level architecture-template domain, several single-file wrapper chains, and inconsistent/missing canonical top-level READMEs.

This migration makes **nine targeted LaTeX source moves** and normalizes **13 README paths** without flattening standards, chapters, diagram assets, or multi-file suites.

## Source tree census

| Metric | Before | Proposed |
|---|---:|---:|
| Immediate `src/` domains | 14 | 13 |
| Tracked `src/` files | 2,168 | 2,169 (one new architecture templates README) |
| `src/` directories | 537 | 530 |
| `.tex` source files (not all standalone) | 1,054 | 1,054 |
| PlantUML source files | 272 | 272 |
| PNG/JPG/JPEG/SVG files | 798 | 798 |
| Immediate domain README coverage | 13/14 (mixed case) | 13/13 (canonical `README.md`) |
| File relocations | — | 22 (9 LaTeX; 13 README) |
| Source-content changes due to moves | — | 0 bytes for all 9 relocated `.tex` blobs |

### File depth below `src/`

The depth count measures the number of directory segments beneath `src/` before the filename. It includes all tracked files, including diagram assets.

| Depth | Baseline | Proposed |
|---:|---:|---:|
| 0 | 1 | 1 |
| 1 | 21 | 21 |
| 2 | 152 | 158 |
| 3 | 371 | 367 |
| 4 | 390 | 389 |
| 5 | 356 | 356 |
| 6 | 780 | 780 |
| 7 | 97 | 97 |

## Taxonomy decisions

**Keep:** `architecture/`, `business-analysis/`, `cornell-notes/`, `data-systems/`, `devops/`, `documentation/`, `electronics/`, `game-development/`, `mathematics/`, `personal/`, `programming/`, `security/`, and `startups/`. These top-level domains communicate genuinely different material uses.

**Consolidate:** `src/templates/architecture/` becomes `src/architecture/templates/` because all four authored sources are ISO/IEC/IEEE 42010 architecture-description/viewpoint material; `src/templates/` had no other content or README and was not a general shared template library. Distinguish these **AD/VP templates** from existing **ADR templates** under `src/architecture/decisions/`.

**Flatten with title-accurate placement:** single-file `shems/`, `kafka/`, `quality/`, and `sba/` wrappers; and the doubly redundant `infrastructure-security/vulnerability-management/trivy/` path. See [migration crosswalk](migration-crosswalk.csv).

**Retain justified depth:** the 2024 C/C++ standards and clause-by-clause Cornell Notes, ISO/IEC/IEEE 42010 study collections, TOGAF/CCoE suites, cloud-architecture diagram sets with PNG/SVG assets, and self-contained product/engineering suites. Large asset counts do not justify rewriting the assets' ownership paths.

**No forced cross-domain moves:** Kafka material really is a Kafka book study plan even though the old filename said `user-stories`; it stays in data-streaming. DevOps secret management and security standards retain distinct responsibilities.

## Tree excerpts (before → after)

```text
src/templates/architecture/             src/architecture/templates/
  42010-ad-template-polished.tex           42010-ad-template-polished.tex
  42010-vp-template-polished.tex           42010-vp-template-polished.tex
  viewpoint-template-polished.tex          viewpoint-template-polished.tex
  viewpoint-section.tex                    viewpoint-section.tex
                                             README.md

src/architecture/examples/shems/        src/architecture/examples/
  shems-architecture-description.tex      shems-architecture-description.tex

src/data-systems/streaming/kafka/        src/data-systems/streaming/
  how-write-effective-user-...tex         kafka-study-plan-user-stories.tex

src/security/infrastructure-security/   src/security/infrastructure-security/
  vulnerability-management/trivy/          trivy-scope-and-objectives.tex
    trivy-scope-and-objectives.tex

src/startups/curricula/quality/          src/startups/curricula/
  minimum-checklist.tex                    minimum-curriculum-quality-checklist.tex

src/startups/support/sba/                src/startups/support/
  top-3-nearby-options.tex                  sba-local-assistance-intake.tex
```

Every immediate domain now uses `src/<domain>/README.md`. This case normalization improves consistency but means external links to the old lowercase paths should be updated.

## README and navigation contract

Every top-level README now contains an overview, scope/boundaries, directory and document map, recommended navigation, build/validation guidance, maintenance conventions, and cross-domain links. Existing specialized editorial content and safety notices were retained. `src/README.md` is the primary domain index. A new `src/architecture/templates/README.md` identifies the three standalone documents and one non-standalone fragment.

## Full tracked-file inventory and verification scope

The [source inventory](source-inventory.csv) includes **all 2,168 baseline tracked `src/` files** with current and proposed paths, format, depth, collection context, provisional title, placement rationale, and risk classification.

**Evidence boundary:** this is an exhaustive **path/tree inventory**, not 2,168 content reviews. Provisional titles are clearly labeled filename-derived except the few sampled document titles; source metadata and dependencies were not parsed for every untouched file. Nine relocated LaTeX source blobs were verified byte-identical using Git object SHAs. Reorganizing thousands of unreviewed files would be unjustified without a semantic content review and per-suite compilation evidence.

## Reference and dependency integrity

- Updated the source catalog, canonical top-domain README links, root README, and affected nested Markdown navigation links.
- Updated live `DUPLICATES_OF_EXISTING` canonical paths in `tooling/scripts/migrate_top_level_intake.py` and `canonical_path` references in `tooling/manifests/top-level-document-intake.json`.
- Preserved historical migration provenance with a dated relocation note in `TOP_LEVEL_INTAKE_INTEGRATION_2026_10_12.md`.
- Repaired the known architecture index reference in `tooling/scripts/plantuml_inventory.py` and four PlantUML reference files.
- New regression tests enforce domain README coverage, consistent section contracts, local top-index links, and migrated source existence.

## Validation record

**Completed statically:** two complete Git trees inspected; all nine moved `.tex` blobs unchanged; 13/13 top-domain README files present exactly once; `src/README.md` present; 175 local links in the top-level domain/source/template README set resolve within the proposed tree. The proposed directory structure contains seven fewer directories and no old `src/templates/` hierarchy.

**Required GitHub CI gate:** `make preflight`, root discovery, unit tests, and the repository's affected-root (or full, for global tooling changes) sharded build. The container used for this assessment cannot clone GitHub directly, so **no completed PDF compilation is claimed in this report**. The PR must stay unmerged until its checks establish build safety.

## Exceptions and remaining risks

- Deep academic/standards structures remain intentionally deep; an arbitrary maximum path depth would damage provenance.
- The path-only inventory cannot guarantee that each untouched source is in its ideal topical domain. Treat further category changes as separate, evidence-driven follow-on PRs.
- Historical externally published links to prior GitHub paths may need manual correction; the crosswalk is the authoritative lookup.
- Some existing nested READMEs intentionally use lowercase names. The 100% canonical policy applies to **immediate** children of `src/`, not all historical subdirectories.
- The `viewpoint-section.tex` file is a **fragment** and must not be counted as a standalone LaTeX root.

## Validation commands

```bash
python3 -m unittest -v tests.test_src_information_architecture
make preflight
make list-roots
make list-categories
make build-changed BASE_REF=<baseline-sha> HEAD_REF=<pr-sha>
# If global build tooling changes select the full corpus, let CI build all shards.
```

The pull request is the approval boundary. Do not merge without a green build.
