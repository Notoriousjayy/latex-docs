# CI/CD engineering

CI/CD and continuous integration guidance for the DevOps domain. This collection preserves pre-existing sources and adds a separately governed engineering suite.

## Collections

| Resource | Scope |
|---|---|
| [Continuous Integration and CI/CD Engineering Documentation Suite](continuous-integration-engineering/README.md) | Nine chapter guides, curriculum, engineering references, labs, security, architecture, benchmarking, and Template–Blank pairs |
| [Continuous Delivery and Release Engineering Suite](continuous-delivery-release-engineering/README.md) | 15 book-aligned chapter guides, 16-week curriculum, 12 labs, AWS/Terraform deployment exercises, release governance, and 17 printable Template–Blank pairs |\n| [Foundations](fundamentals/) | Existing CI/CD foundational references |
| [Pipelines](pipelines/) | Existing delivery-pipeline materials |
| [Diagrams](diagrams/) | Existing delivery diagrams |
| [Pre-read briefing](pre-read-briefing.tex) | Existing LaTeX briefing |

## Governance and validation

The suite's example workflows are located under `continuous-integration-engineering/examples/workflows/` and are not activated in `.github/workflows/`. Pair metadata for both CI and Continuous Delivery is registered in `tooling/manifests/reusable-artifact-pairs.json`.

From the repository root, run `make preflight`, `make build-category-devops`, and `python3 tooling/scripts/validate_artifact_pairs.py`. For local exercise checks see the suite README.

[DevOps domain](../README.md) · [Suite index](continuous-integration-engineering/README.md)
