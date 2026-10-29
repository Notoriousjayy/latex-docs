# Semantic Taxonomy and Discoverability Assessment

**Repository:** `Notoriousjayy/latex-docs`  
**Baseline commit:** `44c818f6650df4cf9059a63d098a47f82d8421b4`  
**Status:** targeted semantic reorganization implemented in a proposed PR; complete manual content classification outstanding.

## Problem and observed evidence

The previous repository layout distributed language-specific secure coding standards across `security/application-security/secure-coding/`, while Java already had a technical rule-catalog and coding guidelines under `programming/languages/java/secure-coding/`. The twelve security standards are standalone language-specific control documents that share a derived baseline structure: language-specific weaknesses, code examples, CodeQL applicability, companion checks and SSDLC gates. Moving them to their respective language contexts reduces ambiguous ownership without changing the security program's cross-language methodology.

Another verified misplacement was the CI/CD + GitHub Actions user-story workbook within AppSec fundamentals: its substantive chapters cover continuous integration, continuous delivery and GitHub Actions implementation. It now lives with DevOps/GitHub Actions materials.

Other inspected examples were **retained**: a geometry user-story study plan is about geometry, and a micro-frontends story-card pack is about front-end engineering. A TOGAF user-story file is only a minimal placeholder, not a completed user-story corpus.

## Implementation choices

- **13 byte-identical LaTeX moves**, with original and destination Git blob SHA matching for each ([crosswalk](migration-crosswalk.csv)).
- Subject-first `programming/languages/README.md` links C/C++, C#, Go, Java, JavaScript, Kotlin, Python, Ruby, Rust, Swift and TypeScript standards.
- Java's existing CERT/Oracle rule catalog is kept alongside its newly colocated derived secure coding standard. The GHAS cross-language catalog stays in Security, as do language-neutral assessment methods.
- Dedicated new leaf READMEs for the newly introduced language collections and C/C++ standards; the emptied previous security/secure-coding folder is removed.
- Updated twelve historical intake canonical paths in the live intake script and manifest. Preserved the historical intake report and appended an explanatory relocation note.
- Added cross-domain discovery catalogs without replicating authored sources.

## Discovery system

The [catalog](../../../catalog/README.md) includes by-domain, by-subject, by-document-type and primary artifact indexes: user stories, templates, workbooks, scorecards, checklists, technical references, assessments, runbooks, study guides and secure coding.

All **1054 tracked LaTeX sources** are recorded once in [the semantic inventory](../../manifests/semantic-document-inventory.json). **23** have evidence from targeted content inspection; **1031** have expressly provisional path/title-derived classification. Unreviewed records have no invented summary or inferred audience. The inventory is a *complete path index*, not a claim of full semantic review.

Search evidence also identifies **42 documents mentioning scorecards**, but these are not all independent scorecards. The FinOps/SLA templates contain an actual restoration scorecard; the BABOK techniques catalog discusses Balanced Scorecard as a method. Both are linked from the scorecards catalog and not mislabeled as standalone files.

## Structural metrics

| Measure | Current proposed tree |
|---|---:|
| Top-level source domains | 13 |
| `.tex` files | 1054 |
| `src/` directories | 538 |
| Leaf directories | 418 |
| Leaf directories with README | 418 |
| Relocated authored LaTeX sources | 13 |
| LaTeX source content changed in moves | 0 bytes |

## Integrity and validation

**Completed static verification:** the Git object SHA of every moved `.tex` file is identical before/after; canonical paths exist and old paths are absent; leaf README coverage is 418/418; the selected LaTeX sources have no move-sensitive local input/graphics/bibliography directives. All tracked source files remain in the tree.

**Automated full-file mechanical scan:** `python3 tooling/scripts/semantic_content_audit.py --check` reads every LaTeX source in full, verifies its Git blob hash against the manifest, and extracts heading/title/dependency and keyword evidence. This is not equivalent to a qualitative content-level review; it does not validate technical meaning or assign verified summaries.

**CI required:** the planning-stage regression tests, preflight, dependency-aware shard build, PlantUML validation and aggregation need to complete. No success is claimed before results exist.

## Explicit outstanding work

The original instruction requests semantic classification of **every** authored document. That cannot honestly be claimed from a filename-based inventory. The remaining 1031 sources require content-level review, reconciliation of mixed-purpose workbooks/templates, and any resulting further moves. The catalog labels these as provisional to avoid premature reclassification.

Current category counts are useful for discovery but may contain false positives (such as documents that discuss a template rather than providing a blank template). Keep one authoritative source and refine the inventory incrementally, updating the indexes as classification evidence improves.

Cross-domain physical restructuring beyond the audited 13 files, including Cornell Notes standards and chapter suites, is deferred until reference and citation dependencies are individually reviewed.

## Review acceptance checklist

- [x] Every moved LaTeX blob preserved byte-for-byte.
- [x] Source root count preserved.
- [x] No leaf directory without README.
- [x] User-story, template, workbook, scorecard and checklist discovery catalogs created.
- [x] Canonical secure coding language index created.
- [ ] CI planning, full compilation and aggregate validation pass.
- [ ] All remaining authored sources receive individual semantic review (follow-on work).
