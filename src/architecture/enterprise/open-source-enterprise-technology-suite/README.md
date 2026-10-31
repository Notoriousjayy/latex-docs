# Open-Source Enterprise Technology Architecture and Operations Suite

**Status:** proposed reference architecture; not a certification, completed control assessment, or production-approved configuration. **Version:** 1.0.0 (2026-10-31). **Primary source:** three existing `latex-docs` LaTeX documents, referenced in place; the originals are not copied or modified.

## Design intent

Integrate application security, security engineering, IAM, ITAM/ITSM, governance, delivery, learning, customer operations and carefully segregated finance decisions under a unified enterprise technology architecture. **Do not deploy everything:** overlap resolution, license/edition review, threat modeling and proven recoverability precede selection.

## Inputs preserved elsewhere

| Source | Role |
|---|---|
| [src/security/technical-documents/open-source-enterprise-security-platform.tex](../../../security/technical-documents/open-source-enterprise-security-platform.tex) | Multi-tier security architecture, OSS tool discovery and qualification; candidates are not automatically approved. |
| [src/security/application-security/operations-stack/enterprise-appsec-operations-stack-handout.tex](../../../security/application-security/operations-stack/enterprise-appsec-operations-stack-handout.tex) | Eleven-tool AppSec, GRC, ITAM/ITSM and delivery stack. GHAS is a commercial exception. |
| [src/personal/finance/open-source-financial-tools-handout.tex](../../../personal/finance/open-source-financial-tools-handout.tex) | Six personal/desktop/self-hosted finance tools; **not** a business ERP selection. |

## Navigation

- **References:** `reference/00-` through `reference/11-` cover scope, provenance, product overlap, data contracts, trust boundaries, financial isolation, licensing, controls, rollout, roles, recovery, and architecture assurance.
- **Operator runbooks:** `runbooks/rb-01` through `rb-06` for identity, findings, source-of-truth reconciliation, recovery, upgrades and privacy incidents.
- **Architecture decisions:** `adrs/adr-0001` through `adr-0005` record proposed, reviewable trade-offs (not signed decisions).
- **Reusable forms:** `templates/` and matching print-friendly `blanks/` contain 11 one-to-one authoring Template/Blank pairs.
- **Machine-checkable registers:** `registers/*.csv` (tools, integrations, controls, waves, authoritative ownership).
- **Diagrams:** `diagrams/*.puml` (text-only PlantUML source; render via repository toolchain after integration).
- **Governance:** `manifest.json` inventories deliverables and `validate_suite.py` validates pairing, references, consistency and optional local compilation.

## Integration guardrails

1. **Identity:** federate Authentik or existing enterprise IdP only where application edition/protocol is tested; access policy remains inside each app.
2. **ITAM/ITSM:** GLPI inventory vs. iTop service/CI/change is a proposed split. Do not enable competing owners for the same attribute.
3. **AppSec:** GHAS is proprietary. Semgrep OSS + Gitleaks is a candidate OSS-first SAST/secrets route; Trivy, ZAP, IAST and SBOM tools remain context-dependent.
4. **Evidence and delivery:** immutable raw findings -> normalized unique ID -> service ownership -> Taiga story/points/sprint -> Eramba independent risk decision -> verified retest. Native APIs are not assumed.
5. **Finance:** GnuCash may suit small-business bookkeeping only after qualification. Actual, Firefly III, HomeBank, Money Manager Ex and Ghostfolio address different personal finance use cases, not general enterprise accounting. Keep bank credentials and transaction records in a separate trust zone.
6. **Quality:** unmapped assets, unknown license status, untested restores and silent event loss are hard release blockers.

## Read / implement sequence

Read `reference/00`, `01`, `02` and `04`; complete tool/ownership Templates; use `reference/03` and `registers/integration-register.csv` to design connectors; apply `reference/07` and `08` for controls and delivery; execute runbooks and archive evidence; complete architecture review and acceptance forms. Planning waves are indicative, not a delivery promise.

## Build and validate

```bash
python3 validate_suite.py
python3 validate_suite.py --compile  # optional; requires pdflatex
# From latex-docs repository root after integration:
make preflight
make build-category-architecture
```

All TeX documents are standalone pdfLaTeX roots; no external fonts or includes. Printable Blank files have labeled empty writing areas and no filled example responses. LaTeX remains the source of truth; generated PDFs are build artifacts.

## Cross-links to existing repository standards

Use existing `src/architecture/c4-model/documentation-suite/` for C4 viewpoint governance and `src/architecture/decisions/` for ADR conventions, `src/data-systems/enterprise-data-governance/` for broader data governance, and `src/architecture/cloud/secure-aws-terraform-repository-deployment/` for cloud-specific IaC boundaries. These are complementary rather than duplicated here.

## Source and verification links

- [NIST Cybersecurity Framework 2.0](https://www.nist.gov/cyberframework), for broad function themes (not a certification claim).
- [Authentik OIDC provider documentation](https://docs.goauthentik.io/add-secure-apps/providers/oauth2/), federation capability; each application still requires validation.
- [GLPI asset documentation](https://help.glpi-project.org/documentation/modules/assets), inventory scope.
- [OWASP ZAP](https://www.zaproxy.org/), authorized dynamic testing.
- [CycloneDX](https://cyclonedx.org/) and [SPDX](https://spdx.dev/), SBOM exchange options.
- [OSI approved licenses](https://opensource.org/licenses), legal qualification reference.

**Publication note:** primary repository source versions and tool revisions must be rechecked at implementation time. No production connector, compliance conformance or live access is asserted.
