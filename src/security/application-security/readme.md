# Application Security

Engineering references for application-security assessment, software auditing, DAST/IAST, secure delivery, vulnerability management and operational program design.

## Navigate

| Area | Coverage |
|---|---|
| [Assessment](assessment/) | Structured assessment suite, testing and labs. |
| [Auditing](auditing/) | Code-review techniques and audit catalogs. |
| [DAST](dast/) | Dynamic testing and tool guides. |
| [Fundamentals](fundamentals/) | Program foundations and secure SDLC concepts. |
| [IAST](iast/) | Interactive application security testing. |
| [Learning](learning/) | Learning paths and course selection. |
| [SAST](sast/) | Secure programming, static analysis, practical laboratories, CI/CD, assessments and printable Template–Blank forms. |
| [Processes](processes/) | Program processes and [PlantUML diagrams](processes/appsec-process-diagrams/readme.md). |

## Language-specific secure coding standards

The standards previously stored beneath this AppSec collection now live with their actual programming languages. See the [secure coding guide by language](../../programming/languages/README.md) and the [cross-language GHAS secure coding catalog](../github-advanced-security/references/ghas-secure-coding-standards-handout.tex). Keep language-neutral secure SDLC assessment controls here.

## Operational sequence

1. Establish authorization, target coverage, risk ownership and testing constraints.
2. Gather SAST, SCA, DAST, IAST and runtime evidence as appropriate.
3. Validate and de-duplicate findings; prioritize by exposure, exploitability and impact.
4. Link remediation, exceptions, approvals and closure evidence to owners and service records.

## Build and review

```bash
make preflight
make build-category-security
make render-plantuml
```

These commands validate documentation outputs, not live product integrations or vulnerability closures.

## Security boundaries

Do not execute testing outside an authorized scope or include customer vulnerabilities, real credentials or sensitive architecture details in a public source artifact. Verify product features and APIs against their supported current releases.

## Related

[Security catalog](../README.md) · [DevOps](../../devops/README.md)
