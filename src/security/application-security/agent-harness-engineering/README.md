# Agent Harness Engineering for Application Security

[LaTeX technical study](agent-harness-engineering-for-application-security.tex) — **Architecture, Design Patterns, Security Controls, and Enterprise Implementation** (v1.0, proposed reference design, 24 November 2026).

## Study contents

- Architecture description organized around ISO/IEC/IEEE 42010:2022 concepts, six C4/UML viewpoints, twelve requirements, and five proposed ADRs.
- Deterministic orchestration, tool brokering, policy decisions, state and evidence management, and trust boundaries.
- SAST, DAST, IAST, SCA, secret scanning, secure code review, contextual remediation, coding-agent governance and CI/CD.
- Python reference example, Rego policy illustration, MCP/Agent Skills integration, threat model, evaluation metrics, production deployment, operational runbooks and nine progressive labs.
- Source register and requirement-to-test traceability.

## Architecture views

| View | Source |
|---|---|
| V1 — system context | [PlantUML](diagrams/appsec-context.puml) |
| V2 — containers | [PlantUML](diagrams/appsec-containers.puml) |
| V3 — orchestration components | [PlantUML](diagrams/appsec-components.puml) |
| V4 — investigation interaction | [PlantUML](diagrams/appsec-investigation-sequence.puml) |
| V5 — lifecycle | [PlantUML](diagrams/appsec-lifecycle.puml) |
| V6 — deployment | [PlantUML](diagrams/appsec-deployment.puml) |

All diagrams use the repository's shared PlantUML style. Generated images are build products. The document includes rendered PNGs when present; otherwise it includes a labeled source reference and summary, so it can compile without generated images.

## Build and validate

From the repository root:

```bash
make preflight
python3 tooling/scripts/plantuml_lint.py
make render-plantuml
make build-category-security
```

For the standalone document, set the house-style search paths from the root, then compile from this suite directory:

```bash
export TEXINPUTS="$(pwd)/tooling/latex//:$(pwd)/tooling/styles/latex//:${TEXINPUTS:-}"
cd src/security/application-security/agent-harness-engineering
latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error -file-line-error agent-harness-engineering-for-application-security.tex
python3 -m unittest discover -s examples -v
python3 examples/harness_demo.py
```

Python 3.10+; standard library only. The example is intentionally synchronous and read-only, with synthetic metadata and no network access. It is not a production authentication, policy, sandbox or audit implementation. No real secrets, live targets, organization-specific findings or credentials are included.

## Related documentation

- [AI Agent Engineering](../../../data-systems/ai-agent-engineering/README.md)
- [Enterprise Code Scanning Triage Governance](../../github-advanced-security/code-scanning/enterprise-triage-governance/README.md)
- [Repository PlantUML framework](../../../../tooling/plantuml/README.md)

## Status and provenance

The source is authoritative. The study uses original proposed controls and training examples informed by official reference pages reviewed on 24 November 2026. It does not assert ISO conformance, operational deployment, empirical quality metrics or regulatory compliance. Check CI and diagram render results before treating the document as build-verified.
