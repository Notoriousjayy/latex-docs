# Cloud Architecture and Engineering

Vendor-neutral cloud-computing references, design guidance and diagrams. The collection separates general mechanisms and architecture patterns from technology-specific implementation decisions.

## Collections

| Collection | Material |
|---|---|
| [Cloud concepts and architecture](concepts-technology-architecture/) | Eighteen chapter-oriented source files addressing models, mechanisms, security, architectures, economics and SLAs. |
| [Cloud engineering suite](engineering-suite/) | Seven engineering, learning, governance, documentation and FinOps guides. |
| [Architecture and diagram library](architecture/) | Diagram sets, architecture index and self-hosting cloud references. |

| [Secure AWS Terraform repository and deployment architecture](secure-aws-terraform-repository-deployment/README.md) | AWS multi-account governance, Terraform deployment roles/state, trust diagrams, six ADRs, and reference workflows. |

## Suggested use

1. Start with `concepts-technology-architecture/` for definitions, mechanisms and service-model assumptions.
2. Use `engineering-suite/` to translate the principles into an architecture plan.
3. Select and adapt diagrams from the [PlantUML collection](architecture/cloud-architecture-diagram-library/readme.md), preserving their modeled scope.
4. Document trade-offs with [ADRs](../decisions/readme.md) and confirm platform-specific details before IaC implementation.

## Build

```bash
make preflight
make build-category-architecture
make render-plantuml
```

These commands build documents and diagrams; they do not provision, test or secure a cloud environment.

## Engineering controls

Check IAM boundaries, regional constraints, data handling, network segmentation, resilience, recoverability, service quotas, operational evidence and current provider guidance for every real deployment.

## Related

[Architecture](../README.md) · [Cloud security](../../security/cloud-security/)
