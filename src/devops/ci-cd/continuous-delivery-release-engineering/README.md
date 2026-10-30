# Continuous Delivery, CI/CD and Release Engineering Documentation Suite

**Canonical repository location:** `src/devops/ci-cd/continuous-delivery-release-engineering/`  
**Book foundation:** Jez Humble and David Farley, *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation* (2010).  
**Edition prepared:** 2026-10-30. **Scope:** Original supplementary learning and engineering materials, not a reproduction of copyrighted text.

## What this suite contains

| Collection | Purpose |
| --- | --- |
| [Study guides](study-guides/README.md) | 15 chapter-aligned conceptual guides, exercises and evidence rubrics |
| [Curriculum](curriculum/README.md) | Prerequisite-based 16-week plan and final capstone assessment |
| [Technical documents](technical-documents/README.md) | Architecture, testing, data, artifact provenance, release, security, observability and traceability references |
| [Laboratories](laboratories/README.md) | Twelve hands-on labs, including GitHub Actions, Terraform, AWS, migration and rollback |
| [Workbooks](workbooks/README.md) | Six printable Template–Blank workbook pairs |
| [Templates](templates/README.md) | Eight printable Template–Blank controlled-record pairs |
| [Scorecards](scorecards/README.md) | Three printable Template–Blank engineering assessment pairs |
| [Examples](examples/README.md) | Non-active GitHub Actions workflows, runnable Python, example Terraform, IAM trust, SQL and validation scripts |
| [Diagrams](diagrams/README.md) | PlantUML pipeline, trust-boundary and migration diagrams |

## Source-of-truth separation

**Book-derived structure:** Chapters 1–15 and their Part I/II/III sequence, covering configuration management, CI, testing, the deployment pipeline, scripts, acceptance, nonfunctional requirements, deployments, environments, data, dependencies, version control, and governance.

**Original modern engineering extensions:** GitHub Actions, Terraform, IAM/OIDC, AWS Lambda, artifact digest and attestation, modern security gates, SLO/latency measurement, and progressive release design. These technologies are discussed as contemporary extensions rather than incorrectly attributed to the 2010 text. Study guides paraphrase the topic at a conceptual level without extensive book excerpts.

## Book chapter crosswalk

| Ch. | Chapter | Study guide |
| ---: | --- | --- |
| 1 | The Problem of Delivering Software | [chapter-01-the-problem-of-delivering-software.tex](study-guides/chapter-01-the-problem-of-delivering-software.tex) |
| 2 | Configuration Management | [chapter-02-configuration-management.tex](study-guides/chapter-02-configuration-management.tex) |
| 3 | Continuous Integration | [chapter-03-continuous-integration.tex](study-guides/chapter-03-continuous-integration.tex) |
| 4 | Implementing a Testing Strategy | [chapter-04-implementing-a-testing-strategy.tex](study-guides/chapter-04-implementing-a-testing-strategy.tex) |
| 5 | Anatomy of the Deployment Pipeline | [chapter-05-anatomy-of-the-deployment-pipeline.tex](study-guides/chapter-05-anatomy-of-the-deployment-pipeline.tex) |
| 6 | Build and Deployment Scripting | [chapter-06-build-and-deployment-scripting.tex](study-guides/chapter-06-build-and-deployment-scripting.tex) |
| 7 | The Commit Stage | [chapter-07-the-commit-stage.tex](study-guides/chapter-07-the-commit-stage.tex) |
| 8 | Automated Acceptance Testing | [chapter-08-automated-acceptance-testing.tex](study-guides/chapter-08-automated-acceptance-testing.tex) |
| 9 | Testing Nonfunctional Requirements | [chapter-09-testing-nonfunctional-requirements.tex](study-guides/chapter-09-testing-nonfunctional-requirements.tex) |
| 10 | Deploying and Releasing Applications | [chapter-10-deploying-and-releasing-applications.tex](study-guides/chapter-10-deploying-and-releasing-applications.tex) |
| 11 | Managing Infrastructure and Environments | [chapter-11-managing-infrastructure-and-environments.tex](study-guides/chapter-11-managing-infrastructure-and-environments.tex) |
| 12 | Managing Data | [chapter-12-managing-data.tex](study-guides/chapter-12-managing-data.tex) |
| 13 | Managing Components and Dependencies | [chapter-13-managing-components-and-dependencies.tex](study-guides/chapter-13-managing-components-and-dependencies.tex) |
| 14 | Advanced Version Control | [chapter-14-advanced-version-control.tex](study-guides/chapter-14-advanced-version-control.tex) |
| 15 | Managing Continuous Delivery | [chapter-15-managing-continuous-delivery.tex](study-guides/chapter-15-managing-continuous-delivery.tex) |

## Start here

1. Follow the [prerequisite curriculum](curriculum/prerequisite-based-curriculum.tex), then read the matching study guide and technical reference.
2. Run laboratories locally before attempting any cloud deployment. Lab examples reside under `examples/` and do not activate GitHub Actions automatically.
3. For each gate, capture a reproducible result, an intentional negative test, the source and artifact identities, and a reviewer.
4. Complete an assessment with the corresponding scorecard; use the Blank edition for printed records.

### Local build and validation

```bash
python -m unittest discover -s examples/lambda -p 'test_*.py' -v
python -m unittest discover -s examples/scripts -p 'test_*.py' -v
python tests/validate_structure.py
# From latex-docs repository root after integration:
make preflight
make build-category-devops
```

All LaTeX files are standalone roots (`\documentclass`). The package can be copied into `src/devops/ci-cd/` without changes to existing material. Do not commit generated `.pdf`, `.aux`, `.log`, `.zip`, `.tfstate`, or `.tfplan` unless the repository explicitly requires the artifact.

## Cloud safety boundaries

The supplied Terraform, IAM trust JSON, and GitHub Actions workflows are instructional examples, not production deployments. They require account isolation, a real security review, existing guarded remote state, exact role trust conditions, approved environment controls, and deployment budget limits. Do not apply without review. The provided canary example is a **simulation**; it does not change AWS routing. Terraform Lambda alias updates shown in the example are all-at-once.

## Selected official external references (modern additions)

- [GitHub: OIDC in AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
- [GitHub: Actions security hardening](https://docs.github.com/en/actions/how-tos/secure-your-work)
- [HashiCorp: saved Terraform plans](https://developer.hashicorp.com/terraform/cli/commands/apply)
- [HashiCorp: state locking](https://developer.hashicorp.com/terraform/language/state/locking)
- [AWS IAM: OIDC role creation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html)
- [AWS CodeDeploy: Lambda deployment process](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-steps-lambda.html)

## Relationship to other repository collections

Use existing [`src/devops/github-actions/`](../../github-actions/README.md) for GitHub-specific quick references and [`src/architecture/cloud/secure-aws-terraform-repository-deployment/`](../../../architecture/cloud/secure-aws-terraform-repository-deployment/README.md) for cloud architecture standards. Repository-wide catalogs of scorecards, templates, and workbooks should index these canonical files after integration rather than duplicate the content.

## Review and maintenance

Revalidate cloud tool versions, runner/action SHA pinning, IAM trust claims, provider APIs, Terraform backend settings and AWS deployment semantics before operational use. The book remains a foundational text; supplementary implementations may evolve as vendor platforms change.
