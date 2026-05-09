# Security

The largest documentation domain: AppSec, GitHub Advanced Security,
certifications, cloud security, and standards (CIS, OWASP).

## Scope

**Belongs here:**
- Application-security programs, processes, and field guides.
- GHAS operational SOPs, runbooks, and cheatsheets.
- Certification study plans (CISSP, CCSP, CISO, GH-500).
- Cloud-security user-story sequences.
- Standards mappings (CIS benchmarks, OWASP Top 10 / API Top 10).

**Does not belong here:**
- General CI/CD content — see `../devops/`.
- Language-level secure-coding rules — see `../programming/languages/<lang>/secure-coding/`.

## Contents

| Child | Purpose |
|---|---|
| `application-security/` | AppSec fundamentals, learning paths, processes, programs, web-security field guides. |
| `certifications/` | CISSP, CISO, GH-500 study plans. |
| `cloud-security/` | Cloud-computing security user-story sequences. |
| `github-advanced-security/` | GHAS administration, code scanning (CodeQL), Dependabot, references, secret scanning. |
| `standards/` | CIS benchmarks; OWASP Top 10 (2025) and API Security Top 10. |

## Conventions

- **Triage SOPs** end with `-triage-sop.tex`.
- **Closure runbooks** end with `-runbook.tex` or `-playbook.tex`.
- **Cheatsheets** live in the relevant `references/` folder, never
  alongside the operational SOP they reference.
- **Field guides** live under `web-security/<vuln-class>/field-guides/<short-slug>/field-guide.tex`.
- **Process diagrams** for AppSec sit in
  `application-security/processes/appsec-process-diagrams/`.

## Building

```bash
make build-category-security
```

## Related

- `../README.md`
- `../programming/languages/c-cpp/standards/misra/` for MISRA rules.
- `../programming/languages/java/secure-coding/` for Oracle CERT rules.



