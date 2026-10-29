# GitHub Actions Architecture Discovery — Engineering Documentation Suite

## Purpose

This collection turns the enterprise-scale GitHub Actions architecture discovery **technical reference** into controlled, project-ready design and engineering records. The reference describes the methodology; the Template documents provide field-level authoring guidance; the printable Blanks are empty forms for project-specific evidence and handwriting.

The discovery engine is intended to run as a **GitHub Action** over authorized repositories within a GitHub organization or enterprise installation. A repository is not necessarily an application, and parsed CI relationships do **not** prove live runtime dependencies.

## Sources and working documents

| Artifact | Guided source | Printable working form |
|---|---|---|
| **Reference methodology** | [Enterprise discovery technical reference](technical-documents/github-actions-architecture-discovery-enterprise-scale.tex) | Not a fill-in form |
| **Architecture Description (AD)** | [AD Template](templates/github-actions-architecture-discovery-ad-template.tex) | [AD Blank](templates/github-actions-architecture-discovery-ad-blank.tex) |
| **Architecture Viewpoint Specification (AVS)** | [Viewpoint Template](templates/github-actions-architecture-discovery-viewpoint-template.tex) | [Viewpoint Blank](templates/github-actions-architecture-discovery-viewpoint-blank.tex) |
| **Implementation workbook** | [Implementation Template](workbooks/github-actions-architecture-discovery-implementation-workbook-template.tex) | [Implementation Blank](workbooks/github-actions-architecture-discovery-implementation-workbook-blank.tex) |
| **Evidence and validation workbook** | [Evidence Template](workbooks/github-actions-architecture-discovery-evidence-workbook-template.tex) | [Evidence Blank](workbooks/github-actions-architecture-discovery-evidence-workbook-blank.tex) |

All eight forms are separate, standalone LaTeX roots. **Blank variants have no printed bracketed instruction text, sample answers, claimed approval, or automatically completed assessment.** Labels, control questions, traceability structures, and unchecked boxes remain. The Template is for authors preparing a form; the Blank is for actual project completion.

## Phase-to-document crosswalk

| Stage | Engineering work | Principal record |
|---|---|---|
| 0 — Control plane | Authorized organization scope, permissions, data classification and denominators | Implementation workbook; AD context and security boundaries |
| 1 — Collector | GitHub Action triggers, pinned revisions, read-only APIs, pagination and checkpointing | Implementation workbook; AD logical architecture |
| 2 — Monorepos | Workspace manifests, component identity, build targets and ambiguity | Implementation workbook; viewpoint conventions |
| 3 — Graph and evidence | Stable node and edge IDs, evidence classes and provenance | Viewpoint specification; evidence workbook; AD data views |
| 4 — Correlation | Registries, release records, IaC, deployment verification and cross-repository mapping | Evidence workbook; AD correspondence views |
| 5 — Governance | Catalog access, review, drift, ownership reconciliation and handover | AD review records; evidence workbook; implementation gates |

Record major choices about GitHub App scope, storage, identity, confidence and retention in separate project ADRs, using [ADR Templates](decisions/readme.md), then cross-reference the AD. An AVS describes reusable view construction and interpretation; it is **not** an ADR or a completed view.

## Evidence integrity rules

1. **Observed (E1):** directly parsed workflow or manifest configuration at a pinned revision.
2. **Inferred (E2):** versioned matching rule with recorded uncertainty; never represent it as independently verified.
3. **Externally verified (E3):** corroboration by deployment records, registry digests, approved service catalog or owner attestation.
4. Keep access-denied, missing, truncated, stale, parse-error and unresolved states distinct.
5. Retain immutable source path/URI, commit SHA, parser and extraction rule version, collection timestamp, and validation evidence for every published relationship.
6. Maintain separate coverage, precision and recall measures for CI topology, component inference, and deployment confirmation.

## Recommended authoring sequence

Read the technical reference; open a copy of the AD **Blank** to record the actual platform scope; use the Viewpoint **Template** to define E1/E2/E3 semantics and the Blank to document the selected view conventions; fill the implementation workbook by phase; validate samples in the evidence workbook before publishing a production architecture catalog. Record any unsatisfied gate as an open finding rather than inventing a pass.

## Build and governance

From the repository root:

```bash
python3 tooling/scripts/validate_artifact_pairs.py
python3 -m unittest discover -s tests -p 'test_enterprise_discovery_suite.py'
make preflight
make build-category-architecture
```

The pair manifest is [`tooling/manifests/reusable-artifact-pairs.json`](../../tooling/manifests/reusable-artifact-pairs.json), and the central [Template–Blank catalog](../../catalog/template-blank-pairs.md) also indexes the four pairs. PDF output is a build artifact; **LaTeX is the canonical source**. An empty form is not evidence of review or ISO/IEC/IEEE 42010 conformance.
