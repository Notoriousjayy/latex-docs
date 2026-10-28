# Application Security Process Diagrams

Thirteen source-controlled PlantUML workflows for secure SDLC integration, application onboarding, security testing and vulnerability management. Named tools are **reference integrations**, not claims of currently deployed automation or control effectiveness.

## Diagram inventory

| Diagram source | Process |
|---|---|
| [01-app-onboarding-coverage-plan.puml](01-app-onboarding-coverage-plan.puml) | Onboarding and coverage plan |
| [02-homegrown-ci-sec-gates-shift-left.puml](02-homegrown-ci-sec-gates-shift-left.puml) | Shift-left CI security gates |
| [03-static-analysis-ghas-coverity-sonarqube.puml](03-static-analysis-ghas-coverity-sonarqube.puml) | SAST analysis and triage |
| [04-sca-dependency-vuln-mgmt-ghas-trivy.puml](04-sca-dependency-vuln-mgmt-ghas-trivy.puml) | SCA and dependency vulnerability management |
| [05-secret-scanning-response-ghas.puml](05-secret-scanning-response-ghas.puml) | Secret scanning and response |
| [06-container-iac-scanning-trivy.puml](06-container-iac-scanning-trivy.puml) | Container, IaC and SBOM scanning |
| [07-dast-lifecycle-rapid7-insightappsec.puml](07-dast-lifecycle-rapid7-insightappsec.puml) | DAST lifecycle and InsightAppSec |
| [08-iast-verified-vulns-seeker.puml](08-iast-verified-vulns-seeker.puml) | IAST and verified findings |
| [09-unified-vuln-mgmt-lifecycle-all-sources.puml](09-unified-vuln-mgmt-lifecycle-all-sources.puml) | Unified vulnerability-management lifecycle |
| [10-cots-saas-vuln-mgmt-vendor-led-fixes.puml](10-cots-saas-vuln-mgmt-vendor-led-fixes.puml) | Vendor-managed COTS/SaaS remediation |
| [11-sonarqube-quality-sec-gate-pr-main.puml](11-sonarqube-quality-sec-gate-pr-main.puml) | SonarQube quality and security gates |
| [12-non-compliant-app-handling-coverage-slas.puml](12-non-compliant-app-handling-coverage-slas.puml) | Non-compliant application handling |
| [13-16-gate-ci-cd-pipeline-appsec-overlay.puml](13-16-gate-ci-cd-pipeline-appsec-overlay.puml) | Sixteen-gate CI/CD AppSec overlay |

## Render and validate

```bash
make render-plantuml
python3 tooling/scripts/plantuml_lint.py
```

Run from the repository root. Source `.puml` files are in this directory; rendered images are organized in `png/`, `svg/` and `jpg/`. Apply [the shared PlantUML framework](../../../../../tooling/plantuml/README.md) when extending a workflow.

## Interpretation

- **AppCode** is the conceptual correlation identifier for application ownership, repositories, security findings and tickets.
- Security gates represent decisions. Define evidence, policy owners, exceptions and enforcement scope when adapting them.
- Verify vendor functionality and license conditions for the target environment before implementation.
- Do not publish credentials, customer findings or live incident evidence in the diagrams.

## Related

[Application Security](../../readme.md)
