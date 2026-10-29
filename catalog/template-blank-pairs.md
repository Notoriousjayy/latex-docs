# Template–Blank Pair Catalog

## Usage contract

**Template:** authoritative authoring instructions, evaluation method and section definitions. **Blank:** separate unfilled copy used to begin work. These variants are not evidence that an architecture or security review was performed or approved.

Architecture descriptions and architecture decision records are distinct document types. Completed examples, instructor keys, and technical reference material are never silently overwritten to create a Blank.

## Registered pair inventory

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

## Outstanding semantic-review queue

These are **not compliant pairs yet**. Their original sources are preserved. Inspect each source's fields, criteria, illustrative values, and dependencies before creating a separate variant.

| Current state | Source | Next action |
|---|---|---|
| HYBRID | [application-review-analysis-template.tex](../src/security/application-security/processes/application-review-analysis-template.tex) | Contains an assessment handbook plus reusable review worksheets. Requires field-level separation; do not discard methodology or technical criteria. |
| TEMPLATE_ONLY | [42010-vp-template-polished.tex](../src/architecture/templates/42010-vp-template-polished.tex) | Standalone viewpoint specification with illustrative authoring material; extract blank without discarding required model-kind fields. |
| TEMPLATE_ONLY | [viewpoint-template-polished.tex](../src/architecture/templates/viewpoint-template-polished.tex) | Long standalone viewpoint worksheet with illustrative sections; needs individual semantic review. |
| HYBRID | [02-ad-templates.tex](../src/architecture/standards/iso-iec-ieee-42010/02-ad-templates.tex) | Contains multiple architecture-description registers plus worked examples; separate the required instruments. |
| REVIEW_REQUIRED | [07-conformance-assessment.tex](../src/architecture/standards/iso-iec-ieee-42010/07-conformance-assessment.tex) | Conformance evidence workbook: retain all criteria, standard source mappings, and acceptance scales. |
| REVIEW_REQUIRED | [05-architecture-documentation-templates.tex](../src/architecture/cloud/engineering-suite/05-architecture-documentation-templates.tex) | Multiple embedded architecture forms require independent pairing decisions. |
| REVIEW_REQUIRED | [06-security-governance-templates.tex](../src/architecture/cloud/engineering-suite/06-security-governance-templates.tex) | Security/governance forms require independent artifact identities. |
| REVIEW_REQUIRED | [07-finops-sla-templates.tex](../src/architecture/cloud/engineering-suite/07-finops-sla-templates.tex) | Contains continuity scorecard plus governance templates; extract without inventing scores or thresholds. |
| REVIEW_REQUIRED | [babok-v3-requirements-traceability-templates.tex](../src/business-analysis/templates/babok-v3-requirements-traceability-templates.tex) | Multiple requirements and traceability forms; classify independently. |
| COMPLETED_ONLY | [startup-plan-template-worksheet.tex](../src/startups/templates/startup-plan-template-worksheet.tex) | Completed Smart Building Manager example; preserve unchanged. |
| REVIEW_REQUIRED | [calculus-applications-companion-workbook.tex](../src/mathematics/workbooks/calculus-applications-companion-workbook.tex) | Contains exercises with companion solution source; distinguish learner-facing blank from answer key. |
| NON_TEMPLATE | [calculus-applications-workbook-solutions.tex](../src/mathematics/workbooks/calculus-applications-workbook-solutions.tex) | Solutions and answer key are not blank workbook variants. |
| REVIEW_REQUIRED | [desk-check-algorithm-workbook.tex](../src/programming/algorithms/desk-check-algorithm-workbook.tex) | Needs exercise and response-area preservation while excluding worked solutions. |

## Validation and interpretation

Run `python3 tooling/scripts/validate_artifact_pairs.py` at the repository root. The validator checks registered pair paths, structural headings, distinct contents, leaf READMEs, and new explicitly named `-template.tex` or `-blank.tex` artifacts. It does **not** demonstrate complete semantic alignment, valid scores, conformity to a standard, or successful PDF compilation.

See [audit report](../tooling/reports/template-blank-audit-2026-10-29.md) and [machine-readable manifest](../tooling/manifests/reusable-artifact-pairs.json). The review queue is a prioritized subset, not an exhaustive classification of all embedded forms.

## Source snapshot (2026-10-29)

- `src/` contained 1,054 `.tex` files.
- Sixteen `-template.tex` files were found by strict filename matching; no `-blank.tex` files existed before this change.
- 16 logical pairs are registered in this change.
- Repository-wide pairing completion is **not established** because numerous reusable instruments are embedded in larger documents.
