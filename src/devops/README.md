# DevOps

Continuous delivery, version control, GitHub Actions, GitOps,
platform-engineering targets, and secrets management.

## Scope

**Belongs here:**
- CI/CD pipeline content, including GitHub Actions.
- SDLC, version-control, and GitHub-platform foundations.
- Platform targets (Kubernetes, Nginx).
- Secrets-management runbooks (HashiCorp Vault).

**Does not belong here:**
- AppSec gates inside CI — see `../security/application-security/`.
- GHAS-specific operational content — see `../security/github-advanced-security/`.

## Contents

| Child | Purpose |
|---|---|
| `ci-cd/` | CI/CD fundamentals, pipelines, and cross-cutting CI diagrams. |
| `foundations/` | SDLC fundamentals, Git, and base GitHub literacy. |
| `github-actions/` | GitHub Actions guides, workflow attribute references, custom actions. |
| `gitops/` | GitOps stack blueprints. |
| `platform/` | GitHub-platform hygiene, Kubernetes user stories, Nginx cookbooks. |
| `secrets-management/` | HashiCorp Vault primers and runbooks. |

## Conventions

- Workflow guides live under `github-actions/`; pipeline architecture
  lives under `ci-cd/pipelines/`. Don't mix the two.
- Cross-cutting CI diagrams (used by multiple roots) live in
  `ci-cd/diagrams/`; per-document diagrams co-locate.

## Building

```bash
make build-category-devops
```

## Related

- `../README.md`
- `../security/github-advanced-security/` (CI security gates).
- `../../tooling/plantuml/config.puml` (shared PlantUML config).
