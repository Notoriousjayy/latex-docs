# Template–Blank Pair Catalog

## Usage contract

**Template:** authoritative authoring instructions, evaluation methodology and section definitions. **Blank:** separate unfilled copy used to begin a real assessment or decision. A Blank never demonstrates that a review was completed or approved.

### Print-ready Blank contract

A **Blank is a printable working form**, not a second instructional template. No bracketed response prompts (`[To complete]`, `[TODO]`, or examples) are permitted in the rendered PDF. Each entry has an empty writing line or response area; evaluation criteria, field labels, rubric definitions and unchecked boxes remain. Bracketed strings used solely for LaTeX syntax (such as package options or description-list labels) are allowed in source because the brackets are not printed. Templates may retain authoring prompts. The validator enforces this rendered-text distinction for registered Blanks, and CI compiles every LaTeX root.

Architecture descriptions and architecture decision records are distinct document types. Completed examples, answer keys and technical references are preserved.

## Enterprise discovery implementation suite

[GitHub Actions Architecture Discovery suite](../src/architecture/github-actions-discovery-suite.md) includes an unchanged technical reference, a project-specific Architecture Description and Viewpoint Specification, and two phase/evidence workbooks. The four paired guided Templates and print-ready Blanks are listed above. Unlike an architecture description, an ADR records one bounded decision; unlike an architecture view, a viewpoint specification defines reusable construction and interpretation conventions.

## Registered pairs

| Logical ID | Family | Template | Blank |
|---|---|---|---|
| ARCH-ADR-AI_AND_AGENTIC_SYSTEMS | architecture-decision-record | [Template](../src/architecture/decisions/templates/adr-ai-and-agentic-systems-template.tex) | [Blank](../src/architecture/decisions/templates/adr-ai-and-agentic-systems-blank.tex) |
| ARCH-ADR-CLOUD_PLATFORM | architecture-decision-record | [Template](../src/architecture/decisions/templates/adr-cloud-platform-template.tex) | [Blank](../src/architecture/decisions/templates/adr-cloud-platform-blank.tex) |
| ARCH-ADR-DATA_AND_STORAGE | architecture-decision-record | [Template](../src/architecture/decisions/templates/adr-data-and-storage-template.tex) | [Blank](../src/architecture/decisions/templates/adr-data-and-storage-blank.tex) |
| ARCH-ADR-DELIVERY_AND_IAC | architecture-decision-record | [Template](../src/architecture/decisions/templates/adr-delivery-and-iac-template.tex) | [Blank](../src/architecture/decisions/templates/adr-delivery-and-iac-blank.tex) |
| ARCH-ADR-GENERIC | architecture-decision-record | [Template](../src/architecture/decisions/templates/adr-generic-template.tex) | [Blank](../src/architecture/decisions/templates/adr-generic-blank.tex) |
| ARCH-ADR-INTEGRATION_AND_API | architecture-decision-record | [Template](../src/architecture/decisions/templates/adr-integration-and-api-template.tex) | [Blank](../src/architecture/decisions/templates/adr-integration-and-api-blank.tex) |
| ARCH-ADR-OBSERVABILITY | architecture-decision-record | [Template](../src/architecture/decisions/templates/adr-observability-template.tex) | [Blank](../src/architecture/decisions/templates/adr-observability-blank.tex) |
| ARCH-ADR-RESILIENCE_AND_CONTINUITY | architecture-decision-record | [Template](../src/architecture/decisions/templates/adr-resilience-and-continuity-template.tex) | [Blank](../src/architecture/decisions/templates/adr-resilience-and-continuity-blank.tex) |
| ARCH-ADR-SECURITY_AND_PRIVACY | architecture-decision-record | [Template](../src/architecture/decisions/templates/adr-security-and-privacy-template.tex) | [Blank](../src/architecture/decisions/templates/adr-security-and-privacy-blank.tex) |
| ARCH-ADR-SOFTWARE_STRUCTURE | architecture-decision-record | [Template](../src/architecture/decisions/templates/adr-software-structure-template.tex) | [Blank](../src/architecture/decisions/templates/adr-software-structure-blank.tex) |
| ARCH-AD-42010 | architecture-description | [Template](../src/architecture/templates/42010-ad-template-polished.tex) | [Blank](../src/architecture/templates/42010-ad-blank.tex) |
| STARTUP-PLAN | planning-worksheet | [Template](../src/startups/templates/startup-plan-template.tex) | [Blank](../src/startups/templates/startup-plan-blank.tex) |
| DOC-LETTERHEAD | correspondence | [Template](../src/documentation/templates/letterhead-template.tex) | [Blank](../src/documentation/templates/letterhead-blank.tex) |
| GAME-GDD | game-design-record | [Template](../src/game-development/templates/game-design-document-gdd-template.tex) | [Blank](../src/game-development/templates/game-design-document-gdd-blank.tex) |
| GAME-GDD-OVERVIEW | game-design-record | [Template](../src/game-development/templates/game-design-document-template.tex) | [Blank](../src/game-development/templates/game-design-document-blank.tex) |
| ARCH-VP-LEGACY | architecture-viewpoint | [Template](../src/architecture/views-and-beyond/advanced-concepts/viewpoint-template.tex) | [Blank](../src/architecture/views-and-beyond/advanced-concepts/viewpoint-blank.tex) |
| ARCH-FINOPS-SLA-WORKBOOK | finops-sla-workbook | [Template](../src/architecture/cloud/engineering-suite/07-finops-sla-templates.tex) | [Blank](../src/architecture/cloud/engineering-suite/07-finops-sla-blank.tex) |
| ARCH-42010-CONFORMANCE-WORKBOOK | architecture-conformance-workbook | [Template](../src/architecture/standards/iso-iec-ieee-42010/07-conformance-assessment.tex) | [Blank](../src/architecture/standards/iso-iec-ieee-42010/07-conformance-assessment-blank.tex) |
| SEC-APPSEC-REVIEW-WORKBOOK | application-security-assessment-workbook | [Template](../src/security/application-security/processes/application-review-analysis-template.tex) | [Blank](../src/security/application-security/processes/application-review-analysis-blank.tex) |

| ARCH-GHA-DISCOVERY-AD | architecture-description | [Template](../src/architecture/templates/github-actions-architecture-discovery-ad-template.tex) | [Blank](../src/architecture/templates/github-actions-architecture-discovery-ad-blank.tex) |
| ARCH-GHA-DISCOVERY-VIEWPOINT | architecture-viewpoint | [Template](../src/architecture/templates/github-actions-architecture-discovery-viewpoint-template.tex) | [Blank](../src/architecture/templates/github-actions-architecture-discovery-viewpoint-blank.tex) |
| ARCH-GHA-DISCOVERY-IMPLEMENTATION | discovery-implementation-workbook | [Template](../src/architecture/workbooks/github-actions-architecture-discovery-implementation-workbook-template.tex) | [Blank](../src/architecture/workbooks/github-actions-architecture-discovery-implementation-workbook-blank.tex) |
| ARCH-GHA-DISCOVERY-EVIDENCE | discovery-evidence-workbook | [Template](../src/architecture/workbooks/github-actions-architecture-discovery-evidence-workbook-template.tex) | [Blank](../src/architecture/workbooks/github-actions-architecture-discovery-evidence-workbook-blank.tex) |

## Priority review queue

The following are **not yet paired or classified to completion**. Original documents remain unchanged.

| State | Source | Remaining decision |
|---|---|---|
| TEMPLATE_ONLY | [42010-vp-template-polished.tex](../src/architecture/templates/42010-vp-template-polished.tex) | Standalone viewpoint specification with illustrative authoring material; extract blank without discarding required model-kind fields. |
| TEMPLATE_ONLY | [viewpoint-template-polished.tex](../src/architecture/templates/viewpoint-template-polished.tex) | Long standalone viewpoint worksheet with illustrative sections; needs individual semantic review. |
| HYBRID | [02-ad-templates.tex](../src/architecture/standards/iso-iec-ieee-42010/02-ad-templates.tex) | Contains multiple architecture-description registers plus worked examples; separate the required instruments. |
| REVIEW_REQUIRED | [05-architecture-documentation-templates.tex](../src/architecture/cloud/engineering-suite/05-architecture-documentation-templates.tex) | Multiple embedded architecture forms require independent pairing decisions. |
| REVIEW_REQUIRED | [06-security-governance-templates.tex](../src/architecture/cloud/engineering-suite/06-security-governance-templates.tex) | Security/governance forms require independent artifact identities. |
| REVIEW_REQUIRED | [babok-v3-requirements-traceability-templates.tex](../src/business-analysis/templates/babok-v3-requirements-traceability-templates.tex) | Multiple requirements and traceability forms; classify independently. |
| COMPLETED_ONLY | [startup-plan-template-worksheet.tex](../src/startups/templates/startup-plan-template-worksheet.tex) | Completed Smart Building Manager example; preserve unchanged. |
| REVIEW_REQUIRED | [calculus-applications-companion-workbook.tex](../src/mathematics/workbooks/calculus-applications-companion-workbook.tex) | Contains exercises with companion solution source; distinguish learner-facing blank from answer key. |
| NON_TEMPLATE | [calculus-applications-workbook-solutions.tex](../src/mathematics/workbooks/calculus-applications-workbook-solutions.tex) | Solutions and answer key are not blank workbook variants. |
| REVIEW_REQUIRED | [desk-check-algorithm-workbook.tex](../src/programming/algorithms/desk-check-algorithm-workbook.tex) | Needs exercise and response-area preservation while excluding worked solutions. |

## Validation boundaries

Run `python3 tooling/scripts/validate_artifact_pairs.py` for structural pairing checks. The existing semantic inventory tracks the original 1,054 canonical `.tex` sources, and the separate governed pairing manifest covers derivative Blank sources. This is an explicit division of responsibilities; neither mechanism independently proves semantic accuracy, scoring integrity, normative conformance, or PDF compilation.

Use the [audit report](../tooling/reports/template-blank-audit-2026-10-29.md) for build status and unresolved scope. The priority review queue does **not** enumerate every embedded instrument within the 1,054 canonical sources.

## Snapshot and counts

- 19 governed Template–Blank pairs, including 10 ADRs, one architecture description, an application security review workbook, a conformance assessment workbook, and a FinOps/SLA workbook with a continuity scorecard.
- 10 documented priority review items; more embedded artifacts may exist.
- Original standalone source count: 1,054 `.tex` documents. No explicitly named `-blank.tex` files existed at baseline.
- Repository-wide 100% completion has **not** been established.

## Algorithm Engineering registered pairs

The nine Algorithm Engineering forms below have print-ready Blank companions and are registered in the machine-readable governance manifest.

| Logical ID | Family | Template | Blank |
|---|---|---|---|
| PROG-ALGO-ALGORITHM_DESIGN_SCORECARD_TEMPLATE | algorithm-assessment | [algorithm-design-scorecard-template.tex](../src/programming/algorithms/algorithm-engineering/templates/algorithm-design-scorecard-template.tex) | [algorithm-design-scorecard-blank.tex](../src/programming/algorithms/algorithm-engineering/blank/algorithm-design-scorecard-blank.tex) |
| PROG-ALGO-BENCHMARK_RUN_SHEET_TEMPLATE | algorithm-assessment | [benchmark-run-sheet-template.tex](../src/programming/algorithms/algorithm-engineering/templates/benchmark-run-sheet-template.tex) | [benchmark-run-sheet-blank.tex](../src/programming/algorithms/algorithm-engineering/blank/benchmark-run-sheet-blank.tex) |
| PROG-ALGO-LABORATORY_ASSESSMENT_TEMPLATE | algorithm-assessment | [laboratory-assessment-template.tex](../src/programming/algorithms/algorithm-engineering/templates/laboratory-assessment-template.tex) | [laboratory-assessment-blank.tex](../src/programming/algorithms/algorithm-engineering/blank/laboratory-assessment-blank.tex) |
| PROG-ALGO-LEARNING_PROGRESS_TRACKER_TEMPLATE | algorithm-assessment | [learning-progress-tracker-template.tex](../src/programming/algorithms/algorithm-engineering/templates/learning-progress-tracker-template.tex) | [learning-progress-tracker-blank.tex](../src/programming/algorithms/algorithm-engineering/blank/learning-progress-tracker-blank.tex) |
| PROG-ALGO-MATHEMATICAL_PROOF_REVIEW_TEMPLATE | algorithm-assessment | [mathematical-proof-review-template.tex](../src/programming/algorithms/algorithm-engineering/templates/mathematical-proof-review-template.tex) | [mathematical-proof-review-blank.tex](../src/programming/algorithms/algorithm-engineering/blank/mathematical-proof-review-blank.tex) |
| PROG-ALGO-ARITHMETIC_AND_NUMERICAL_ACCURACY_WORKBOOK | algorithm-analysis-workbook | [arithmetic-and-numerical-accuracy-workbook.tex](../src/programming/algorithms/algorithm-engineering/workbooks/arithmetic-and-numerical-accuracy-workbook.tex) | [arithmetic-and-numerical-accuracy-workbook-blank.tex](../src/programming/algorithms/algorithm-engineering/blank/arithmetic-and-numerical-accuracy-workbook-blank.tex) |
| PROG-ALGO-ASYMPTOTIC_AND_PROOF_WORKBOOK | algorithm-analysis-workbook | [asymptotic-and-proof-workbook.tex](../src/programming/algorithms/algorithm-engineering/workbooks/asymptotic-and-proof-workbook.tex) | [asymptotic-and-proof-workbook-blank.tex](../src/programming/algorithms/algorithm-engineering/blank/asymptotic-and-proof-workbook-blank.tex) |
| PROG-ALGO-COMBINATORICS_AND_CONSTRAINTS_WORKBOOK | algorithm-analysis-workbook | [combinatorics-and-constraints-workbook.tex](../src/programming/algorithms/algorithm-engineering/workbooks/combinatorics-and-constraints-workbook.tex) | [combinatorics-and-constraints-workbook-blank.tex](../src/programming/algorithms/algorithm-engineering/blank/combinatorics-and-constraints-workbook-blank.tex) |
| PROG-ALGO-RANDOMNESS_AND_STATISTICS_WORKBOOK | algorithm-analysis-workbook | [randomness-and-statistics-workbook.tex](../src/programming/algorithms/algorithm-engineering/workbooks/randomness-and-statistics-workbook.tex) | [randomness-and-statistics-workbook-blank.tex](../src/programming/algorithms/algorithm-engineering/blank/randomness-and-statistics-workbook-blank.tex) |

## Algorithm Analysis and Analytic Combinatorics registered pairs

All nine artifacts have guided authoring forms and separate print-ready blank variants. The pairs are registered in `tooling/manifests/reusable-artifact-pairs.json`.

| Logical ID | Family | Template or Workbook | Blank |
|---|---|---|---|
| PROG-AAC-ALGORITHM-ANALYSIS-RECORD | algorithm-analysis-record | [Source](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/templates/algorithm-analysis-record-template.tex) | [Blank](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/templates/algorithm-analysis-record-blank.tex) |
| PROG-AAC-CAPSTONE-REVIEW | algorithm-analysis-record | [Source](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/templates/capstone-review-template.tex) | [Blank](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/templates/capstone-review-blank.tex) |
| PROG-AAC-EXPERIMENT-PLAN | algorithm-analysis-record | [Source](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/templates/experiment-plan-template.tex) | [Blank](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/templates/experiment-plan-blank.tex) |
| PROG-AAC-LABORATORY-REPORT | algorithm-analysis-record | [Source](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/templates/laboratory-report-template.tex) | [Blank](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/templates/laboratory-report-blank.tex) |
| PROG-AAC-PROOF-ASSESSMENT | algorithm-analysis-record | [Source](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/templates/proof-assessment-template.tex) | [Blank](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/templates/proof-assessment-blank.tex) |
| PROG-AAC-ASYMPTOTIC-ANALYSIS | algorithm-analysis-workbook | [Source](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/workbooks/asymptotic-analysis-workbook.tex) | [Blank](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/workbooks/asymptotic-analysis-workbook-blank.tex) |
| PROG-AAC-COMBINATORIAL-STRUCTURES | algorithm-analysis-workbook | [Source](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/workbooks/combinatorial-structures-workbook.tex) | [Blank](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/workbooks/combinatorial-structures-workbook-blank.tex) |
| PROG-AAC-GENERATING-FUNCTIONS | algorithm-analysis-workbook | [Source](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/workbooks/generating-functions-workbook.tex) | [Blank](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/workbooks/generating-functions-workbook-blank.tex) |
| PROG-AAC-RECURRENCE-ANALYSIS | algorithm-analysis-workbook | [Source](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/workbooks/recurrence-analysis-workbook.tex) | [Blank](../src/programming/algorithms/algorithm-analysis-and-analytic-combinatorics/workbooks/recurrence-analysis-workbook-blank.tex) |
