# AppSec PlantUML Process Set (Preserved + Extended)

This bundle contains a **preserved** set of AppSec process diagrams, extended to include:

- **SonarQube** quality + security gates
- A **non-compliant application** handling process
- A **16-gate CI/CD pipeline overlay** that crosswalks AppSec processes/tools to each gate
- **Application Code (AppCode)** as the correlation key across repos, tools, and ticketing

## How to render

Use any PlantUML renderer (CLI or IDE plugin). Each `.puml` is standalone and includes the shared style:

- `puml/appsec-style.puml`

## Diagrams

1. `01-application-onboarding.puml` — App onboarding + coverage plan (AppCode)
2. `02-homegrown-ci-security-gates.puml` — Homegrown CI security gates (SonarQube + GHAS + Trivy)
3. `03-sast-analysis-and-triage.puml` — Static analysis triage (GHAS + Coverity + SonarQube)
4. `04-sca-dependency-vuln-management.puml` — SCA/dependencies (GHAS + Trivy SBOM)
5. `05-secret-scanning-response.puml` — Secret response (GHAS)
6. `06-container-iac-scanning-trivy.puml` — Container/IaC/SBOM (Trivy)
7. `07-dast-insightappsec.puml` — DAST lifecycle (InsightAppSec)
8. `08-iast-seeker-verified.puml` — IAST verified findings (Seeker)
9. `09-vulnerability-management-lifecycle.puml` — Unified vulnerability lifecycle (all sources)
10. `10-cots-saas-vendor-vuln-management.puml` — Vendor-led remediation (COTS/SaaS)
11. `11-sonarqube-quality-security-gate.puml` — SonarQube quality/security gate
12. `12-non-compliant-application-handling.puml` — Non-compliant handling + enforcement
13. `13-16-gate-cicd-appsec-overlay.puml` — 16-gate CI/CD pipeline AppSec overlay

## Conventions

- **Left-to-right** flow, limited palette, clear partitions, labeled decisions
- **AppCode** is referenced in every process where ownership/correlation matters
- Gates are marked with the `<<gate>>` stereotype for consistent highlighting
