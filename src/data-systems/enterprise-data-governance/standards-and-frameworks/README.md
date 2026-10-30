# Data Governance Standards and Frameworks Reference

**Status:** Proposed enterprise governance engineering material. No official ISO normative text, proprietary official DCAM assessment instrument, legal opinion, or compliance certification is included.

## Deliverables

| Requested artifact | LaTeX source |
|---|---|
| 1. Standards and Frameworks Technical Reference | [Technical reference](technical-documents/standards-and-frameworks-technical-reference.tex) |
| 2. Governance Framework Selection and Applicability Matrix | [Template](templates/governance-framework-selection-and-applicability-matrix-template.tex) / [Blank](templates/governance-framework-selection-and-applicability-matrix-blank.tex) |
| 3. Standards-to-Enterprise-Control Traceability Workbook | [Template](workbooks/standards-to-enterprise-control-traceability-workbook-template.tex) / [Blank](workbooks/standards-to-enterprise-control-traceability-workbook-blank.tex) |
| 5. DCAM-Based Capability Assessment Scorecard | [Template](scorecards/dcam-based-capability-assessment-scorecard-template.tex) / [Blank](scorecards/dcam-based-capability-assessment-scorecard-blank.tex) |
| 6. Data Governance Regulatory Applicability Register | [Template](registers/data-governance-regulatory-applicability-register-template.tex) / [Blank](registers/data-governance-regulatory-applicability-register-blank.tex) |
| 7. Data Quality and Metadata Standards Crosswalk | [Template](templates/data-quality-and-metadata-standards-crosswalk-template.tex) / [Blank](templates/data-quality-and-metadata-standards-crosswalk-blank.tex) |
| 8. Governance Compliance Evidence Register | [Template](registers/governance-compliance-evidence-register-template.tex) / [Blank](registers/governance-compliance-evidence-register-blank.tex) |
| 4. Governance Roles and Decision Rights Specification | [Roles and decision rights](technical-documents/governance-roles-and-decision-rights-specification.tex) |

## Leaf directories

- [technical-documents](technical-documents/README.md)
- [templates](templates/README.md)
- [workbooks](workbooks/README.md)
- [scorecards](scorecards/README.md)
- [registers](registers/README.md)

## How to apply

1. Classify the authority: law, standard, body of knowledge, governance framework or capability model.
2. Verify the edition, part and legal/business applicability.
3. Select a reference and approve its policy/control objectives.
4. Map requirements to business ownership, conceptual/logical/physical models, enforcement points and test cases.
5. Register protected evidence and assess operating effectiveness.
6. Address exceptions, retain findings and revalidate after changes.

**Traceability chain:** Source/edition → applicability → policy → control → owner → system implementation → verification evidence → finding → approved closure.

## Source and license boundary

See [Publisher source register](SOURCE-REGISTER.md). ISO 8000, ISO/IEC 11179 and ISO/IEC 5259 are multi-part series. ISO/IEC 38505-1:2026 supersedes the 2017 edition. EDM Association DCAM v3's eight components, 34 capabilities and 101 sub-capabilities are publicly described, but this suite's rating heuristic is an original local self-assessment, **not** an official DCAM score. Law applicability requires professional legal review.

## Template–Blank contract

Every operational instrument is published in two independent, standalone root `.tex` files. Guided Templates contain authoring notes; the print-ready Blank companion contains only headings, field labels and empty writing boxes for responses. No bracketed instructions, completed answers, invented scores or approval placeholders appear in the rendered Blanks.

## Build and pairing validation

From repository root:

```sh
python3 tooling/scripts/validate_artifact_pairs.py
make preflight
make build-category-data-systems
```

Compile results and visual pagination are not presumed successful until checked through CI or local PDF builds. Completed operational forms and confidential evidence should not be committed to this public repository.

## Related material

- [Enterprise Data Modeling and Database Architecture](../../enterprise-data-modeling/README.md)
- [Data Systems index](../../README.md)
- [Enterprise Data Governance](../README.md)
