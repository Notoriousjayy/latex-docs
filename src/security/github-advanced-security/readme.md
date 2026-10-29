# GitHub Advanced Security Engineering

Technical source documentation for administering and operating GitHub security features. The materials are reusable guidance; they do **not** establish that an account or repository has a particular license, feature enabled or deployed security controls.

## Explore

| Area | Scope |
|---|---|
| [administration/](administration) | Permissions, enablement and policy |
| [code-scanning/](code-scanning) | Analysis, CodeQL and finding triage |
| [dependabot/](dependabot) | Dependency vulnerability management |
| [references/](references) | Commands, terms and operational reference |
| [secret-scanning/](secret-scanning) | Exposed secret response and prioritization |

## Operating workflow

1. Confirm plan/feature availability, policies, permissions and current product behavior.
2. Establish repository coverage, owners, alert routing and risk-based prioritization.
3. Verify findings; track remediation, exception approval and closure evidence.
4. Revoke/rotate confirmed exposed secrets and investigate their usage as appropriate.
5. Pilot configuration changes in a representative, nonproduction repository before broad rollout.

## Build

```bash
make preflight
make build-category-security
```

These commands compile LaTeX references; they do not change GitHub settings or run code/security scanning. Keep production secrets and real incident details out of public documentation.

## Related

[Security catalog](../README.md) · [DevOps](../../devops/README.md)
