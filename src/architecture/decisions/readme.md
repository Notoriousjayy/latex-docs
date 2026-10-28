# Architecture Decision Record (ADR) Library

Source-first **blank ADR templates** and review guidance. This is not a register of adopted decisions. Documents are independently compilable pdfLaTeX roots using the `technical-design-spec` semantic module.

## Start here

Use the [generic template](templates/adr-generic-template.tex) by default; select a specialized template only when it materially improves the evidence or controls captured. The adopting project retains approval authority and a unique, immutable decision ID.

## Templates

| Template | Use when the architectural choice concerns |
|---|---|
| [Generic ADR](templates/adr-generic-template.tex) | Any architecturally significant decision; default starting point |
| [Cloud platform](templates/adr-cloud-platform-template.tex) | Landing zones, isolation, networks, IAM, cloud provider or service models |
| [Security and privacy](templates/adr-security-and-privacy-template.tex) | Trust boundaries, threat mitigation, authorization, personal data, risk |
| [Data and storage](templates/adr-data-and-storage-template.tex) | Persistence, consistency, ownership, schema evolution, backup or retention |
| [Integration and API](templates/adr-integration-and-api-template.tex) | Sync/async integration, contracts, messaging, ordering and delivery semantics |
| [Delivery and IaC](templates/adr-delivery-and-iac-template.tex) | Terraform, CI/CD, release approval, supply-chain provenance and policy |
| [Resilience and continuity](templates/adr-resilience-and-continuity-template.tex) | Availability patterns, fault domains, failover, RTO/RPO or DR |
| [Observability](templates/adr-observability-template.tex) | Metrics, logs, traces, SLIs/SLOs, alert design and telemetry budgets |
| [Software structure](templates/adr-software-structure-template.tex) | Modules, services, layering, ownership and decomposition |
| [AI and agentic systems](templates/adr-ai-and-agentic-systems-template.tex) | Model choice, RAG, agent tool authority, evaluation and fallback |

Read the [ADR Governance and Review Guide](adr-lifecycle-and-review-guide.tex) for
lifecycle, reviewers, supersession, evidence, traceability, and decision rights.

## Distinguish related artifacts

- [ISO/IEC/IEEE 42010 architecture-description template](../standards/iso-iec-ieee-42010/02-ad-templates.tex):
  complete AD, stakeholder concern coverage, views and correspondences; *AD* is
  **architecture description**, not architecture decision.
- [Correspondence and decision records](../standards/iso-iec-ieee-42010/05-correspondence-decisions.tex):
  decision and rationale traceability within architecture descriptions.
- [Cloud ADR worksheet](../cloud/engineering-suite/05-architecture-documentation-templates.tex):
  shorter cloud assessment and ADR worksheet; remains useful as an entry form.
- [CCoE Decision Log 3.4](../governance/ccoe/execution/3-4-decision-log.tex):
  cross-project decision inventory, not a replacement for a full ADR.
- [Micro-frontend decision framework](../../programming/web/micro-frontends/03-architecture-decision-framework.tex):
  detailed domain guidance; reference as evidence or attach a domain ADR.

## Authoring workflow

1. Copy the generic template, or one specialty only when it changes the
   evidence needed; do **not** create multiple ADRs for the same decision.
2. Assign an immutable ID in the adopting project's own register and name
   the new document `docs/adr/0001-short-title.tex` (or its established AD
   directory). Keep these library templates unchanged.
3. Replace all bracketed prompts. Record owner/authority, problem,
   constraints, alternatives (including the status quo when feasible),
   selected option, disqualifiers, benefits and adverse consequences.
4. Record measurable decision tests, owners, evidence URIs, risk treatment,
   AD/viewpoint/concern links and supersession or review triggers.
5. Review via pull request with architecture, security, operations, product
   and/or data reviewers as appropriate. Only the accountable authority can
   approve the architectural choice. Keep rejection and supersession history.
6. Link decisions from architecture descriptions, CCoE logs, change requests,
   implementation work items and control-evidence records without duplicating
   the complete source artifacts.

### Lifecycle states

`Proposed` → `Accepted` → `Deprecated` or `Superseded`; `Rejected` is
an alternative to acceptance. Acceptance requires explicit accountable
approval, not merely a merge or a colored status badge.

### Build

From the repository root:

```bash
make preflight
make list-roots
make build-category-architecture
# Or use the same canonical helper for this path:
python3 tooling/scripts/latex_build.py build-category architecture
```

PDFs and LaTeX build artifacts must not be committed. The roots use the shared `technical-design-spec` semantic module. Use `make publish` for the full staged PDF corpus; the category command otherwise uses source-adjacent output.

## Traceability model

For architectural decisions relevant to an ISO/IEC/IEEE 42010:2022 AD,
record the relevant architecture-description ID and revision, stakeholder
and concern IDs, viewpoint/view/component IDs, correspondences and known
inconsistencies, plus implementation controls and test/evidence links.
These are locally recommended linking practices, not a claim that an ADR
by itself satisfies the standard.

## Scope boundaries

This library defines **blank ADRs** and governance guidance. It does
not retrospectively label architectural choices within existing guides
as approved ADRs, does not override security/change approval processes,
and does not migrate the existing 42010 AD templates or the CCoE register.
