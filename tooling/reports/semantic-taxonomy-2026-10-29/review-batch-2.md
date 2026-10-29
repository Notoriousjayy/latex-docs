# Targeted semantic review — reusable artifacts (batch 2)

## Scope and evidence

This follow-on review inspects **29 additional authored LaTeX sources** for their actual purpose, structural sections and intended use. It changes the metadata classification of verifiable cases but **does not relocate or rewrite any source documents** in this batch.

The repository now has **52 content-reviewed sources** out of **1,054**, leaving **1,002 provisional** classifications. These figures describe the manifest review status, not a claim of a complete repository-wide semantic assessment.

The [content-review evidence table](review-batch-2.csv) records actual titles, excerpts identified by source sections, review roles, type rationale, source Git SHA and related risks. The main inventory is maintained in [semantic-document-inventory.json](../../manifests/semantic-document-inventory.json). Subsequent artifact-type catalogs are generated from that manifest by [build_semantic_catalogs.py](../../scripts/build_semantic_catalogs.py).

## Corrected taxonomy examples

| Source | New primary type | Why |
|---|---|---|
| ISO/IEC/IEEE 42010 conformance assessment | Workbook | Clause checks, assessor fields, evidence disposition and review questions are meant to be completed, not only copied as a template |
| CMake cross-platform performance chapter | Technical reference | Compilers, cache reproducibility and benchmarks dominate; a decision-record example is only embedded |
| Python testing/security/performance | Handbook | A multi-chapter assurance guide spanning testing, threat analysis, profiling and laboratories |
| ECMAScript testing/conformance | Implementation guide | Test262 adoption, tests, CI and verification procedures; embedded test specification is secondary |
| GitHub quick-start checklist | Implementation guide | A complete repository and community-health setup playbook, not merely a tick-box checklist |
| Two AppSec code-audit catalogs | Technical references | Strategies/techniques selection and operational reasoning, not completed assessments |
| Open-source enterprise security platform | Architecture document | Reference architectures, platform components and tooling-selection criteria comprise its core |
| AuditPack startup plan and SBA roadmap | Business plans | Venture formation and operating milestones; not security assessments |
| CPython engineering curriculum | Study guide | Prerequisites, modules, capstone and grading; labs and workbook exercises are secondary |
| LaTeX assessment curricula shared preamble | Non-standalone fragment | No documentclass; used only as shared preamble for a connected assessment curriculum |

These are semantics-based distinctions: the presence of a sample worksheet, template, checklist or rubric inside a reference does **not** make the whole document that artifact type.

## Confirmed exact duplicate requiring governance

The file `src/business-analysis/workbooks/babok-minimum-checklist.tex` has Git blob SHA `0c85b9f31ea5475f9f62f4a220b3aa4b4308dcd9`, identical to `src/startups/workbooks/minimum-curriculum-quality-checklist.tex`. Its title and body are **Minimum Curriculum Quality Checklist**, with sections for review criteria, ratings and notes. It does **not** address BABOK business analysis specifically. This is a genuine duplicated source with a misleading path, not two different checklists. No deletion was performed because existing LaTeX root counts and consumers require a separate deduplication review. Recommend selecting the education/startup curriculum version as canonical, then removing or relocating the misnamed duplicate after consumers and build gates are reconciled.

## Catalog implementation and controls

- Generated, authoritative listings: by domain, by subject, by primary document type, and reusable artifact-specific catalogs.
- Curated exception pages: scorecards with embedded evidence and secure coding by language remain hand-reviewed because terms found in a document do not imply the document's primary type.
- Adds distinct `business-plan` and `latex-fragment` controlled values, and separate discovery pages for source fragments, business plans, handbooks and architecture documents.
- Generator command: `python3 tooling/scripts/build_semantic_catalogs.py --write`; CI `--check` fails when committed navigational catalogs no longer match metadata.
- The existing complete-source mechanical audit additionally checks any explicitly confirmed standalone/root flags against actual source `\\documentclass` presence.

## Remaining limitations

The **1,002** unreviewed documents remain marked provisional. The two duplicate checklists are left unchanged pending a safe migration. Other source fragments may remain marked provisional until checked individually. External links and compilation correctness need the current PR's CI checks; no new LaTeX content files were changed in this metadata-only follow-on. The existing tracker [issue #14](https://github.com/Notoriousjayy/latex-docs/issues/14) remains the full semantic review work queue.
