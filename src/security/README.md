# Security

## Overview

Security engineering references, assessment workflows, standards mappings, learning plans and operational runbooks. Start with the workflow or control family relevant to the problem; these documents are not claims of product compliance or a deployed security program.

## Scope and boundaries

Use this domain for AppSec, security architecture, security programs, standards, and security operations. Software design decisions belong in [Architecture](../architecture/README.md), while delivery automation belongs in [DevOps](../devops/README.md).

## Directory map and documentation catalog

| Area | What it contains | Sources |
|---|---|---:|
| [`application-security/`](application-security/) | Application assessments, vulnerabilities, DAST/SAST, program processes and field guides. | 65 |
| [`certifications/`](certifications/) | Role- and certification-oriented study material. | 3 |
| [`cloud-security/`](cloud-security/) | Cloud security engineering and cloud security curricula. | 2 |
| [`enterprise-security/`](enterprise-security/) | Enterprise security architecture and operations. | 1 |
| [`github-advanced-security/`](github-advanced-security/) | Code scanning, dependency alerts, secret scanning and GHAS operations. | 36 |
| [`governance-risk-compliance/`](governance-risk-compliance/) | ISMS, risk and SOC 2 control engineering. | 10 |
| [`infrastructure-security/`](infrastructure-security/) | Infrastructure protection and hardening. | 1 |
| [`security-engineering/`](security-engineering/) | General security engineering methods and references. | 8 |
| [`standards/`](standards/) | CIS, OWASP, ISO/IEC 27000-family and related standards material. | 24 |

## Build and validate

```bash
make preflight
make build-category-security
make list-roots
```

The category command discovers standalone LaTeX roots and builds them with the shared pdfLaTeX toolchain. To stage PDFs under `public/pdfs/`, use `make publish` from the repository root. The commands above describe the supported interface; they do not imply that every root has been compiled in this change.

## Recommended navigation

- Use the [AppSec process diagrams](application-security/processes/appsec-process-diagrams/readme.md) as cross-tool workflow references, not evidence that a named integration is deployed.

- Distinguish vulnerability identification, validation, prioritization, remediation and exception approval in operational playbooks.

- For architecture-level trade-offs, start with [security and privacy ADR templates](../architecture/decisions/readme.md).

## Maintenance conventions

- Verify dated standards, product features and benchmark versions against authoritative publications before operational use.

- Do not store real credentials, incident details, customer identifiers or sensitive assessments in this public repository.

- Link rules and procedures to actual evidence; avoid presenting guidance as certification or audit attestation.

## Related domains

- [DevOps delivery and platform documentation](../devops/README.md)

- [Source catalog](../README.md)
